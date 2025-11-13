import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from athena_helper import AthenaHelper
import numpy as np

st.set_page_config(page_title="Job Skills Analyzer Pro", page_icon="📊", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .insight-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        margin: 20px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_athena():
    return AthenaHelper()

@st.cache_data(ttl=300)
def load_all_data():
    """Load and cache all data"""
    athena = get_athena()
    stats_df = athena.get_job_stats()
    skills_df = athena.get_top_skills(limit=100)
    skills_df["job_count"] = skills_df["job_count"].astype(int)
    skills_df["percentage"] = skills_df["percentage"].astype(float)
    return stats_df, skills_df

# Skill categories with job role mapping
SKILL_CATEGORIES = {
    "Soft Skills": ["Communication", "Leadership", "Teamwork", "Problem Solving", "Sales", "Customer Service", "Negotiation"],
    "Business Tools": ["Excel", "PowerPoint", "Project Management", "CRM", "Salesforce", "SAP", "Power BI", "Tableau"],
    "Programming": ["Python", "JavaScript", "Java", "TypeScript", "C++", "C#", "Go", "Ruby", "PHP", "Swift", "Kotlin", "Rust"],
    "Web Development": ["React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Express"],
    "Databases": ["SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Oracle"],
    "Cloud & DevOps": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Jenkins", "Git", "CI/CD"],
    "Data & Analytics": ["Data Analysis", "Business Analysis", "Financial Analysis", "Big Data", "ETL", "Spark", "Kafka"],
    "AI & ML": ["Machine Learning", "Deep Learning", "TensorFlow", "PyTorch"],
    "Marketing": ["Social Media", "SEO", "Content Marketing", "Google Analytics", "Digital Marketing"],
    "Design": ["UI/UX", "Figma", "Photoshop", "Adobe Illustrator", "Sketch"],
    "Quality & Process": ["Quality Assurance", "Agile", "Scrum", "Test Automation", "Selenium"],
    "APIs & Integration": ["REST API", "GraphQL", "Microservices"]
}

# Job role to skill mapping (approximate)
JOB_ROLES = {
    "Software Engineer": ["Python", "JavaScript", "SQL", "Git", "REST API", "Docker", "AWS", "React", "Agile"],
    "Data Analyst": ["Excel", "SQL", "Python", "Tableau", "Power BI", "Data Analysis", "Communication"],
    "Product Manager": ["Communication", "Leadership", "Agile", "Jira", "Excel", "Project Management", "Problem Solving"],
    "Marketing Manager": ["Communication", "Social Media", "SEO", "Google Analytics", "Content Marketing", "Excel", "Leadership"],
    "Sales Representative": ["Communication", "Sales", "CRM", "Salesforce", "Customer Service", "Negotiation", "Excel"],
    "DevOps Engineer": ["AWS", "Docker", "Kubernetes", "CI/CD", "Terraform", "Git", "Python", "Jenkins"],
    "UX/UI Designer": ["UI/UX", "Figma", "Photoshop", "Communication", "Problem Solving", "Adobe Illustrator"],
    "Business Analyst": ["Excel", "SQL", "Business Analysis", "Communication", "Power BI", "Project Management"],
    "Full Stack Developer": ["JavaScript", "React", "Node.js", "SQL", "Python", "Git", "REST API", "AWS"],
    "Data Scientist": ["Python", "Machine Learning", "SQL", "TensorFlow", "Data Analysis", "Big Data", "Communication"],
    "Project Manager": ["Project Management", "Communication", "Leadership", "Agile", "Excel", "PowerPoint", "Problem Solving"],
    "Customer Success Manager": ["Communication", "Customer Service", "CRM", "Problem Solving", "Sales", "Excel"]
}

# Header
st.title("🚀 Job Market Skills Intelligence Platform")
st.markdown("### Real-time Analytics Powered by AWS | 1,000+ LinkedIn Jobs Analyzed")
st.divider()

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/250x80/667eea/ffffff?text=Skills+Analyzer", use_column_width=True)
    
    st.header("🎛️ Dashboard Controls")
    
    # View mode
    view_mode = st.radio(
        "Analysis Mode",
        ["📊 Market Overview", "🎯 Career Advisor", "🔬 Deep Dive", "📈 Trends & Patterns"],
        help="Choose your analysis perspective"
    )
    
    st.divider()
    
    # Filters
    st.subheader("🔧 Filters")
    
    selected_categories = st.multiselect(
        "Skill Categories",
        options=list(SKILL_CATEGORIES.keys()),
        default=list(SKILL_CATEGORIES.keys())
    )
    
    min_percentage = st.slider("Min. Job Percentage", 0, 50, 0, 
                               help="Show skills in at least X% of jobs")
    
    show_count = st.slider("Number of Skills", 5, 50, 20)
    
    st.divider()
    
    # Data info
    st.subheader("ℹ️ Data Info")
    st.caption("🗄️ Source: AWS Athena")
    st.caption("📊 Jobs: 1,000 real postings")
    st.caption("🔄 Updated: Real-time")
    
    if st.button("♻️ Refresh All Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Load data
with st.spinner("🔄 Loading data from AWS Athena..."):
    stats_df, all_skills_df = load_all_data()
    
    total_jobs = int(stats_df["total_jobs"].iloc[0])
    jobs_with_skills = int(stats_df["jobs_with_skills"].iloc[0])
    avg_skills = float(stats_df["avg_skills"].iloc[0])

# Filter skills based on selection
if selected_categories:
    selected_skills = []
    for category in selected_categories:
        selected_skills.extend(SKILL_CATEGORIES[category])
    filtered_skills_df = all_skills_df[all_skills_df["skill"].isin(selected_skills)]
else:
    filtered_skills_df = all_skills_df.copy()

filtered_skills_df = filtered_skills_df[filtered_skills_df["percentage"] >= min_percentage]
display_skills_df = filtered_skills_df.head(show_count)

# =============================================================================
# VIEW MODE: MARKET OVERVIEW
# =============================================================================
if view_mode == "📊 Market Overview":
    
    # Key Metrics Row
    st.subheader("📈 Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📊 Total Jobs", f"{total_jobs:,}", help="LinkedIn jobs analyzed")
    
    with col2:
        detection_rate = (jobs_with_skills/total_jobs*100)
        st.metric("✅ Detection Rate", f"{detection_rate:.1f}%", 
                 f"{jobs_with_skills:,} jobs", help="Jobs with identified skills")
    
    with col3:
        if not display_skills_df.empty:
            st.metric("🏆 #1 Skill", display_skills_df.iloc[0]["skill"], 
                     f"{display_skills_df.iloc[0]['percentage']:.1f}%")
    
    with col4:
        st.metric("📚 Avg Skills/Job", f"{avg_skills:.1f}", 
                 "Multi-skilled", help="Average skills per posting")
    
    with col5:
        st.metric("🎯 Unique Skills", len(all_skills_df), 
                 "Tracked", help="Total distinct skills found")
    
    st.divider()
    
    # Major Insight
    soft_skills = ["Communication", "Leadership", "Teamwork", "Sales", "Customer Service"]
    tech_skills = ["Python", "JavaScript", "SQL", "AWS", "Docker"]
    
    soft_data = all_skills_df[all_skills_df["skill"].isin(soft_skills)]
    tech_data = all_skills_df[all_skills_df["skill"].isin(tech_skills)]
    
    if not soft_data.empty and not tech_data.empty:
        soft_avg = soft_data["percentage"].mean()
        tech_avg = tech_data["percentage"].mean()
        difference = soft_avg - tech_avg
        
        st.markdown(f"""
        <div class="insight-box">
        💡 <b>MAJOR INSIGHT</b>: Soft skills average <b>{soft_avg:.1f}%</b> demand vs Technical skills <b>{tech_avg:.1f}%</b> 
        ({'+' if difference > 0 else ''}{difference:.1f}% difference)
        <br><br>
        🎯 <b>Recommendation</b>: Job seekers should prioritize communication and interpersonal skills alongside technical expertise!
        </div>
        """, unsafe_allow_html=True)
    
    # Main visualization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📊 Top {len(display_skills_df)} Most Demanded Skills")
        
        if not display_skills_df.empty:
            # Color code by category
            colors = []
            for skill in display_skills_df["skill"]:
                if skill in soft_skills:
                    colors.append('#FF6B6B')  # Red for soft
                elif skill in tech_skills:
                    colors.append('#4ECDC4')  # Teal for tech
                else:
                    colors.append('#95E1D3')  # Green for others
            
            fig = go.Figure(go.Bar(
                x=display_skills_df["percentage"],
                y=display_skills_df["skill"],
                orientation='h',
                marker=dict(
                    color=colors,
                    line=dict(color='white', width=1)
                ),
                text=display_skills_df["percentage"].apply(lambda x: f"{x:.1f}%"),
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Demand: %{x:.1f}%<br>Jobs: %{customdata}<extra></extra>',
                customdata=display_skills_df["job_count"]
            ))
            
            fig.update_layout(
                height=max(500, len(display_skills_df) * 30),
                xaxis_title="Percentage of Jobs",
                yaxis_title="",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Legend
            st.caption("🔴 Soft Skills | 🟢 Technical Skills | 🟡 Other Skills")
    
    with col2:
        st.subheader("🎨 Category Distribution")
        
        # Calculate category totals
        category_totals = {}
        for category, skills_list in SKILL_CATEGORIES.items():
            cat_skills = all_skills_df[all_skills_df["skill"].isin(skills_list)]
            if not cat_skills.empty:
                category_totals[category] = int(cat_skills["job_count"].sum())
        
        cat_df = pd.DataFrame(list(category_totals.items()), columns=["Category", "Total Mentions"])
        cat_df = cat_df.sort_values("Total Mentions", ascending=False)
        
        fig_pie = px.pie(
            cat_df,
            values="Total Mentions",
            names="Category",
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='outside', textinfo='percent+label')
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Detailed comparison
    st.divider()
    st.subheader("📊 Category Performance Comparison")
    
    category_stats = []
    for category, skills_list in SKILL_CATEGORIES.items():
        cat_skills = all_skills_df[all_skills_df["skill"].isin(skills_list)]
        if not cat_skills.empty:
            category_stats.append({
                "Category": category,
                "Avg Demand": float(cat_skills["percentage"].mean()),
                "Top Skill": cat_skills.iloc[0]["skill"],
                "# Skills Found": len(cat_skills),
                "Total Mentions": int(cat_skills["job_count"].sum())
            })
    
    cat_stats_df = pd.DataFrame(category_stats).sort_values("Avg Demand", ascending=False)
    
    fig_cat = px.bar(
        cat_stats_df,
        x="Avg Demand",
        y="Category",
        orientation='h',
        text="Avg Demand",
        color="Avg Demand",
        color_continuous_scale="Viridis",
        title="Average Skill Demand by Category"
    )
    fig_cat.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_cat.update_layout(height=400)
    st.plotly_chart(fig_cat, use_container_width=True)
    
    st.dataframe(cat_stats_df, use_container_width=True, hide_index=True)

# =============================================================================
# VIEW MODE: CAREER ADVISOR
# =============================================================================
elif view_mode == "🎯 Career Advisor":
    
    st.header("🎯 Personalized Career Skills Advisor")
    st.markdown("**Select your target job role to discover the most important skills employers want**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        selected_role = st.selectbox(
            "🎓 What job role are you targeting?",
            options=list(JOB_ROLES.keys()),
            help="Select your desired career path"
        )
    
    with col2:
        experience_level = st.select_slider(
            "💼 Your Experience Level",
            options=["Entry Level", "Mid Level", "Senior Level", "Expert"],
            value="Mid Level"
        )
    
    st.divider()
    
    # Get required skills for selected role
    required_skills = JOB_ROLES[selected_role]
    role_skills_data = all_skills_df[all_skills_df["skill"].isin(required_skills)].copy()
    
    if not role_skills_data.empty:
        # Sort by demand
        role_skills_data = role_skills_data.sort_values("percentage", ascending=False)
        
        # Calculate readiness score
        total_demand = role_skills_data["percentage"].sum()
        avg_demand = role_skills_data["percentage"].mean()
        
        st.success(f"✅ Found {len(role_skills_data)} relevant skills for **{selected_role}** role")
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Required Skills", len(role_skills_data), 
                     f"of {len(required_skills)} total")
        
        with col2:
            st.metric("📈 Avg Market Demand", f"{avg_demand:.1f}%",
                     "per skill")
        
        with col3:
            if not role_skills_data.empty:
                st.metric("🏆 Most Critical", role_skills_data.iloc[0]["skill"],
                         f"{role_skills_data.iloc[0]['percentage']:.1f}%")
        
        with col4:
            competitiveness = "🔥 High" if avg_demand > 20 else "📊 Medium" if avg_demand > 10 else "✅ Accessible"
            st.metric("💪 Competition Level", competitiveness,
                     "demand intensity")
        
        st.divider()
        
        # Skill breakdown
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"📋 Essential Skills for {selected_role}")
            
            # Priority categorization
            role_skills_data["Priority"] = role_skills_data["percentage"].apply(
                lambda x: "🔴 Critical" if x >= 20 else "🟡 Important" if x >= 10 else "🟢 Valuable"
            )
            
            fig_role = px.bar(
                role_skills_data,
                x="percentage",
                y="skill",
                orientation='h',
                color="Priority",
                text="percentage",
                color_discrete_map={
                    "🔴 Critical": "#FF6B6B",
                    "🟡 Important": "#FFD93D",
                    "🟢 Valuable": "#6BCB77"
                },
                title=f"Skill Priority Matrix - {selected_role}"
            )
            fig_role.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_role.update_layout(height=max(400, len(role_skills_data) * 35))
            st.plotly_chart(fig_role, use_container_width=True)
        
        with col2:
            st.subheader("📊 Skill Details")
            
            for idx, row in role_skills_data.iterrows():
                priority = row["Priority"]
                with st.expander(f"{priority} {row['skill']}"):
                    st.write(f"**Market Demand:** {row['percentage']:.1f}%")
                    st.write(f"**Jobs Requiring:** {row['job_count']:,}")
                    
                    if row['percentage'] >= 30:
                        st.info("🔥 Extremely high demand - TOP priority!")
                    elif row['percentage'] >= 15:
                        st.warning("⚡ High demand - Important to have")
                    else:
                        st.success("✅ Moderate demand - Nice to have")
        
        st.divider()
        
        # Learning path recommendation
        st.subheader("🎓 Your Personalized Learning Path")
        
        critical_skills = role_skills_data[role_skills_data["percentage"] >= 20]["skill"].tolist()
        important_skills = role_skills_data[(role_skills_data["percentage"] >= 10) & 
                                           (role_skills_data["percentage"] < 20)]["skill"].tolist()
        valuable_skills = role_skills_data[role_skills_data["percentage"] < 10]["skill"].tolist()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🔴 Phase 1: Critical")
            st.markdown("**Master these first**")
            for skill in critical_skills:
                st.markdown(f"- {skill}")
            if not critical_skills:
                st.info("✅ All critical skills covered!")
        
        with col2:
            st.markdown("### 🟡 Phase 2: Important")
            st.markdown("**Learn these next**")
            for skill in important_skills:
                st.markdown(f"- {skill}")
            if not important_skills:
                st.info("✅ All important skills covered!")
        
        with col3:
            st.markdown("### 🟢 Phase 3: Valuable")
            st.markdown("**Nice to have**")
            for skill in valuable_skills:
                st.markdown(f"- {skill}")
            if not valuable_skills:
                st.info("✅ All valuable skills covered!")
        
        # Download career report
        st.divider()
        career_report = role_skills_data.copy()
        career_report["Role"] = selected_role
        career_report = career_report[["Role", "skill", "percentage", "job_count", "Priority"]]
        career_report.columns = ["Target Role", "Skill", "Market Demand %", "Job Count", "Priority"]
        
        csv = career_report.to_csv(index=False)
        st.download_button(
            label=f"📥 Download {selected_role} Career Report",
            data=csv,
            file_name=f"{selected_role.replace(' ', '_')}_skills_report.csv",
            mime="text/csv",
            use_container_width=True
        )

# =============================================================================
# VIEW MODE: DEEP DIVE
# =============================================================================
elif view_mode == "🔬 Deep Dive":
    
    st.header("🔬 Advanced Skill Analysis")
    
    # Skill comparison tool
    st.subheader("⚔️ Skill Comparison Tool")
    
    col1, col2 = st.columns(2)
    
    with col1:
        skill1 = st.selectbox("Select first skill", all_skills_df["skill"].tolist(), key="skill1")
    
    with col2:
        skill2 = st.selectbox("Select second skill", all_skills_df["skill"].tolist(), 
                             index=1, key="skill2")
    
    if skill1 and skill2:
        data1 = all_skills_df[all_skills_df["skill"] == skill1].iloc[0]
        data2 = all_skills_df[all_skills_df["skill"] == skill2].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(skill1, f"{data1['percentage']:.1f}%", 
                     f"{data1['job_count']:,} jobs")
        
        with col2:
            difference = data1['percentage'] - data2['percentage']
            st.metric("Difference", f"{abs(difference):.1f}%",
                     f"{'↑' if difference > 0 else '↓'} {skill1 if difference > 0 else skill2}")
        
        with col3:
            st.metric(skill2, f"{data2['percentage']:.1f}%",
                     f"{data2['job_count']:,} jobs")
        
        # Visual comparison
        comparison_df = pd.DataFrame({
            "Skill": [skill1, skill2],
            "Market Demand %": [data1['percentage'], data2['percentage']],
            "Job Count": [data1['job_count'], data2['job_count']]
        })
        
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name='Market Demand %',
            x=comparison_df['Skill'],
            y=comparison_df['Market Demand %'],
            marker_color=['#667eea', '#764ba2']
        ))
        fig_comp.update_layout(title="Head-to-Head Comparison", height=400)
        st.plotly_chart(fig_comp, use_container_width=True)
    
    st.divider()
    
    # Search and explore
    st.subheader("🔍 Search & Explore")
    
    search_term = st.text_input("🔎 Search for skills", placeholder="e.g., Python, Excel, Communication...")
    
    if search_term:
        search_results = all_skills_df[all_skills_df["skill"].str.contains(search_term, case=False)]
        
        if not search_results.empty:
            st.success(f"✅ Found {len(search_results)} matching skills")
            
            for idx, row in search_results.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{row['skill']}**")
                with col2:
                    st.write(f"📊 {row['percentage']:.1f}%")
                with col3:
                    st.write(f"👥 {row['job_count']:,} jobs")
        else:
            st.warning(f"No skills found matching '{search_term}'")
    
    st.divider()
    
    # Full data table with advanced filtering
    st.subheader("📋 Complete Skills Database")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sort_by = st.selectbox("Sort by", ["Market Demand %", "Job Count", "Alphabetical"])
    
    with col2:
        sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)
    
    with col3:
        show_rows = st.number_input("Show rows", 10, 100, 25)
    
    # Apply sorting
    display_df = all_skills_df.copy()
    
    if sort_by == "Market Demand %":
        display_df = display_df.sort_values("percentage", ascending=(sort_order == "Ascending"))
    elif sort_by == "Job Count":
        display_df = display_df.sort_values("job_count", ascending=(sort_order == "Ascending"))
    else:
        display_df = display_df.sort_values("skill", ascending=(sort_order == "Ascending"))
    
    display_df = display_df.head(show_rows)
    
    # Add ranking
    display_df["Rank"] = range(1, len(display_df) + 1)
    display_df = display_df[["Rank", "skill", "percentage", "job_count"]]
    display_df.columns = ["Rank", "Skill", "Market Demand %", "Job Count"]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
    
    # Export options
    csv = display_df.to_csv(index=False)
    st.download_button(
        "📥 Download Complete Dataset",
        data=csv,
        file_name="skills_analysis_full.csv",
        mime="text/csv",
        use_container_width=True
    )

