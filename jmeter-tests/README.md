# JMeter Performance Testing Guide

## Overview
This document outlines the performance testing strategy for the Yelp Prototype Lab 2 using Apache JMeter.

## Test Requirements

Test the following APIs at concurrency levels: **100, 200, 300, 400, and 500** concurrent users

### APIs to Test:
1. **User Authentication** - `POST /login`
2. **Restaurant Search** - `GET /restaurants/search`
3. **Review Submission** - `POST /reviews` (triggers Kafka flow)

## Installation

### macOS:
```bash
brew install jmeter
```

### Linux/Windows:
Download from: https://jmeter.apache.org/download_jmeter.cgi

## Test Plans

### 1. User Authentication Test (login.jmx)

**Endpoint**: `POST http://localhost:8001/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Configuration**:
- Thread Group: 100, 200, 300, 400, 500 threads
- Ramp-up Period: 30 seconds
- Loop Count: 1
- HTTP Header: `Content-Type: application/json`

### 2. Restaurant Search Test (search.jmx)

**Endpoint**: `GET http://localhost:8002/restaurants/search?q=pizza&city=San+Francisco`

**Configuration**:
- Thread Group: 100, 200, 300, 400, 500 threads
- Ramp-up Period: 30 seconds
- Loop Count: 5
- Random query parameters

### 3. Review Submission Test (review.jmx)

**Endpoint**: `POST http://localhost:8003/reviews`

**Request Body**:
```json
{
  "restaurant_id": "${restaurant_id}",
  "user_id": "${user_id}",
  "rating": ${__Random(1,5)},
  "comment": "Test review from JMeter"
}
```

**Configuration**:
- Thread Group: 100, 200, 300, 400, 500 threads
- Ramp-up Period: 30 seconds
- Loop Count: 1
- Includes Kafka message processing

## Running Tests

### Command Line (Recommended for Lab):
```bash
# Run test and save results
jmeter -n -t jmeter-tests/login.jmx -l jmeter-tests/results/login-100.jtl -e -o jmeter-tests/results/login-100-report

# For each concurrency level
for users in 100 200 300 400 500; do
  jmeter -n -t jmeter-tests/login.jmx \
    -Jusers=$users \
    -l jmeter-tests/results/login-${users}.jtl \
    -e -o jmeter-tests/results/login-${users}-report
done
```

### GUI Mode (For Test Development):
```bash
jmeter
# Open .jmx files from the GUI
```

## Metrics to Collect

For each test at each concurrency level, record:

1. **Average Response Time** (ms)
2. **Throughput** (requests/sec)
3. **Error Rate** (%)
4. **Min/Max Response Time** (ms)
5. **90th Percentile** (ms)
6. **95th Percentile** (ms)

## Expected Results Analysis

### Example Analysis Template:

| Concurrency | Avg Response Time (ms) | Throughput (req/s) | Error Rate (%) |
|-------------|------------------------|-------------------|----------------|
| 100         | 45                     | 180               | 0.0            |
| 200         | 92                     | 320               | 0.1            |
| 300         | 185                    | 410               | 0.5            |
| 400         | 380                    | 450               | 2.0            |
| 500         | 650                    | 480               | 5.2            |

### Analysis Points:
- **100 users**: System handles well, low latency
- **200 users**: Slight increase in response time, throughput scales linearly
- **300 users**: Response time doubles, system approaching capacity
- **400 users**: Significant degradation, errors begin to appear
- **500 users**: System overloaded, high error rate, maximum throughput reached

## Bottleneck Identification

Common bottlenecks to analyze:
1. **Kafka Message Processing**: Check consumer lag
2. **MongoDB Connection Pool**: Monitor connection usage
3. **CPU/Memory**: Check pod resource limits
4. **Network I/O**: Check inter-service communication

## Generating Graphs

JMeter automatically generates HTML reports with graphs when using `-e -o` flags.

Manual graph creation:
```python
# Create performance graph
import matplotlib.pyplot as plt

concurrency = [100, 200, 300, 400, 500]
avg_response_time = [45, 92, 185, 380, 650]

plt.figure(figsize=(10, 6))
plt.plot(concurrency, avg_response_time, marker='o', linewidth=2, markersize=8)
plt.xlabel('Concurrency Level (Users)')
plt.ylabel('Average Response Time (ms)')
plt.title('Performance Under Load - Average Response Time')
plt.grid(True, alpha=0.3)
plt.savefig('performance-graph.png', dpi=300, bbox_inches='tight')
```

## Pre-Test Checklist

Before running tests:
- [ ] All services are running (docker-compose up)
- [ ] Kafka is healthy and consumers are running
- [ ] MongoDB Atlas is accessible
- [ ] Test user accounts are created
- [ ] Sample restaurant data is loaded

## Post-Test Cleanup

After tests:
```bash
# Check Kafka consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --all-groups

# Check MongoDB performance
# Use MongoDB Atlas monitoring dashboard
```

## Screenshots Required for Lab Report

1. JMeter Summary Report for each API
2. Response Time Graph (100-500 users)
3. Throughput Graph
4. Kafka Consumer monitoring (showing message processing)
5. MongoDB Atlas metrics during test

## Files Included

- `login.jmx` - User authentication test plan
- `search.jmx` - Restaurant search test plan
- `review.jmx` - Review submission test plan (with Kafka)
- `test-data.csv` - Sample test data
- `run-all-tests.sh` - Script to run all tests at all concurrency levels
