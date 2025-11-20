import boto3
import time
import pandas as pd

class AthenaHelper:
    def __init__(self):
        self.client = boto3.client('athena', region_name='us-east-1')
        self.database = 'job_skills_db'
        self.output_location = 's3://job-skills-athena-results-624943535027/'
    
    def run_query(self, query):
        """Execute Athena query and return results as DataFrame"""
        # Start query execution
        response = self.client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': self.database},
            ResultConfiguration={'OutputLocation': self.output_location}
        )
        
        query_execution_id = response['QueryExecutionId']
        
        # Wait for query to complete
        while True:
            result = self.client.get_query_execution(QueryExecutionId=query_execution_id)
            status = result['QueryExecution']['Status']['State']
            
            if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
            time.sleep(1)
        
        if status == 'SUCCEEDED':
            # Get results
            result = self.client.get_query_results(QueryExecutionId=query_execution_id)
            
            # Convert to DataFrame
            columns = [col['Label'] for col in result['ResultSet']['ResultSetMetadata']['ColumnInfo']]
            rows = []
            for row in result['ResultSet']['Rows'][1:]:  # Skip header row
                rows.append([field.get('VarCharValue', '') for field in row['Data']])
            
            return pd.DataFrame(rows, columns=columns)
        else:
            raise Exception(f"Query failed with status: {status}")
    
    def get_top_skills(self, limit=15):
        """Get top skills from Athena"""
        query = f"""
        SELECT 
            skill,
            COUNT(*) as job_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs_with_skills WHERE skill_count > 0), 2) as percentage
        FROM jobs_with_skills
        CROSS JOIN UNNEST(skills) AS t(skill)
        GROUP BY skill
        ORDER BY job_count DESC
        LIMIT {limit}
        """
        return self.run_query(query)
    
    def get_job_stats(self):
        """Get overall job statistics"""
        query = """
        SELECT 
            COUNT(*) as total_jobs,
            COUNT(DISTINCT CASE WHEN skill_count > 0 THEN id END) as jobs_with_skills,
            AVG(skill_count) as avg_skills
        FROM jobs_with_skills
        """
        return self.run_query(query)
