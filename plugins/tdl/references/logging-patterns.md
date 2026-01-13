# Structured Logging Patterns for Traceability

## Overview

Structured logging is essential for traceability because it:
- Enables fast searching and filtering
- Connects logs to requests, users, and requirements
- Supports distributed tracing
- Facilitates root cause analysis
- Enables automated alerting and analysis

## Core Principles

### 1. **Use Structured Format (JSON)**

❌ **String logging (hard to parse)**:
```python
logger.info(f"User {user_id} updated device {device_id} property {prop_name} to {value}")
```

✅ **Structured logging (easy to query)**:
```python
logger.info(
    "Device property updated",
    extra={
        "user_id": user_id,
        "device_id": device_id,
        "property_name": prop_name,
        "new_value": value,
        "action": "device.property.update"
    }
)
```

### 2. **Include Trace Context**

Every log entry should include identifiers for tracing:

```python
logger.info(
    "API request received",
    extra={
        "request_id": request_id,      # Unique per request
        "trace_id": trace_id,           # Distributed tracing
        "user_id": user_id,             # Who
        "session_id": session_id,       # Session context
        "correlation_id": correlation_id # Related requests
    }
)
```

### 3. **Use Consistent Field Names**

Establish naming conventions:

```python
STANDARD_FIELDS = {
    "timestamp": "ISO 8601 timestamp",
    "level": "DEBUG | INFO | WARNING | ERROR | CRITICAL",
    "message": "Human-readable message",
    "service": "Service name",
    "environment": "production | staging | development",
    "version": "Application version",

    # Request context
    "request_id": "Unique request identifier",
    "trace_id": "Distributed trace ID",
    "span_id": "Trace span ID",

    # User context
    "user_id": "User identifier",
    "session_id": "Session identifier",

    # Application context
    "action": "Action being performed (dot notation)",
    "resource_type": "Type of resource",
    "resource_id": "Resource identifier",

    # Error context
    "error_type": "Error class/type",
    "error_message": "Error message",
    "stack_trace": "Full stack trace",

    # Performance
    "duration_ms": "Operation duration in milliseconds",
    "status_code": "HTTP status code"
}
```

## Language-Specific Examples

### Python (with AWS Lambda Powertools)

```python
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths

logger = Logger(service="my-service")

@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST
)
def lambda_handler(event, context):
    # Automatic injection of request_id, trace_id, etc.

    user_id = event.get("requestContext", {}).get("authorizer", {}).get("userId")

    logger.info(
        "Processing device command",
        extra={
            "user_id": user_id,
            "device_id": event["pathParameters"]["device_id"],
            "command": event["body"]["command"],
            "action": "device.command.execute",
            "requirement": "REQ-003"  # Traceability!
        }
    )

    try:
        result = process_command(event)

        logger.info(
            "Command executed successfully",
            extra={
                "device_id": event["pathParameters"]["device_id"],
                "result": result,
                "duration_ms": 150,
                "action": "device.command.complete"
            }
        )

        return {"statusCode": 200, "body": result}

    except Exception as e:
        logger.exception(
            "Command execution failed",
            extra={
                "device_id": event["pathParameters"]["device_id"],
                "error_type": type(e).__name__,
                "action": "device.command.error",
                "requirement": "REQ-003"
            }
        )
        raise
```

### JavaScript/TypeScript (with Pino)

```typescript
import pino from 'pino';

const logger = pino({
  base: {
    service: 'my-service',
    environment: process.env.NODE_ENV,
    version: process.env.APP_VERSION
  }
});

// Add trace context middleware
app.use((req, res, next) => {
  req.log = logger.child({
    request_id: req.id,
    trace_id: req.headers['x-amzn-trace-id'],
    user_id: req.user?.id
  });
  next();
});

// In handler
app.post('/devices/:deviceId/commands', async (req, res) => {
  req.log.info({
    action: 'device.command.received',
    device_id: req.params.deviceId,
    command: req.body.command,
    requirement: 'REQ-003'
  }, 'Device command received');

  const startTime = Date.now();

  try {
    const result = await executeCommand(req.params.deviceId, req.body.command);

    req.log.info({
      action: 'device.command.complete',
      device_id: req.params.deviceId,
      duration_ms: Date.now() - startTime,
      status: 'success'
    }, 'Command executed successfully');

    res.json(result);
  } catch (error) {
    req.log.error({
      action: 'device.command.error',
      device_id: req.params.deviceId,
      error_type: error.name,
      error_message: error.message,
      stack_trace: error.stack,
      duration_ms: Date.now() - startTime
    }, 'Command execution failed');

    throw error;
  }
});
```

### Go (with Zap)

