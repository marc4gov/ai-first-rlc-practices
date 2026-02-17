#!/usr/bin/env python3
"""
RLC Setup Wizard - Analyzes repositories and prescribes RLC configurations

This tool:
1. Analyzes a repository to detect languages, frameworks, and deployment
2. Asks questions about runtime environment
3. Prescribes event handling infrastructure
4. Generates customized RLC agent team configuration
5. Creates setup artifacts for the specific environment
"""

import os
import re
import json
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class CloudProvider(Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREM = "on_prem"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class ComputePlatform(Enum):
    KUBERNETES = "kubernetes"
    SERVERLESS = "serverless"
    VM = "vm"
    CONTAINER = "container"
    BARE_METAL = "bare_metal"
    UNKNOWN = "unknown"


class Language(Enum):
    PYTHON = "python"
    GO = "go"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    DOTNET = "dotnet"
    RUBY = "ruby"
    PHP = "php"
    RUST = "rust"
    UNKNOWN = "unknown"


@dataclass
class RepositoryAnalysis:
    """Results of repository analysis"""
    path: str
    languages: List[Language]
    frameworks: List[str]
    deployment_configs: List[str]
    observability_tools: List[str]
    cloud_provider: CloudProvider
    compute_platform: ComputePlatform
    has_docker: bool
    has_helm: bool
    has_terraform: bool


@dataclass
class EventHandlingPrescription:
    """Prescribed event handling setup"""
    metrics_source: str
    log_source: str
    trace_source: str
    alert_destination: str
    ingestion_methods: List[str]
    required_integrations: List[str]
    setup_commands: List[str]


@dataclass
class AgentTeamPrescription:
    """Prescribed agent team for the environment"""
    core_agents: List[str]
    observer_agents: List[str]
    monitor_agents: List[str]
    alerter_agents: List[str]
    controller_agents: List[str]
    responder_agents: List[str]
    optional_agents: List[str]
    custom_config: Dict[str, Any] = field(default_factory=dict)


class RepositoryAnalyzer:
    """Analyzes repository to detect characteristics"""

    LANGUAGE_INDICATORS = {
        Language.PYTHON: ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile", "*.py"],
        Language.GO: ["go.mod", "go.sum", "*.go"],
        Language.JAVASCRIPT: ["package.json", "*.js", "package-lock.json"],
        Language.TYPESCRIPT: ["tsconfig.json", "*.ts", "*.tsx"],
        Language.JAVA: ["pom.xml", "build.gradle", "*.java", "gradle.properties"],
        Language.DOTNET: ["*.csproj", "*.sln", "project.json"],
        Language.RUBY: ["Gemfile", "*.rb"],
        Language.PHP: ["composer.json", "*.php"],
        Language.RUST: ["Cargo.toml", "*.rs"],
    }

    FRAMEWORK_INDICATORS = {
        "django": ["django"],
        "flask": ["flask"],
        "fastapi": ["fastapi"],
        "express": ["express"],
        "spring": ["spring-boot", "springframework"],
        "rails": ["rails"],
        "react": ["react"],
        "vue": ["vue"],
        "angular": ["@angular"],
    }

    DEPLOYMENT_INDICATORS = {
        ("kubernetes", ComputePlatform.KUBERNETES): [
            "kubernetes/", "k8s/", "helm/", "Chart.yaml",
            "deployment.yaml", "deployment.yml", "*.yaml"
        ],
        ("docker", ComputePlatform.CONTAINER): [
            "Dockerfile", "docker-compose.yml", "docker-compose.yaml", ".dockerignore"
        ],
        ("terraform", ComputePlatform.KUBERNETES): [
            "*.tf", "terraform/", "main.tf"
        ],
        ("serverless", ComputePlatform.SERVERLESS): [
            "serverless.yml", "serverless.ts", "serverless.yaml",
            "template.yaml", "app.sam.yaml"
        ],
        ("cloudrun", ComputePlatform.SERVERLESS): [
            "app.yaml", "cloudbuild.yaml"
        ],
    }

    OBSERVABILITY_INDICATORS = {
        "prometheus": ["prometheus.yml", "prometheus/", "Prometheusfile"],
        "datadog": ["datadog/", "datadog.yaml", "dd-agent"],
        "cloudwatch": ["cloudwatch", "aws-embedded-metrics"],
        "grafana": ["grafana/", "dashboards/"],
        "loki": ["loki.yml", "loki-config.yaml"],
        "opentelemetry": ["opentelemetry.py", "otel_", "tracing/"],
    }

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

    def analyze(self) -> RepositoryAnalysis:
        """Perform comprehensive repository analysis"""
        all_files = self._get_all_files()

        return RepositoryAnalysis(
            path=str(self.repo_path),
            languages=self._detect_languages(all_files),
            frameworks=self._detect_frameworks(all_files),
            deployment_configs=self._detect_deployment(all_files),
            observability_tools=self._detect_observability(all_files),
            cloud_provider=self._detect_cloud_provider(all_files),
            compute_platform=self._detect_compute_platform(all_files),
            has_docker=self._has_file(all_files, "Dockerfile"),
            has_helm=self._has_file(all_files, "Chart.yaml"),
            has_terraform=self._has_any_extension(all_files, ".tf"),
        )

    def _get_all_files(self) -> List[str]:
        """Get all files in repository"""
        files = []
        try:
            for item in self.repo_path.rglob("*"):
                if item.is_file():
                    # Convert to relative path
                    rel_path = item.relative_to(self.repo_path)
                    files.append(str(rel_path))
        except PermissionError:
            pass
        return files

    def _detect_languages(self, files: List[str]) -> List[Language]:
        """Detect programming languages from files"""
        detected = set()

        for lang, indicators in self.LANGUAGE_INDICATORS.items():
            for indicator in indicators:
                if indicator.startswith("*"):
                    # Extension pattern
                    ext = indicator.replace("*", "")
                    if any(f.endswith(ext) for f in files):
                        detected.add(lang)
                        break
                else:
                    # Filename pattern
                    if any(indicator in f for f in files):
                        detected.add(lang)
                        break

        return list(detected) if detected else [Language.UNKNOWN]

    def _detect_frameworks(self, files: List[str]) -> List[str]:
        """Detect frameworks from dependency files"""
        detected = []

        for framework, indicators in self.FRAMEWORK_INDICATORS.items():
            for indicator in indicators:
                # Check in dependency files
                for file in files:
                    if file in ["requirements.txt", "package.json", "pom.xml", "Gemfile"]:
                        file_path = self.repo_path / file
                        if file_path.exists():
                            content = file_path.read_text().lower()
                            if indicator.lower() in content:
                                detected.append(framework)
                                break

        return list(set(detected))

    def _detect_deployment(self, files: List[str]) -> List[str]:
        """Detect deployment configurations"""
        detected = []

        for name, platform in self.DEPLOYMENT_INDICATORS.items():
            deployment_name, platform_type = name
            for indicator in platform:
                if indicator.startswith("*"):
                    ext = indicator.replace("*", "")
                    if any(f.endswith(ext) for f in files):
                        detected.append(deployment_name)
                        break
                elif any(indicator in f for f in files):
                    detected.append(deployment_name)
                    break

        return detected

    def _detect_observability(self, files: List[str]) -> List[str]:
        """Detect existing observability tools"""
        detected = []

        for tool, indicators in self.OBSERVABILITY_INDICATORS.items():
            for indicator in indicators:
                if any(indicator in f for f in files):
                    detected.append(tool)
                    break

        return detected

    def _detect_cloud_provider(self, files: List[str]) -> CloudProvider:
        """Detect cloud provider from configuration"""
        # Check for AWS indicators
        if any("terraform" in f and f.endswith(".tf") for f in files):
            tf_files = [f for f in files if f.endswith(".tf")]
            for tf_file in tf_files:
                content = (self.repo_path / tf_file).read_text().lower()
                if "aws_" in content or '"aws"' in content:
                    return CloudProvider.AWS

        # Check for GCP indicators
        if any("cloudbuild.yaml" in f or "app.yaml" in f for f in files):
            return CloudProvider.GCP

        # Check for Azure indicators
        if any("azure-pipelines" in f or "main.bicep" in f for f in files):
            return CloudProvider.AZURE

        # Default
        return CloudProvider.UNKNOWN

    def _detect_compute_platform(self, files: List[str]) -> ComputePlatform:
        """Detect compute platform"""
        for name, platform in self.DEPLOYMENT_INDICATORS.items():
            deployment_name, platform_type = name
            for indicator in platform:
                if any(indicator in f for f in files):
                    return platform_type

        return ComputePlatform.UNKNOWN

    def _has_file(self, files: List[str], filename: str) -> bool:
        """Check if a specific file exists"""
        return any(f == filename or f.endswith(f"/{filename}") for f in files)

    def _has_any_extension(self, files: List[str], ext: str) -> bool:
        """Check if any file has the given extension"""
        return any(f.endswith(ext) for f in files)


class EventHandlingPrescriber:
    """Prescribes event handling based on environment"""

    def __init__(self):
        self.prescriptions = {
            # Kubernetes prescriptions
            (CloudProvider.AWS, ComputePlatform.KUBERNETES): self._eks_prescription,
            (CloudProvider.GCP, ComputePlatform.KUBERNETES): self._gke_prescription,
            (CloudProvider.UNKNOWN, ComputePlatform.KUBERNETES): self._kubernetes_prescription,

            # Serverless prescriptions
            (CloudProvider.AWS, ComputePlatform.SERVERLESS): self._aws_lambda_prescription,
            (CloudProvider.GCP, ComputePlatform.SERVERLESS): self._cloud_run_prescription,

            # Default
            (CloudProvider.UNKNOWN, ComputePlatform.UNKNOWN): self._generic_prescription,
        }

    def prescribe(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Generate prescription based on analysis"""
        key = (analysis.cloud_provider, analysis.compute_platform)
        prescriber = self.prescriptions.get(key, self._generic_prescription)
        return prescriber(analysis)

    def _kubernetes_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Standard Kubernetes prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus",
            log_source="Loki",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "Prometheus scraping (/metrics endpoint)",
                "Fluent Bit DaemonSet for logs",
                "OpenTelemetry Collector for traces"
            ],
            required_integrations=[
                "kube-state-metrics",
                "cadvisor",
                "node-exporter"
            ],
            setup_commands=[
                "kubectl apply -f monitoring/prometheus/",
                "kubectl apply -f monitoring/loki/",
                "kubectl apply -f monitoring/tempo/",
                "kubectl apply -f monitoring/fluent-bit/"
            ]
        )

    def _eks_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """AWS EKS specific prescription"""
        base = self._kubernetes_prescription(analysis)
        base.ingestion_methods.extend([
            "AWS CloudWatch adapter for Prometheus",
            "AWS Distro for OpenTelemetry (ADOT)"
        ])
        return base

    def _gke_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Google GKE specific prescription"""
        return EventHandlingPrescription(
            metrics_source="Cloud Monitoring (Prometheus compatible)",
            log_source="Cloud Logging",
            trace_source="Cloud Trace",
            alert_destination="Cloud Alerting",
            ingestion_methods=[
                "OpenTelemetry Agent",
                "Cloud Monitoring sidecar"
            ],
            required_integrations=[
                "Google Cloud Operations agent"
            ],
            setup_commands=[
                "gcloud operations agent policies create --policy=otel-policy.yaml"
            ]
        )

    def _aws_lambda_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """AWS Lambda prescription"""
        return EventHandlingPrescription(
            metrics_source="CloudWatch Metrics",
            log_source="CloudWatch Logs",
            trace_source="X-Ray",
            alert_destination="CloudWatch Alarms → SNS → PagerDuty",
            ingestion_methods=[
                "CloudWatch Metrics automatic",
                "CloudWatch Logs automatic",
                "X-Ray tracing (enable in Lambda config)"
            ],
            required_integrations=[
                "CloudWatch Logs Insights",
                "X-Ray daemon"
            ],
            setup_commands=[
                "aws lambda update-function-configuration --function-name <name> --tracing-config Mode=Active"
            ]
        )

    def _cloud_run_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Google Cloud Run prescription"""
        return EventHandlingPrescription(
            metrics_source="Cloud Monitoring",
            log_source="Cloud Logging",
            trace_source="Cloud Trace",
            alert_destination="Cloud Alerting",
            ingestion_methods=[
                "Cloud Logging automatic",
                "Cloud Monitoring with log-based metrics"
            ],
            required_integrations=[
                "Cloud Operations (Stackdriver)"
            ],
            setup_commands=[
                "gcloud run services update <service> --enable-execution-snapshot"  # For debugging
            ]
        )

    def _generic_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Generic prescription when platform unknown"""
        return EventHandlingPrescription(
            metrics_source="Prometheus (recommended)",
            log_source="Loki (recommended)",
            trace_source="Tempo (recommended)",
            alert_destination="Alertmanager (recommended)",
            ingestion_methods=[
                "Application instrumented with /metrics endpoint",
                "Structured logs to stdout",
                "OpenTelemetry SDK for traces"
            ],
            required_integrations=[
                "Requires manual setup"
            ],
            setup_commands=[
                "Please specify hosting platform for detailed setup"
            ]
        )


class AgentTeamPrescriber:
    """Prescribes agent team based on environment"""

    CORE_AGENTS = [
        "incident-commander",
        "auto-remediator",
        "post-mortem-writer"
    ]

    def __init__(self):
        pass

    def prescribe(self, analysis: RepositoryAnalysis) -> AgentTeamPrescription:
        """Generate agent team prescription"""

        # Base team
        observers = ["metrics-collector", "health-checker"]
        monitors = ["threshold-evaluator"]
        alerters = ["alert-router"]
        controllers = ["auto-remediator"]
        responders = ["runbook-executor", "recovery-monitor"]
        optional = []

        # Add environment-specific agents
        if analysis.compute_platform == ComputePlatform.KUBERNETES:
            observers.extend(["log-aggregator", "pod-health-monitor"])
            monitors.extend(["anomaly-detector"])
            optional.extend(["kubernetes-specialist", "resource-quotas-tracker"])

        if analysis.compute_platform == ComputePlatform.SERVERLESS:
            observers.extend(["log-aggregator"])
            monitors.extend(["cold-start-monitor", "concurrency-analyzer"])
            optional.extend(["cost-analyzer"])

        if analysis.cloud_provider in [CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE]:
            optional.append("cost-analyzer")

        # Add framework-specific agents
        if "django" in analysis.frameworks or "flask" in analysis.frameworks:
            optional.append("python-performance-analyzer")

        if "express" in analysis.frameworks:
            optional.append("nodejs-memory-analyzer")

        return AgentTeamPrescription(
            core_agents=self.CORE_AGENTS,
            observer_agents=list(set(observers)),
            monitor_agents=list(set(monitors)),
            alerter_agents=list(set(alerters)),
            controller_agents=list(set(controllers)),
            responder_agents=list(set(responders)),
            optional_agents=list(set(optional)),
            custom_config={
                "compute_platform": analysis.compute_platform.value,
                "cloud_provider": analysis.cloud_provider.value,
                "languages": [l.value for l in analysis.languages],
                "frameworks": analysis.frameworks
            }
        )


class SetupArtifactGenerator:
    """Generates setup artifacts for the specific environment"""

    def generate(self, analysis: RepositoryAnalysis,
                 event_rx: EventHandlingPrescription,
                 team_rx: AgentTeamPrescription,
                 output_dir: str):
        """Generate all setup artifacts"""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        artifacts = {}

        # 1. Generate RLC configuration
        rlc_config = self._generate_rlc_config(analysis, team_rx)
        config_file = output_path / "rlc-config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(rlc_config, f, default_flow_style=False)
        artifacts["rlc_config"] = str(config_file)

        # 2. Generate event handling setup
        event_setup = self._generate_event_setup(analysis, event_rx)
        event_file = output_path / "event-handling-setup.yaml"
        with open(event_file, "w") as f:
            yaml.dump(event_setup, f, default_flow_style=False)
        artifacts["event_setup"] = str(event_file)

        # 3. Generate agent installation script
        install_script = self._generate_install_script(team_rx)
        script_file = output_path / "install-agents.sh"
        with open(script_file, "w") as f:
            f.write(install_script)
        os.chmod(script_file, 0o755)
        artifacts["install_script"] = str(script_file)

        # 4. Generate README
        readme = self._generate_readme(analysis, event_rx, team_rx)
        readme_file = output_path / "SETUP-README.md"
        with open(readme_file, "w") as f:
            f.write(readme)
        artifacts["readme"] = str(readme_file)

        # 5. Generate platform-specific manifests
        if analysis.compute_platform == ComputePlatform.KUBERNETES:
            k8s_manifests = self._generate_kubernetes_manifests(event_rx)
            k8s_dir = output_path / "kubernetes-manifests"
            k8s_dir.mkdir(exist_ok=True)
            for name, content in k8s_manifests.items():
                manifest_file = k8s_dir / name
                with open(manifest_file, "w") as f:
                    f.write(content)
            artifacts["kubernetes_manifests"] = str(k8s_dir)

        return artifacts

    def _generate_rlc_config(self, analysis: RepositoryAnalysis,
                            team_rx: AgentTeamPrescription) -> Dict:
        """Generate RLC gates configuration"""
        return {
            "gates": {
                "detection": {
                    "required_agents": ["event-classifier"],
                    "platform_specific": team_rx.custom_config
                },
                "triage": {
                    "required_agents": ["incident-commander", "triage-analyst"]
                },
                "response": {
                    "required_agents": team_rx.controller_agents + team_rx.responder_agents
                },
                "resolution": {
                    "required_agents": ["post-mortem-writer"]
                }
            },
            "agent_team": {
                "core": team_rx.core_agents,
                "observers": team_rx.observer_agents,
                "monitors": team_rx.monitor_agents,
                "alerters": team_rx.alerter_agents,
                "controllers": team_rx.controller_agents,
                "responders": team_rx.responder_agents,
                "optional": team_rx.optional_agents
            },
            "environment": {
                "compute_platform": analysis.compute_platform.value,
                "cloud_provider": analysis.cloud_provider.value,
                "languages": [l.value for l in analysis.languages],
                "frameworks": analysis.frameworks
            }
        }

    def _generate_event_setup(self, analysis: RepositoryAnalysis,
                             event_rx: EventHandlingPrescription) -> Dict:
        """Generate event handling setup"""
        return {
            "metrics": {
                "source": event_rx.metrics_source,
                "ingestion": event_rx.ingestion_methods[0] if event_rx.ingestion_methods else "manual"
            },
            "logs": {
                "source": event_rx.log_source,
                "ingestion": event_rx.ingestion_methods[1] if len(event_rx.ingestion_methods) > 1 else "manual"
            },
            "traces": {
                "source": event_rx.trace_source,
                "ingestion": event_rx.ingestion_methods[2] if len(event_rx.ingestion_methods) > 2 else "manual"
            },
            "alerts": {
                "destination": event_rx.alert_destination,
                "integrations": event_rx.required_integrations
            },
            "setup_commands": event_rx.setup_commands
        }

    def _generate_install_script(self, team_rx: AgentTeamPrescription) -> str:
        """Generate agent installation script"""
        agents = (team_rx.core_agents + team_rx.observer_agents +
                 team_rx.monitor_agents + team_rx.alerter_agents +
                 team_rx.controller_agents + team_rx.responder_agents)

        script = """#!/bin/bash
# RLC Agent Installation Script
# Generated by RLC Setup Wizard

set -e

echo "Installing RLC Agents..."

# Create agents directory
mkdir -p .claude/agents/rlc

# Copy agents
"""
        for agent in agents:
            script += f"cp agents/{agent}.md .claude/agents/rlc/\n"

        script += """
echo "✅ Agents installed"
echo ""
echo "Next steps:"
echo "  1. Review rlc-config.yaml"
echo "  2. Set up event handling per event-handling-setup.yaml"
echo "  3. Test with: python events/ingestion/event-ingester.py --help"
"""
        return script

    def _generate_readme(self, analysis: RepositoryAnalysis,
                        event_rx: EventHandlingPrescription,
                        team_rx: AgentTeamPrescription) -> str:
        """Generate setup README"""
        return f"""# RLC Setup for {analysis.cloud_provider.value.upper()} {analysis.compute_platform.value.upper()}

## Environment Analysis

- **Languages**: {', '.join([l.value for l in analysis.languages])}
- **Frameworks**: {', '.join(analysis.frameworks) if analysis.frameworks else 'None detected'}
- **Compute Platform**: {analysis.compute_platform.value}
- **Cloud Provider**: {analysis.cloud_provider.value}

## Event Handling Setup

### Metrics
- **Source**: {event_rx.metrics_source}
- **Ingestion**: {event_rx.ingestion_methods[0] if event_rx.ingestion_methods else 'TBD'}

### Logs
- **Source**: {event_rx.log_source}
- **Ingestion**: {event_rx.ingestion_methods[1] if len(event_rx.ingestion_methods) > 1 else 'TBD'}

### Alerts
- **Destination**: {event_rx.alert_destination}

## Agent Team Configuration

### Core Agents
{chr(10).join(f'- {a}' for a in team_rx.core_agents)}

### Observers
{chr(10).join(f'- {a}' for a in team_rx.observer_agents)}

### Monitors
{chr(10).join(f'- {a}' for a in team_rx.monitor_agents)}

### Alerters
{chr(10).join(f'- {a}' for a in team_rx.alerter_agents)}

### Controllers
{chr(10).join(f'- {a}' for a in team_rx.controller_agents)}

### Responders
{chr(10).join(f'- {a}' for a in team_rx.responder_agents)}

### Optional (Recommended)
{chr(10).join(f'- {a}' for a in team_rx.optional_agents)}

## Setup Steps

1. **Install agents**
   ```bash
   ./install-agents.sh
   ```

2. **Configure event sources**
   See `event-handling-setup.yaml` for specific commands.

3. **Test the setup**
   ```bash
   python events/ingestion/event-ingester.py --type test --severity low --title "Test event"
   ```

## Platform-Specific Notes

"""

    def _generate_kubernetes_manifests(self, event_rx: EventHandlingPrescription) -> Dict[str, str]:
        """Generate Kubernetes manifests"""
        manifests = {}

        # Fluent Bit DaemonSet
        manifests["fluent-bit-daemonset.yaml"] = """apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: fluent-bit
  template:
    metadata:
      labels:
        app: fluent-bit
    spec:
      containers:
      - name: fluent-bit
        image: fluent/fluent-bit:2.2
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
"""

        return manifests


# CLI Interface
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="RLC Setup Wizard - Configure RLC for your repository"
    )
    parser.add_argument("repo_path", help="Path to repository to analyze")
    parser.add_argument("--output", default="./rlc-setup", help="Output directory for setup artifacts")
    parser.add_argument("--cloud", help="Override cloud provider detection")
    parser.add_argument("--platform", help="Override compute platform detection")

    args = parser.parse_args()

    print(f"🧙 RLC Setup Wizard")
    print(f"Analyzing: {args.repo_path}")
    print()

    # Analyze repository
    analyzer = RepositoryAnalyzer(args.repo_path)
    analysis = analyzer.analyze()

    # Apply overrides if provided
    if args.cloud:
        try:
            analysis.cloud_provider = CloudProvider(args.cloud.lower())
        except ValueError:
            print(f"Invalid cloud provider: {args.cloud}")

    if args.platform:
        try:
            analysis.compute_platform = ComputePlatform(args.platform.lower())
        except ValueError:
            print(f"Invalid platform: {args.platform}")

    # Display analysis
    print("Repository Analysis:")
    print(f"  Languages: {', '.join([l.value for l in analysis.languages])}")
    print(f"  Frameworks: {', '.join(analysis.frameworks) if analysis.frameworks else 'None detected'}")
    print(f"  Deployment: {', '.join(analysis.deployment_configs) if analysis.deployment_configs else 'None detected'}")
    print(f"  Cloud Provider: {analysis.cloud_provider.value}")
    print(f"  Compute Platform: {analysis.compute_platform.value}")
    print()

    # Generate prescriptions
    event_prescriber = EventHandlingPrescriber()
    event_rx = event_prescriber.prescribe(analysis)

    team_prescriber = AgentTeamPrescriber()
    team_rx = team_prescriber.prescribe(analysis)

    # Generate artifacts
    generator = SetupArtifactGenerator()
    artifacts = generator.generate(analysis, event_rx, team_rx, args.output)

    print("Event Handling Prescription:")
    print(f"  Metrics: {event_rx.metrics_source}")
    print(f"  Logs: {event_rx.log_source}")
    print(f"  Alerts: {event_rx.alert_destination}")
    print()

    print("Agent Team Prescription:")
    print(f"  Core: {len(team_rx.core_agents)} agents")
    print(f"  Observers: {len(team_rx.observer_agents)} agents")
    print(f"  Monitors: {len(team_rx.monitor_agents)} agents")
    print(f"  Total: {len(team_rx.core_agents) + len(team_rx.observer_agents) + len(team_rx.monitor_agents)} agents")
    print()

    print(f"✅ Setup artifacts generated in: {args.output}")
    print()
    print("Generated files:")
    for name, path in artifacts.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()
