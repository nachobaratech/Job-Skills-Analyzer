# Fix all references to aws_athena_database.job_skills_db

# Fix main.tf
with open('main.tf', 'r') as f:
    content = f.read()

# Replace references with hardcoded database name
content = content.replace(
    'depends_on = [aws_athena_database.job_skills_db]',
    '# depends_on = [aws_athena_database.job_skills_db] # Database managed manually'
)
content = content.replace(
    'ATHENA_DATABASE = aws_athena_database.job_skills_db.name',
    'ATHENA_DATABASE = "job_skills_db"  # Database managed manually'
)

with open('main.tf', 'w') as f:
    f.write(content)

# Fix outputs.tf
with open('outputs.tf', 'r') as f:
    content = f.read()

content = content.replace(
    'value       = aws_athena_database.job_skills_db.name',
    'value       = "job_skills_db"  # Database managed manually'
)

with open('outputs.tf', 'w') as f:
    f.write(content)

print("✅ Fixed all Athena database references")
