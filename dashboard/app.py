import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from athena_helper import AthenaHelper
import time

st.set_page_config(page_title="Job Skills Analyzer", page_icon="📊", layout="wide")

# Custom CSS for cool styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .hot-skill {
        background-color: #ff4444;
        padding: 5px 10px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
    .growing-skill {
        background-color: #44ff44;
        padding: 5px 10px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
    .stable-skill {
        background-color: #4444ff;
        padding: 5px 10px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_athena():
    return AthenaHelper()

st.title("📊 Job Market Skills Gap Analyzer")
st.markdown("### 🔴 **LIVE** Real-time analysis from AWS Athena Database")
st.divider()

with st.sidebar:
    st.header("🎯 About")
    st.write("Real-time job market intelligence")
    st.divider()
    
    st.header("📊 Data Source")
    st.info("1,000+ real LinkedIn jobs queried live from AWS Athena")
    st.divider()
    
    st.header("🔧 Filters")
    top_n = st.slider("Number of skills", 5, 30, 15)
    
    st.divider()
    
    # NEW: Skill Recommender
    st.header("🎯 Skill Recommender")
    user_role = st.selectbox("Your target role:", [
        "Select a role...",
        "Full Stack Developer",
        "Data Engineer", 
        "DevOps Engineer",
        "Backend Developer",
        "Frontend Developer"
    ])
    
    if user_role != "Select a role...":
        recommendations = {
            "Full Stack Developer": ["Python", "JavaScript", "React", "SQL", "REST API"],
            "Data Engineer": ["Python", "SQL", "AWS", "Kafka", "Docker"],
            "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "CI/CD", "Git"],
            "Backend Developer": ["Python", "REST API", "SQL", "Docker", "Git"],
            "Frontend Developer": ["JavaScript", "React", "TypeScript", "Node.js", "Git"]
        }
        
        st.success(f"**Top skills for {user_role}:**")
        for skill in recommendations[user_role]:
            st.write(f"✅ {skill}")
    
    st.divider()
    
    if st.button("🔄 Refresh Data"):
        st.cache_resource.clear()
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔍 Analysis", "📂 Categories", "⚡ Connection Info"])

with tab1:
    # Show loading animation
    with st.spinner("🔄 Querying AWS Athena database..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        start_time = time.time()
        try:
            athena = get_athena()
            
            status_text.text("⏳ Executing SQL query...")
            progress_bar.progress(30)
            
            stats_df = athena.get_job_stats()
            progress_bar.progress(60)
            
            query_time = time.time() - start_time
            
            total_jobs = int(stats_df["total_jobs"].iloc[0])
            jobs_with_skills = int(stats_df["jobs_with_skills"].iloc[0])
            avg_skills = float(stats_df["avg_skills"].iloc[0])
            
            status_text.text("📊 Fetching top skills...")
            progress_bar.progress(80)
            
            skills_df = athena.get_top_skills(limit=top_n)
            skills_df["job_count"] = skills_df["job_count"].astype(int)
            skills_df["percentage"] = skills_df["percentage"].astype(float)
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            top_skill = skills_df.iloc[0]["skill"]
            top_percentage = skills_df.iloc[0]["percentage"]
            
            st.success(f"✅ Data loaded from Athena in {query_time:.2f} seconds!")
            
            # Metrics with trend indicators
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Total Jobs", f"{total_jobs:,}", "Live from S3")
            
            with col2:
                st.metric("✅ Jobs with Skills", f"{jobs_with_skills:,}", 
                         f"{(jobs_with_skills/total_jobs*100):.1f}%")
            
            with col3:
                st.metric("🏆 #1 Skill", top_skill, f"{top_percentage}%")
            
            with col4:
                st.metric("📈 Avg Skills/Job", f"{avg_skills:.1f}", "Real data")
            
            st.divider()
            
            # NEW: Add skill trend indicators
            st.subheader("🔥 Skill Demand Levels")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🔥 HOT (30%+)")
                hot_skills = skills_df[skills_df["percentage"] >= 30]
                for _, row in hot_skills.iterrows():
                    st.markdown(f'<div class="hot-skill">{row["skill"]}: {row["percentage"]:.1f}%</div>', 
                               unsafe_allow_html=True)
                    st.write("")
            
            with col2:
                st.markdown("### 📈 GROWING (15-30%)")
                growing_skills = skills_df[(skills_df["percentage"] >= 15) & (skills_df["percentage"] < 30)]
                for _, row in growing_skills.iterrows():
                    st.markdown(f'<div class="growing-skill">{row["skill"]}: {row["percentage"]:.1f}%</div>', 
                               unsafe_allow_html=True)
                    st.write("")
            
            with col3:
                st.markdown("### 🟢 STABLE (5-15%)")
                stable_skills = skills_df[(skills_df["percentage"] >= 5) & (skills_df["percentage"] < 15)]
                for _, row in stable_skills.iterrows():
                    st.markdown(f'<div class="stable-skill">{row["skill"]}: {row["percentage"]:.1f}%</div>', 
                               unsafe_allow_html=True)
                    st.write("")
            
            st.divider()
            
            st.header(f"📊 Top {top_n} Skills")
            st.caption("🔴 LIVE data from Athena")
            
            fig = px.bar(
                skills_df, 
                x="percentage", 
                y="skill", 
                orientation="h",
                color="percentage",
                color_continuous_scale="Viridis",
                text="percentage",
                title=f"Skills Demand ({total_jobs:,} jobs)"
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📉 Market Share")
                fig_pie = px.pie(skills_df.head(10), values="job_count", names="skill", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.subheader("📊 Job Counts")
                fig_bar = px.bar(skills_df.head(10), x="skill", y="job_count", color="job_count")
                fig_bar.update_layout(showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

with tab2:
    st.header("🔍 Detailed Analysis")
    if "skills_df" in locals():
        st.dataframe(skills_df, use_container_width=True, hide_index=True)
        csv = skills_df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "skills_data.csv", "text/csv")

with tab3:
    st.header("📂 Skill Categories")
    st.write("Skills grouped by technology domain")
    
    if "skills_df" in locals():
        categories = {
            "Methodology": ["REST API", "Agile"],
            "Programming": ["Python", "JavaScript", "Java", "TypeScript"],
            "Cloud": ["AWS", "Docker", "Kubernetes"],
            "Data": ["SQL", "MongoDB"],
            "DevOps": ["Git", "CI/CD"],
            "ML/AI": ["Machine Learning", "Kafka"],
            "Web": ["React", "Node.js"]
        }
        
        categorized_data = {}
        for category, skill_list in categories.items():
            category_skills = skills_df[skills_df["skill"].isin(skill_list)]
            if not category_skills.empty:
                categorized_data[category] = {
                    "total_jobs": int(category_skills["job_count"].sum()),
                    "skills": category_skills
                }
        
        sorted_categories = sorted(categorized_data.items(), 
                                  key=lambda x: x[1]["total_jobs"], 
                                  reverse=True)
        
        col1, col2 = st.columns(2)
        
        for i, (category, data) in enumerate(sorted_categories):
            col = col1 if i % 2 == 0 else col2
            
            with col:
                st.subheader(f"{category}")
                st.metric("Total Jobs", data["total_jobs"])
                
                for _, row in data["skills"].iterrows():
                    st.write(f"**{row['skill']}**: {row['job_count']} jobs ({row['percentage']:.1f}%)")
                
                st.divider()
        
        st.subheader("📊 Category Comparison")
        
        category_totals = pd.DataFrame([
            {"Category": cat, "Total Jobs": data["total_jobs"]}
            for cat, data in sorted_categories
        ])
        
        fig = px.bar(
            category_totals,
            x="Total Jobs",
            y="Category",
            orientation="h",
            title="Jobs by Technology Domain",
            color="Total Jobs",
            color_continuous_scale="Blues"
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("⚡ Athena Connection")
    st.code("""Database: job_skills_db
Table: jobs_with_skills
Storage: S3 (job-skills-raw-223280412524)
Query Engine: Amazon Athena""")
    
    st.code("""SELECT skill, COUNT(*) as job_count,
    ROUND(COUNT(*) * 100.0 / 
        (SELECT COUNT(*) FROM jobs_with_skills 
         WHERE skill_count > 0), 2) as percentage
FROM jobs_with_skills
CROSS JOIN UNNEST(skills) AS t(skill)
GROUP BY skill
ORDER BY job_count DESC
LIMIT 15""", language="sql")
    
    if "query_time" in locals():
        st.success(f"⚡ Query time: {query_time:.3f}s")
