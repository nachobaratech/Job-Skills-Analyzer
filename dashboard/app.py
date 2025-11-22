import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from athena_helper import AthenaHelper
import numpy as np
from collections import defaultdict
from itertools import combinations
import boto3
from botocore.exceptions import ClientError
import json

st.set_page_config(
    page_title="Job Skills Intelligence Platform", 
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# AUTHENTICATION SYSTEM
# ============================================================================

class CognitoAuth:
    """AWS Cognito Authentication Handler"""
    
    def __init__(self):
        self.user_pool_id = "us-east-1_dl3mvEfzR"
        self.client_id = "1i80rbk9u5rkf34m6n60ocs7vj"
        self.region = "us-east-1"
        
        try:
            self.client = boto3.client('cognito-idp', region_name=self.region)
        except Exception as e:
            self.client = None
    
    def authenticate(self, username, password):
        """Authenticate user with Cognito"""
        if not self.client:
            return None, "Cognito client not initialized"
        
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            if 'AuthenticationResult' in response:
                return response['AuthenticationResult'], None
            else:
                return None, "Authentication failed"
                
        except ClientError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
    
    def sign_up(self, email, password):
        """Sign up a new user with Cognito using email as username"""
        if not self.client:
            return None, "Cognito client not initialized"
        
        try:
            response = self.client.sign_up(
                ClientId=self.client_id,
                Username=email,  # Use email as username
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email}
                ]
            )
            return response, None
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                return None, "This email is already registered. Please sign in."
            elif error_code == 'InvalidPasswordException':
                return None, "Password does not meet requirements. Must be at least 8 characters with uppercase, lowercase, number, and special character."
            elif error_code == 'InvalidParameterException':
                return None, "Invalid email format. Please enter a valid email address."
            else:
                return None, str(e)
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
    
    def confirm_signup(self, username, confirmation_code):
        """Confirm user signup with verification code"""
        if not self.client:
            return None, "Cognito client not initialized"
        
        try:
            response = self.client.confirm_sign_up(
                ClientId=self.client_id,
                Username=username,
                ConfirmationCode=confirmation_code
            )
            return response, None
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'CodeMismatchException':
                return None, "Invalid verification code. Please check the code and try again."
            elif error_code == 'ExpiredCodeException':
                return None, "Verification code has expired. Please request a new code."
            elif error_code == 'NotAuthorizedException':
                return None, "User is already confirmed."
            else:
                return None, str(e)
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
    
    def resend_confirmation_code(self, username):
        """Resend confirmation code to user"""
        if not self.client:
            return None, "Cognito client not initialized"
        
        try:
            response = self.client.resend_confirmation_code(
                ClientId=self.client_id,
                Username=username
            )
            return response, None
        except ClientError as e:
            return None, str(e)
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"

if 'cognito_auth' not in st.session_state:
    st.session_state.cognito_auth = CognitoAuth()

