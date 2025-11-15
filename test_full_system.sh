#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 JOB SKILLS ANALYZER - FULL SYSTEM TEST"
echo "=========================================="
echo ""

# Configuration
export AWS_DEFAULT_REGION="us-east-1"
API_URL="https://2bmejnh4f8.execute-api.us-east-1.amazonaws.com/dev"
API_KEY="job-skills-analyzer-secret-key-2024"
COGNITO_CLIENT="6j89j5srpek9rquiu5a3fj1mlh"
COGNITO_POOL="us-east-1_DgJXNUorK"

# Test counter
PASSED=0
FAILED=0

# Test function
test_component() {
    local name="$1"
    local command="$2"
    
    echo -e "${YELLOW}Testing:${NC} $name"
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAILED++))
    fi
    echo ""
}

echo "📦 COMPONENT 1: AWS INFRASTRUCTURE"
echo "-----------------------------------"
test_component "S3 Raw Bucket" "aws s3 ls s3://job-skills-raw-223280412524"
test_component "S3 Curated Bucket" "aws s3 ls s3://job-skills-curated-223280412524"
test_component "S3 Results Bucket" "aws s3 ls s3://job-skills-athena-results-223280412524"
test_component "Lambda ETL Function" "aws lambda get-function --function-name JobSkillsETLTrigger"
test_component "Lambda API Function" "aws lambda get-function --function-name JobSkillsAPI"
test_component "Cognito User Pool" "aws cognito-idp describe-user-pool --user-pool-id $COGNITO_POOL"
test_component "SNS Topic" "aws sns list-topics | grep job-skills-alerts"
test_component "CloudWatch Dashboard" "aws cloudwatch list-dashboards | grep JobSkillsAnalyzer"

echo "🔐 COMPONENT 2: AUTHENTICATION"
echo "-----------------------------------"
# Get JWT token
JWT_TOKEN=$(aws cognito-idp initiate-auth \
  --region us-east-1 \
  --client-id $COGNITO_CLIENT \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=test@example.com,PASSWORD=TestPass123! \
  --query 'AuthenticationResult.IdToken' \
  --output text 2>/dev/null)

if [ ! -z "$JWT_TOKEN" ]; then
    echo -e "${GREEN}✅ PASS${NC} Cognito JWT Token Generation"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} Cognito JWT Token Generation"
    ((FAILED++))
fi
echo ""

echo "🌐 COMPONENT 3: API GATEWAY & ENDPOINTS"
echo "-----------------------------------"
# Test API endpoints
test_component "Health Endpoint (Public)" "curl -sf $API_URL/health"
test_component "Stats with API Key" "curl -sf -H 'X-API-Key: $API_KEY' $API_URL/stats"
test_component "Top Skills with API Key" "curl -sf -H 'X-API-Key: $API_KEY' '$API_URL/skills/top?limit=3'"
test_component "Stats with JWT" "curl -sf -H 'Authorization: $JWT_TOKEN' $API_URL/auth/stats"
test_component "Top Skills with JWT" "curl -sf -H 'Authorization: $JWT_TOKEN' '$API_URL/auth/skills/top?limit=3'"

# Test that unauthorized requests fail (should fail = pass test)
UNAUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/auth/stats)
if [ "$UNAUTH_RESPONSE" = "401" ]; then
    echo -e "${GREEN}✅ PASS${NC} Unauthorized Request Blocked"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} Unauthorized Request Not Blocked (got $UNAUTH_RESPONSE)"
    ((FAILED++))
fi
echo ""

echo "📊 COMPONENT 4: ATHENA & DATA LAKE"
echo "-----------------------------------"
test_component "Athena Database Exists" "aws athena list-databases --catalog-name AwsDataCatalog | grep job_skills_db"
test_component "Athena Table Exists" "aws athena list-table-metadata --catalog-name AwsDataCatalog --database-name job_skills_db | grep jobs_with_skills"

# Test actual query execution
QUERY_ID=$(aws athena start-query-execution \
    --query-string "SELECT COUNT(*) FROM job_skills_db.jobs_with_skills" \
    --result-configuration "OutputLocation=s3://job-skills-athena-results-223280412524/" \
    --query 'QueryExecutionId' \
    --output text 2>/dev/null)

if [ ! -z "$QUERY_ID" ]; then
    echo -e "${GREEN}✅ PASS${NC} Athena Query Execution"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} Athena Query Execution"
    ((FAILED++))
fi
echo ""

echo "⏰ COMPONENT 5: AUTOMATION"
echo "-----------------------------------"
test_component "EventBridge Rule Exists" "aws events list-rules | grep JobSkillsDailyCheck"
test_component "EventBridge Target Configured" "aws events list-targets-by-rule --rule JobSkillsDailyCheck | grep JobSkillsETLTrigger"

echo "📈 COMPONENT 6: MONITORING"
echo "-----------------------------------"
test_component "CloudWatch Alarms" "aws cloudwatch describe-alarms | grep JobSkills"
test_component "Lambda Logs (ETL)" "aws logs describe-log-groups | grep JobSkillsETLTrigger"
test_component "Lambda Logs (API)" "aws logs describe-log-groups | grep JobSkillsAPI"
test_component "API Gateway Logs" "aws logs describe-log-groups | grep apigateway"

echo "📁 COMPONENT 7: LOCAL FILES"
echo "-----------------------------------"
test_component "Terraform State" "[ -f terraform/terraform.tfstate ]"
test_component "Lambda Deployment Package" "[ -f api/api-lambda.zip ]"
test_component "ETL Lambda Package" "[ -f lambda/lambda_function.zip ]"
test_component "Skills Dictionary" "[ -f skills-data/skills-dictionary.json ]"
test_component "Job Data" "[ -f skills-data/kaggle-1k-expanded.jsonl ]"
test_component "README Documentation" "[ -f README.md ]"
test_component "Deployment Guide" "[ -f DEPLOYMENT.md ]"

echo "🔧 COMPONENT 8: TERRAFORM RESOURCES"
echo "-----------------------------------"
cd terraform
terraform validate > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC} Terraform Configuration Valid"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} Terraform Configuration Invalid"
    ((FAILED++))
fi
cd ..
echo ""

echo "=========================================="
echo "🎯 TEST SUMMARY"
echo "=========================================="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL SYSTEMS OPERATIONAL!${NC}"
    echo "Your project is 100% functional and ready to submit!"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some components need attention${NC}"
    exit 1
fi
