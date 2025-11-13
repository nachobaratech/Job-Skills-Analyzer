#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "dashboard"))

from athena_helper import AthenaHelper
import pandas as pd
from itertools import combinations
from collections import defaultdict

class AdvancedAnalytics:
    def __init__(self):
        self.athena = AthenaHelper()
    
    def get_skill_cooccurrence(self, min_count=5):
        """Find skills that frequently appear together"""
        print("🔍 Analyzing skill co-occurrences...")
        
        query = """
        SELECT id, skills, skill_count
        FROM jobs_with_skills
        WHERE skill_count >= 2
        """
        
        df = self.athena.run_query(query)
        
        cooccurrence = defaultdict(int)
        
        for _, row in df.iterrows():
            try:
                skills_list = eval(row["skills"]) if isinstance(row["skills"], str) else row["skills"]
                
                for skill1, skill2 in combinations(sorted(skills_list), 2):
                    pair = f"{skill1} + {skill2}"
                    cooccurrence[pair] += 1
            except:
                continue
        
        results = [(pair, count) for pair, count in cooccurrence.items() if count >= min_count]
        results.sort(key=lambda x: x[1], reverse=True)
        
        print(f"✅ Found {len(results)} skill pairs")
        return results
    
    def get_skill_categories(self):
        """Categorize skills into groups"""
        categories = {
            "Programming": ["Python", "JavaScript", "Java", "TypeScript"],
            "Cloud": ["AWS", "Docker", "Kubernetes"],
            "Data": ["SQL", "MongoDB"],
            "Web": ["React", "Node.js"],
            "DevOps": ["Git", "CI/CD"],
            "Methodology": ["Agile", "REST API"],
            "ML": ["Machine Learning", "Kafka"]
        }
        
        df = self.athena.get_top_skills(limit=50)
        
        categorized = defaultdict(list)
        
        for _, row in df.iterrows():
            skill = row["skill"]
            for category, skills in categories.items():
                if skill in skills:
                    categorized[category].append({
                        "skill": skill,
                        "count": int(row["job_count"]),
                        "percentage": float(row["percentage"])
                    })
                    break
        
        return dict(categorized)

if __name__ == "__main__":
    analytics = AdvancedAnalytics()
    
    print("=" * 60)
    print("📊 SKILL CO-OCCURRENCE ANALYSIS")
    print("=" * 60)
    
    cooccurrence = analytics.get_skill_cooccurrence(min_count=5)
    
    print("\n🔝 Top 15 Skill Pairs:")
    for i, (pair, count) in enumerate(cooccurrence[:15], 1):
        print(f"{i:2d}. {pair:40s}: {count:3d} jobs")
    
    print("\n" + "=" * 60)
    print("📂 SKILL CATEGORIES")
    print("=" * 60)
    
    categorized = analytics.get_skill_categories()
    
    for category, skills in sorted(categorized.items()):
        print(f"\n{category}:")
        for skill in skills:
            print(f"  • {skill['skill']:20s}: {skill['count']:3d} jobs ({skill['percentage']:.1f}%)")
    
    print("\n✅ Advanced analytics complete!")
