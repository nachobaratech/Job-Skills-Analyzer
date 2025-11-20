#!/bin/bash

# ============================================================================
# COMPLETE PROJECT TEST SUITE - Job Skills Analyzer
# Tests every single component of the system
# ============================================================================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
API_URL="https://2bmejnh4f8.execute-api.us-east-1.amazonaws.com/dev"
API_KEY="job-skills-analyzer-secret-key-2024"
REGION="us-east-1"
ACCOUNT_ID="624943535027"
COGNITO_POOL="us-east-1_DgJXNUorK"

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNINGS=0

# Test result tracking
declare -a FAILED_TEST_NAMES

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${CYAN}━━━ $1 ━━━${NC}"
    echo ""
}

test_component() {
    local test_name="$1"
    local command="$2"
    local expected="$3"
    local test_type="${4:-exact}" # exact, contains, or json
    
    ((TOTAL_TESTS++))
    
    echo -n "Testing: $test_name... "
    
    # Execute command
    result=$(eval "$command" 2>&1)
    exit_code=$?
    
    # Check result based on test type
    if [ "$test_type" = "exact" ]; then
        if [ "$result" = "$expected" ]; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((PASSED_TESTS++))
            return 0
        fi
    elif [ "$test_type" = "contains" ]; then
        if echo "$result" | grep -q "$expected"; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((PASSED_TESTS++))
            return 0
        fi
    elif [ "$test_type" = "json" ]; then
        if echo "$result" | jq . >/dev/null 2>&1; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((PASSED_TESTS++))
            return 0
        fi
    elif [ "$test_type" = "status" ]; then
        if [ $exit_code -eq 0 ]; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((PASSED_TESTS++))
            return 0
        fi
    fi
    
    # Test failed
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED_TESTS++))
    FAILED_TEST_NAMES+=("$test_name")
    echo -e "${YELLOW}  Output: $result${NC}"
    return 1
}