# =============================================================================
# VIEW MODE: TRENDS & PATTERNS
# =============================================================================
elif view_mode == "📈 Trends & Patterns":
    
    st.header("📈 Market Trends & Pattern Analysis")
    
    # Skill demand distribution
    st.subheader("📊 Demand Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram of skill demand
        fig_hist = px.histogram(
            all_skills_df,
            x="percentage",
            nbins=20,
            title="Distribution of Skill Demand",
            labels={"percentage": "Market Demand %", "count": "Number of Skills"},
            color_discrete_sequence=["#667eea"]
        )
        fig_hist.add_vline(x=all_skills_df["percentage"].median(), 
                          line_dash="dash", line_color="red",
                          annotation_text=f"Median: {all_skills_df['percentage'].median():.1f}%")
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Box plot by category
        category_data = []
        for category, skills_list in SKILL_CATEGORIES.items():
            cat_skills = all_skills_df[all_skills_df["skill"].isin(skills_list)]
            for _, row in cat_skills.iterrows():
                category_data.append({
                    "Category": category,
                    "Demand": row["percentage"]
                })
        
        if category_data:
            cat_box_df = pd.DataFrame(category_data)
            fig_box = px.box(
                cat_box_df,
                x="Category",
                y="Demand",
                title="Demand Variability by Category",
                color="Category",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_box.update_xaxis(tickangle=-45)
            st.plotly_chart(fig_box, use_container_width=True)
    
    st.divider()
    
    # Top vs Bottom performers
    st.subheader("🏆 Top Performers vs 📉 Least Demanded")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔥 Top 10 Hottest Skills")
        top_10 = all_skills_df.head(10)
        
        for idx, row in top_10.iterrows():
            progress_val = int(row['percentage'])
            st.markdown(f"**{idx+1}. {row['skill']}**")
            st.progress(min(progress_val, 100))
            st.caption(f"{row['percentage']:.1f}% | {row['job_count']:,} jobs")
    
    with col2:
        st.markdown("### 🧊 Bottom 10 Niche Skills")
        bottom_10 = all_skills_df.tail(10).sort_values("percentage", ascending=True)
        
        for idx, row in bottom_10.iterrows():
            progress_val = int(row['percentage'])
            st.markdown(f"**{row['skill']}**")
            st.progress(max(progress_val, 5))
            st.caption(f"{row['percentage']:.1f}% | {row['job_count']:,} jobs")
    
    st.divider()
    
    # Skill saturation analysis
    st.subheader("🎯 Market Saturation Levels")
    
    # Categorize by saturation
    saturated = all_skills_df[all_skills_df["percentage"] >= 30]
    competitive = all_skills_df[(all_skills_df["percentage"] >= 15) & (all_skills_df["percentage"] < 30)]
    emerging = all_skills_df[(all_skills_df["percentage"] >= 5) & (all_skills_df["percentage"] < 15)]
    niche = all_skills_df[all_skills_df["percentage"] < 5]
    
    saturation_data = {
        "🔴 Saturated (≥30%)": len(saturated),
        "🟠 Competitive (15-30%)": len(competitive),
        "🟡 Emerging (5-15%)": len(emerging),
        "🟢 Niche (<5%)": len(niche)
    }
    
    sat_df = pd.DataFrame(list(saturation_data.items()), columns=["Category", "Count"])
    
    fig_sat = px.pie(
        sat_df,
        values="Count",
        names="Category",
        title="Market Saturation Distribution",
        color_discrete_sequence=["#FF6B6B", "#FFA500", "#FFD700", "#90EE90"],
        hole=0.4
    )
    st.plotly_chart(fig_sat, use_container_width=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔴 Saturated", len(saturated), "High competition")
    with col2:
        st.metric("🟠 Competitive", len(competitive), "Medium competition")
    with col3:
        st.metric("🟡 Emerging", len(emerging), "Growing demand")
    with col4:
        st.metric("🟢 Niche", len(niche), "Specialized")
    
    # Strategic recommendations
    st.divider()
    st.subheader("💡 Strategic Insights & Recommendations")
    
    insights = []
    
    if len(saturated) > 0:
        insights.append(f"🔴 **High Competition Alert**: {len(saturated)} skills are saturated (>30% demand). "
                       f"Top saturated skill: **{saturated.iloc[0]['skill']}** at {saturated.iloc[0]['percentage']:.1f}%")
    
    if len(emerging) > 0:
        insights.append(f"🟡 **Opportunity Zone**: {len(emerging)} emerging skills (5-15% demand) offer good entry points. "
                       f"Consider: **{', '.join(emerging.head(3)['skill'].tolist())}**")
    
    if len(niche) > 0:
        insights.append(f"🟢 **Specialization Potential**: {len(niche)} niche skills (<5% demand) for differentiation. "
                       f"These could be competitive advantages in specific roles.")
    
    # Soft skills dominance
    soft_in_top10 = len(all_skills_df.head(10)[all_skills_df.head(10)["skill"].isin(
        ["Communication", "Leadership", "Teamwork", "Sales", "Customer Service"]
    )])
    
    if soft_in_top10 >= 3:
        insights.append(f"💼 **Soft Skills Dominance**: {soft_in_top10} of top 10 skills are soft skills. "
                       "Interpersonal abilities are crucial across all roles.")
    
    for insight in insights:
        st.info(insight)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🗄️ Data Source: AWS Athena")
with col2:
    st.caption("☁️ Powered by: S3 + Lambda + SNS")
with col3:
    st.caption("⚡ Real-time: Sub-2s query response")

