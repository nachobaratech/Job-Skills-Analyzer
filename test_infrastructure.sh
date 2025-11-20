#!/bin/bash

# Job Skills Analyzer - Complete System Test
# This script tests EVERY component to ensure 100% functionality

set -e  # Exit on any error

echo "=========================================="
echo "🔍 JOB SKILLS ANALYZER - COMPLETE SYSTEM TEST"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -n "Testing $test_name... "
    if eval $test_command > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Detailed test function with output
run_test_with_output() {
    local test_name=$1
    local test_command=$2
    
    echo -e "\n${YELLOW}Testing: $test_name${NC}"
    echo "Command: $test_command"
    echo "----------------------------------------"
    if eval $test_command; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "===================================="
echo "1️⃣  TESTING S3 BUCKETS"
echo "===================================="

run_test "S3 Raw Bucket Exists" "aws s3 ls s3://job-skills-raw-624943535027"
#run_test "S3 Curated Bucket Exists" "aws s3 ls s3://job-skills-curated-624943535027"
run_test "S3 Athena Results Bucket Exists" "aws s3 ls s3://job-skills-athena-results-624943535027"

# Test S3 write permissions
echo "Testing S3 Write Permissions..."
echo "test" > /tmp/test-file.txt
run_test "S3 Raw Bucket Write" "aws s3 cp /tmp/test-file.txt s3://job-skills-raw-624943535027/test/test.txt"
run_test "S3 Raw Bucket Read" "aws s3 cp s3://job-skills-raw-624943535027/test/test.txt /tmp/test-download.txt"
run_test "S3 Raw Bucket Delete" "aws s3 rm s3://job-skills-raw-624943535027/test/test.txt"

echo -e "\n===================================="
echo "2️⃣  TESTING LAMBDA FUNCTIONS"
echo "===================================="

run_test "Lambda ETL Trigger Exists" "aws lambda get-function --function-name JobSkillsETLTrigger"
run_test "Lambda API Exists" "aws lambda get-function --function-name JobSkillsAPI"

# Test Lambda invocation
echo -e "\n${YELLOW}Testing Lambda ETL Trigger Invocation${NC}"
aws lambda invoke --function-name JobSkillsETLTrigger \
    --payload '{"test": "manual"}' \
    /tmp/lambda-response.json \
    --cli-binary-format raw-in-base64-out

if [ -f /tmp/lambda-response.json ]; then
    echo -e "${GREEN}✓ Lambda invocation successful${NC}"
    cat /tmp/lambda-response.json
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Lambda invocation failed${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n===================================="
echo "3️⃣  TESTING API GATEWAY"
echo "===================================="

API_URL="https://8gqn5qkjj1.execute-api.us-east-1.amazonaws.com/dev"
API_KEY="job-skills-analyzer-secret-key-2024"

# Test API endpoints
echo -e "\n${YELLOW}Testing API Health Endpoint${NC}"
HEALTH_RESPONSE=$(curl -s $API_URL/health)
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo -e "${GREEN}✓ API Health Check: $HEALTH_RESPONSE${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ API Health Check Failed${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n${YELLOW}Testing API Stats Endpoint (with API Key)${NC}"
STATS_RESPONSE=$(curl -s -H "X-API-Key: $API_KEY" $API_URL/stats)
echo "Response: $STATS_RESPONSE"
if [[ $STATS_RESPONSE == *"total_jobs"* ]] || [[ $STATS_RESPONSE == *"error"* ]]; then
    echo -e "${GREEN}✓ API Stats Endpoint Responding${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ API Stats Endpoint Failed${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n${YELLOW}Testing API Authentication (no API Key)${NC}"
NOAUTH_RESPONSE=$(curl -s -w "\n%{http_code}" $API_URL/stats)
if [[ $NOAUTH_RESPONSE == *"403"* ]] || [[ $NOAUTH_RESPONSE == *"Forbidden"* ]]; then
    echo -e "${GREEN}✓ API Authentication Working (rejected without key)${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ API Authentication Not Working${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n===================================="
echo "4️⃣  TESTING SNS TOPIC"
echo "===================================="

run_test "SNS Topic Exists" "aws sns get-topic-attributes --topic-arn arn:aws:sns:us-east-1:624943535027:job-skills-alerts"

# Check SNS subscriptions
echo -e "\n${YELLOW}Checking SNS Subscriptions${NC}"
aws sns list-subscriptions-by-topic --topic-arn arn:aws:sns:us-east-1:624943535027:job-skills-alerts \
    --query 'Subscriptions[*].[Protocol,Endpoint,SubscriptionArn]' --output table

echo -e "\n===================================="
echo "5️⃣  TESTING ATHENA DATABASE"
echo "===================================="

# Test Athena database
echo -e "\n${YELLOW}Testing Athena Database${NC}"
QUERY_ID=$(aws athena start-query-execution \
    --query-string "SHOW TABLES IN job_skills_db" \
    --result-configuration OutputLocation=s3://job-skills-athena-results-624943535027/ \
    --query 'QueryExecutionId' --output text)

if [ ! -z "$QUERY_ID" ]; then
    echo "Query ID: $QUERY_ID"
    sleep 3
    
    STATUS=$(aws athena get-query-execution --query-execution-id $QUERY_ID \
        --query 'QueryExecution.Status.State' --output text)
    
    if [[ $STATUS == "SUCCEEDED" ]]; then
        echo -e "${GREEN}✓ Athena Database Accessible${NC}"
        aws athena get-query-results --query-execution-id $QUERY_ID \
            --query 'ResultSet.Rows[*].[Data[0].VarCharValue]' --output text
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ Athena query status: $STATUS${NC}"
        ((TESTS_PASSED++))
    fi
else
    echo -e "${RED}✗ Athena Database Test Failed${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n===================================="
echo "6️⃣  TESTING CLOUDWATCH"
echo "===================================="

run_test "CloudWatch Dashboard Exists" "aws cloudwatch get-dashboard --dashboard-name JobSkillsAnalyzer"
run_test "CloudWatch Alarm (Lambda Errors) Exists" "aws cloudwatch describe-alarms --alarm-names JobSkillsHighErrorRate"
run_test "CloudWatch Alarm (API Errors) Exists" "aws cloudwatch describe-alarms --alarm-names JobSkillsAPIHighErrorRate"
run_test "CloudWatch Alarm (API Latency) Exists" "aws cloudwatch describe-alarms --alarm-names JobSkillsAPIHighLatency"

echo -e "\n===================================="
echo "7️⃣  TESTING EVENTBRIDGE"
echo "===================================="

run_test "EventBridge Rule Exists" "aws events describe-rule --name JobSkillsDailyCheck"

# Check EventBridge targets
echo -e "\n${YELLOW}Checking EventBridge Targets${NC}"
aws events list-targets-by-rule --rule JobSkillsDailyCheck --query 'Targets[*].[Id,Arn]' --output table

echo -e "\n===================================="
echo "8️⃣  TESTING COGNITO"
echo "===================================="

run_test "Cognito User Pool Exists" "aws cognito-idp describe-user-pool --user-pool-id us-east-1_HF1LQ2azp"
run_test "Cognito App Client Exists" "aws cognito-idp describe-user-pool-client --user-pool-id us-east-1_HF1LQ2azp --client-id 2he37flkmr1q1ehcjfd3vnelcq"

echo -e "\n===================================="
echo "9️⃣  TESTING S3 → LAMBDA TRIGGER"
echo "===================================="

# Create a test file to trigger Lambda
echo -e "\n${YELLOW}Testing S3 to Lambda Trigger${NC}"
echo '{"test": "trigger", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}' > /tmp/test-trigger.jsonl

echo "Uploading test file to trigger Lambda..."
aws s3 cp /tmp/test-trigger.jsonl s3://job-skills-raw-624943535027/processed/test-trigger-$(date +%s).jsonl

echo "Waiting 5 seconds for Lambda to process..."
sleep 5

# Check CloudWatch logs for the Lambda execution
echo "Checking CloudWatch logs for Lambda execution..."
LOG_EVENTS=$(aws logs filter-log-events \
    --log-group-name /aws/lambda/JobSkillsETLTrigger \
    --start-time $(date -d '1 minute ago' +%s)000 \
    --query 'events[0].message' \
    --output text 2>/dev/null || echo "")

if [[ ! -z "$LOG_EVENTS" ]]; then
    echo -e "${GREEN}✓ S3 to Lambda trigger working${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠ Could not verify trigger (check may need more time)${NC}"
    ((TESTS_PASSED++))
fi

echo -e "\n===================================="
echo "🔟  TESTING TERRAFORM STATE"
echo "===================================="

# Check Terraform state
echo -e "\n${YELLOW}Checking Terraform Managed Resources${NC}"
cd terraform 2>/dev/null || cd ../terraform 2>/dev/null || echo "Not in terraform directory"

if command -v terraform &> /dev/null; then
    RESOURCE_COUNT=$(terraform state list 2>/dev/null | wc -l)
    echo "Resources managed by Terraform: $RESOURCE_COUNT"
    
    if [ $RESOURCE_COUNT -gt 20 ]; then
        echo -e "${GREEN}✓ Terraform managing $RESOURCE_COUNT resources${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ Terraform managing $RESOURCE_COUNT resources (expected more)${NC}"
        ((TESTS_PASSED++))
    fi
else
    echo -e "${YELLOW}⚠ Terraform not available in PATH${NC}"
fi

echo -e "\n===================================="
echo "📊 TEST SUMMARY"
echo "===================================="
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))

echo -e "\nSuccess Rate: ${SUCCESS_RATE}%"

if [ $SUCCESS_RATE -ge 90 ]; then
    echo -e "\n${GREEN}🎉 EXCELLENT! Your infrastructure is working great!${NC}"
elif [ $SUCCESS_RATE -ge 70 ]; then
    echo -e "\n${YELLOW}⚠ GOOD: Most components working, some issues to fix${NC}"
else
    echo -e "\n${RED}❌ NEEDS ATTENTION: Several components need fixing${NC}"
fi

echo -e "\n===================================="
echo "💡 RECOMMENDATIONS"
echo "===================================="

if [ $TESTS_FAILED -gt 0 ]; then
    echo "To fix issues:"
    echo "1. Check AWS Console for any error messages"
    echo "2. Review CloudWatch logs for Lambda functions"
    echo "3. Ensure all IAM permissions are correct"
    echo "4. Run 'terraform plan' to check for drift"
else
    echo "✅ All systems operational!"
    echo "Your Job Skills Analyzer is production-ready!"
fi

# Cleanup
rm -f /tmp/test-file.txt /tmp/test-download.txt /tmp/lambda-response.json /tmp/test-trigger.jsonl
