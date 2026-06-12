# PoC Plan: Hive (hive-agent-memory)

**Project**: [DJLougen/hive](https://github.com/DJLougen/hive)
**PoC Type**: llm-app (agent orchestration layer)
**Date**: 2026-06-12

## Objective

Deploy the Hive agent memory and context compression stack on OpenShift AI to validate that:

1. The FastAPI REST API server starts and serves all endpoints correctly in a containerized UBI environment
2. CPU-side routing, context compression, and causal memory tracking work end-to-end
3. The deployment is production-ready with health/readiness probes, security context, and resource limits

## Project Classification

| Attribute | Value |
|-----------|-------|
| Project type | llm-app |
| Deployment model | Deployment (long-running service) |
| Resource profile | small (256Mi-512Mi, 250m-500m CPU) |
| GPU required | No |
| PVC required | No |
| LLM API required | No |
| Sidecar containers | None |

## Components

| Component | Language | Entry Point | Port |
|-----------|----------|-------------|------|
| hive | Python 3.10+ | scripts/hive_api_server.py | 8080 |

## Infrastructure Requirements

- **Base image**: registry.access.redhat.com/ubi9/python-312
- **Container registry**: quay.io/aicatalyst/hive:latest
- **Namespace**: poc-hive
- **Build strategy**: OpenShift BuildConfig (binary build)
- **Build namespace**: autopoc-test-builds

## Test Scenarios

### Scenario 1: Health Check
- **Type**: HTTP
- **Endpoint**: GET /health
- **Expected**: HTTP 200 with `{"status": "alive"}`
- **Timeout**: 30s

### Scenario 2: Ready Check
- **Type**: HTTP
- **Endpoint**: GET /ready
- **Expected**: HTTP 200 with `{"status": "ready"}`
- **Timeout**: 30s

### Scenario 3: Route Request
- **Type**: HTTP
- **Endpoint**: POST /route
- **Input**: `{"goal": "What is the weather today?", "available_tools": ["search", "calculator"], "step": 0}`
- **Expected**: HTTP 200 with JSON containing `tool`, `args`, `confidence`, `escalated`, `source` fields
- **Timeout**: 30s

### Scenario 4: Compress Request
- **Type**: HTTP
- **Endpoint**: POST /compress
- **Input**: `{"role": "user", "content": "Hello world, this is a test message for compression"}`
- **Expected**: HTTP 200 with JSON containing `role`, `content`, `label` fields
- **Timeout**: 30s

### Scenario 5: Remember and Recall
- **Type**: HTTP
- **Endpoint**: POST /remember then GET /recall
- **Input**: Remember: `{"key": "test-endpoint", "value": "/v1/api", "trust": 1.0}`, Recall: `?key=test-endpoint`
- **Expected**: Remember returns `{"status": "ok"}`, Recall returns `{"key": "test-endpoint", "value": "/v1/api"}`
- **Timeout**: 30s

## Service URL

```
http://hive.poc-hive.svc.cluster.local:8080
```

## Success Criteria

- All 5 test scenarios pass
- Pod is Running with readiness probe passing
- No CrashLoopBackOff or ImagePullBackOff errors
- Response times under 5 seconds for all endpoints