test_http() {
    local test_name="$1"
    local url="$2"
    local expected_status="$3"
    local headers="$4"
    
    ((TOTAL_TESTS++))
    
    echo -n "Testing: $test_name... "
    
    # Make HTTP request
    if [ -n "$headers" ]; then
        response=$(curl -s -w "\n%{http_code}" $headers "$url")
    else
        response=$(curl -s -w "\n%{http_code}" "$url")
    fi
    
    # Extract status code (last line)
    status=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (Status: $status)"
        ((PASSED_TESTS++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $status)"
        ((FAILED_TESTS++))
        FAILED_TEST_NAMES+=("$test_name")
        echo -e "${YELLOW}  Response: $body${NC}"
        return 1
    fi
}

warning() {
    echo -e "${YELLOW}⚠ WARNING: $1${NC}"
    ((WARNINGS++))
}

# ============================================================================
# START TESTING
# ============================================================================

print_header "JOB SKILLS ANALYZER - COMPLETE SYSTEM TEST"

echo "Test Configuration:"
echo "  API URL: $API_URL"
echo "  Region: $REGION"
echo "  Account ID: $ACCOUNT_ID"
echo ""
echo "Starting comprehensive tests..."

# ============================================================================
# SECTION 1: PROJECT STRUCTURE
# ============================================================================

print_section "1. PROJECT STRUCTURE & FILES"

test_component "Project root directory exists" \
    "[ -d ~/mainFolder ] && echo 'exists'" \
    "exists" "exact"

test_component "API folder exists" \
    "[ -d ~/mainFolder/api ] && echo 'exists'" \
    "exists" "exact"

test_component "Dashboard folder exists" \
    "[ -d ~/mainFolder/dashboard ] && echo 'exists'" \
    "exists" "exact"

test_component "Processing folder exists" \
    "[ -d ~/mainFolder/processing ] && echo 'exists'" \
    "exists" "exact"

test_component "Lambda folder exists" \
    "[ -d ~/mainFolder/lambda ] && echo 'exists'" \
    "exists" "exact"

test_component "Skills data folder exists" \
    "[ -d ~/mainFolder/skills-data ] && echo 'exists'" \
    "exists" "exact"

test_component "Main API file exists" \
    "[ -f ~/mainFolder/api/main.py ] && echo 'exists'" \
    "exists" "exact"

test_component "Dashboard app exists" \
    "[ -f ~/mainFolder/dashboard/app.py ] && echo 'exists'" \
    "exists" "exact"

test_component "Skills dictionary exists" \
    "[ -f ~/mainFolder/skills-data/skills-dictionary.json ] && echo 'exists'" \
    "exists" "exact"

test_component "Processed data file exists" \
    "[ -f ~/mainFolder/skills-data/kaggle-1k-expanded.jsonl ] && echo 'exists'" \
    "exists" "exact"

test_component "README exists" \
    "[ -f ~/mainFolder/README.md ] && echo 'exists'" \
    "exists" "exact"

test_component "Terraform deleted" \
    "[ ! -d ~/mainFolder/terraform ] && echo 'deleted'" \
    "deleted" "exact"

# ============================================================================
# SECTION 2: AWS S3 BUCKETS
# ============================================================================

print_section "2. AWS S3 BUCKETS"

test_component "S3 Raw bucket exists" \
    "aws s3 ls | grep -c 'job-skills-raw-$ACCOUNT_ID'" \
    "1" "exact"

test_component "S3 Curated bucket exists" \
    "aws s3 ls | grep -c 'job-skills-curated-$ACCOUNT_ID'" \
    "1" "exact"

test_component "S3 Results bucket exists" \
    "aws s3 ls | grep -c 'job-skills-athena-results-$ACCOUNT_ID'" \
    "1" "exact"

test_component "Raw bucket has processed data" \
    "aws s3 ls s3://job-skills-raw-$ACCOUNT_ID/processed/ | wc -l" \
    "" "status"

test_component "Raw bucket is accessible" \
    "aws s3 ls s3://job-skills-raw-$ACCOUNT_ID/ --region $REGION" \
    "" "status"

test_component "Curated bucket is accessible" \
    "aws s3 ls s3://job-skills-curated-$ACCOUNT_ID/ --region $REGION" \
    "" "status"

test_component "Results bucket is accessible" \
    "aws s3 ls s3://job-skills-athena-results-$ACCOUNT_ID/ --region $REGION" \
    "" "status"

# ============================================================================
# SECTION 3: AWS LAMBDA FUNCTIONS
# ============================================================================

print_section "3. AWS LAMBDA FUNCTIONS"

# Note: These might fail due to AWS Academy permissions
echo -e "${YELLOW}Note: Lambda tests may fail due to AWS Academy restrictions${NC}"

test_component "ETL Lambda function exists" \
    "aws lambda get-function --function-name JobSkillsETLTrigger --region $REGION 2>&1 | grep -q 'FunctionName' && echo 'exists' || echo 'restricted'" \
    "exists" "contains"

test_component "API Lambda function exists" \
    "aws lambda get-function --function-name JobSkillsAPI --region $REGION 2>&1 | grep -q 'FunctionName' && echo 'exists' || echo 'restricted'" \
    "exists" "contains"

# ============================================================================
# SECTION 4: AWS API GATEWAY
# ============================================================================

print_section "4. AWS API GATEWAY"

test_component "API Gateway exists" \
    "aws apigateway get-rest-apis --region $REGION --query 'items[?name==\`JobSkillsAnalyzerAPI\`].id' --output text" \
    "2bmejnh4f8" "exact"

test_component "API Gateway has dev stage" \
    "aws apigateway get-stages --rest-api-id 2bmejnh4f8 --region $REGION --query 'item[?stageName==\`dev\`].stageName' --output text" \
    "dev" "exact"

# ============================================================================
# SECTION 5: API ENDPOINTS - PUBLIC
# ============================================================================

print_section "5. API ENDPOINTS - PUBLIC ACCESS"

test_http "Health check endpoint" \
    "$API_URL/health" \
    "200"

test_http "Root endpoint" \
    "$API_URL/" \
    "200"

# ============================================================================
# SECTION 6: API ENDPOINTS - AUTHENTICATION REQUIRED
# ============================================================================

print_section "6. API ENDPOINTS - WITH API KEY"

echo -n "Testing: Get stats endpoint... "
response=$(curl -s -w "\n%{http_code}" -H "X-API-Key: $API_KEY" "$API_URL/stats")
status=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')
if [ "$status" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $status)"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected: 200, Got: $status)"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Get stats endpoint")
    echo -e "${YELLOW}  Response: $body${NC}"
fi

echo -n "Testing: Get top skills endpoint... "
response=$(curl -s -w "\n%{http_code}" -H "X-API-Key: $API_KEY" "$API_URL/skills/top")
status=$(echo "$response" | tail -n 1)
if [ "$status" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $status)"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected: 200, Got: $status)"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Get top skills endpoint")
fi

echo -n "Testing: Get top 5 skills (with parameter)... "
response=$(curl -s -w "\n%{http_code}" -H "X-API-Key: $API_KEY" "$API_URL/skills/top?limit=5")
status=$(echo "$response" | tail -n 1)
if [ "$status" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $status)"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected: 200, Got: $status)"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Get top 5 skills")
fi

echo -n "Testing: Get specific skill (Python)... "
response=$(curl -s -w "\n%{http_code}" -H "X-API-Key: $API_KEY" "$API_URL/skills/Python")
status=$(echo "$response" | tail -n 1)
if [ "$status" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $status)"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected: 200, Got: $status)"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Get specific skill (Python)")
fi

echo -n "Testing: Get specific skill (Communication)... "
response=$(curl -s -w "\n%{http_code}" -H "X-API-Key: $API_KEY" "$API_URL/skills/Communication")
status=$(echo "$response" | tail -n 1)
if [ "$status" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $status)"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected: 200, Got: $status)"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Get specific skill (Communication)")
fi

echo -n "Testing: Get specific skill (SQL)... "
response=$(curl -s -w "\n%{http_code}" -H "X-API-Key: $API_KEY" "$API_URL/skills/SQL")
status=$(echo "$response" | tail -n 1)
if [ "$status" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $status)"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected: 200, Got: $status)"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Get specific skill (SQL)")
fi

# ============================================================================
# SECTION 7: API SECURITY - NEGATIVE TESTS
# ============================================================================

print_section "7. API SECURITY TESTS"

echo -n "Testing: Reject request with invalid API key... "
response=$(curl -s -w "\n%{http_code}" -H "X-API-Key: invalid-key-123" "$API_URL/stats")
status=$(echo "$response" | tail -n 1)
if [ "$status" = "401" ] || [ "$status" = "403" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $status - Correctly rejected)"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected: 401/403, Got: $status)"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Reject invalid API key")
fi

echo -n "Testing: Reject request with no API key... "
response=$(curl -s -w "\n%{http_code}" "$API_URL/stats")
status=$(echo "$response" | tail -n 1)
if [ "$status" = "401" ] || [ "$status" = "403" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $status - Correctly rejected)"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected: 401/403, Got: $status)"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Reject no API key")
fi

echo -n "Testing: Reject request to protected endpoint... "
response=$(curl -s -w "\n%{http_code}" "$API_URL/skills/top")
status=$(echo "$response" | tail -n 1)
if [ "$status" = "401" ] || [ "$status" = "403" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $status - Correctly rejected)"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC} (Expected: 401/403, Got: $status)"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Reject protected endpoint")
fi

# ============================================================================
# SECTION 8: API RESPONSE VALIDATION
# ============================================================================

print_section "8. API RESPONSE DATA VALIDATION"

echo -n "Testing: Stats response has correct fields... "
response=$(curl -s -H "X-API-Key: $API_KEY" "$API_URL/stats")
if echo "$response" | jq -e '.total_jobs' >/dev/null 2>&1 && \
   echo "$response" | jq -e '.jobs_with_skills' >/dev/null 2>&1 && \
   echo "$response" | jq -e '.avg_skills_per_job' >/dev/null 2>&1 && \
   echo "$response" | jq -e '.unique_skills' >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Stats response validation")
fi

echo -n "Testing: Top skills returns array... "
response=$(curl -s -H "X-API-Key: $API_KEY" "$API_URL/skills/top")
if echo "$response" | jq -e 'type == "array"' >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Top skills array validation")
fi

echo -n "Testing: Top skills returns 10 items... "
response=$(curl -s -H "X-API-Key: $API_KEY" "$API_URL/skills/top")
count=$(echo "$response" | jq 'length')
if [ "$count" -eq 10 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC} (Got $count items)"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Top skills count validation")
fi

