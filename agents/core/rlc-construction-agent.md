# RLC Construction Agent

**Category**: Core | **Responder**
**Primary Role**: Infrastructure Setup | **Secondary**: Configuration Tuning

## Overview

The RLC Construction Agent transforms the wizard's prescriptions into actual infrastructure and configuration within your codebase. It acts as the "builder" that takes architectural recommendations and makes them concrete.

## Responsibilities

1. **Infrastructure Provisioning**
   - Set up event handling components (metrics, logs, traces, alerts)
   - Configure ingestion methods for the chosen stack
   - Set up alert destinations and routing

2. **Agent Team Configuration**
   - Configure RLC agents based on codebase characteristics
   - Tune agent parameters for the specific platform
   - Set up communication channels between agents

3. **Codebase Integration**
   - Add instrumentation to existing code
   - Create configuration files in the codebase
   - Set up CI/CD integration for observability

4. **Validation**
   - Verify setup completeness
   - Test event flow from ingestion to alerting
   - Validate agent communication

## Inputs

The Construction Agent consumes:

```yaml
# From wizard output
rlc-config.yaml          # RLC gates and agent team configuration
event-handling-setup.yaml # Event handling stack configuration
```

## Setup Process

### Phase 1: Analyze Prescriptions

```python
def analyze_prescriptions(setup_dir: str):
    """Read and validate wizard output"""
    config = load_yaml(f"{setup_dir}/rlc-config.yaml")
    event_setup = load_yaml(f"{setup_dir}/event-handling-setup.yaml")

    return {
        "platform": config["environment"]["compute_platform"],
        "provider": config["environment"]["cloud_provider"],
        "languages": config["environment"]["languages"],
        "frameworks": config["environment"]["frameworks"],
        "event_handling": event_setup["primary_option"],
        "agents": config["agent_team"]
    }
```

### Phase 2: Infrastructure Setup

#### 2.1 Metrics Setup

```python
def setup_metrics(prescription: dict, repo_root: str):
    """Configure metrics collection based on tier"""

    tier = prescription["tier"]

    if tier == "budget":
        # Self-hosted Prometheus
        create_file(repo_root, "observability/prometheus/config.yml", """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'your-app'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: /metrics
""")
        create_docker_compose_service("prometheus", PROMETHEUS_CONFIG)
        create_docker_compose_service("grafana", GRAFANA_CONFIG)

    elif tier == "balanced":
        # Grafana Cloud
        create_file(repo_root, ".env.grafana", """
GRAFANA_CLOUD_INSTANCE_ID=your-instance-id
GRAFANA_API_KEY=your-api-key
GRAFANA_CLOUD_PROM_URL=https://prometheus-{instance}.grafana.net
""")
        add_to_gitignore(repo_root, ".env.grafana")

    elif tier == "premium":
        # Datadog/New Relic
        if prescription["name"] == "Datadog":
            create_file(repo_root, "datadog.yaml", """
api_key: ${DD_API_KEY}
site: datadoghq.com
logs:
  enabled: true
metrics:
  enabled: true
""")
```

#### 2.2 Logging Setup

```python
def setup_logging(prescription: dict, repo_root: str, languages: list):
    """Configure logging based on stack"""

    if "python" in languages:
        create_file(repo_root, "observability/logging_config.py", """
import structlog
import logging

def configure_logging(service_name: str):
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging to emit JSON
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=[logging.StreamHandler()]
    )
""")

    if "rust" in languages:
        create_file(repo_root, "observability/Cargo.toml.snippet", """
[dependencies]
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["json", "env-filter"] }
tracing-opentelemetry = "0.22"
opentelemetry = "0.21"
opentelemetry-jaeger = "0.20"
""")
```

#### 2.3 Tracing Setup

```python
def setup_tracing(prescription: dict, repo_root: str, languages: list):
    """Configure distributed tracing"""

    if "python" in languages:
        create_file(repo_root, "observability/tracing.py", """
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def configure_tracing(service_name: str, otlp_endpoint: str):
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    return trace.get_tracer(__name__, "1.0.0")
""")

    if "rust" in languages:
        create_file(repo_root, "observability/src/tracing.rs", """
use opentelemetry::global;
use tracing_subscriber::{layer::SubscriberExt, EnvFilter};

pub fn init_tracing(service_name: &'static str) {
    let tracer = opentelemetry_jaeger::new_pipeline()
        .with_service_name(service_name)
        .install_simple()
        .expect("Failed to install tracer");

    tracing_subscriber::registry()
        .with(tracing_opentelemetry::layer().with_tracer(tracer))
        .with(EnvFilter::from_default_env())
        .with(tracing_subscriber::fmt::layer())
        .init();
}
""")
```

### Phase 3: Agent Configuration

```python
def configure_agents(prescription: dict, repo_root: str):
    """Configure RLC agent team"""

    # Create agent configuration directory
    agent_dir = Path(repo_root) / ".rlc" / "agents"
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Configure priority agents
    priority_agents = prescription.get("priority_agents", [])

    for agent_name in priority_agents:
        agent_config = generate_agent_config(agent_name, prescription)
        write_file(agent_dir / f"{agent_name}.yaml", agent_config)

    # Create agent communication config
    comm_config = generate_comm_config(prescription)
    write_file(agent_dir / "communication.yaml", comm_config)

    # Create gate configuration
    gate_config = generate_gate_config(prescription["gates"])
    write_file(Path(repo_root) / ".rlc" / "config" / "gates.yaml", gate_config)
```

### Phase 4: Codebase Integration

