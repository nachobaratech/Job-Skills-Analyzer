import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from athena_helper import AthenaHelper

st.set_page_config(page_title="Job Skills Analyzer", page_icon="📊", layout="wide")

@st.cache_resource
def get_athena():
    return AthenaHelper()

# Define skill categories
SKILL_CATEGORIES = {
    "Soft Skills": ["Communication", "Leadership", "Teamwork", "Problem Solving", "Sales"],
    "Business Tools": ["Excel", "PowerPoint", "Project Management", "CRM", "Salesforce", "SAP", "Power BI"],
    "Technical Skills": ["Python", "JavaScript", "Java", "SQL", "AWS", "Docker", "Git", "CI/CD", "Azure"],
    "Marketing": ["Social Media", "SEO", "Content Marketing", "Google Analytics"],
    "Design": ["UI/UX", "Figma", "Photoshop"],
    "Data & Analytics": ["Data Analysis", "Business Analysis", "Financial Analysis", "Tableau", "Big Data", "ETL"],
    "DevOps": ["Agile", "Scrum", "Quality Assurance"],
    "Other": ["REST API", "Go", "React", "Customer Service"]
}

st.title("📊 Job Market Skills Gap Analyzer")
st.markdown("### 🔴 **LIVE** Real-time analysis from AWS Athena")
st.divider()

# SIDEBAR WITH FILTERS
with st.sidebar:
    st.header("🎯 About")
    st.write("Real-time job market intelligence")
    st.divider()
    
    st.header("🔧 Filters")
    
    # Category filter
    selected_categories = st.multiselect(
        "Filter by Category",
        options=list(SKILL_CATEGORIES.keys()),
        default=list(SKILL_CATEGORIES.keys()),
        help="Select which skill categories to display"
    )
    
    # Top N slider
    top_n = st.slider("Number of skills to show", 5, 30, 15)
    
    # Minimum percentage filter
    min_percentage = st.slider("Minimum job percentage", 0, 50, 0, 
                               help="Show only skills appearing in at least X% of jobs")
    
    st.divider()
    
    st.header("📊 Data Source")
    st.info("1,000 real LinkedIn jobs")
    
    if st.button("🔄 Refresh Data"):
        st.cache_resource.clear()
        st.rerun()

# MAIN CONTENT
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview", 
    "🔍 Detailed Analysis",
    "📊 Category Comparison",
    "⚡ Connection Info"
])