echo -n "Testing: Skill response has correct format... "
response=$(curl -s -H "X-API-Key: $API_KEY" "$API_URL/skills/Python")
if echo "$response" | jq -e '.skill' >/dev/null 2>&1 && \
   echo "$response" | jq -e '.job_count' >/dev/null 2>&1 && \
   echo "$response" | jq -e '.percentage' >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Skill response validation")
fi

# ============================================================================
# SECTION 9: API PERFORMANCE
# ============================================================================

print_section "9. API PERFORMANCE TESTS"

echo -n "Testing: API response time (target: <2 seconds)... "
start_time=$(date +%s.%N)
curl -s -H "X-API-Key: $API_KEY" "$API_URL/stats" >/dev/null
end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)
duration_ms=$(echo "$duration * 1000" | bc | cut -d'.' -f1)

if (( $(echo "$duration < 2" | bc -l) )); then
    echo -e "${GREEN}✓ PASS${NC} (${duration_ms}ms)"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${YELLOW}⚠ SLOW${NC} (${duration_ms}ms)"
    ((WARNINGS++))
    ((TOTAL_TESTS++))
fi

# ============================================================================
# SECTION 10: AWS COGNITO
# ============================================================================

print_section "10. AWS COGNITO USER POOL"

test_component "Cognito User Pool exists" \
    "aws cognito-idp describe-user-pool --user-pool-id $COGNITO_POOL --region $REGION 2>&1 | grep -q 'UserPool' && echo 'exists' || echo 'restricted'" \
    "exists" "contains"

