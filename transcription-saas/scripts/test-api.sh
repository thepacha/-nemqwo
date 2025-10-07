#!/bin/bash

# VoiceScript AI - API Testing Script
echo "🧪 Testing VoiceScript AI API..."

API_URL="http://localhost:8000"
TEST_EMAIL="test@example.com"
TEST_PASSWORD="testpassword123"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Test 1: Check if API is running
echo -e "${YELLOW}Testing API health...${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/")
print_result $([ "$response" = "200" ] && echo 0 || echo 1) "API Health Check"

# Test 2: Register a test user
echo -e "${YELLOW}Testing user registration...${NC}"
register_response=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"full_name\":\"Test User\"}")

if echo "$register_response" | grep -q "email"; then
    print_result 0 "User Registration"
else
    print_result 1 "User Registration"
fi

# Test 3: Login
echo -e "${YELLOW}Testing user login...${NC}"
login_response=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=$TEST_EMAIL&password=$TEST_PASSWORD")

if echo "$login_response" | grep -q "access_token"; then
    print_result 0 "User Login"
    # Extract token for further tests
    TOKEN=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
else
    print_result 1 "User Login"
    echo "Cannot proceed with authenticated tests without token"
    exit 1
fi

# Test 4: Get transcriptions (should be empty)
echo -e "${YELLOW}Testing transcriptions endpoint...${NC}"
transcriptions_response=$(curl -s -X GET "$API_URL/transcriptions" \
  -H "Authorization: Bearer $TOKEN")

if echo "$transcriptions_response" | grep -q "\[\]"; then
    print_result 0 "Get Transcriptions (Empty)"
else
    print_result 1 "Get Transcriptions"
fi

# Test 5: Create API key
echo -e "${YELLOW}Testing API key creation...${NC}"
apikey_response=$(curl -s -X POST "$API_URL/api-keys" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test API Key\"}")

if echo "$apikey_response" | grep -q "tsk_"; then
    print_result 0 "API Key Creation"
else
    print_result 1 "API Key Creation"
fi

# Test 6: Get current subscription
echo -e "${YELLOW}Testing subscription endpoint...${NC}"
subscription_response=$(curl -s -X GET "$API_URL/subscriptions/current" \
  -H "Authorization: Bearer $TOKEN")

if echo "$subscription_response" | grep -q "plan_name"; then
    print_result 0 "Get Current Subscription"
else
    print_result 1 "Get Current Subscription"
fi

echo ""
echo -e "${GREEN}🎉 API testing completed!${NC}"
echo ""
echo "Test user created:"
echo "  Email: $TEST_EMAIL"
echo "  Password: $TEST_PASSWORD"
echo ""
echo "You can now test the frontend at http://localhost:3000"