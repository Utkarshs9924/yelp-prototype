#!/bin/bash

# Run all JMeter tests at different concurrency levels
# Usage: ./run-all-tests.sh

JMETER_HOME=${JMETER_HOME:-"/usr/local/bin"}
TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="$TEST_DIR/results"

# Create results directory
mkdir -p "$RESULTS_DIR"

echo "🚀 Starting JMeter Performance Tests"
echo "======================================"

# Test configurations
TESTS=("login" "search" "review")
USERS=(100 200 300 400 500)

# Function to run a single test
run_test() {
    local test_name=$1
    local user_count=$2
    
    echo ""
    echo "📊 Running $test_name test with $user_count concurrent users..."
    
    jmeter -n \
        -t "$TEST_DIR/${test_name}.jmx" \
        -Jusers=$user_count \
        -l "$RESULTS_DIR/${test_name}-${user_count}.jtl" \
        -e -o "$RESULTS_DIR/${test_name}-${user_count}-report" \
        2>&1 | grep -E "summary|Err:"
    
    if [ $? -eq 0 ]; then
        echo "✅ $test_name test ($user_count users) completed"
    else
        echo "❌ $test_name test ($user_count users) failed"
    fi
}

# Run all tests
for test in "${TESTS[@]}"; do
    for users in "${USERS[@]}"; do
        run_test "$test" "$users"
        sleep 10  # Wait between tests
    done
done

echo ""
echo "======================================"
echo "✅ All tests completed!"
echo "📁 Results saved to: $RESULTS_DIR"
echo ""
echo "To view reports, open:"
for test in "${TESTS[@]}"; do
    for users in "${USERS[@]}"; do
        echo "  file://$RESULTS_DIR/${test}-${users}-report/index.html"
    done
done