```go
package main

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func main() {
    config := zap.NewProductionConfig()
    config.EncoderConfig.TimeKey = "timestamp"
    config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

    logger, _ := config.Build()
    defer logger.Sync()

    // Add base fields
    logger = logger.With(
        zap.String("service", "my-service"),
        zap.String("environment", os.Getenv("ENV")),
        zap.String("version", version),
    )
}

// In handler
func handleDeviceCommand(ctx context.Context, deviceID string, command Command) error {
    // Get trace context
    requestID := ctx.Value("request_id").(string)
    userID := ctx.Value("user_id").(string)

    logger.Info("Processing device command",
        zap.String("request_id", requestID),
        zap.String("user_id", userID),
        zap.String("device_id", deviceID),
        zap.String("command", command.Type),
        zap.String("action", "device.command.execute"),
        zap.String("requirement", "REQ-003"),
    )

    start := time.Now()

    result, err := executeCommand(deviceID, command)
    duration := time.Since(start)

    if err != nil {
        logger.Error("Command execution failed",
            zap.String("request_id", requestID),
            zap.String("device_id", deviceID),
            zap.Error(err),
            zap.String("error_type", fmt.Sprintf("%T", err)),
            zap.Duration("duration_ms", duration),
            zap.String("action", "device.command.error"),
        )
        return err
    }

    logger.Info("Command executed successfully",
        zap.String("request_id", requestID),
        zap.String("device_id", deviceID),
        zap.Duration("duration_ms", duration),
        zap.String("action", "device.command.complete"),
    )

    return nil
}
```

## Logging Levels

### Level Guidelines

| Level | When to Use | Examples |
|-------|-------------|----------|
| **DEBUG** | Detailed diagnostic info | Variable values, function entry/exit |
| **INFO** | Important business events | User actions, state changes, requests |
| **WARNING** | Unexpected but handled | Deprecated API usage, fallback to default |
| **ERROR** | Error but recoverable | Failed API call with retry, validation error |
| **CRITICAL** | System failure | Database unavailable, out of memory |

### Examples

```python
# DEBUG - Development/troubleshooting only
logger.debug(
    "Validating device property",
    extra={
        "device_id": device_id,
        "property": property_name,
        "value": value,
        "validation_rules": rules
    }
)

# INFO - Business events (most common)
logger.info(
    "User logged in",
    extra={
        "user_id": user_id,
        "login_method": "oauth",
        "action": "user.login"
    }
)

# WARNING - Something unexpected but handled
logger.warning(
    "Using cached data due to API timeout",
    extra={
        "api_endpoint": endpoint,
        "cache_age_seconds": 300,
        "action": "cache.fallback"
    }
)

# ERROR - Recoverable error
logger.error(
    "Failed to send notification",
    extra={
        "user_id": user_id,
        "notification_type": "email",
        "error_type": "SmtpError",
        "retry_count": 3,
        "action": "notification.error"
    }
)

# CRITICAL - System failure
logger.critical(
    "Database connection pool exhausted",
    extra={
        "pool_size": 10,
        "active_connections": 10,
        "waiting_requests": 50,
        "action": "system.critical"
    }
)
```

## Traceability Patterns

### 1. **Requirement Tracing**

Tag logs with requirement IDs:

```python
logger.info(
    "Device property validated",
    extra={
        "device_id": device_id,
        "property": property_name,
        "requirement": "REQ-005",  # Links to requirement
        "action": "device.property.validate"
    }
)
```

Query logs by requirement:

```bash
# CloudWatch Insights
fields @timestamp, message, device_id, property
| filter requirement = "REQ-005"
| sort @timestamp desc
```

### 2. **User Action Tracking**

Track complete user journeys:

```python
# Login
logger.info("User login", extra={
    "user_id": user_id,
    "action": "user.login",
    "correlation_id": correlation_id
})

# Action
logger.info("Device command", extra={
    "user_id": user_id,
    "action": "device.command.execute",
    "correlation_id": correlation_id  # Same correlation ID
})

# Logout
logger.info("User logout", extra={
    "user_id": user_id,
    "action": "user.logout",
    "correlation_id": correlation_id  # Same correlation ID
})
```

Query complete user session:

```bash
fields @timestamp, action, message
| filter correlation_id = "abc-123"
| sort @timestamp asc
```

### 3. **Error Correlation**

Link errors to production traces:

```python
try:
    result = external_api_call()
except Exception as e:
    logger.error(
        "External API call failed",
        extra={
            "api_endpoint": endpoint,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "trace_id": trace_id,  # AWS X-Ray trace
            "request_id": request_id,
            "requirement": "REQ-008",
            "stack_trace": traceback.format_exc()
        }
    )
```

### 4. **Performance Tracking**

Log operation durations for analysis:

