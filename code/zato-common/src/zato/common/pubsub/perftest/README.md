# Zato PubSub Performance Tests

K6 performance test scripts for Zato PubSub REST API.

## Prerequisites

- k6 installed
- Zato PubSub REST server running (default: http://localhost:44556)
- Environment variables set:
  - `Zato_Test_PubSub_OpenAPI_Username`
  - `Zato_Test_PubSub_OpenAPI_Password`

## Test Scripts

### Individual Operations

- `publish.js` - High-volume message publishing
- `subscribe.js` - Topic subscription performance
- `pull_messages.js` - Message retrieval performance
- `unsubscribe.js` - Unsubscription performance

### Complete Workflow

- `full_workflow.js` - End-to-end workflow testing (subscribe → publish → pull → unsubscribe)

## Running Tests

```bash
# Set credentials
export Zato_Test_PubSub_OpenAPI_Username="demo"
export Zato_Test_PubSub_OpenAPI_Password="demo"

# Optional: Set custom server URL
export Zato_Test_PubSub_OpenAPI_URL="http://localhost:44556"

# Set number of topics to cycle through
export Zato_Test_PubSub_OpenAPI_Max_Topics=3

# Set number of VUs and iterations per VU
export Zato_Test_PubSub_OpenAPI_VUs=10
export Zato_Test_PubSub_OpenAPI_Iterations_Per_VU=50

# Run individual tests
k6 run publish.js
k6 run subscribe.js
k6 run pull_messages.js
k6 run unsubscribe.js

# Run complete workflow
k6 run full_workflow.js

# Run with custom options
k6 run --vus 50 --duration 2m publish.js

# Save results
k6 run --out json=results.json full_workflow.js
```

## Test Stages

Each test uses staged load patterns:

- **Ramp-up**: Gradually increase load
- **Steady state**: Maintain peak load
- **Ramp-down**: Gradually decrease load

## Thresholds

Tests include performance thresholds:

- Response time: p95 < 500-1000ms
- Error rate: < 5-10%
- Operation success rates: > 90-95%

## Metrics

K6 tracks:

- HTTP request duration
- Request failure rate
- Custom checks per operation
- Throughput (requests/second)