with tab1:
    with st.spinner("🔄 Querying AWS Athena..."):
        try:
            athena = get_athena()
            stats_df = athena.get_job_stats()
            
            total_jobs = int(stats_df["total_jobs"].iloc[0])
            jobs_with_skills = int(stats_df["jobs_with_skills"].iloc[0])
            avg_skills = float(stats_df["avg_skills"].iloc[0])
            
            skills_df = athena.get_top_skills(limit=50)
            skills_df["job_count"] = skills_df["job_count"].astype(int)
            skills_df["percentage"] = skills_df["percentage"].astype(float)
            
            # Filter by selected categories
            if selected_categories:
                selected_skills = []
                for category in selected_categories:
                    selected_skills.extend(SKILL_CATEGORIES[category])
                skills_df = skills_df[skills_df["skill"].isin(selected_skills)]
            
            # Filter by minimum percentage
            skills_df = skills_df[skills_df["percentage"] >= min_percentage]
            
            # Limit to top N
            skills_df = skills_df.head(top_n)
            
            st.success("✅ Data loaded successfully!")
            
            # KEY METRICS
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Total Jobs", f"{total_jobs:,}")
            
            with col2:
                detection_rate = (jobs_with_skills/total_jobs*100)
                st.metric("✅ Jobs with Skills", f"{jobs_with_skills:,}", 
                         f"{detection_rate:.1f}%")
            
            with col3:
                if not skills_df.empty:
                    top_skill = skills_df.iloc[0]["skill"]
                    top_pct = skills_df.iloc[0]["percentage"]
                    st.metric("🏆 Top Skill", top_skill, f"{top_pct:.1f}%")
                else:
                    st.metric("🏆 Top Skill", "N/A")
            
            with col4:
                st.metric("📈 Avg Skills/Job", f"{avg_skills:.1f}")
            
            st.divider()
            
            # INSIGHT BOX
            if not skills_df.empty:
                soft_skills = ["Communication", "Leadership", "Teamwork", "Sales"]
                tech_skills = ["Python", "JavaScript", "SQL", "AWS"]
                
                soft_in_data = skills_df[skills_df["skill"].isin(soft_skills)]
                tech_in_data = skills_df[skills_df["skill"].isin(tech_skills)]
                
                if not soft_in_data.empty and not tech_in_data.empty:
                    soft_avg = soft_in_data["percentage"].mean()
                    tech_avg = tech_in_data["percentage"].mean()
                    
                    st.info(f"""
                    💡 **KEY INSIGHT**: Soft skills average {soft_avg:.1f}% vs Technical skills {tech_avg:.1f}%
                    
                    Employers value communication and teamwork MORE than pure technical abilities!
                    """)
            
            # MAIN CHART
            st.subheader(f"📊 Top {len(skills_df)} Skills (Filtered)")
            
            if not skills_df.empty:
                fig = px.bar(
                    skills_df,
                    x="percentage",
                    y="skill",
                    orientation="h",
                    color="percentage",
                    color_continuous_scale="Viridis",
                    text="percentage",
                    title=f"Skills Demand Analysis ({len(skills_df)} skills shown)"
                )
                fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                fig.update_layout(height=max(400, len(skills_df) * 25), showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No skills match your filters. Try adjusting the filters.")
            
            # PIE CHART AND DISTRIBUTION
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📉 Market Share")
                if len(skills_df) >= 10:
                    top_10 = skills_df.head(10).copy()
                    remaining = skills_df.iloc[10:]
                    
                    if len(remaining) > 0:
                        other_count = remaining["job_count"].sum()
                        other_row = pd.DataFrame([{
                            "skill": "Other",
                            "job_count": other_count,
                            "percentage": (other_count / jobs_with_skills) * 100
                        }])
                        pie_data = pd.concat([top_10, other_row], ignore_index=True)
                    else:
                        pie_data = top_10
                    
                    fig_pie = px.pie(pie_data, values="job_count", names="skill", 
                                    hole=0.4, title="Top 10 Skills + Other")
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Select at least 10 skills to show pie chart")
            
            with col2:
                st.subheader("📊 Distribution")
                if not skills_df.empty:
                    # Categorize skills
                    skill_types = []
                    for _, row in skills_df.iterrows():
                        skill_name = row["skill"]
                        category = "Other"
                        for cat, skills_list in SKILL_CATEGORIES.items():
                            if skill_name in skills_list:
                                category = cat
                                break
                        skill_types.append(category)
                    
                    skills_df["category"] = skill_types
                    
                    category_counts = skills_df["category"].value_counts()
                    
                    fig_dist = px.bar(
                        x=category_counts.values,
                        y=category_counts.index,
                        orientation='h',
                        title="Skills by Category",
                        labels={'x': 'Number of Skills', 'y': 'Category'},
                        color=category_counts.values,
                        color_continuous_scale="Blues"
                    )
                    st.plotly_chart(fig_dist, use_container_width=True)
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

with tab2:
    st.header("🔍 Detailed Skill Analysis")
    
    if 'skills_df' in locals() and not skills_df.empty:
        # Add search box
        search_term = st.text_input("🔎 Search for a skill", "")
        
        if search_term:
            filtered = skills_df[skills_df["skill"].str.contains(search_term, case=False)]
            if not filtered.empty:
                st.dataframe(filtered, use_container_width=True, hide_index=True)
            else:
                st.warning(f"No skills found matching '{search_term}'")
        else:
            st.dataframe(skills_df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = skills_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_skills_data.csv",
            mime="text/csv"
        )
        
        # Stats about filtered data
        st.divider()
        st.subheader("📊 Filtered Data Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Skills Shown", len(skills_df))
        with col2:
            if not skills_df.empty:
                st.metric("Avg Percentage", f"{skills_df['percentage'].mean():.1f}%")
        with col3:
            if not skills_df.empty:
                st.metric("Total Job Mentions", f"{skills_df['job_count'].sum():,}")

with tab3:
    st.header("📊 Category Comparison")
    
    if 'skills_df' in locals() and not skills_df.empty:
        # Get all skills for category analysis
        all_skills_df = athena.get_top_skills(limit=100)
        
        category_summary = []
        for category, skills_list in SKILL_CATEGORIES.items():
            category_skills = all_skills_df[all_skills_df["skill"].isin(skills_list)]
            if not category_skills.empty:
                avg_pct = float(category_skills["percentage"].mean())
                total_jobs = int(category_skills["job_count"].sum())
                num_skills = len(category_skills)
                
                category_summary.append({
                    "Category": category,
                    "Avg Demand %": avg_pct,
                    "Total Job Mentions": total_jobs,
                    "# of Skills": num_skills
                })
        
        summary_df = pd.DataFrame(category_summary)
        summary_df = summary_df.sort_values("Avg Demand %", ascending=False)
        
        # Visualization
        fig_cat = px.bar(
            summary_df,
            x="Avg Demand %",
            y="Category",
            orientation='h',
            title="Average Demand by Skill Category",
            color="Avg Demand %",
            color_continuous_scale="RdYlGn",
            text="Avg Demand %"
        )
        fig_cat.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_cat, use_container_width=True)
        
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

with tab4:
    st.header("⚡ System Information")
    
    st.subheader("🗄️ Athena Connection")
    st.code("""Database: job_skills_db
Table: jobs_with_skills
Region: us-east-1
Storage: S3 (job-skills-raw-223280412524)""")
    
    st.subheader("📊 Sample Query")
    st.code("""SELECT skill, COUNT(*) as job_count,
    ROUND(COUNT(*) * 100.0 / 
        (SELECT COUNT(*) FROM jobs_with_skills 
         WHERE skill_count > 0), 2) as percentage
FROM jobs_with_skills
CROSS JOIN UNNEST(skills) AS t(skill)
GROUP BY skill
ORDER BY job_count DESC
LIMIT 15""", language="sql")