```python
def integrate_observability(repo_root: str, languages: list):
    """Add observability to existing code"""

    if "python" in languages:
        # Add middleware to FastAPI/Django
        if has_fastapi(repo_root):
            add_to_main_py("""
from app.rlc_observability import configure_metrics, configure_logging, configure_tracing

app = FastAPI()

# Initialize RLC observability
configure_metrics(app)
configure_logging("my-service")
configure_tracing("my-service", "http://otel-collector:4317")
""")

    if "rust" in languages:
        # Add to main.rs
        if has_main_rs(repo_root):
            add_to_main_rs("""
mod observability;

#[tokio::main]
async fn main() {
    observability::init_tracing("my-service");
    // Your app code here
}
""")
```

### Phase 5: CI/CD Integration

```python
def setup_ci_integration(repo_root: str, platform: str):
    """Add observability to CI/CD pipeline"""

    if has_github_actions(repo_root):
        create_workflow(repo_root, "rlc-observability.yml", """
name: RLC Observability Check

on:
  pull_request:
  push:
    branches: [main]

jobs:
  verify-observability:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Verify RLC Configuration
        run: |
          ./.rlc/scripts/verify-config.sh

      - name: Test Event Ingestion
        run: |
          ./.rlc/scripts/test-ingestion.sh
""")
```

## Agent-Specific Configurations

### Incident Commander

```yaml
# .rlc/agents/incident-commander.yaml
agent:
  name: incident-commander
  enabled: true

incident_severity_thresholds:
  auto_declare:
    - SEV0: system_outage
    - SEV1: data_loss
    - SEV2: service_degradation > 50%

escalation:
  oncall_hours: business_hours
  escalation_paths:
    SEV0: [oncall_engineer, tech_lead, engineering_manager]
    SEV1: [oncall_engineer, tech_lead]
```

### Metrics Collector

```yaml
# .rlc/agents/metrics-collector.yaml
agent:
  name: metrics-collector
  enabled: true

collection:
  interval: 15s
  sources:
    - type: prometheus
      endpoint: /metrics
    - type: otlp
      endpoint: :4317

red_method:
  enabled: true
  endpoints:
    - path: /api/*
      rate_threshold: 100
      error_threshold: 0.05
      duration_threshold: 500ms
```

### Auto-Remediator

```yaml
# .rlc/agents/auto-remediator.yaml
agent:
  name: auto-remediator
  enabled: true

actions:
  safe_actions:
    - restart_pod
    - clear_cache
    - scale_up

  approval_required:
    - rollback_deployment
    - modify_database
    - delete_resources

safety_checks:
  require_confirmation: true
  dry_run: false
  max_retries: 3
```

## Validation

```python
def validate_setup(repo_root: str) -> dict:
    """Verify the RLC setup is complete"""

    results = {
        "checks": [],
        "status": "pending"
    }

    # Check configuration files
    config_files = [
        ".rlc/config/gates.yaml",
        ".rlc/agents/communication.yaml",
        "observability/prometheus/config.yml"
    ]

    for file in config_files:
        exists = Path(repo_root / file).exists()
        results["checks"].append({
            "name": f"config_exists:{file}",
            "status": "pass" if exists else "fail"
        })

    # Check agent configs
    agent_dir = Path(repo_root) / ".rlc" / "agents"
    if agent_dir.exists():
        agent_configs = list(agent_dir.glob("*.yaml"))
        results["checks"].append({
            "name": "agent_configs_count",
            "status": "pass" if len(agent_configs) >= 3 else "fail",
            "value": len(agent_configs)
        })

    results["status"] = "pass" if all(c["status"] == "pass" for c in results["checks"]) else "fail"
    return results
```

## Usage

```bash
# After running the wizard
python tools/wizard/rlc-setup-wizard.py . --output ./rlc-setup

# Run the construction agent
python -m rlc.agents.construction build ./rlc-setup

# Or use the CLI
rlc-construction build --config ./rlc-setup

# Validate the setup
rlc-construction validate --repo-root .
```

## Output Structure

```
your-repo/
├── .rlc/
│   ├── config/
│   │   └── gates.yaml          # RLC gates configuration
│   ├── agents/
│   │   ├── incident-commander.yaml
│   │   ├── metrics-collector.yaml
│   │   ├── auto-remediator.yaml
│   │   └── communication.yaml
│   └── scripts/
│       ├── verify-config.sh
│       └── test-ingestion.sh
├── observability/
│   ├── prometheus/
│   │   └── config.yml
│   ├── loki/
│   │   └── config.yml
│   ├── logging.py              # Python logging setup
│   ├── tracing.py              # Python tracing setup
│   └── Cargo.toml.snippet      # Rust observability deps
├── docker-compose.yml          # (budget tier) Local observability stack
├── .env.grafana                # (balanced tier) Grafana Cloud credentials
└── .github/
    └── workflows/
        └── rlc-observability.yml
```

## Collaboration with Other Agents

1. **Incident Commander**: Receives infrastructure topology for incident response
2. **Metrics Collector**: Uses configured scraping endpoints
3. **Auto-Remediator**: Knows what infrastructure is safe to modify
4. **Post-Mortem Writer**: Has infrastructure context for incident documentation

## Failure Modes

| Scenario | Handling |
|----------|----------|
| Invalid wizard output | Fail with clear error message |
| Missing dependencies | Warn and provide installation commands |
| Platform mismatch | Detect and suggest corrections |
| Conflicting configs | Ask user for resolution |

## Success Criteria

- [ ] All configuration files created in correct locations
- [ ] Agent team configuration matches wizard prescription
- [ ] Observability libraries integrated into code
- [ ] CI/CD pipeline updated
- [ ] Validation checks pass
- [ ] Event flow test succeeds