```python
start_time = time.time()

# ... operation ...

duration_ms = (time.time() - start_time) * 1000

logger.info(
    "Database query completed",
    extra={
        "query_type": "get_device_properties",
        "device_id": device_id,
        "duration_ms": duration_ms,
        "result_count": len(results),
        "action": "db.query.complete"
    }
)
```

Query slow operations:

```bash
fields @timestamp, query_type, duration_ms
| filter action = "db.query.complete"
| filter duration_ms > 1000
| stats avg(duration_ms), max(duration_ms) by query_type
```

## Best Practices

### 1. **Sensitive Data Masking**

Never log sensitive information:

```python
from typing import Any

def mask_sensitive(data: dict[str, Any]) -> dict[str, Any]:
    """Mask sensitive fields in log data."""
    sensitive_fields = {"password", "token", "api_key", "secret"}

    masked = {}
    for key, value in data.items():
        if key.lower() in sensitive_fields:
            masked[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked[key] = mask_sensitive(value)
        else:
            masked[key] = value

    return masked

# Usage
logger.info(
    "API call made",
    extra=mask_sensitive({
        "endpoint": "/devices",
        "headers": {
            "Authorization": "Bearer secret-token",  # Will be masked
            "Content-Type": "application/json"
        }
    })
)
```

### 2. **Log Sampling**

For high-volume operations, use sampling:

```python
import random

# Log only 1% of successful requests
if random.random() < 0.01 or status_code >= 400:
    logger.info(
        "Request completed",
        extra={
            "status_code": status_code,
            "duration_ms": duration
        }
    )
```

### 3. **Log Retention Strategy**

Different retention for different log levels:

```
DEBUG: 1 day (development only)
INFO: 30 days
WARNING: 90 days
ERROR: 1 year
CRITICAL: 2 years
```

### 4. **Action Taxonomy**

Use consistent action naming:

```
Format: <resource>.<action>.<state>

Examples:
- user.login.success
- user.login.failure
- device.command.execute
- device.command.complete
- device.command.error
- api.request.received
- api.request.complete
- db.query.start
- db.query.complete
```

## Querying Logs

### CloudWatch Insights Examples

```bash
# Find all logs for a requirement
fields @timestamp, @message, action
| filter requirement = "REQ-003"
| sort @timestamp desc
| limit 100

# Trace a specific request
fields @timestamp, action, @message
| filter request_id = "abc-123"
| sort @timestamp asc

# Find errors by type
fields @timestamp, error_type, error_message
| filter level = "ERROR"
| stats count() by error_type
| sort count desc

# Performance analysis
fields @timestamp, action, duration_ms
| filter action like /device.command/
| stats avg(duration_ms), max(duration_ms), min(duration_ms) by action
```

### ELK Stack Examples

```json
// Find logs by requirement
GET /logs/_search
{
  "query": {
    "match": {
      "requirement": "REQ-003"
    }
  }
}

// Trace request across services
GET /logs/_search
{
  "query": {
    "match": {
      "trace_id": "1-68e3927d-3dd1ffab"
    }
  },
  "sort": [
    { "@timestamp": "asc" }
  ]
}

// Error aggregation
GET /logs/_search
{
  "size": 0,
  "query": {
    "match": {
      "level": "ERROR"
    }
  },
  "aggs": {
    "by_error_type": {
      "terms": {
        "field": "error_type.keyword",
        "size": 10
      }
    }
  }
}
```

## Integration with Monitoring

### Alerting Based on Logs

```yaml
# CloudWatch Alarm
MetricFilter:
  FilterPattern: '{ $.level = "ERROR" && $.requirement = "REQ-003" }'
  MetricTransformations:
    - MetricName: REQ003Errors
      MetricNamespace: Application
      MetricValue: 1

Alarm:
  MetricName: REQ003Errors
  Threshold: 10
  EvaluationPeriods: 1
  Period: 300
  AlarmActions:
    - !Ref SNSTopic
```

### Dashboards

Create dashboards showing:
- Error rate by requirement
- Performance metrics by action
- User activity by correlation ID
- Trace visualization by trace_id

## Summary Checklist

- [ ] Use structured (JSON) logging format
- [ ] Include trace context (request_id, trace_id, user_id)
- [ ] Use consistent field names across services
- [ ] Tag logs with requirement IDs for traceability
- [ ] Mask sensitive information
- [ ] Use appropriate log levels
- [ ] Include duration metrics for performance tracking
- [ ] Use correlation IDs for distributed tracing
- [ ] Implement log sampling for high-volume events
- [ ] Set up proper log retention policies
- [ ] Create alerts for critical errors
- [ ] Build dashboards for key metrics
- [ ] Document your action taxonomy
- [ ] Test log queries before production
