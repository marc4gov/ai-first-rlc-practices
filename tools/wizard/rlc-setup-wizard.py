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
    # Major Cloud Providers
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"

    # European Cloud Providers
    SCALEWAY = "scaleway"       # France
    OVHCLOUD = "ovhcloud"        # France
    EXOSCALE = "exoscale"        # France (Outscale)
    CLEVER_CLOUD = "clever_cloud" # France
    HETZNER = "hetzner"          # Germany
    IONOS = "ionos"              # Germany
    GCORE = "gcore"              # Luxembourg
    LINODE = "linode"            # Akamai (originally US, popular in EU)

    # PaaS / Container Platforms (Global with EU presence)
    HEROKU = "heroku"            # Salesforce
    VERCEL = "vercel"            # Edge network with EU regions
    NETLIFY = "netlify"           # Edge network with EU regions
    RAILWAY = "railway"           # US-based, popular in EU
    RENDER = "render"             # US-based
    FLY_IO = "fly_io"             # Edge regions worldwide

    # Cloud-adjacent platforms
    DIGITAL_OCEAN = "digital_ocean"  # US with EU datacenters
    VULTR = "vultr"                  # US with EU datacenters

    # Self-hosted options
    SELF_HOSTED = "self_hosted"
    ON_PREM = "on_prem"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class ComputePlatform(Enum):
    KUBERNETES = "kubernetes"
    KUBERNETES_EKS = "kubernetes_eks"
    KUBERNETES_GKE = "kubernetes_gke"
    KUBERNETES_AKS = "kubernetes_aks"
    KUBERNETES_SELF = "kubernetes_self"
    KUBERNETES_K3S = "kubernetes_k3s"
    SERVERLESS = "serverless"
    SERVERLESS_LAMBDA = "serverless_lambda"
    SERVERLESS_CLOUD_RUN = "serverless_cloud_run"
    SERVERLESS_CLOUD_FUNCTIONS = "serverless_cloud_functions"
    PAAS_HEROKU = "paas_heroku"
    PAAS_VERCEL = "paas_vercel"
    PAAS_NETLIFY = "paas_netlify"
    PAAS_RAILWAY = "paas_railway"
    PAAS_RENDER = "paas_render"
    PAAS_FLY_IO = "paas_fly_io"
    VM = "vm"
    CONTAINER = "container"
    DOCKER_COMPOSE = "docker_compose"
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
        # Kubernetes distributions
        ("kubernetes", ComputePlatform.KUBERNETES): [
            "kubernetes/", "k8s/", "helm/", "Chart.yaml",
            "deployment.yaml", "deployment.yml", "k8s/",
            "namespace.yaml", "configmap.yaml", "secret.yaml"
        ],
        ("kubernetes-eks", ComputePlatform.KUBERNETES_EKS): [
            "eks/", "aws-eks/", "*.eks.yaml",
            "aws-sdk/", "amazon-eks/"
        ],
        ("kubernetes-gke", ComputePlatform.KUBERNETES_GKE): [
            "gke/", "gke-config.yaml", "gcloud/",
            "google-gke/", "*.gke.yaml"
        ],
        ("kubernetes-aks", ComputePlatform.KUBERNETES_AKS): [
            "aks/", "azure-aks/", "*.aks.yaml",
            "azure-k8s/", "microsoft-aks/"
        ],
        ("kubernetes-k3s", ComputePlatform.KUBERNETES_K3S): [
            "k3s/", "k3s-config.yaml", "rancher/",
            "k3s-cluster/"
        ],
        ("kubernetes-self", ComputePlatform.KUBERNETES_SELF): [
            "kubeadm.yaml", "kubeadm-config.yaml",
            "self-hosted-k8s/"
        ],

        # Docker / Container
        ("docker", ComputePlatform.CONTAINER): [
            "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
            ".dockerignore", ".containerignore"
        ],
        ("docker-compose", ComputePlatform.DOCKER_COMPOSE): [
            "docker-compose.yml", "docker-compose.yaml",
            "compose.yml", "compose.yaml",
            "docker-compose.override.yml"
        ],

        # Serverless Frameworks
        ("serverless", ComputePlatform.SERVERLESS): [
            "serverless.yml", "serverless.ts", "serverless.yaml",
            "serverless/", "serverless-framework/"
        ],
        ("aws-lambda", ComputePlatform.SERVERLESS_LAMBDA): [
            "template.yaml", "app.sam.yaml", "sam.yaml",
            "aws-sam/", "lambda/", ".aws-sam/"
        ],
        ("cloud-run", ComputePlatform.SERVERLESS_CLOUD_RUN): [
            "app.yaml", "cloudbuild.yaml", "cloudrun/",
            "CloudRun/", "cloud-run/"
        ],
        ("cloud-functions", ComputePlatform.SERVERLESS_CLOUD_FUNCTIONS): [
            "main.py", "index.py", "gcf/",
            "cloudfunctions/", "google-cloud-functions/"
        ],

        # PaaS / Cloud Providers
        ("heroku", ComputePlatform.PAAS_HEROKU): [
            "Procfile", "heroku.yml", ".heroku/",
            "heroku/", "app.json"
        ],
        ("vercel", ComputePlatform.PAAS_VERCEL): [
            "vercel.json", ".vercel/", "vercel/",
            "now.json", ".now/"
        ],
        ("netlify", ComputePlatform.PAAS_NETLIFY): [
            "netlify.toml", ".netlify/", "netlify/",
            "_headers", "_redirects"
        ],
        ("railway", ComputePlatform.PAAS_RAILWAY): [
            "railway.json", "railway/", ".railway/",
            "railway.toml", "railway.app/"
        ],
        ("render", ComputePlatform.PAAS_RENDER): [
            "render.yaml", "render/", "render.yaml",
            ".render/", "render.com/"
        ],
        ("fly-io", ComputePlatform.PAAS_FLY_IO): [
            "fly.toml", ".fly/", "fly/",
            "fly.io/", "fly.app/"
        ],

        # European cloud providers
        ("scaleway", ComputePlatform.VM): [
            "scaleway.yml", "scaleway/", "scw/",
            "scaleway.com/"
        ],
        ("ovhcloud", ComputePlatform.VM): [
            "ovh.yml", "ovh/", "ovhcloud/",
            "ovh.conf"
        ],
        ("hetzner", ComputePlatform.VM): [
            "hetzner.yml", "hetzner/", "hcloud/",
            "hetzner.com/"
        ],
        ("exoscale", ComputePlatform.VM): [
            "exoscale.yml", "exoscale/", "exo/",
            "exoscale.com/"
        ],
        ("clever-cloud", ComputePlatform.PAAS_HEROKU): [
            "clever-cloud/", "clever.json",
            "clever-cloud.com/"
        ],

        # Infrastructure as Code
        ("terraform", ComputePlatform.KUBERNETES): [
            "*.tf", "terraform/", "main.tf", "variables.tf",
            "outputs.tf", "modules/"
        ],
        ("ansible", ComputePlatform.VM): [
            "playbook.yml", "ansible/", "ansible.cfg",
            "inventory/", "requirements.yml"
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
        """Detect cloud provider from configuration files and metadata"""

        # Check specific provider indicators
        provider_indicators = {
            # AWS
            CloudProvider.AWS: [
                ("terraform", lambda c: "aws_" in c or "hashicorp/aws" in c),
                ("serverless", lambda c: "aws:" in c or "aws-iam" in c),
                ("template.yaml", lambda c: "aws:aws:" in c or "AWS::" in c),
                ("Procfile", lambda c: False),  # Exclude from AWS check
            ],

            # GCP
            CloudProvider.GCP: [
                ("cloudbuild.yaml", lambda c: True),
                ("app.yaml", lambda c: "runtime:" in c),  # Cloud Run app.yaml
                ("main.py", lambda c: False),  # Exclude generic .py
                ("terraform", lambda c: "google" in c and "google_compute" in c),
            ],

            # Azure
            CloudProvider.AZURE: [
                ("azure-pipelines", lambda c: True),
                ("main.bicep", lambda c: True),
                ("terraform", lambda c: "azurerm" in c),
                ("template.yaml", lambda c: "azure:" in c),
            ],

            # European providers
            CloudProvider.SCALEWAY: [
                ("terraform", lambda c: "scaleway" in c or "scaleway" in c),
                ("scaleway.yml", lambda c: True),
                ("scw/", lambda c: True),
            ],

            CloudProvider.OVHCLOUD: [
                ("terraform", lambda c: "ovh" in c),
                ("ovh.yml", lambda c: True),
                ("ovh.conf", lambda c: True),
            ],

            CloudProvider.HETZNER: [
                ("terraform", lambda c: "hetzner" in c or "hcloud" in c),
                ("hetzner.yml", lambda c: True),
                ("hcloud/", lambda c: True),
            ],

            CloudProvider.EXOSCALE: [
                ("terraform", lambda c: "exoscale" in c),
                ("exoscale.yml", lambda c: True),
                ("exo/", lambda c: True),
            ],

            CloudProvider.IONOS: [
                ("terraform", lambda c: "ionos" in c),
                ("ionos.yml", lambda c: True),
            ],

            CloudProvider.GCORE: [
                ("terraform", lambda c: "gcore" in c),
                ("gcore.yml", lambda c: True),
            ],

            # PaaS providers
            CloudProvider.HEROKU: [
                ("Procfile", lambda c: True),
                ("heroku.yml", lambda c: True),
                ("app.json", lambda c: '"name"' in c and '"buildpacks"' in c),
            ],

            CloudProvider.VERCEL: [
                ("vercel.json", lambda c: True),
                ("now.json", lambda c: True),
                (".vercel/", lambda c: True),
            ],

            CloudProvider.NETLIFY: [
                ("netlify.toml", lambda c: True),
                ("_headers", lambda c: True),
                ("_redirects", lambda c: True),
            ],

            CloudProvider.RAILWAY: [
                ("railway.json", lambda c: True),
                ("railway.toml", lambda c: True),
                ("railway.app", lambda c: True),
            ],

            CloudProvider.RENDER: [
                ("render.yaml", lambda c: True),
                ("render.com/", lambda c: True),
            ],

            CloudProvider.FLY_IO: [
                ("fly.toml", lambda c: True),
                ("fly.io/", lambda c: True),
                (".fly/", lambda c: True),
            ],

            CloudProvider.DIGITAL_OCEAN: [
                ("terraform", lambda c: "digitalocean" in c),
                (".do/", lambda c: True),
                ("do.yml", lambda c: True),
            ],

            CloudProvider.VULTR: [
                ("terraform", lambda c: "vultr" in c),
                ("vultr.yml", lambda c: True),
            ],

            CloudProvider.LINODE: [
                ("terraform", lambda c: "linode" in c or "akamai" in c),
                ("linode.yml", lambda c: True),
            ],
        }

        # Check each provider's indicators
        for provider, indicators in provider_indicators.items():
            for file_pattern, content_check in indicators:
                # Check if file exists matching pattern
                matching_files = [f for f in files if file_pattern in f.lower()]

                for file in matching_files:
                    file_path = self.repo_path / file
                    if file_path.exists() and file_path.is_file():
                        try:
                            content = file_path.read_text().lower()
                            if content_check(content):
                                return provider
                        except Exception:
                            pass

        # Check content of dependency files for provider hints
        for dep_file in ["package.json", "requirements.txt", "pom.xml", "build.gradle"]:
            if dep_file in files:
                file_path = self.repo_path / dep_file
                if file_path.exists():
                    content = file_path.read_text().lower()

                    # Check for provider-specific packages
                    provider_packages = {
                        CloudProvider.AWS: ["aws-sdk", "@aws-sdk/", "boto3", "aws-cdk"],
                        CloudProvider.GCP: ["@google-cloud/", "google-cloud-", "gcloud"],
                        CloudProvider.AZURE: ["@azure/", "azure-"],
                        CloudProvider.HEROKU: ["heroku"],
                        CloudProvider.VERCEL: ["vercel", "@vercel/"],
                        CloudProvider.NETLIFY: ["netlify-cli", "netlify-"],
                        CloudProvider.SCALEWAY: ["scaleway"],
                        CloudProvider.HETZNER: ["hetzner", "hcloud"],
                    }

                    for provider, packages in provider_packages.items():
                        if any(pkg in content for pkg in packages):
                            return provider

        # Default to unknown
        return CloudProvider.UNKNOWN

    def _detect_compute_platform(self, files: List[str]) -> ComputePlatform:
        """Detect compute platform"""
        # Check in priority order: more specific platforms first
        priority_order = [
            ComputePlatform.DOCKER_COMPOSE,
            ComputePlatform.SERVERLESS_LAMBDA,
            ComputePlatform.SERVERLESS_CLOUD_RUN,
            ComputePlatform.SERVERLESS_CLOUD_FUNCTIONS,
            ComputePlatform.PAAS_HEROKU,
            ComputePlatform.PAAS_VERCEL,
            ComputePlatform.PAAS_NETLIFY,
            ComputePlatform.PAAS_RAILWAY,
            ComputePlatform.PAAS_RENDER,
            ComputePlatform.PAAS_FLY_IO,
            ComputePlatform.KUBERNETES_K3S,
            ComputePlatform.KUBERNETES_SELF,
            ComputePlatform.KUBERNETES_AKS,
            ComputePlatform.KUBERNETES_GKE,
            ComputePlatform.KUBERNETES_EKS,
            ComputePlatform.KUBERNETES,
            ComputePlatform.VM,
            ComputePlatform.CONTAINER,
        ]

        for target_platform in priority_order:
            for (deployment_name, platform_type), indicators in self.DEPLOYMENT_INDICATORS.items():
                if platform_type == target_platform:
                    for indicator in indicators:
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
            (CloudProvider.AWS, ComputePlatform.KUBERNETES_EKS): self._eks_prescription,
            (CloudProvider.GCP, ComputePlatform.KUBERNETES): self._gke_prescription,
            (CloudProvider.GCP, ComputePlatform.KUBERNETES_GKE): self._gke_prescription,
            (CloudProvider.AZURE, ComputePlatform.KUBERNETES_AKS): self._aks_prescription,
            (CloudProvider.UNKNOWN, ComputePlatform.KUBERNETES): self._kubernetes_prescription,
            (CloudProvider.SCALEWAY, ComputePlatform.KUBERNETES): self._scaleway_k8s_prescription,
            (CloudProvider.HETZNER, ComputePlatform.KUBERNETES): self._hetzner_k8s_prescription,
            (CloudProvider.OVHCLOUD, ComputePlatform.KUBERNETES): self._ovh_k8s_prescription,
            (CloudProvider.EXOSCALE, ComputePlatform.KUBERNETES): self._exoscale_k8s_prescription,

            # Serverless prescriptions
            (CloudProvider.AWS, ComputePlatform.SERVERLESS): self._aws_lambda_prescription,
            (CloudProvider.AWS, ComputePlatform.SERVERLESS_LAMBDA): self._aws_lambda_prescription,
            (CloudProvider.GCP, ComputePlatform.SERVERLESS): self._cloud_run_prescription,
            (CloudProvider.GCP, ComputePlatform.SERVERLESS_CLOUD_RUN): self._cloud_run_prescription,
            (CloudProvider.GCP, ComputePlatform.SERVERLESS_CLOUD_FUNCTIONS): self._cloud_functions_prescription,

            # PaaS prescriptions
            (CloudProvider.HEROKU, ComputePlatform.PAAS_HEROKU): self._heroku_prescription,
            (CloudProvider.VERCEL, ComputePlatform.PAAS_VERCEL): self._vercel_prescription,
            (CloudProvider.NETLIFY, ComputePlatform.PAAS_NETLIFY): self._netlify_prescription,
            (CloudProvider.RAILWAY, ComputePlatform.PAAS_RAILWAY): self._railway_prescription,
            (CloudProvider.RENDER, ComputePlatform.PAAS_RENDER): self._render_prescription,
            (CloudProvider.FLY_IO, ComputePlatform.PAAS_FLY_IO): self._fly_io_prescription,

            # VM prescriptions (European clouds)
            (CloudProvider.SCALEWAY, ComputePlatform.VM): self._scaleway_vm_prescription,
            (CloudProvider.HETZNER, ComputePlatform.VM): self._hetzner_vm_prescription,
            (CloudProvider.OVHCLOUD, ComputePlatform.VM): self._ovh_vm_prescription,
            (CloudProvider.EXOSCALE, ComputePlatform.VM): self._exoscale_vm_prescription,
            (CloudProvider.IONOS, ComputePlatform.VM): self._ionos_vm_prescription,
            (CloudProvider.GCORE, ComputePlatform.VM): self._gcore_vm_prescription,
            (CloudProvider.DIGITAL_OCEAN, ComputePlatform.VM): self._digitalocean_vm_prescription,
            (CloudProvider.VULTR, ComputePlatform.VM): self._vultr_vm_prescription,
            (CloudProvider.LINODE, ComputePlatform.VM): self._linode_vm_prescription,

            # Docker Compose
            (CloudProvider.SELF_HOSTED, ComputePlatform.DOCKER_COMPOSE): self._docker_compose_prescription,
            (CloudProvider.UNKNOWN, ComputePlatform.DOCKER_COMPOSE): self._docker_compose_prescription,

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

    def _cloud_functions_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Google Cloud Functions prescription"""
        return EventHandlingPrescription(
            metrics_source="Cloud Monitoring",
            log_source="Cloud Logging",
            trace_source="Cloud Trace",
            alert_destination="Cloud Alerting",
            ingestion_methods=[
                "Cloud Logging automatic",
                "Cloud Monitoring metrics"
            ],
            required_integrations=[
                "Cloud Functions logs automatically",
                "Cloud Monitoring"
            ],
            setup_commands=[
                "gcloud functions deploy <function> --trigger-http --runtime=python39"
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

    # ========== European Cloud Provider Prescriptions ==========

    def _scaleway_k8s_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Scaleway Kubernetes prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus (Scaleway Managed Prometheus)",
            log_source="Loki or Scaleway Logs",
            trace_source="Tempo or Grafana Cloud",
            alert_destination="Alertmanager or Grafana OnCall",
            ingestion_methods=[
                "Prometheus scraping via ServiceMonitor",
                "Fluent Bit for logs to Scaleway Object Storage",
                "OpenTelemetry Collector for traces"
            ],
            required_integrations=[
                "kube-state-metrics",
                "cadvisor",
                "Scaleway Container Registry metrics"
            ],
            setup_commands=[
                "helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack",
                "kubectl apply -f https://raw.githubusercontent.com/scaleway/fluent-bit/master/compose/k8s/fluent-bit-daemonset.yaml"
            ]
        )

    def _scaleway_vm_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Scaleway VM prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus node exporter",
            log_source="Loki with Vector shipping",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "node_exporter on all instances",
                "Vector agent for log shipping",
                "OpenTelemetry Collector"
            ],
            required_integrations=[
                "node_exporter",
                "cadvisor",
                "Vector"
            ],
            setup_commands=[
                "scw instance attach <instance-id> --ip <load-balancer-ip>",
                "curl -L https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz | tar xz"
            ]
        )

    def _hetzner_k8s_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Hetzner Kubernetes prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus",
            log_source="Loki",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "Prometheus via ServiceMonitor",
                "Fluent Bit DaemonSet to Hetzner Storage Box",
                "OpenTelemetry Collector"
            ],
            required_integrations=[
                "kube-state-metrics",
                "cadvisor",
                "Hetzner Cloud Controller Manager metrics"
            ],
            setup_commands=[
                "helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack",
                "hcloud volume create --size 10 --name loki-storage --automount"
            ]
        )

    def _hetzner_vm_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Hetzner VM prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus node exporter",
            log_source="Loki",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "node_exporter on all hcloud servers",
                "Prometheus scraping hcloud metrics",
                "Fluent Bit for logs"
            ],
            required_integrations=[
                "node_exporter",
                "hcloud-exporter"
            ],
            setup_commands=[
                "wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz",
                "hcloud server attach-to-network <server-id> --network <metrics-network>"
            ]
        )

    def _ovh_k8s_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """OVHcloud Kubernetes prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus (Managed Public Cloud)",
            log_source="Loki or Graylog",
            trace_source="Tempo or Jaeger",
            alert_destination="Alertmanager or Grafana OnCall",
            ingestion_methods=[
                "Prometheus via ServiceMonitor",
                "Fluent Bit for Logs to OVH Object Storage",
                "OpenTelemetry"
            ],
            required_integrations=[
                "kube-state-metrics",
                "OVH Metrics"
            ],
            setup_commands=[
                "kubectl apply -f https://raw.githubusercontent.com/ovh/manager/master/kube-prometheus/"
            ]
        )

    def _ovh_vm_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """OVHcloud VM prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus node exporter",
            log_source="Loki with OVH Logs integration",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "node_exporter",
                "OVH Logs API (vflow or syslog)",
                "OpenTelemetry"
            ],
            required_integrations=[
                "node_exporter",
                "OVH Logs agent"
            ],
            setup_commands=[
                "ovh vrack create --name observability",
                "curl -L https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz | tar xz"
            ]
        )

    def _exoscale_k8s_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Exoscale Kubernetes prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus",
            log_source="Loki or Exoscale POL (Private Object Locker)",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "Prometheus scraping",
                "Fluent Bit to Exoscale Object Storage",
                "OpenTelemetry"
            ],
            required_integrations=[
                "kube-state-metrics",
                "Exoscale container registry metrics"
            ],
            setup_commands=[
                "exo compute instance list",
                "kubectl apply -f monitoring/"
            ]
        )

    def _exoscale_vm_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Exoscale VM prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus node exporter",
            log_source="Loki",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "node_exporter",
                "Fluent Bit",
                "OpenTelemetry Collector"
            ],
            required_integrations=[
                "node_exporter",
                "Exoscale API metrics via exporter"
            ],
            setup_commands=[
                "exo compute instance create --name <monitoring>"
            ]
        )

    def _ionos_vm_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """IONOS VM prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus node exporter",
            log_source="Loki",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "node_exporter",
                "Fluent Bit",
                "OpenTelemetry"
            ],
            required_integrations=[
                "node_exporter",
                "IONOS API metrics"
            ],
            setup_commands=[
                "ionosctl server create"
            ]
        )

    def _gcore_vm_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """G-Core Cloud VM prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus node exporter",
            log_source="Loki",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "node_exporter",
                "Fluent Bit",
                "OpenTelemetry"
            ],
            required_integrations=[
                "node_exporter",
                "G-Core CDN metrics"
            ],
            setup_commands=[
                "gcore compute instance create"
            ]
        )

    def _digitalocean_vm_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """DigitalOcean VM prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus node exporter + DO exporter",
            log_source="Loki",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "node_exporter + do_exporter",
                "Fluent Bit",
                "OpenTelemetry"
            ],
            required_integrations=[
                "node_exporter",
                "DigitalOcean exporter (do_exporter)"
            ],
            setup_commands=[
                "doctl compute droplet create",
                "helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack"
            ]
        )

    def _vultr_vm_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Vultr VM prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus node exporter + Vultr exporter",
            log_source="Loki",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "node_exporter + vultr_exporter",
                "Fluent Bit",
                "OpenTelemetry"
            ],
            required_integrations=[
                "node_exporter",
                "Vultr exporter"
            ],
            setup_commands=[
                "vultr-server create",
                "curl -sSL https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz | tar xz"
            ]
        )

    def _linode_vm_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Linode/Akamai VM prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus node exporter + Linode exporter",
            log_source="Loki",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "node_exporter + linode_exporter",
                "Fluent Bit",
                "OpenTelemetry"
            ],
            required_integrations=[
                "node_exporter",
                "Linode exporter"
            ],
            setup_commands=[
                "linode-cli linodes create",
                "curl -sSL https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz | tar xz"
            ]
        )

    # ========== PaaS Provider Prescriptions ==========

    def _heroku_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Heroku prescription"""
        return EventHandlingPrescription(
            metrics_source="Heroku Labs Metrics",
            log_source="Heroku Logplex ( drains to Loki)",
            trace_source="Heroku Runtime (via OpenTelemetry)",
            alert_destination="Heroku Alerts → PagerDuty/Slack",
            ingestion_methods=[
                "Heroku Labs metrics endpoint",
                "Log drain to Loki HTTPS endpoint",
                "OpenTelemetry SDK for APM"
            ],
            required_integrations=[
                "Heroku Logplex drain",
                "Heroku dyno metrics"
            ],
            setup_commands=[
                "heroku addons:create heroku-redis -h <app>",
                "heroku drains:add https://loki.example.com/loki/api/v1/push -h <app>"
            ]
        )

    def _vercel_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Vercel prescription"""
        return EventHandlingPrescription(
            metrics_source="Vercel Analytics",
            log_source="Vercel Logs ( drain to Loki)",
            trace_source="Vercel APM or OpenTelemetry",
            alert_destination="Vercel Notifications → PagerDuty",
            ingestion_methods=[
                "Vercel Analytics dashboard",
                "Log drain to Loki",
                "OpenTelemetry instrumentation"
            ],
            required_integrations=[
                "Vercel Log Drain",
                "Vercel Edge Network metrics"
            ],
            setup_commands=[
                "vercel link integrate --project-id=<project>",
                "Add log drain in Vercel dashboard"
            ]
        )

    def _netlify_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Netlify prescription"""
        return EventHandlingPrescription(
            metrics_source="Netlify Analytics",
            log_source="Netlify Logs ( drain to Loki)",
            trace_source="Edge Functions APM",
            alert_destination="Netlify Notifications → Slack",
            ingestion_methods=[
                "Netlify Analytics",
                "Functions log drains",
                "OpenTelemetry for edge functions"
            ],
            required_integrations=[
                "Netlify Functions logs",
                "Edge Network metrics"
            ],
            setup_commands=[
                "netlify addons:create analytics",
                "Configure log drain in netlify.toml"
            ]
        )

    def _railway_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Railway prescription"""
        return EventHandlingPrescription(
            metrics_source="Railway Metrics",
            log_source="Railway Logs (structured JSON)",
            trace_source="OpenTelemetry",
            alert_destination="Railway Notifications → PagerDuty",
            ingestion_methods=[
                "Railway built-in metrics",
                "Log forwarder to Loki",
                "OpenTelemetry SDK"
            ],
            required_integrations=[
                "Railway metrics endpoint",
                "Log forwarding"
            ],
            setup_commands=[
                "railway variables set METRICS_ENDPOINT=<prometheus>",
                "railway domain"
            ]
        )

    def _render_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Render prescription"""
        return EventHandlingPrescription(
            metrics_source="Render Metrics",
            log_source="Render Logs ( drain to Loki)",
            trace_source="OpenTelemetry",
            alert_destination="Render Alerts → PagerDuty",
            ingestion_methods=[
                "Render dashboard metrics",
                "Log drain to Loki",
                "OpenTelemetry SDK"
            ],
            required_integrations=[
                "Render log drains",
                "Render metrics API"
            ],
            setup_commands=[
                "render env set METRICS_KEY=<key>",
                "Add log drain in Render dashboard"
            ]
        )

    def _fly_io_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Fly.io prescription"""
        return EventHandlingPrescription(
            metrics_source="Fly.io Metrics + Prometheus",
            log_source="Fly.io Logs ( drain to Loki)",
            trace_source="Fly.io Tracing",
            alert_destination="Alertmanager → PagerDuty",
            ingestion_methods=[
                "flyctl metrics",
                "Log forwarding to Loki",
                "OpenTelemetry tracing"
            ],
            required_integrations=[
                "flyctl agent command for metrics",
                "Log forwarding"
            ],
            setup_commands=[
                "flyctl agent create --region <region>",
                "fly volumes create loki-data --region <region>"
            ]
        )

    # ========== Additional Prescriptions ==========

    def _aks_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Azure AKS prescription"""
        return EventHandlingPrescription(
            metrics_source="Azure Monitor Managed Prometheus",
            log_source="Azure Monitor Logs / Container Insights",
            trace_source="Azure Application Insights / Grafana Tempo",
            alert_destination="Azure Monitor Alerts → Action Groups",
            ingestion_methods=[
                "Azure Monitor Metrics",
                "Container Insights for logs",
                "Azure Monitor Agent for traces"
            ],
            required_integrations=[
                "Azure Monitor metrics addon",
                "Container Insights"
            ],
            setup_commands=[
                "az aks enable-addons -a monitoring -n <clusterName> -g <resourceGroup>",
                "az aks update --resource-group <RG> --name <cluster> --enable-azure-monitor-metrics"
            ]
        )

    def _docker_compose_prescription(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Docker Compose prescription"""
        return EventHandlingPrescription(
            metrics_source="Prometheus",
            log_source="Loki",
            trace_source="Tempo",
            alert_destination="Alertmanager",
            ingestion_methods=[
                "Prometheus scraping container metrics",
                "Fluent Bit container for log aggregation",
                "OpenTelemetry Collector sidecar"
            ],
            required_integrations=[
                "cAdvisor",
                "node_exporter (on host)",
                "Prometheus in docker-compose"
            ],
            setup_commands=[
                "Add Prometheus, Grafana, Loki services to docker-compose.yml",
                "docker-compose up -d monitoring-stack"
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

        # Kubernetes variants
        if analysis.compute_platform in [
            ComputePlatform.KUBERNETES, ComputePlatform.KUBERNETES_EKS,
            ComputePlatform.KUBERNETES_GKE, ComputePlatform.KUBERNETES_AKS,
            ComputePlatform.KUBERNETES_SELF, ComputePlatform.KUBERNETES_K3S
        ]:
            observers.extend(["log-aggregator", "pod-health-monitor"])
            monitors.extend(["anomaly-detector"])
            optional.extend(["kubernetes-specialist", "resource-quotas-tracker"])

        # Serverless variants
        if analysis.compute_platform in [
            ComputePlatform.SERVERLESS, ComputePlatform.SERVERLESS_LAMBDA,
            ComputePlatform.SERVERLESS_CLOUD_RUN, ComputePlatform.SERVERLESS_CLOUD_FUNCTIONS
        ]:
            observers.extend(["log-aggregator"])
            monitors.extend(["cold-start-monitor", "concurrency-analyzer"])
            optional.append("cost-analyzer")

        # PaaS variants
        if analysis.compute_platform in [
            ComputePlatform.PAAS_HEROKU, ComputePlatform.PAAS_VERCEL,
            ComputePlatform.PAAS_NETLIFY, ComputePlatform.PAAS_RAILWAY,
            ComputePlatform.PAAS_RENDER, ComputePlatform.PAAS_FLY_IO
        ]:
            monitors.extend(["edge-function-monitor", "deployment-monitor"])
            optional.append("cost-analyzer")

        # VM variants (including European clouds)
        if analysis.compute_platform == ComputePlatform.VM:
            observers.extend(["log-aggregator"])
            monitors.extend(["host-resource-monitor"])
            if analysis.cloud_provider not in [CloudProvider.SELF_HOSTED, CloudProvider.ON_PREM]:
                optional.append("cost-analyzer")

        # Docker Compose
        if analysis.compute_platform == ComputePlatform.DOCKER_COMPOSE:
            observers.extend(["log-aggregator"])
            monitors.extend(["container-health-monitor"])
            optional.extend(["docker-network-monitor"])

        # Cloud provider cost monitoring
        if analysis.cloud_provider in [
            CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE,
            CloudProvider.SCALEWAY, CloudProvider.DIGITAL_OCEAN,
            CloudProvider.VULTR, CloudProvider.LINODE, CloudProvider.HEROKU,
            CloudProvider.RAILWAY, CloudProvider.RENDER, CloudProvider.FLY_IO
        ]:
            if "cost-analyzer" not in optional:
                optional.append("cost-analyzer")

        # Framework-specific agents
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
