#!/usr/bin/env python3
"""
RLC Construction Agent - Builds event handling infrastructure

This agent takes the wizard's prescription and constructs:
1. Event handling infrastructure (metrics, logs, traces, alerts)
2. RLC agent team configuration
3. Codebase instrumentation
4. CI/CD integration
"""

import os
import re
import shutil
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ConstructionConfig:
    """Configuration for the construction process"""
    repo_root: str
    setup_dir: str
    dry_run: bool = False
    skip_code_instrumentation: bool = False
    skip_ci_integration: bool = False


class RLCConstructionAgent:
    """Builds RLC infrastructure based on wizard prescriptions"""

    def __init__(self, config: ConstructionConfig):
        self.config = config
        self.repo_root = Path(config.repo_root).resolve()
        self.setup_dir = Path(config.setup_dir).resolve()

        # Load prescriptions
        self.rlc_config = self._load_yaml(self.setup_dir / "rlc-config.yaml")
        self.event_setup = self._load_yaml(self.setup_dir / "event-handling-setup.yaml")

        self.environment = self.rlc_config.get("environment", {})
        self.agents = self.rlc_config.get("agent_team", {})
        self.event_handling = self.event_setup.get("primary_option", {})
        self.selected_tier = self.event_setup.get("selected_tier", "balanced")

    def _load_yaml(self, path: Path) -> Dict:
        """Load YAML file safely"""
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def build(self) -> Dict[str, Any]:
        """Execute the full construction process"""

        results = {
            "steps": [],
            "artifacts": [],
            "status": "pending"
        }

        try:
            # Phase 1: Create RLC directory structure
            self._create_rlc_structure(results)

            # Phase 2: Setup event handling infrastructure
            self._setup_event_handling(results)

            # Phase 3: Configure agents
            self._configure_agents(results)

            # Phase 4: Codebase integration (optional)
            if not self.config.skip_code_instrumentation:
                self._integrate_codebase(results)

            # Phase 5: CI/CD integration (optional)
            if not self.config.skip_ci_integration:
                self._integrate_ci_cd(results)

            # Phase 6: Create utility scripts
            self._create_scripts(results)

            # Phase 7: Validate setup
            validation = self._validate_setup()
            results["validation"] = validation

            if validation["status"] == "pass":
                results["status"] = "success"
            else:
                results["status"] = "incomplete"

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)

        return results

    def _create_rlc_structure(self, results: Dict):
        """Create RLC directory structure"""
        step = "create_rlc_structure"

        directories = [
            self.repo_root / ".rlc" / "config",
            self.repo_root / ".rlc" / "agents",
            self.repo_root / ".rlc" / "scripts",
            self.repo_root / "observability" / "prometheus",
            self.repo_root / "observability" / "loki",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            results["artifacts"].append(f"dir:{directory.relative_to(self.repo_root)}")

        self._log_step(step, "Created RLC directory structure", results)

    def _setup_event_handling(self, results: Dict):
        """Setup event handling based on tier"""
        step = "setup_event_handling"
        tier = self.selected_tier

        if tier == "budget":
            self._setup_budget_tier(results)
        elif tier == "balanced":
            self._setup_balanced_tier(results)
        elif tier == "premium":
            self._setup_premium_tier(results)

        self._log_step(step, f"Setup {tier} tier event handling", results)

    def _setup_budget_tier(self, results: Dict):
        """Setup self-hosted LGTM stack"""
        languages = self.environment.get("languages", [])

        # Prometheus configuration
        prometheus_config = {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
            },
            "scrape_configs": [
                {
                    "job_name": "your-app",
                    "static_configs": [{"targets": ["localhost:8080"]}],
                    "metrics_path": "/metrics"
                },
                {
                    "job_name": "prometheus",
                    "static_configs": [{"targets": ["localhost:9090"]}]
                }
            ],
            "rule_files": ["/etc/prometheus/rules/*.yml"]
        }

        prometheus_file = self.repo_root / "observability" / "prometheus" / "config.yml"
        self._write_yaml(prometheus_file, prometheus_config)
        results["artifacts"].append(f"file:{prometheus_file.relative_to(self.repo_root)}")

        # Loki configuration
        loki_config = {
            "server": {
                "http_listen_port": 3100
            },
            "positions": {
                "filename": "/tmp/loki/positions.yaml"
            },
            "clients": [{
                "url": "http://localhost:3100/loki/api/v1/push"
            }],
            "scrape_configs": [{
                "job_name": "your-app",
                "static_configs": [{
                    "targets": ["localhost"],
                    "labels": {"job": "your-app", "env": "dev"}
                }]
            }]
        }

        loki_file = self.repo_root / "observability" / "loki" / "config.yml"
        self._write_yaml(loki_file, loki_config)
        results["artifacts"].append(f"file:{loki_file.relative_to(self.repo_root)}")

        # Docker Compose for local observability
        docker_compose = {
            "version": "3.8",
            "services": {
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "ports": ["9090:9090"],
                    "volumes": ["./observability/prometheus/config.yml:/etc/prometheus/prometheus.yml"],
                    "command": "--config.file=/etc/prometheus/prometheus.yml --enable-feature=exemplar-storage"
                },
                "grafana": {
                    "image": "grafana/grafana:latest",
                    "ports": ["3000:3000"],
                    "environment": {
                        "GF_SECURITY_ADMIN_PASSWORD": "admin",
                        "GF_USERS_ALLOW_SIGN_UP": "false"
                    },
                    "volumes": ["grafana-storage:/var/lib/grafana"]
                },
                "loki": {
                    "image": "grafana/loki:latest",
                    "ports": ["3100:3100"],
                    "volumes": ["./observability/loki/config.yml:/etc/loki/local-config.yaml"]
                },
                "tempo": {
                    "image": "grafana/tempo:latest",
                    "ports": ["3200:3200", "4317:4317"],
                    "command": "--config.file=/etc/tempo/config.yaml"
                }
            },
            "volumes": {
                "grafana-storage": {}
            }
        }

        compose_file = self.repo_root / "docker-compose.obs.yml"
        self._write_yaml(compose_file, docker_compose)
        results["artifacts"].append(f"file:{compose_file.relative_to(self.repo_root)}")

        # Add observability dependency based on language
        if "python" in languages:
            self._add_python_observability_deps(results)
        elif "rust" in languages:
            self._add_rust_observability_deps(results)
        elif "javascript" in languages or "typescript" in languages:
            self._add_js_observability_deps(results)

    def _setup_balanced_tier(self, results: Dict):
        """Setup Grafana Cloud (or similar managed service)"""
        languages = self.environment.get("languages", [])

        # Grafana Cloud environment template
        grafana_env = """# Grafana Cloud Configuration
# Get these values from: https://grafana.com/docs/grafana-cloud/quickstart/docker-linux/
GRAFANA_CLOUD_INSTANCE_ID=your-instance-id
GRAFANA_API_KEY=your-api-key
GRAFANA_CLOUD_PROM_URL=https://prometheus-{instance}.grafana.net
GRAFANA_CLOUD_LOKI_URL=https://logs-{instance}.grafana.net
GRAFANA_CLOUD_TEMPO_URL=https://tempo-{instance}.grafana.net
"""

        env_file = self.repo_root / ".env.grafana"
        if not self.config.dry_run:
            with open(env_file, 'w') as f:
                f.write(grafana_env)
        results["artifacts"].append(f"file:{env_file.relative_to(self.repo_root)}")

        # Grafana Agent configuration
        grafana_agent_config = {
            "server": {"http_listen_port": 12345},
            "metrics": {
                "global": {"scrape_interval": "60s"},
                "configs": [{
                    "name": "default",
                    "scrape_configs": [{
                        "job_name": "your-app",
                        "static_configs": [{"targets": ["localhost:8080"]}]
                    }],
                    "remote_write": [{
                        "url": "${GRAFANA_CLOUD_PROM_URL}/api/prom/push",
                        "headers": {"Authorization": "Bearer ${GRAFANA_API_KEY}"}
                    }]
                }]
            },
            "logs": {
                "configs": [{
                    "name": "default",
                    "clients": [{
                        "url": "${GRAFANA_CLOUD_LOKI_URL}/loki/api/v1/push",
                        "headers": {"Authorization": "Bearer ${GRAFANA_API_KEY}"}
                    }],
                    "scrape_configs": [{
                        "job_name": "your-app",
                        "static_configs": [{
                            "targets": ["localhost"],
                            "labels": {"job": "your-app", "env": os.environ.get("ENV", "dev")}
                        }]
                    }]
                }]
            },
            "traces": {
                "configs": [{
                    "name": "default",
                    "remote_write": [{
                        "endpoint": "${GRAFANA_CLOUD_TEMPO_URL}",
                        "headers": {"Authorization": "Bearer ${GRAFANA_API_KEY}"}
                    }]
                }]
            }
        }

        agent_file = self.repo_root / "observability" / "grafana-agent.yml"
        self._write_yaml(agent_file, grafana_agent_config)
        results["artifacts"].append(f"file:{agent_file.relative_to(self.repo_root)}")

        # Language-specific instrumentation
        if "python" in languages:
            self._add_python_observability_deps(results, managed=True)
        elif "rust" in languages:
            self._add_rust_observability_deps(results, managed=True)
        elif "javascript" in languages or "typescript" in languages:
            self._add_js_observability_deps(results, managed=True)

    def _setup_premium_tier(self, results: Dict):
        """Setup premium observability (Datadog, New Relic, etc.)"""
        provider_name = self.event_handling.get("name", "").lower()

        if "datadog" in provider_name:
            self._setup_datadog(results)
        elif "new relic" in provider_name:
            self._setup_new_relic(results)
        else:
            # Fallback to balanced
            self._setup_balanced_tier(results)

    def _setup_datadog(self, results: Dict):
        """Setup Datadog integration"""
        languages = self.environment.get("languages", [])

        datadog_config = {
            "api_key": "${DD_API_KEY}",
            "site": "datadoghq.com",
            "logs": {"enabled": True},
            "metrics": {"enabled": True},
            "traces": {"enabled": True}
        }

        datadog_file = self.repo_root / "observability" / "datadog.yaml"
        self._write_yaml(datadog_file, datadog_config)
        results["artifacts"].append(f"file:{datadog_file.relative_to(self.repo_root)}")

        # Add Datadog dependencies
        if "python" in languages:
            self._add_file_content(
                self.repo_root / "observability" / "requirements-datadog.txt",
                "datadog-lambda==4.76.0\ndatadog==0.44.0\n"
            )
            results["artifacts"].append("file:observability/requirements-datadog.txt")

    def _setup_new_relic(self, results: Dict):
        """Setup New Relic integration"""
        languages = self.environment.get("languages", [])

        newrelic_config = {
            "license_key": "${NEW_RELIC_LICENSE_KEY}",
            "app_name": "${NEW_RELIC_APP_NAME}",
            "logs": {"enabled": True}
        }

        newrelic_file = self.repo_root / "observability" / "newrelic.yaml"
        self._write_yaml(newrelic_file, newrelic_config)
        results["artifacts"].append(f"file:{newrelic_file.relative_to(self.repo_root)}")

    def _add_python_observability_deps(self, results: Dict, managed: bool = False):
        """Add Python observability dependencies"""
        requirements = """# Observability
structlog==23.1.0
opentelemetry-api==1.20.0
opentelemetry-sdk==1.20.0
opentelemetry-instrumentation-flask==0.41b0
opentelemetry-instrumentation-fastapi==0.41b0
opentelemetry-exporter-otlp==1.20.0
prometheus-client==0.19.0
"""

        if managed:
            requirements += "grafana-otlp==1.0.0\n"

        req_file = self.repo_root / "observability" / "requirements.txt"
        self._add_file_content(req_file, requirements)
        results["artifacts"].append(f"file:{req_file.relative_to(self.repo_root)}")

    def _add_rust_observability_deps(self, results: Dict, managed: bool = False):
        """Add Rust observability dependencies"""
        cargo_snippet = """# Observability dependencies
[dependencies]
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["json", "env-filter"] }
tracing-opentelemetry = "0.22"
opentelemetry = "0.21"
opentelemetry-jaeger = "0.20"
opentelemetry-prometheus = "0.14"
metrics = "0.21"
"""

        cargo_file = self.repo_root / "observability" / "Cargo.toml.snippet"
        self._add_file_content(cargo_file, cargo_snippet)
        results["artifacts"].append(f"file:{cargo_file.relative_to(self.repo_root)}")

        # Rust instrumentation module
        rust_module = """use opentelemetry::global;
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

pub fn init_metrics() {
    use prometheus::{Counter, Histogram, IntCounter, IntHistogram};
    use lazy_static::lazy_static;

    lazy_static! {
        static ref REQUEST_COUNT: IntCounter =
            IntCounter::new("http_requests_total", "Total HTTP requests").unwrap();
        static ref REQUEST_DURATION: Histogram =
            Histogram::with_histogram(Histogram::new("http_request_duration_seconds").unwrap());
    }
}
"""
        tracing_file = self.repo_root / "observability" / "src" / "instrumentation.rs"
        tracing_file.parent.mkdir(parents=True, exist_ok=True)
        self._add_file_content(tracing_file, rust_module)
        results["artifacts"].append(f"file:{tracing_file.relative_to(self.repo_root)}")

    def _add_js_observability_deps(self, results: Dict, managed: bool = False):
        """Add JavaScript/TypeScript observability dependencies"""
        package_json = """{
  "dependencies": {
    "@opentelemetry/api": "^1.7.0",
    "@opentelemetry/sdk-node": "^0.45.0",
    "@opentelemetry/auto-instrumentations": "^0.40.0",
    "@opentelemetry/exporter-trace-otlp-grpc": "^0.45.0",
    "pino": "^8.16.0"
  }
}
"""
        package_file = self.repo_root / "observability" / "package.json"
        self._add_file_content(package_file, package_json)
        results["artifacts"].append(f"file:{package_file.relative_to(self.repo_root)}")

    def _configure_agents(self, results: Dict):
        """Configure RLC agents based on prescription"""
        step = "configure_agents"

        # Get priority agents
        priority_agents = self.event_setup.get("priority_agents", [])
        if not priority_agents:
            priority_agents = [
                "incident-commander",
                "metrics-collector",
                "health-checker",
                "alert-router",
                "auto-remediator"
            ]

        for agent_name in priority_agents:
            agent_config = self._generate_agent_config(agent_name)
            agent_file = self.repo_root / ".rlc" / "agents" / f"{agent_name}.yaml"
            self._write_yaml(agent_file, agent_config)
            results["artifacts"].append(f"file:.rlc/agents/{agent_name}.yaml")

        # Create communication config
        comm_config = self._generate_comm_config()
        comm_file = self.repo_root / ".rlc" / "agents" / "communication.yaml"
        self._write_yaml(comm_file, comm_config)
        results["artifacts"].append(f"file:.rlc/agents/communication.yaml")

        # Copy gates configuration
        gates_source = self.setup_dir / "rlc-config.yaml"
        gates_dest = self.repo_root / ".rlc" / "config" / "gates.yaml"
        if gates_source.exists():
            shutil.copy(gates_source, gates_dest)
            results["artifacts"].append("file:.rlc/config/gates.yaml")

        self._log_step(step, f"Configured {len(priority_agents)} agents", results)

    def _generate_agent_config(self, agent_name: str) -> Dict:
        """Generate configuration for a specific agent"""
        base_config = {
            "agent": {
                "name": agent_name,
                "enabled": True,
                "version": "1.0.0"
            },
            "environment": {
                "compute_platform": self.environment.get("compute_platform", "unknown"),
                "cloud_provider": self.environment.get("cloud_provider", "unknown"),
                "languages": self.environment.get("languages", [])
            }
        }

        # Agent-specific configurations
        if agent_name == "incident-commander":
            base_config.update({
                "incident_severity_thresholds": {
                    "auto_declare": {
                        "SEV0": ["system_outage", "data_loss"],
                        "SEV1": ["service_degradation_high", "authentication_failure"],
                        "SEV2": ["service_degradation", "elevated_error_rate"]
                    }
                },
                "escalation": {
                    "oncall_hours": "24x7",
                    "escalation_paths": {
                        "SEV0": ["oncall_engineer", "tech_lead", "engineering_manager"],
                        "SEV1": ["oncall_engineer", "tech_lead"],
                        "SEV2": ["oncall_engineer"]
                    }
                }
            })

        elif agent_name == "metrics-collector":
            base_config.update({
                "collection": {
                    "interval": "15s",
                    "sources": [
                        {"type": "prometheus", "endpoint": "/metrics"},
                        {"type": "otlp", "endpoint": ":4317"}
                    ]
                },
                "red_method": {
                    "enabled": True,
                    "endpoints": [
                        {
                            "path": "/api/*",
                            "rate_threshold": 100,
                            "error_threshold": 0.05,
                            "duration_threshold": "500ms"
                        }
                    ]
                }
            })

        elif agent_name == "auto-remediator":
            base_config.update({
                "actions": {
                    "safe_actions": [
                        "restart_pod",
                        "clear_cache",
                        "scale_up"
                    ],
                    "approval_required": [
                        "rollback_deployment",
                        "modify_database",
                        "delete_resources"
                    ]
                },
                "safety_checks": {
                    "require_confirmation": True,
                    "dry_run": False,
                    "max_retries": 3
                }
            })

        return base_config

    def _generate_comm_config(self) -> Dict:
        """Generate agent communication configuration"""
        return {
            "communication": {
                "channels": {
                    "incident_response": {
                        "type": "topic",
                        "protocol": "nats",
                        "address": "nats://localhost:4222"
                    },
                    "event_correlation": {
                        "type": "stream",
                        "protocol": "nats",
                        "address": "nats://localhost:4222"
                    },
                    "alert_routing": {
                        "type": "queue",
                        "protocol": "nats",
                        "address": "nats://localhost:4222"
                    }
                },
                "emergency_response": {
                    "formation": "3-2-3-2",
                    "timeout": "30s"
                }
            }
        }

    def _integrate_codebase(self, results: Dict):
        """Add observability instrumentation to existing code"""
        step = "integrate_codebase"
        languages = self.environment.get("languages", [])

        changes_made = []

        if "python" in languages:
            changes = self._integrate_python_codebase()
            changes_made.extend(changes)

        if "rust" in languages:
            changes = self._integrate_rust_codebase()
            changes_made.extend(changes)

        if "javascript" in languages or "typescript" in languages:
            changes = self._integrate_js_codebase()
            changes_made.extend(changes)

        for change in changes_made:
            results["artifacts"].append(f"instrumentation:{change}")

        self._log_step(step, f"Integrated observability into {len(changes_made)} files", results)

    def _integrate_python_codebase(self) -> List[str]:
        """Integrate observability into Python codebase"""
        changes = []

        # Look for main.py or app.py
        for main_file in ["main.py", "app.py", "wsgi.py", "asgi.py"]:
            if (self.repo_root / main_file).exists():
                # Add instrumentation import
                instrumentation_code = """

# RLC Observability
from observability.logging import configure_logging
from observability.tracing import configure_tracing

# Initialize observability
configure_logging("my-service")
configure_tracing("my-service", "http://otel-collector:4317")
"""
                self._append_to_file(self.repo_root / main_file, instrumentation_code)
                changes.append(main_file)

        # Check for common frameworks
        if self._has_dependency("fastapi"):
            self._add_fastapi_instrumentation()
            changes.append("fastapi_middleware")

        if self._has_dependency("django"):
            self._add_django_instrumentation()
            changes.append("django_middleware")

        return changes

    def _integrate_rust_codebase(self) -> List[str]:
        """Integrate observability into Rust codebase"""
        changes = []

        # Look for main.rs
        if (self.repo_root / "src" / "main.rs").exists():
            main_file = self.repo_root / "src" / "main.rs"
            instrumentation = """
mod observability;

fn main() {
    observability::init_tracing("my-service");
    // Your application code here
}
"""
            self._append_to_file(main_file, instrumentation)
            changes.append("src/main.rs")

        return changes

    def _integrate_js_codebase(self) -> List[str]:
        """Integrate observability into JavaScript/TypeScript codebase"""
        changes = []

        # Look for index files
        for index_file in ["index.js", "index.ts", "server.js", "server.ts"]:
            if (self.repo_root / index_file).exists():
                instrumentation = """

// RLC Observability
const { NodeTracerProvider } = require('@opentelemetry/sdk-node');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

const provider = new NodeTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'my-service',
  }),
});

provider.register();
"""
                self._append_to_file(self.repo_root / index_file, instrumentation)
                changes.append(index_file)

        return changes

    def _integrate_ci_cd(self, results: Dict):
        """Integrate RLC checks into CI/CD pipeline"""
        step = "integrate_ci_cd"

        # Check for GitHub Actions
        github_actions_dir = self.repo_root / ".github" / "workflows"
        if github_actions_dir.exists():
            workflow = {
                "name": "RLC Observability Check",
                "on": {
                    "pull_request": None,
                    "push": {"branches": ["main"]},
                },
                "jobs": {
                    "verify-observability": {
                        "runs-on": "ubuntu-latest",
                        "steps": [
                            {"uses": "actions/checkout@v4"},
                            {"name": "Verify RLC Configuration", "run": "./.rlc/scripts/verify-config.sh"},
                            {"name": "Test Event Ingestion", "run": "./.rlc/scripts/test-ingestion.sh"}
                        ]
                    }
                }
            }

            workflow_file = github_actions_dir / "rlc-observability.yml"
            self._write_yaml(workflow_file, workflow)
            results["artifacts"].append("file:.github/workflows/rlc-observability.yml")

        self._log_step(step, "Added CI/CD observability checks", results)

    def _create_scripts(self, results: Dict):
        """Create utility scripts"""
        step = "create_scripts"

        # Verification script
        verify_script = """#!/bin/bash
# Verify RLC configuration

echo "Verifying RLC configuration..."

# Check required files
required_files=(
    ".rlc/config/gates.yaml"
    ".rlc/agents/communication.yaml"
)

missing=0
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing: $file"
        missing=$((missing + 1))
    else
        echo "✅ Found: $file"
    fi
done

if [ $missing -gt 0 ]; then
    echo "❌ Configuration incomplete: $missing files missing"
    exit 1
fi

echo "✅ Configuration verified"
"""

        verify_file = self.repo_root / ".rlc" / "scripts" / "verify-config.sh"
        self._write_script(verify_file, verify_script)
        results["artifacts"].append("file:.rlc/scripts/verify-config.sh")

        # Test ingestion script
        test_ingestion_script = """#!/bin/bash
# Test event ingestion

echo "Testing event ingestion..."

# Check if observability stack is running
if docker ps | grep -q prometheus; then
    echo "✅ Prometheus is running"
else
    echo "⚠️  Prometheus not running (start with: docker-compose -f docker-compose.obs.yml up -d)"
fi

# Test metrics endpoint
if curl -s http://localhost:8080/metrics > /dev/null; then
    echo "✅ Metrics endpoint accessible"
else
    echo "⚠️  Metrics endpoint not accessible"
fi
"""

        test_file = self.repo_root / ".rlc" / "scripts" / "test-ingestion.sh"
        self._write_script(test_file, test_ingestion_script)
        results["artifacts"].append("file:.rlc/scripts/test-ingestion.sh")

        # README for the setup
        readme = f"""# RLC Setup

This directory contains your Runtime LifeCycle configuration.

## Quick Start

### Start Observability Stack (Budget Tier)

```bash
docker-compose -f docker-compose.obs.yml up -d
```

### Verify Configuration

```bash
./.rlc/scripts/verify-config.sh
```

### Test Event Ingestion

```bash
./.rlc/scripts/test-ingestion.sh
```

## Configuration

### Event Handling
- **Tier**: {self.selected_tier}
- **Metrics**: {self.event_handling.get('metrics_source', 'N/A')}
- **Logs**: {self.event_handling.get('log_source', 'N/A')}
- **Traces**: {self.event_handling.get('trace_source', 'N/A')}
- **Alerts**: {self.event_handling.get('alert_destination', 'N/A')}

### Environment
- **Platform**: {self.environment.get('compute_platform', 'unknown')}
- **Provider**: {self.environment.get('cloud_provider', 'unknown')}
- **Languages**: {', '.join(self.environment.get('languages', []))}

## Agents

The following RLC agents are configured:

"""
        for agent in self.agents.get("core", []):
            readme += f"- **{agent}**: Core agent\n"

        readme += """

## Next Steps

1. Configure your credentials in the appropriate `.env.*` files
2. Start the observability stack
3. Run the verification scripts
4. Deploy your application with instrumentation

## Documentation

See the main RLC documentation for more details on agent capabilities.
"""

        readme_file = self.repo_root / ".rlc" / "README.md"
        if not self.config.dry_run:
            with open(readme_file, 'w') as f:
                f.write(readme)
        results["artifacts"].append("file:.rlc/README.md")

        self._log_step(step, "Created utility scripts", results)

    def _validate_setup(self) -> Dict[str, Any]:
        """Validate the RLC setup"""
        checks = []

        # Check configuration files
        required_configs = [
            ".rlc/config/gates.yaml",
            ".rlc/agents/communication.yaml",
            ".rlc/README.md"
        ]

        for config in required_configs:
            exists = (self.repo_root / config).exists()
            checks.append({
                "name": f"config_exists:{config}",
                "status": "pass" if exists else "fail"
            })

        # Check agent configs
        agent_dir = self.repo_root / ".rlc" / "agents"
        if agent_dir.exists():
            agent_configs = list(agent_dir.glob("*.yaml"))
            checks.append({
                "name": "agent_configs_count",
                "status": "pass" if len(agent_configs) >= 3 else "warning",
                "value": len(agent_configs)
            })

        # Check observability setup
        observability_files = [
            "observability/prometheus/config.yml",
            "observability/loki/config.yml"
        ]

        for obs_file in observability_files:
            exists = (self.repo_root / obs_file).exists()
            checks.append({
                "name": f"observability_exists:{obs_file}",
                "status": "pass" if exists else "warning"
            })

        # Check scripts
        scripts = [
            ".rlc/scripts/verify-config.sh",
            ".rlc/scripts/test-ingestion.sh"
        ]

        for script in scripts:
            exists = (self.repo_root / script).exists()
            checks.append({
                "name": f"script_exists:{script}",
                "status": "pass" if exists else "warning"
            })

        overall_status = "pass"
        if any(c["status"] == "fail" for c in checks):
            overall_status = "fail"
        elif any(c["status"] == "warning" for c in checks):
            overall_status = "warning"

        return {
            "status": overall_status,
            "checks": checks,
            "summary": {
                "total": len(checks),
                "passed": sum(1 for c in checks if c["status"] == "pass"),
                "failed": sum(1 for c in checks if c["status"] == "fail"),
                "warnings": sum(1 for c in checks if c["status"] == "warning")
            }
        }

    # Helper methods

    def _write_yaml(self, path: Path, data: Dict):
        """Write YAML file"""
        if not self.config.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def _write_script(self, path: Path, content: str):
        """Write executable script"""
        if not self.config.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            os.chmod(path, 0o755)

    def _add_file_content(self, path: Path, content: str):
        """Add content to a file"""
        if not self.config.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)

    def _append_to_file(self, path: Path, content: str):
        """Append content to an existing file"""
        if not self.config.dry_run and path.exists():
            with open(path, 'a') as f:
                f.write(content)

    def _has_dependency(self, package: str) -> bool:
        """Check if a dependency exists in the codebase"""
        # Check requirements.txt
        req_file = self.repo_root / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text().lower()
            if package.lower() in content:
                return True

        # Check package.json
        pkg_file = self.repo_root / "package.json"
        if pkg_file.exists():
            content = pkg_file.read_text().lower()
            if package.lower() in content:
                return True

        return False

    def _log_step(self, step: str, message: str, results: Dict):
        """Log a construction step"""
        results["steps"].append({
            "step": step,
            "message": message
        })
        print(f"  ✓ {message}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="RLC Construction Agent - Build event handling infrastructure"
    )
    parser.add_argument("command", choices=["build", "validate"], help="Command to run")
    parser.add_argument("--repo-root", default=".", help="Path to repository root")
    parser.add_argument("--config", default="./rlc-setup", help="Path to wizard output")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--skip-code", action="store_true", help="Skip codebase instrumentation")
    parser.add_argument("--skip-ci", action="store_true", help="Skip CI/CD integration")

    args = parser.parse_args()

    config = ConstructionConfig(
        repo_root=args.repo_root,
        setup_dir=args.config,
        dry_run=args.dry_run,
        skip_code_instrumentation=args.skip_code,
        skip_ci_integration=args.skip_ci
    )

    agent = RLCConstructionAgent(config)

    if args.command == "build":
        print("🏗️  RLC Construction Agent")
        print(f"   Repository: {config.repo_root}")
        print(f"   Config: {config.setup_dir}")
        print()

        if args.dry_run:
            print("⚠️  DRY RUN MODE - No files will be modified")
            print()

        results = agent.build()

        print()
        print("=" * 60)
        if results["status"] == "success":
            print("✅ CONSTRUCTION COMPLETE")
        elif results["status"] == "incomplete":
            print("⚠️  CONSTRUCTION INCOMPLETE - Some warnings")
        else:
            print("❌ CONSTRUCTION FAILED")

        print(f"   Steps: {len(results['steps'])}")
        print(f"   Artifacts: {len(results['artifacts'])}")

        if "validation" in results:
            v = results["validation"]["summary"]
            print(f"   Validation: {v['passed']}/{v['total']} passed")
            if v['warnings'] > 0:
                print(f"   Warnings: {v['warnings']}")
            if v['failed'] > 0:
                print(f"   Failed: {v['failed']}")

    elif args.command == "validate":
        agent = RLCConstructionAgent(config)
        validation = agent._validate_setup()

        print("🔍 RLC Validation")
        print()

        for check in validation["checks"]:
            status_icon = "✅" if check["status"] == "pass" else "⚠️" if check["status"] == "warning" else "❌"
            print(f"{status_icon} {check['name']}")
            if "value" in check:
                print(f"   Value: {check['value']}")

        print()
        print(f"Status: {validation['status'].upper()}")
        print(f"Passed: {validation['summary']['passed']}/{validation['summary']['total']}")


if __name__ == "__main__":
    main()