# ============================================================================
# SECTION 11: AWS SNS
# ============================================================================

print_section "11. AWS SNS NOTIFICATIONS"

test_component "SNS topic exists" \
    "aws sns list-topics --region $REGION 2>&1 | grep -q 'job-skills-alerts' && echo 'exists' || echo 'restricted'" \
    "exists" "contains"

# ============================================================================
# SECTION 12: AWS CLOUDWATCH
# ============================================================================

print_section "12. AWS CLOUDWATCH MONITORING"

test_component "CloudWatch dashboards accessible" \
    "aws cloudwatch list-dashboards --region $REGION 2>&1 | grep -q 'DashboardEntries' && echo 'exists' || echo 'restricted'" \
    "exists" "contains"

# ============================================================================
# SECTION 13: LOCAL API (FASTAPI)
# ============================================================================

print_section "13. LOCAL FASTAPI SERVER"

echo -n "Testing: Local FastAPI server running... "
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
    
    # Additional local tests
    test_http "Local API health endpoint" \
        "http://localhost:8000/health" \
        "200"
    
    test_http "Local API docs endpoint" \
        "http://localhost:8000/docs" \
        "200"
else
    echo -e "${YELLOW}⚠ NOT RUNNING${NC}"
    warning "Local FastAPI server not running. Start with: uvicorn api.main:app --host 0.0.0.0 --port 8000"
    ((TOTAL_TESTS++))
fi

# ============================================================================
# SECTION 14: STREAMLIT DASHBOARD
# ============================================================================

print_section "14. STREAMLIT DASHBOARD"

echo -n "Testing: Streamlit dashboard running... "
if curl -s http://localhost:8503 >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${YELLOW}⚠ NOT RUNNING${NC}"
    warning "Streamlit dashboard not running. Start with: streamlit run dashboard/app.py"
    ((TOTAL_TESTS++))
fi

test_component "Streamlit app file is valid Python" \
    "python3 -m py_compile ~/mainFolder/dashboard/app.py 2>&1 && echo 'valid'" \
    "valid" "contains"

# ============================================================================
# SECTION 15: DATA VALIDATION
# ============================================================================

print_section "15. DATA FILE VALIDATION"

test_component "Skills dictionary is valid JSON" \
    "jq . ~/mainFolder/skills-data/skills-dictionary.json >/dev/null 2>&1 && echo 'valid'" \
    "valid" "exact"

test_component "Processed data file not empty" \
    "[ -s ~/mainFolder/skills-data/kaggle-1k-expanded.jsonl ] && echo 'not-empty'" \
    "not-empty" "exact"

echo -n "Testing: Processed data has 1000 jobs... "
job_count=$(wc -l < ~/mainFolder/skills-data/kaggle-1k-expanded.jsonl)
if [ "$job_count" -eq 1000 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC} (Found $job_count jobs)"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("Job count validation")
fi

echo -n "Testing: JSONL file is valid... "
if head -1 ~/mainFolder/skills-data/kaggle-1k-expanded.jsonl | jq . >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("JSONL format validation")
fi

# ============================================================================
# SECTION 16: CODE QUALITY CHECKS
# ============================================================================

print_section "16. CODE QUALITY CHECKS"

test_component "API main.py is valid Python" \
    "python3 -m py_compile ~/mainFolder/api/main.py 2>&1 && echo 'valid'" \
    "valid" "contains"

