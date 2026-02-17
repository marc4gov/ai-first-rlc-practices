# Event Handling Module

The Event Handling Module is the core of the RLC framework, processing events from detection through resolution.

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Sources    │────▶│  Ingestion  │────▶│   Router    │
│             │     │             │     │             │
│ • Webhooks  │     │ • Normalize │     │ • Route     │
│ • Queues    │     │ • Validate  │     │ • Filter    │
│ • Streams   │     │ • Enrich    │     │ • Transform │
└─────────────┘     └─────────────┘     └─────────────┘
                                                │
                                                ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Correlation│◀────│  State      │────▶│   Agents    │
│             │     │  Machine    │     │             │
│ • Group     │     │ • Incident  │     │ • Detect    │
│ • Aggregate │     │ • Status    │     │ • Respond   │
│ • Dedupe    │     │ • Lifecycle │     │ • Recover   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Components

### 1. Event Ingestion

**Location**: `events/ingestion/event-ingester.py`

Handles ingestion from multiple sources:
- **Webhooks**: HTTP POST endpoints for event submission
- **Prometheus**: Alert webhook integration
- **CloudWatch**: SNS notification handling
- **Manual**: CLI and API-based manual event creation

**Event Structure**:
```python
{
    "event_id": "EVT-20240115-abc123",
    "event_type": "metric.anomaly",
    "severity": "critical",
    "source": "prometheus",
    "timestamp": "2024-01-15T10:30:00Z",
    "title": "High error rate detected",
    "description": "Error rate exceeded 5% threshold",
    "metadata": {...}
}
```

### 2. Event Routing

**Location**: `events/routing/event-router.py`

Routes events to appropriate agents based on:
- Event type patterns
- Severity levels
- Service ownership
- Custom rules

**Default Routing**:
- Critical events → incident-commander
- Security events → security-monitor
- Anomalies → anomaly-detector
- Threshold breaches → threshold-evaluator

### 3. Event Correlation

**Location**: `events/correlation/`

Groups related events to reduce noise and identify patterns:
- Time-based correlation (events within time window)
- Service-based correlation (events from same service)
- Causal correlation (downstream effects)

**Correlation Rules**:
```yaml
correlation:
  time_window: "5m"
  grouping:
    - by: ["service", "region"]
    - min_events: 3
    - max_group_size: 10
```

### 4. State Machine

**Location**: `events/state_machine/incident-state-machine.py`

Manages incident lifecycle through states:
- **detecting** → Event detected, classification needed
- **triaging** → Assessing impact and response
- **responding** → Active response in progress
- **recovering** → Monitoring recovery
- **resolved** → Service restored
- **post_mortem** → Documentation in progress
- **closed** → Complete with documentation

## Usage

### Ingesting Events

```bash
# Manual event ingestion
python events/ingestion/event-ingester.py \
  --type metric.threshold \
  --severity high \
  --title "API latency spike" \
  --description "p99 latency exceeded 1s"
```

### Routing Events

```bash
# Test routing
python events/routing/event-router.py \
  --title "Database connection failed" \
  --type metric.anomaly \
  --severity critical

# List routing rules
python events/routing/event-router.py --list-rules
```

### Managing Incidents

```bash
# Create incident
python events/state_machine/incident-state-machine.py create \
  --id INC-20240115-001 \
  --title "Payment API down" \
  --severity SEV1 \
  --services payment-api

# Transition incident
python events/state_machine/incident-state-machine.py transition \
  --id INC-20240115-001 \
  --to triaging \
  --reason "Initial assessment complete" \
  --actor incident-commander

# Complete gate
python events/state_machine/incident-state-machine.py complete-gate \
  --id INC-20240115-001 \
  --gate detection

# Show incident
python events/state_machine/incident-state-machine.py show \
  --id INC-20240115-001

# List incidents
python events/state_machine/incident-state-machine.py list \
  --state responding
```

## Event Types

### Standard Event Types

| Type | Description | Typical Severity |
|------|-------------|------------------|
| `metric.anomaly` | Statistical deviation detected | medium |
| `metric.threshold` | Threshold breach | high/critical |
| `log.error` | Error log entry detected | medium |
| `log.anomaly` | Unusual log pattern | medium |
| `trace.error` | Distributed trace error | high |
| `health.failed` | Health check failure | high |
| `deployment.failed` | Deployment failure | critical |
| `security.event` | Security-related event | high/critical |
| `customer.report` | Customer-reported issue | high |
| `manual.report` | Manually reported event | varies |

## Extending the Event System

### Adding a New Event Source

1. Create ingestion method in `event-ingester.py`:
```python
async def ingest_custom_source(self, data: Dict[str, Any]) -> Event:
    # Convert custom format to standard Event
    return await self._process_event(event)
```

2. Add routing rule in `event-router.py`:
```python
RoutingRule(
    name="custom_source_rule",
    priority=50,
    pattern="custom\\.event",
    agent="custom-agent",
    strategy=RoutingStrategy.SINGLE,
    conditions={}
)
```

### Adding a New State

1. Add to `IncidentState` enum:
```python
class IncidentState(Enum):
    # ... existing states
    CUSTOM_STATE = "custom_state"
```

2. Add valid transitions:
```python
VALID_TRANSITIONS = {
    # ... existing transitions
    IncidentState.PREVIOUS: [IncidentState.CUSTOM_STATE],
    IncidentState.CUSTOM_STATE: [IncidentState.NEXT]
}
```

## Monitoring the Event System

### Key Metrics to Track

- **Event ingestion rate**: Events per second by source
- **Routing distribution**: Events per agent
- **Processing latency**: Time from ingestion to routing
- **State transition frequency**: How often incidents change state
- **Active incidents**: Current count by state and severity

### Dashboard Recommendations

Create dashboards showing:
1. Event volume over time (by type, severity)
2. Agent workload (events per agent)
3. Incident lifecycle (time in each state)
4. Routing effectiveness (events processed, errors)

## Troubleshooting

### Events Not Being Processed

1. Check ingestion logs: `grep "Event ingested" /var/log/rlc/ingestion.log`
2. Verify routing rules: `python events/routing/event-router.py --list-rules`
3. Test with known event: Use manual event ingestion

### Incidents Stuck in State

1. Check gate requirements: All gates must be complete before certain transitions
2. Verify permissions: Some transitions require specific actor roles
3. Review state machine logs: Check for transition errors

### High Event Volume

1. Enable sampling at ingestion source
2. Add filtering rules to drop low-value events
3. Implement aggregation for high-frequency events
4. Review retention policies

## Best Practices

1. **Always normalize events**: Convert all sources to standard Event format
2. **Correlate before alerting**: Group related events to reduce noise
3. **Use state machine consistently**: Don't skip states or bypass gates
4. **Monitor the event system**: The event system needs monitoring too
5. **Version your event schemas**: Breaking changes should be versioned
6. **Document custom event types**: Maintain a catalog of event types in use

---

For more information, see:
- [RLC Gates Configuration](../.rlc/config/rlc-gates.yaml)
- [Agent Communication Protocols](../agents/rlc-communication-protocols.yaml)
- [Incident State Machine](../events/state_machine/incident-state-machine.py)