def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def login_page():
    """Display professional login page"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; padding: 40px;'>
            <h1 style='color: #1e3a8a; font-size: 2.5em; margin-bottom: 10px; font-weight: 600;'>Job Skills Intelligence Platform</h1>
            <p style='color: #64748b; font-size: 1.1em; font-weight: 400;'>Real-time Job Market Analytics & Insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("### Secure Login")
            
            username = st.text_input(
                "Email Address", 
                placeholder="your.email@example.com",
                key="login_username"
            )
            password = st.text_input(
                "Password", 
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("Sign In", use_container_width=True, type="primary"):
                    if username and password:
                        with st.spinner("Authenticating..."):
                            auth_result, error = st.session_state.cognito_auth.authenticate(username, password)
                    
                            if auth_result:
                                st.session_state.authenticated = True
                                st.session_state.username = username
                                st.session_state.id_token = auth_result.get('IdToken')
                                st.session_state.access_token = auth_result.get('AccessToken')
                                st.success("Welcome back!")
                                st.rerun()
                            else:
                                st.error(f"Authentication failed: {error}")
                    else:
                        st.warning("Please enter both email and password")
            
            with col_b:
                if st.button("Demo Access", use_container_width=True):
                    st.session_state.authenticated = True
                    st.session_state.username = "demo_user"
                    st.session_state.demo_mode = True
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Link to sign up
            col_center = st.columns([1, 1, 1])[1]
            with col_center:
                if st.button("Don't have an account? Sign Up", use_container_width=True, type="secondary"):
                    st.session_state.show_signup = True
                    st.rerun()

def signup_page():
    """Display professional sign up page"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; padding: 40px;'>
            <h1 style='color: #1e3a8a; font-size: 2.5em; margin-bottom: 10px; font-weight: 600;'>Create Your Account</h1>
            <p style='color: #64748b; font-size: 1.1em; font-weight: 400;'>Join the Job Skills Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("### Sign Up")
            
            email = st.text_input(
                "Email Address", 
                placeholder="your.email@example.com",
                key="signup_email",
                help="Your email will be used as your username to sign in"
            )
            
            password = st.text_input(
                "Password", 
                type="password",
                placeholder="Create a strong password",
                key="signup_password",
                help="Must be at least 8 characters with uppercase, lowercase, number, and special character"
            )
            
            confirm_password = st.text_input(
                "Confirm Password", 
                type="password",
                placeholder="Re-enter your password",
                key="signup_confirm_password"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("Create Account", use_container_width=True, type="primary"):
                    if email and password and confirm_password:
                        if password != confirm_password:
                            st.error("Passwords do not match!")
                        elif len(password) < 8:
                            st.error("Password must be at least 8 characters long!")
                        else:
                            with st.spinner("Creating your account..."):
                                result, error = st.session_state.cognito_auth.sign_up(email, password)
                                
                                if result:
                                    st.success("Account created successfully! Please check your email for a 6-digit verification code.")
                                    # Store email for verification step
                                    st.session_state.verification_email = email
                                    st.session_state.show_verification = True
                                    st.session_state.show_signup = False
                                    import time
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error(f"Sign up failed: {error}")
                    else:
                        st.warning("Please fill in all fields")
            
            with col_b:
                if st.button("Back to Login", use_container_width=True):
                    st.session_state.show_signup = False
                    st.rerun()

def verification_page():
    """Display email verification page"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; padding: 40px;'>
            <h1 style='color: #1e3a8a; font-size: 2.5em; margin-bottom: 10px; font-weight: 600;'>Verify Your Email</h1>
            <p style='color: #64748b; font-size: 1.1em; font-weight: 400;'>Enter the 6-digit code sent to your email</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            # Show the email address being verified
            verification_email = st.session_state.get('verification_email', '')
            st.info(f"Verification code sent to: **{verification_email}**")
            
            st.markdown("### Enter Verification Code")
            
            # 6-digit code input
            verification_code = st.text_input(
                "6-Digit Code",
                placeholder="976899",
                max_chars=6,
                key="verification_code",
                help="Check your email inbox for the verification code"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("Verify", use_container_width=True, type="primary"):
                    if verification_code and len(verification_code) == 6:
                        with st.spinner("Verifying your account..."):
                            result, error = st.session_state.cognito_auth.confirm_signup(
                                verification_email, 
                                verification_code
                            )
                            
                            if result:
                                st.success("Email verified successfully! You can now sign in.")
                                # Clear verification state
                                st.session_state.show_verification = False
                                st.session_state.verification_email = None
                                import time
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"Verification failed: {error}")
                    else:
                        st.warning("Please enter a 6-digit verification code")
            
            with col_b:
                if st.button("Resend Code", use_container_width=True):
                    with st.spinner("Resending verification code..."):
                        result, error = st.session_state.cognito_auth.resend_confirmation_code(verification_email)
                        
                        if result:
                            st.success("Verification code resent! Check your email.")
                        else:
                            st.error(f"Failed to resend code: {error}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Link back to login
            col_center = st.columns([1, 1, 1])[1]
            with col_center:
                if st.button("Back to Login", use_container_width=True, type="secondary"):
                    st.session_state.show_verification = False
                    st.session_state.show_signup = False
                    st.rerun()

# ============================================================================
# PROFESSIONAL CSS STYLING
# ============================================================================

st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #f8fafc;
    }
    
    /* Headers - formal, no emojis */
    h1, h2, h3 {
        color: #1e293b;
        font-weight: 600;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar - professional look */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%);
        border-right: 1px solid #e2e8f0;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Remove radio button styling - make it clean list */
    .stRadio > div {
        background-color: transparent;
        border: none;
    }
    
    .stRadio > div > label {
        background-color: white;
        padding: 12px 16px;
        border-radius: 6px;
        border: 1px solid #e2e8f0;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s;
        display: block;
        font-weight: 500;
        color: #475569;
    }
    
    .stRadio > div > label:hover {
        border-color: #3b82f6;
        background-color: #f8fafc;
    }
    
    .stRadio > div > label[data-checked="true"] {
        background-color: #3b82f6;
        border-color: #3b82f6;
        color: white;
        font-weight: 600;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5em;
        color: #1e40af;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        color: #64748b;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
        border: none;
        font-family: 'Inter', sans-serif;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Tabs - formal rectangular style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f1f5f9;
        padding: 4px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 6px;
        border: none;
        color: #64748b;
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e2e8f0;
        color: #1e293b;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #1e40af;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        font-weight: 500;
        color: #1e293b;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #3b82f6;
        background-color: #f8fafc;
    }
    
    /* Data tables */
    .dataframe {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px;
    }
    
    /* Remove extra padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Professional card styling */
    .professional-card {
        background: white;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 0.5rem;
    }
    
    /* Insight boxes */
    .insight-box {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        padding: 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        margin: 16px 0;
    }
    
    /* Skill category boxes */
    .skill-category {
        background: white;
        border-left: 4px solid;
        padding: 16px;
        border-radius: 6px;
        margin: 12px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .skill-category.high-demand {
        border-left-color: #dc2626;
        background: linear-gradient(90deg, #fef2f2 0%, white 100%);
    }
    
    .skill-category.moderate-demand {
        border-left-color: #f59e0b;
        background: linear-gradient(90deg, #fffbeb 0%, white 100%);
    }
    
    .skill-category.low-demand {
        border-left-color: #3b82f6;
        background: linear-gradient(90deg, #eff6ff 0%, white 100%);
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #10b981 100%);
        border-radius: 4px;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_resource
def get_athena():
    return AthenaHelper()

@st.cache_data(ttl=300)
def load_all_data():
    """Load and cache all data from Athena"""
    athena = get_athena()
    stats_df = athena.get_job_stats()
    skills_df = athena.get_top_skills(limit=100)
    skills_df["job_count"] = skills_df["job_count"].astype(int)
    skills_df["percentage"] = skills_df["percentage"].astype(float)
    return stats_df, skills_df

@st.cache_data(ttl=300)
def get_all_jobs_with_skills():
    """Get all jobs with their skills from Athena"""
    athena = get_athena()
    
    query = """
    SELECT id, title, company, skills, skill_count
    FROM jobs_with_skills
    WHERE skill_count > 0
    """
    
    return athena.run_query(query)

@st.cache_data(ttl=300)
def parse_skills_from_string(skills_str):
    """Parse skills array from string format"""
    if not skills_str or skills_str == '[]':
        return []
    
    skills_str = skills_str.strip('[]').replace("'", "").replace('"', '')
    skills = [s.strip() for s in skills_str.split(',') if s.strip()]
    
    return skills

@st.cache_data(ttl=300)
def calculate_skill_cooccurrence(min_support=5):
    """Calculate real skill co-occurrence from Athena data"""
    jobs_df = get_all_jobs_with_skills()
    
    cooccurrence = defaultdict(int)
    skill_frequencies = defaultdict(int)
    
    for _, row in jobs_df.iterrows():
        skills = parse_skills_from_string(row['skills'])
        
        for skill in skills:
            skill_frequencies[skill] += 1
        
        if len(skills) >= 2:
            for skill1, skill2 in combinations(sorted(skills), 2):
                pair_key = f"{skill1}|||{skill2}"
                cooccurrence[pair_key] += 1
    
    results = []
    for pair, count in cooccurrence.items():
        if count >= min_support:
            skill1, skill2 = pair.split('|||')
            results.append({
                'skill1': skill1,
                'skill2': skill2,
                'count': count,
                'skill1_freq': skill_frequencies[skill1],
                'skill2_freq': skill_frequencies[skill2]
            })
    
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values('count', ascending=False)
    
    return df

@st.cache_data(ttl=300)
def get_skills_for_job_title(job_keyword):
    """Get skills required for jobs matching the keyword"""
    athena = get_athena()
    
    query = f"""
    SELECT skills, skill_count
    FROM jobs_with_skills
    WHERE LOWER(title) LIKE '%{job_keyword.lower()}%'
    AND skill_count > 0
    """
    
    jobs_df = athena.run_query(query)
    
    if jobs_df.empty:
        return None
    
    skill_counts = defaultdict(int)
    total_jobs = len(jobs_df)
    
    for _, row in jobs_df.iterrows():
        skills = parse_skills_from_string(row['skills'])
        for skill in skills:
            skill_counts[skill] += 1
    
    result = pd.DataFrame([
        {'skill': skill, 'job_count': count, 'percentage': (count / total_jobs) * 100}
        for skill, count in skill_counts.items()
    ])
    
    return result.sort_values('job_count', ascending=False)

@st.cache_data(ttl=300)
def get_common_job_titles(limit=20):
    """Get most common job titles"""
    athena = get_athena()
    
    query = f"""
    SELECT title, COUNT(*) as count
    FROM jobs_with_skills
    WHERE skill_count > 0
    GROUP BY title
    ORDER BY count DESC
    LIMIT {limit}
    """
    
    df = athena.run_query(query)
    return df['title'].tolist() if not df.empty else []

@st.cache_data(ttl=300)
def get_job_titles_by_skills(selected_skills):
    """Find jobs that match selected skills"""
    jobs_df = get_all_jobs_with_skills()
    
    matching_jobs = []
    
    for _, row in jobs_df.iterrows():
        job_skills = parse_skills_from_string(row['skills'])
        
        if not job_skills:
            continue
        
        matching = set(selected_skills) & set(job_skills)
        missing = set(job_skills) - set(selected_skills)
        
        match_percentage = (len(matching) / len(job_skills)) * 100 if job_skills else 0
        
        matching_jobs.append({
            'title': row['title'],
            'company': row['company'],
            'total_required': len(job_skills),
            'total_matched': len(matching),
            'match_percentage': match_percentage,
            'matching_skills': list(matching),
            'missing_skills': list(missing)
        })
    
    return sorted(matching_jobs, key=lambda x: x['match_percentage'], reverse=True)

@st.cache_data(ttl=300)
def calculate_seniority_stats():
    """Calculate statistics by seniority level"""
    jobs_df = get_all_jobs_with_skills()
    
    # Convert skill_count to numeric
    jobs_df['skill_count'] = pd.to_numeric(jobs_df['skill_count'], errors='coerce')
    
    seniority_map = {
        'Junior': ['junior', 'entry', 'associate', 'jr'],
        'Mid-Level': ['mid', 'intermediate', 'level ii', 'level 2'],
        'Senior': ['senior', 'sr', 'lead', 'principal', 'staff'],
        'Manager': ['manager', 'director', 'head of', 'vp', 'chief'],
        'Other': []
    }
    
    jobs_df['seniority'] = 'Other'
    
    for seniority, keywords in seniority_map.items():
        for keyword in keywords:
            mask = jobs_df['title'].str.lower().str.contains(keyword, na=False)
            jobs_df.loc[mask, 'seniority'] = seniority
    
    stats = jobs_df.groupby('seniority').agg({
        'skill_count': 'mean',
        'id': 'count'
    }).reset_index()
    
    stats.columns = ['seniority', 'avg_skills', 'job_count']
    
    seniority_skills = {}
    for seniority in stats['seniority']:
        seniority_jobs = jobs_df[jobs_df['seniority'] == seniority]
        skill_counts = defaultdict(int)
        
        for _, row in seniority_jobs.iterrows():
            skills = parse_skills_from_string(row['skills'])
            for skill in skills:
                skill_counts[skill] += 1
        
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        seniority_skills[seniority] = [skill for skill, _ in top_skills]
    
    return stats, seniority_skills

# ============================================================================
# ENHANCED CHART FUNCTIONS
# ============================================================================

def create_top_skills_treemap(skills_df):
    """Create treemap for better visualization of top skills"""
    top_20 = skills_df.head(20).copy()
    
    fig = px.treemap(
        top_20,
        path=['skill'],
        values='job_count',
        color='percentage',
        color_continuous_scale='Blues',
        title='Top 20 Skills Market Share'
    )
    
    fig.update_traces(
        textposition="middle center",
        textfont=dict(size=14, color='black', family='Arial, sans-serif'),
        hovertemplate='<b>%{label}</b><br>Jobs: %{value}<br>Market Share: %{color:.1f}%<extra></extra>'
    )
    
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig

def create_skills_comparison_chart(skills_df):
    """Create combined bar and line chart"""
    top_20 = skills_df.head(20).copy()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(
            x=top_20['skill'],
            y=top_20['job_count'],
            name='Number of Jobs',
            marker_color='#3b82f6',
            text=top_20['job_count'],
            textposition='outside',
            textfont=dict(size=10)
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=top_20['skill'],
            y=top_20['percentage'],
            name='Market Penetration (%)',
            line=dict(color='#dc2626', width=3),
            mode='lines+markers',
            marker=dict(size=8)
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Skill", tickangle=-45)
    fig.update_yaxes(title_text="Number of Jobs", secondary_y=False)
    fig.update_yaxes(title_text="Market Penetration (%)", secondary_y=True)
    
    fig.update_layout(
        title='Top 20 Skills: Absolute Demand vs Market Penetration',
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_skill_pairing_heatmap(cooccur_df):
    """Create heatmap for skill pairings"""
    if cooccur_df.empty or len(cooccur_df) < 5:
        return None
    
    top_pairs = cooccur_df.head(25)
    
    # Get unique skills
    all_skills = set()
    for _, row in top_pairs.iterrows():
        all_skills.add(row['skill1'])
        all_skills.add(row['skill2'])
    
    skill_list = sorted(list(all_skills))
    
    # Create matrix
    matrix = pd.DataFrame(0, index=skill_list, columns=skill_list)
    
    for _, row in top_pairs.iterrows():
        matrix.loc[row['skill1'], row['skill2']] = row['count']
        matrix.loc[row['skill2'], row['skill1']] = row['count']
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix.values,
        x=matrix.columns,
        y=matrix.index,
        colorscale='Blues',
        text=matrix.values,
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='%{y} + %{x}<br>Co-occurrence: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Skill Co-occurrence Heatmap',
        height=600,
        xaxis_title='',
        yaxis_title='',
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig

def create_seniority_grouped_chart(seniority_stats):
    """Create grouped bar chart for seniority analysis"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=seniority_stats['seniority'],
        y=seniority_stats['avg_skills'],
        name='Avg Skills Required',
        marker_color='#3b82f6',
        text=seniority_stats['avg_skills'].round(1),
        textposition='outside',
        yaxis='y',
        offsetgroup=0
    ))
    
    fig.add_trace(go.Bar(
        x=seniority_stats['seniority'],
        y=seniority_stats['job_count'],
        name='Number of Jobs',
        marker_color='#10b981',
        text=seniority_stats['job_count'].astype(int),
        textposition='outside',
        yaxis='y2',
        offsetgroup=1
    ))
    
    fig.update_layout(
        title='Skills Requirements and Job Volume by Seniority',
        yaxis=dict(title='Average Skills Required'),
        yaxis2=dict(title='Number of Jobs', overlaying='y', side='right'),
        barmode='group',
        height=500,
        legend=dict(x=0.01, y=0.99),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main_dashboard():
    """Main dashboard interface"""
    
    # Professional Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("# Job Skills Intelligence Platform")
        st.markdown("**Comprehensive Job Market Analytics Dashboard**")
    with col2:
        if st.session_state.get('demo_mode'):
            st.info("Demo Access")
        else:
            st.success(f"Logged in: {st.session_state.get('username', 'User')}")
        
        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Load data
    try:
        stats_df, all_skills_df = load_all_data()
        
        total_jobs = int(stats_df["total_jobs"].iloc[0])
        jobs_with_skills = int(stats_df["jobs_with_skills"].iloc[0])
        avg_skills = float(stats_df["avg_skills"].iloc[0])
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Professional Sidebar
    with st.sidebar:
        st.markdown("## Dashboard Navigation")
        
        view_mode = st.radio(
            "Select Analysis View",
            [
                "Market Overview",
                "Skills for Jobs",
                "Jobs for You",
                "Skill Pairings",
                "Seniority Analysis",
                "Deep Dive"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.markdown("### Key Metrics")
        st.metric("Total Jobs", f"{total_jobs:,}")
        st.metric("Unique Skills", len(all_skills_df))
        st.metric("Avg Skills per Job", f"{avg_skills:.1f}")
        st.metric("Coverage Rate", f"{(jobs_with_skills/total_jobs)*100:.1f}%")
        
        st.markdown("---")
        
        st.markdown("### Data Source")
        st.caption("Database: AWS Athena")
        st.caption(f"Jobs Analyzed: {jobs_with_skills:,}")
        st.caption("Update Frequency: Real-time")
    
    # KPI Metrics
    st.markdown("## Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", f"{total_jobs:,}", help="Total number of job postings analyzed")
    
    with col2:
        coverage = (jobs_with_skills / total_jobs) * 100
        st.metric("Jobs with Skills", f"{jobs_with_skills:,}", f"{coverage:.1f}% coverage")
    
    with col3:
        st.metric("Avg Skills Required", f"{avg_skills:.1f}", help="Average skills per job posting")
    
    with col4:
        st.metric("Unique Skills", f"{len(all_skills_df)}", help="Total distinct skills identified")
    
    st.markdown("---")
    
    # =============================================================================
    # MAIN CONTENT
    # =============================================================================
    
    if view_mode == "Market Overview":
        tabs = st.tabs(["Top Skills Analysis", "Skill Demand Distribution"])
        
        with tabs[0]:
            st.markdown("## Top Skills in the Job Market")
            
            # Treemap visualization
            st.plotly_chart(create_top_skills_treemap(all_skills_df), use_container_width=True)
            
            st.markdown("---")
            
            # Combined chart
            st.plotly_chart(create_skills_comparison_chart(all_skills_df), use_container_width=True)
            
            st.markdown("---")
            
            # Detailed skills table
            st.markdown("### Comprehensive Skills Ranking")
            
            display_df = all_skills_df.head(20).copy()
            display_df['rank'] = range(1, len(display_df) + 1)
            display_df = display_df[['rank', 'skill', 'job_count', 'percentage']]
            display_df.columns = ['Rank', 'Skill', 'Job Count', 'Market Share (%)']
            display_df['Market Share (%)'] = display_df['Market Share (%)'].round(2)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
        
        with tabs[1]:
            st.markdown("## Skill Demand Distribution Analysis")
            
            # Categorize skills
            high_demand = all_skills_df[all_skills_df['percentage'] >= 20].copy()
            moderate_demand = all_skills_df[(all_skills_df['percentage'] >= 10) & (all_skills_df['percentage'] < 20)].copy()
            emerging_skills = all_skills_df[(all_skills_df['percentage'] >= 5) & (all_skills_df['percentage'] < 10)].copy()
            niche_skills = all_skills_df[all_skills_df['percentage'] < 5].copy()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribution pie chart
                categories = pd.DataFrame({
                    'Category': ['High Demand (≥20%)', 'Moderate Demand (10-20%)', 'Emerging Skills (5-10%)', 'Niche Skills (<5%)'],
                    'Count': [len(high_demand), len(moderate_demand), len(emerging_skills), len(niche_skills)]
                })
                
                fig = px.pie(
                    categories,
                    values='Count',
                    names='Category',
                    title='Skills Distribution by Demand Level',
                    color_discrete_sequence=['#dc2626', '#f59e0b', '#3b82f6', '#6366f1']
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=600, paper_bgcolor='white')
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Summary statistics
                st.markdown("### Distribution Statistics")
                
                st.markdown("""
                <div class='professional-card'>
                    <h4 style='margin-top: 0;'>High Demand Skills</h4>
                    <p style='font-size: 2em; margin: 10px 0; color: #dc2626;'>{}</p>
                    <p style='color: #64748b;'>Market share ≥ 20%</p>
                </div>
                """.format(len(high_demand)), unsafe_allow_html=True)
                
                st.markdown("""
                <div class='professional-card'>
                    <h4 style='margin-top: 0;'>Moderate Demand Skills</h4>
                    <p style='font-size: 2em; margin: 10px 0; color: #f59e0b;'>{}</p>
                    <p style='color: #64748b;'>Market share 10-20%</p>
                </div>
                """.format(len(moderate_demand)), unsafe_allow_html=True)
                
                st.markdown("""
                <div class='professional-card'>
                    <h4 style='margin-top: 0;'>Emerging & Niche Skills</h4>
                    <p style='font-size: 2em; margin: 10px 0; color: #3b82f6;'>{}</p>
                    <p style='color: #64748b;'>Market share < 10%</p>
                </div>
                """.format(len(emerging_skills) + len(niche_skills)), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Detailed breakdowns in professional format - REORDERED
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### Niche & Specialized Skills")
                st.caption("Specialized skills for specific roles")
                
                # Show first 10 niche skills
                for idx, row in niche_skills.head(10).iterrows():
                    st.markdown(f"""
                    <div class='skill-category low-demand'>
                        <strong>{row['skill']}</strong><br>
                        <small>{row['job_count']} jobs • {row['percentage']:.1f}% market share</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add expander for remaining niche skills
                if len(niche_skills) > 10:
                    with st.expander(f"➕ Show {len(niche_skills) - 10} more niche skills"):
                        for idx, row in niche_skills.iloc[10:].iterrows():
                            st.markdown(f"""
                            <div class='skill-category low-demand'>
                                <strong>{row['skill']}</strong><br>
                                <small>{row['job_count']} jobs • {row['percentage']:.1f}% market share</small>
                            </div>
                            """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### Moderate Demand Skills")
                st.caption("Important skills with growing presence")
                
                for idx, row in moderate_demand.head(10).iterrows():
                    st.markdown(f"""
                    <div class='skill-category moderate-demand'>
                        <strong>{row['skill']}</strong><br>
                        <small>{row['job_count']} jobs • {row['percentage']:.1f}% market share</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("### High Demand Skills")
                st.caption("Essential skills with highest market penetration")
                
                for idx, row in high_demand.head(10).iterrows():
                    st.markdown(f"""
                    <div class='skill-category high-demand'>
                        <strong>{row['skill']}</strong><br>
                        <small>{row['job_count']} jobs • {row['percentage']:.1f}% market share</small>
                    </div>
                    """, unsafe_allow_html=True)
        

    
    elif view_mode == "Skills for Jobs":
        st.markdown("## Skills Requirements by Job Title")
        st.caption("Analyze specific skills required for different job positions")
        
        common_titles = get_common_job_titles()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_mode = st.radio(
                "Search Method",
                ["Search by keyword", "Select from common titles"],
                horizontal=True
            )
        
        if search_mode == "Search by keyword":
            job_keyword = st.text_input("Enter job title (e.g., 'Data Analyst', 'Software Engineer')")
        else:
            job_keyword = st.selectbox("Select a job title", common_titles)
        
        if job_keyword:
            with st.spinner(f"Analyzing jobs matching '{job_keyword}'..."):
                skills_for_job = get_skills_for_job_title(job_keyword)
            
            if skills_for_job is not None and not skills_for_job.empty:
                st.success(f"Analysis complete: {len(skills_for_job)} skills identified across matching positions")
                
                st.markdown("---")
                
                # Better visualization - horizontal bar chart
                top_skills = skills_for_job.head(20)
                
                # Dynamic title with actual number of skills
                num_skills_shown = len(top_skills)
                
                fig = px.bar(
                    top_skills,
                    y='skill',
                    x='percentage',
                    orientation='h',
                    title=f"Top {num_skills_shown} Skills for '{job_keyword}' Positions",
                    labels={'percentage': 'Required in % of Jobs', 'skill': 'Skill'},
                    color='percentage',
                    color_continuous_scale='RdYlGn',
                    text='percentage'
                )
                
                fig.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside',
                    textfont=dict(size=11)
                )
                
                fig.update_layout(
                    height=600,
                    yaxis={'categoryorder': 'total ascending'},
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    xaxis_title='Percentage of Jobs Requiring Skill',
                    yaxis_title=''
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Professional skills breakdown
                st.markdown("## Skills Analysis Summary")
                
                critical = skills_for_job[skills_for_job['percentage'] >= 50]
                important = skills_for_job[(skills_for_job['percentage'] >= 25) & (skills_for_job['percentage'] < 50)]
                nice_to_have = skills_for_job[skills_for_job['percentage'] < 25]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### Critical Skills")
                    st.caption("Required in ≥50% of positions")
                    
                    st.metric("Count", len(critical))
                    
                    if not critical.empty:
                        for idx, row in critical.iterrows():
                            st.markdown(f"""
                            <div class='skill-category high-demand'>
                                <strong>{row['skill']}</strong><br>
                                <small>Required: {row['percentage']:.1f}% | Jobs: {row['job_count']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No critical skills identified")
                
                with col2:
                    st.markdown("### Important Skills")
                    st.caption("Required in 25-50% of positions")
                    
                    st.metric("Count", len(important))
                    
                    if not important.empty:
                        for idx, row in important.head(10).iterrows():
                            st.markdown(f"""
                            <div class='skill-category moderate-demand'>
                                <strong>{row['skill']}</strong><br>
                                <small>Required: {row['percentage']:.1f}% | Jobs: {row['job_count']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No important skills identified")
                
                with col3:
                    st.markdown("### Nice-to-Have Skills")
                    st.caption("Required in <25% of positions")
                    
                    st.metric("Count", len(nice_to_have))
                    
                    if not nice_to_have.empty:
                        for idx, row in nice_to_have.head(10).iterrows():
                            st.markdown(f"""
                            <div class='skill-category low-demand'>
                                <strong>{row['skill']}</strong><br>
                                <small>Required: {row['percentage']:.1f}% | Jobs: {row['job_count']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No nice-to-have skills identified")
                
                st.markdown("---")
                
                # Complete skills table
                st.markdown("### Complete Skills Breakdown")
                
                display_df = skills_for_job.copy()
                display_df['rank'] = range(1, len(display_df) + 1)
                display_df = display_df[['rank', 'skill', 'job_count', 'percentage']]
                display_df.columns = ['Rank', 'Skill', 'Job Count', 'Required in % of Jobs']
                display_df['Required in % of Jobs'] = display_df['Required in % of Jobs'].round(2)
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
                
            else:
                st.warning(f"No jobs found matching '{job_keyword}'. Please try a different search term.")
        else:
            st.info("Please enter or select a job title to begin analysis")
    
    elif view_mode == "Jobs for You":
        st.markdown("## Job Matching Analysis")
        st.caption("Find positions that match your skill profile")
        
        all_skills_list = all_skills_df['skill'].tolist()
        
        st.markdown("### Your Skills Profile")
        selected_skills = st.multiselect(
            "Select all skills you possess:",
            all_skills_list,
            help="Choose multiple skills from the list"
        )
        
        if selected_skills:
            st.success(f"Skills selected: {len(selected_skills)}")
            
            # Show selected skills in a nice format
            with st.expander("View your selected skills"):
                cols = st.columns(3)
                for idx, skill in enumerate(selected_skills):
                    with cols[idx % 3]:
                        st.markdown(f"✓ {skill}")
            
            with st.spinner("Analyzing job matches..."):
                matching_jobs = get_job_titles_by_skills(selected_skills)
            
            st.markdown("---")
            
            matching_jobs = [j for j in matching_jobs if j['match_percentage'] > 0]
            
            if matching_jobs:
                # Summary statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Matches", len(matching_jobs))
                
                with col2:
                    excellent = len([j for j in matching_jobs if j['match_percentage'] >= 80])
                    st.metric("Excellent Matches", excellent, help="≥80% match")
                
                with col3:
                    good = len([j for j in matching_jobs if 50 <= j['match_percentage'] < 80])
                    st.metric("Good Matches", good, help="50-80% match")
                
                with col4:
                    partial = len([j for j in matching_jobs if 25 <= j['match_percentage'] < 50])
                    st.metric("Partial Matches", partial, help="25-50% match")
                
                st.markdown("---")
                
                # Pagination for all jobs
                st.markdown(f"## All Matching Positions ({len(matching_jobs)} jobs)")
                
                # Items per page
                items_per_page = st.select_slider(
                    "Jobs per page",
                    options=[10, 20, 50, 100, len(matching_jobs)],
                    value=20
                )
                
                total_pages = (len(matching_jobs) - 1) // items_per_page + 1
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    page = st.number_input(
                        f"Page (1-{total_pages})",
                        min_value=1,
                        max_value=total_pages,
                        value=1
                    )
                
                start_idx = (page - 1) * items_per_page
                end_idx = min(start_idx + items_per_page, len(matching_jobs))
                
                page_jobs = matching_jobs[start_idx:end_idx]
                
                st.caption(f"Showing jobs {start_idx + 1}-{end_idx} of {len(matching_jobs)}")
                
                for i, job in enumerate(page_jobs, start_idx + 1):
                    match_pct = job['match_percentage']
                    
                    if match_pct >= 80:
                        status = "Excellent Match"
                        status_color = "#10b981"
                        bg_color = "#d1fae5"
                    elif match_pct >= 50:
                        status = "Good Match"
                        status_color = "#3b82f6"
                        bg_color = "#dbeafe"
                    elif match_pct >= 25:
                        status = "Partial Match"
                        status_color = "#f59e0b"
                        bg_color = "#fef3c7"
                    else:
                        status = "Weak Match"
                        status_color = "#ef4444"
                        bg_color = "#fee2e2"
                    
                    with st.expander(
                        f"#{i}. {job['title']} at {job['company']} — {match_pct:.0f}% Match ({status})",
                        expanded=(i <= start_idx + 3)  # Expand first 3 on each page
                    ):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Match Percentage", f"{match_pct:.1f}%")
                            st.progress(match_pct / 100)
                        
                        with col2:
                            st.metric(
                                "Your Skills Coverage",
                                f"{job['total_matched']}/{job['total_required']}"
                            )
                        
                        with col3:
                            st.metric(
                                "Additional Skills Needed",
                                len(job['missing_skills'])
                            )
                        
                        st.markdown("---")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Skills You Have (Matching):**")
                            if job['matching_skills']:
                                for skill in sorted(job['matching_skills']):
                                    st.markdown(f"✓ {skill}")
                            else:
                                st.markdown("*None*")
                        
                        with col2:
                            st.markdown("**Skills You Need:**")
                            if job['missing_skills']:
                                for skill in sorted(job['missing_skills'])[:15]:
                                    st.markdown(f"• {skill}")
                                if len(job['missing_skills']) > 15:
                                    st.markdown(f"*...and {len(job['missing_skills']) - 15} more*")
                            else:
                                st.success("You have all required skills for this position!")
            else:
                st.warning("No matching jobs found. Try selecting different skills.")
        else:
            st.info("Select your skills above to find matching job opportunities")
    
    elif view_mode == "Skill Pairings":
        st.markdown("## Skill Co-occurrence Analysis")
        st.caption("Understanding which skills are commonly required together")
        
        with st.spinner("Analyzing skill combinations..."):
            cooccur_df = calculate_skill_cooccurrence(min_support=5)
        
        if not cooccur_df.empty:
            tabs = st.tabs(["Co-occurrence Matrix", "Top Skill Pairs", "Network Analysis"])
            
            with tabs[0]:
                st.markdown("### Skill Co-occurrence Heatmap")
                
                fig = create_skill_pairing_heatmap(cooccur_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough data for heatmap visualization")
                
                st.markdown("---")
                
                st.markdown("### Interpretation Guide")
                st.markdown("""
                <div class='professional-card'>
                    <strong>How to read this heatmap:</strong><br><br>
                    • Darker colors indicate stronger co-occurrence between skills<br>
                    • Numbers show how many jobs require both skills together<br>
                    • Diagonal cells are empty (a skill doesn't co-occur with itself)<br>
                    • Symmetric matrix (same value appears twice for each pair)
                </div>
                """, unsafe_allow_html=True)
            
            with tabs[1]:
                st.markdown("### Most Common Skill Combinations")
                
                top_20 = cooccur_df.head(20)
                
                fig = px.bar(
                    top_20,
                    y=top_20['skill1'] + ' + ' + top_20['skill2'],
                    x='count',
                    orientation='h',
                    title='Top 20 Skill Pairs by Co-occurrence',
                    labels={'count': 'Number of Jobs', 'y': 'Skill Combination'},
                    color='count',
                    color_continuous_scale='Viridis',
                    text='count'
                )
                
                fig.update_traces(textposition='outside')
                fig.update_layout(
                    height=700,
                    yaxis={'categoryorder': 'total ascending'},
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                st.markdown("### Detailed Skill Pair Analysis")
                
                for idx, row in cooccur_df.head(15).iterrows():
                    with st.expander(f"{row['skill1']} + {row['skill2']} ({row['count']} jobs)"):
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Co-occurrence", f"{row['count']} jobs")
                        
                        with col2:
                            skill1_data = all_skills_df[all_skills_df['skill'] == row['skill1']]
                            if not skill1_data.empty:
                                st.metric(
                                    f"{row['skill1']}",
                                    f"{skill1_data.iloc[0]['percentage']:.1f}%",
                                    help=f"Appears in {row['skill1_freq']} jobs total"
                                )
                        
                        with col3:
                            skill2_data = all_skills_df[all_skills_df['skill'] == row['skill2']]
                            if not skill2_data.empty:
                                st.metric(
                                    f"{row['skill2']}",
                                    f"{skill2_data.iloc[0]['percentage']:.1f}%",
                                    help=f"Appears in {row['skill2_freq']} jobs total"
                                )
                        
                        st.markdown("---")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**{row['skill1']}** appears in **{row['skill1_freq']}** jobs total")
                            if not skill1_data.empty:
                                st.caption(f"Market penetration: {skill1_data.iloc[0]['percentage']:.2f}%")
                        
                        with col2:
                            st.markdown(f"**{row['skill2']}** appears in **{row['skill2_freq']}** jobs total")
                            if not skill2_data.empty:
                                st.caption(f"Market penetration: {skill2_data.iloc[0]['percentage']:.2f}%")
            
            with tabs[2]:
                st.markdown("### Skill Network Visualization")
                
                fig = create_skill_network_chart(cooccur_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                st.markdown("### Network Statistics")
                
                skill_connections = defaultdict(int)
                for _, row in cooccur_df.iterrows():
                    skill_connections[row['skill1']] += 1
                    skill_connections[row['skill2']] += 1
                
                most_connected = sorted(skill_connections.items(), key=lambda x: x[1], reverse=True)[:10]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Most Connected Skills")
                    st.caption("Skills that frequently pair with others")
                    
                    for skill, connections in most_connected:
                        st.markdown(f"""
                        <div class='professional-card'>
                            <strong>{skill}</strong><br>
                            <small>Pairs with {connections} other skills</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    # Connectivity distribution
                    connectivity_df = pd.DataFrame(most_connected, columns=['Skill', 'Connections'])
                    
                    fig = px.bar(
                        connectivity_df,
                        x='Connections',
                        y='Skill',
                        orientation='h',
                        title='Top 10 Most Versatile Skills',
                        color='Connections',
                        color_continuous_scale='Blues'
                    )
                    
                    fig.update_layout(
                        height=400,
                        yaxis={'categoryorder': 'total ascending'},
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown(f"""
                    <div class='insight-box'>
                        <h4 style='margin-top: 0; color: white;'>Most Versatile Skill</h4>
                        <p style='font-size: 1.5em; margin: 10px 0;'>{most_connected[0][0]}</p>
                        <p>Pairs with {most_connected[0][1]} different skills</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Insufficient data for co-occurrence analysis. Try adjusting parameters.")
    
    elif view_mode == "Seniority Analysis":
        st.markdown("## Skills Requirements by Career Level")
        st.caption("Understanding how skill requirements vary across seniority levels")
        
        with st.spinner("Calculating seniority statistics..."):
            seniority_stats, seniority_skills = calculate_seniority_stats()
        
        # Enhanced grouped chart
        st.plotly_chart(create_seniority_grouped_chart(seniority_stats), use_container_width=True)
        
        st.markdown("---")
        
        # Detailed seniority breakdown
        st.markdown("## Detailed Analysis by Seniority Level")
        
        for _, row in seniority_stats.iterrows():
            seniority = row['seniority']
            avg_skills = row['avg_skills']
            job_count = row['job_count']
            
            with st.expander(f"{seniority} Level — Avg {avg_skills:.1f} skills | {int(job_count)} positions"):
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Average Skills Required", f"{avg_skills:.2f}")
                
                with col2:
                    st.metric("Total Positions", f"{int(job_count):,}")
                
                with col3:
                    pct_of_total = (job_count / total_jobs) * 100
                    st.metric("Market Share", f"{pct_of_total:.1f}%")
                
                st.markdown("---")
                
                st.markdown("### Most Common Skills for This Level")
                
                skills_list = seniority_skills.get(seniority, [])
                if skills_list:
                    cols = st.columns(2)
                    for idx, skill in enumerate(skills_list):
                        with cols[idx % 2]:
                            st.markdown(f"• {skill}")
                else:
                    st.info("No specific skills data available for this level")
        
        st.markdown("---")
        
        # Summary insights
        st.markdown("## Career Progression Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            junior_avg = seniority_stats[seniority_stats['seniority'] == 'Junior']['avg_skills'].values
            senior_avg = seniority_stats[seniority_stats['seniority'] == 'Senior']['avg_skills'].values
            
            if len(junior_avg) > 0 and len(senior_avg) > 0:
                skill_increase = senior_avg[0] - junior_avg[0]
                
                st.markdown(f"""
                <div class='insight-box'>
                    <h4 style='margin-top: 0; color: white;'>Skill Development Path</h4>
                    <p style='font-size: 1.3em; margin: 10px 0;'>+{skill_increase:.1f} skills</p>
                    <p>Average increase from Junior to Senior level</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            manager_jobs = seniority_stats[seniority_stats['seniority'] == 'Manager']['job_count'].values
            if len(manager_jobs) > 0:
                manager_pct = (manager_jobs[0] / total_jobs) * 100
                
                st.markdown(f"""
                <div class='professional-card'>
                    <h4 style='margin-top: 0;'>Management Positions</h4>
                    <p style='font-size: 2em; margin: 10px 0; color: #1e40af;'>{manager_pct:.1f}%</p>
                    <p style='color: #64748b;'>of total job market</p>
                </div>
                """, unsafe_allow_html=True)
    
    else:  # Deep Dive
        st.markdown("## Comprehensive Data Analysis")
        
        tabs = st.tabs(["Complete Skills Database", "Data Export"])
        
        with tabs[0]:
            st.markdown("### All Skills Ranked by Demand")
            st.caption(f"Complete database of {len(all_skills_df)} unique skills identified")
            
            # Enhanced dataframe with better formatting
            display_df = all_skills_df.copy()
            display_df['rank'] = range(1, len(display_df) + 1)
            display_df = display_df[['rank', 'skill', 'job_count', 'percentage']]
            display_df.columns = ['Rank', 'Skill', 'Job Count', 'Market Share (%)']
            display_df['Market Share (%)'] = display_df['Market Share (%)'].round(2)
            
            # Filtering options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                min_jobs = st.number_input(
                    "Minimum job count",
                    min_value=0,
                    max_value=int(display_df['Job Count'].max()),
                    value=0
                )
            
            with col2:
                max_jobs = st.number_input(
                    "Maximum job count",
                    min_value=0,
                    max_value=int(display_df['Job Count'].max()),
                    value=int(display_df['Job Count'].max())
                )
            
            with col3:
                search_skill = st.text_input("Search for skill", "")
            
            # Apply filters
            filtered_df = display_df[
                (display_df['Job Count'] >= min_jobs) &
                (display_df['Job Count'] <= max_jobs)
            ]
            
            if search_skill:
                filtered_df = filtered_df[
                    filtered_df['Skill'].str.contains(search_skill, case=False, na=False)
                ]
            
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                height=600
            )
            
            st.caption(f"Showing {len(filtered_df)} of {len(display_df)} total skills")
        
        with tabs[1]:
            st.markdown("### Export Data")
            st.caption("Download complete datasets for further analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="Download Skills Data (CSV)",
                    data=all_skills_df.to_csv(index=False).encode('utf-8'),
                    file_name='job_skills_complete_data.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            
            with col2:
                st.download_button(
                    label="Download Summary Stats (CSV)",
                    data=stats_df.to_csv(index=False).encode('utf-8'),
                    file_name='job_market_summary_stats.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            
            with col3:
                # Export co-occurrence data
                cooccur_export = calculate_skill_cooccurrence(min_support=3)
                st.download_button(
                    label="Download Skill Pairs (CSV)",
                    data=cooccur_export.to_csv(index=False).encode('utf-8'),
                    file_name='skill_cooccurrence_data.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            
            st.markdown("---")
            
            st.markdown("#### Export Information")
            st.markdown("""
            <div class='professional-card'>
                <strong>Data Formats:</strong><br>
                • CSV files compatible with Excel, Python, R, and other analytics tools<br>
                • UTF-8 encoding for international character support<br>
                • Column headers included for easy data import<br><br>
                
                <strong>Usage Recommendations:</strong><br>
                • Use skills data for trend analysis and forecasting<br>
                • Use summary stats for reporting and presentations<br>
                • Use skill pairs for network analysis and correlation studies
            </div>
            """, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTION FOR NETWORK CHART (same as before)
# ============================================================================

def create_skill_network_chart(cooccur_df):
    """Create network visualization"""
    if cooccur_df.empty or len(cooccur_df) < 3:
        return None
    
    top_pairs = cooccur_df.head(20)
    
    nodes = set()
    for _, row in top_pairs.iterrows():
        nodes.add(row['skill1'])
        nodes.add(row['skill2'])
    
    node_list = list(nodes)
    node_indices = {node: i for i, node in enumerate(node_list)}
    
    edge_x = []
    edge_y = []
    
    np.random.seed(42)
    angles = np.linspace(0, 2*np.pi, len(node_list), endpoint=False)
    node_x = np.cos(angles)
    node_y = np.sin(angles)
    
    for _, row in top_pairs.iterrows():
        x0, y0 = node_x[node_indices[row['skill1']]], node_y[node_indices[row['skill1']]]
        x1, y1 = node_x[node_indices[row['skill2']]], node_y[node_indices[row['skill2']]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#cbd5e1'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_list,
        textposition="top center",
        textfont=dict(size=11, family='Arial, sans-serif'),
        marker=dict(
            size=20,
            color='#3b82f6',
            line=dict(width=2, color='white')
        )
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title='Skill Connectivity Network',
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application entry point"""
    
    if not check_authentication():
        # Check if user needs to verify email
        if st.session_state.get('show_verification', False):
            verification_page()
        # Check if user wants to see signup page
        elif st.session_state.get('show_signup', False):
            signup_page()
        else:
            login_page()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()