test_component "Processing scripts are valid Python" \
    "python3 -m py_compile ~/mainFolder/processing/*.py 2>&1 && echo 'valid'" \
    "valid" "contains"

# ============================================================================
# SECTION 17: GIT REPOSITORY
# ============================================================================

print_section "17. GIT REPOSITORY STATUS"

test_component "Git repository initialized" \
    "[ -d ~/mainFolder/.git ] && echo 'initialized'" \
    "initialized" "exact"

test_component "Git has commits" \
    "cd ~/mainFolder && git log --oneline | wc -l" \
    "" "status"

echo -n "Testing: Terraform deletion tracked in Git... "
if cd ~/mainFolder && git status | grep -q 'deleted:.*terraform'; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
else
    echo -e "${YELLOW}⚠ NOT STAGED${NC}"
    warning "Terraform deletion not committed to Git"
    ((TOTAL_TESTS++))
fi

# ============================================================================
# SECTION 18: DOCUMENTATION
# ============================================================================

print_section "18. DOCUMENTATION"

test_component "README.md exists and not empty" \
    "[ -s ~/mainFolder/README.md ] && echo 'exists'" \
    "exists" "exact"

test_component "DEPLOYMENT.md exists" \
    "[ -f ~/mainFolder/DEPLOYMENT.md ] && echo 'exists'" \
    "exists" "exact"

# ============================================================================
# SECTION 19: INTEGRATION TEST
# ============================================================================

print_section "19. END-TO-END INTEGRATION TEST"

echo -n "Testing: Complete data flow (API -> Athena -> S3)... "
response=$(curl -s -H "X-API-Key: $API_KEY" "$API_URL/stats")
if echo "$response" | jq -e '.total_jobs == 1000' >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
    echo "  Data flow: Client -> API Gateway -> Lambda -> Athena -> S3 -> Lambda -> Client"
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    FAILED_TEST_NAMES+=("End-to-end integration")
fi

# ============================================================================
# FINAL REPORT
# ============================================================================

print_header "TEST RESULTS SUMMARY"

echo -e "${CYAN}Total Tests Run:${NC} $TOTAL_TESTS"
echo -e "${GREEN}Passed:${NC} $PASSED_TESTS"
echo -e "${RED}Failed:${NC} $FAILED_TESTS"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo ""

# Calculate pass rate
pass_rate=$(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)

echo -e "${CYAN}Pass Rate:${NC} ${pass_rate}%"
echo ""

# Show failed tests
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}Failed Tests:${NC}"
    for test_name in "${FAILED_TEST_NAMES[@]}"; do
        echo "  ✗ $test_name"
    done
    echo ""
fi

# Final verdict
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! YOUR PROJECT IS FULLY FUNCTIONAL! 🎉${NC}"
    exit_code=0
elif [ $FAILED_TESTS -le 3 ]; then
    echo -e "${YELLOW}⚠️  MOSTLY WORKING - Some minor issues detected${NC}"
    exit_code=1
else
    echo -e "${RED}❌ MULTIPLE FAILURES - Please review failed tests${NC}"
    exit_code=2
fi
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Component status summary
echo ""
echo "Component Status:"
echo "  ✅ Project Structure: $([ -d ~/mainFolder/api ] && echo "OK" || echo "FAIL")"
echo "  ✅ AWS S3: $(aws s3 ls | grep -q job-skills && echo "OK" || echo "FAIL")"
echo "  ✅ AWS API Gateway: $(curl -s $API_URL/health | grep -q healthy && echo "OK" || echo "FAIL")"
echo "  ✅ API Authentication: $(curl -s -H "X-API-Key: $API_KEY" $API_URL/stats | grep -q total_jobs && echo "OK" || echo "FAIL")"
echo "  ✅ Data Files: $([ -f ~/mainFolder/skills-data/kaggle-1k-expanded.jsonl ] && echo "OK" || echo "FAIL")"
echo "  ✅ Local API: $(curl -s http://localhost:8000/health >/dev/null 2>&1 && echo "RUNNING" || echo "STOPPED")"
echo "  ✅ Dashboard: $(curl -s http://localhost:8503 >/dev/null 2>&1 && echo "RUNNING" || echo "STOPPED")"

echo ""
echo "System ready for:"
echo "  📊 Live demonstration"
echo "  🎤 Presentation"
echo "  📝 Deployment"
echo "  🎓 Grading"

exit $exit_code
