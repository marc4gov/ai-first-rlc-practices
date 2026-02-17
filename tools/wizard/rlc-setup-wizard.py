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
class EventHandlingOption:
    """A single event handling option with cost and quality assessment"""
    name: str  # Budget, Balanced, or Premium
    tier: str  # budget, balanced, premium
    metrics_source: str
    log_source: str
    trace_source: str
    alert_destination: str
    ingestion_methods: List[str]
    required_integrations: List[str]
    setup_commands: List[str]
    estimated_monthly_cost: str  # e.g., "<$50", "$50-200", "$200+"
    setup_complexity: str  # Low, Medium, High
    pros: List[str]
    cons: List[str]
    best_for: List[str]  # Use cases this option is best for


@dataclass
class EventHandlingPrescription:
    """Prescribed event handling setup with multiple options"""
    primary: EventHandlingOption  # Recommended option
    options: List[EventHandlingOption]  # All available options
    selected_tier: str = "balanced"  # Default selection


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
    """Prescribes event handling based on environment with price-quality tiers"""

    def __init__(self):
        # Map (provider, platform) to tiered options generator
        self.prescriptions = {
            # Kubernetes prescriptions
            (CloudProvider.UNKNOWN, ComputePlatform.KUBERNETES): self._kubernetes_tiered,
            (CloudProvider.AWS, ComputePlatform.KUBERNETES): self._eks_tiered,
            (CloudProvider.GCP, ComputePlatform.KUBERNETES): self._gke_tiered,
            (CloudProvider.AZURE, ComputePlatform.KUBERNETES_AKS): self._aks_tiered,
            (CloudProvider.SCALEWAY, ComputePlatform.KUBERNETES): self._scaleway_k8s_tiered,
            (CloudProvider.HETZNER, ComputePlatform.KUBERNETES): self._hetzner_k8s_tiered,
            (CloudProvider.OVHCLOUD, ComputePlatform.KUBERNETES): self._ovh_k8s_tiered,
            (CloudProvider.EXOSCALE, ComputePlatform.KUBERNETES): self._exoscale_k8s_tiered,
            (CloudProvider.DIGITAL_OCEAN, ComputePlatform.KUBERNETES): self._digitalocean_k8s_tiered,

            # Serverless prescriptions
            (CloudProvider.AWS, ComputePlatform.SERVERLESS): self._lambda_tiered,
            (CloudProvider.AWS, ComputePlatform.SERVERLESS_LAMBDA): self._lambda_tiered,
            (CloudProvider.GCP, ComputePlatform.SERVERLESS): self._cloud_run_tiered,
            (CloudProvider.GCP, ComputePlatform.SERVERLESS_CLOUD_RUN): self._cloud_run_tiered,

            # PaaS prescriptions
            (CloudProvider.HEROKU, ComputePlatform.PAAS_HEROKU): self._heroku_tiered,
            (CloudProvider.VERCEL, ComputePlatform.PAAS_VERCEL): self._vercel_tiered,
            (CloudProvider.NETLIFY, ComputePlatform.PAAS_NETLIFY): self._netlify_tiered,
            (CloudProvider.RAILWAY, ComputePlatform.PAAS_RAILWAY): self._railway_tiered,
            (CloudProvider.RENDER, ComputePlatform.PAAS_RENDER): self._render_tiered,
            (CloudProvider.FLY_IO, ComputePlatform.PAAS_FLY_IO): self._fly_io_tiered,

            # VM prescriptions (European clouds)
            (CloudProvider.SCALEWAY, ComputePlatform.VM): self._scaleway_vm_tiered,
            (CloudProvider.HETZNER, ComputePlatform.VM): self._hetzner_vm_tiered,
            (CloudProvider.OVHCLOUD, ComputePlatform.VM): self._ovh_vm_tiered,
            (CloudProvider.EXOSCALE, ComputePlatform.VM): self._exoscale_vm_tiered,
            (CloudProvider.IONOS, ComputePlatform.VM): self._ionos_vm_tiered,
            (CloudProvider.DIGITAL_OCEAN, ComputePlatform.VM): self._digitalocean_vm_tiered,
            (CloudProvider.VULTR, ComputePlatform.VM): self._vultr_vm_tiered,
            (CloudProvider.LINODE, ComputePlatform.VM): self._linode_vm_tiered,

            # Docker Compose
            (CloudProvider.UNKNOWN, ComputePlatform.DOCKER_COMPOSE): self._docker_compose_tiered,
            (CloudProvider.SELF_HOSTED, ComputePlatform.DOCKER_COMPOSE): self._docker_compose_tiered,

            # Default
            (CloudProvider.UNKNOWN, ComputePlatform.UNKNOWN): self._generic_tiered,
        }

    def prescribe(self, analysis: RepositoryAnalysis) -> EventHandlingPrescription:
        """Generate tiered prescription based on analysis"""
        key = (analysis.cloud_provider, analysis.compute_platform)
        tiered_generator = self.prescriptions.get(key, self._generic_tiered)
        options = tiered_generator(analysis)

        # Default to balanced tier as primary
        primary = next((o for o in options if o.tier == "balanced"), options[0] if options else None)

        return EventHandlingPrescription(
            primary=primary,
            options=options,
            selected_tier="balanced"
        )

    # ========== Tiered Option Creators ==========

    def _create_option(self, tier: str, name: str, provider: str,
                       metrics: str, logs: str, traces: str, alerts: str,
                       ingestion: List[str], integrations: List[str], commands: List[str],
                       cost: str, complexity: str, pros: List[str], cons: List[str], best_for: List[str]) -> EventHandlingOption:
        """Helper to create an EventHandlingOption"""
        return EventHandlingOption(
            name=name,
            tier=tier,
            metrics_source=metrics,
            log_source=logs,
            trace_source=traces,
            alert_destination=alerts,
            ingestion_methods=ingestion,
            required_integrations=integrations,
            setup_commands=commands,
            estimated_monthly_cost=cost,
            setup_complexity=complexity,
            pros=pros,
            cons=cons,
            best_for=best_for
        )

    # ========== Kubernetes Tiered Options (Best Price-Quality) ==========

    def _kubernetes_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Kubernetes tiered options - self-hosted"""
        return [
            # BUDGET - Open source self-hosted
            self._create_option(
                tier="budget", name="Open Source Self-Hosted", provider="kubernetes",
                metrics="Prometheus (self-hosted)",
                logs="Loki (self-hosted to MinIO/S3)",
                traces="Tempo (self-hosted to MinIO/S3)",
                alerts="Alertmanager",
                ingestion_methods=["Prometheus scraping", "Fluent Bit DaemonSet", "OpenTelemetry Collector basic"],
                integrations=["kube-state-metrics", "cadvisor", "node-exporter"],
                commands=["helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack",
                         "helm install loki grafana/loki-stack",
                         "helm install tempo grafana/tempo"],
                cost="<$30", complexity="High",
                pros=["Zero software cost", "Full control", "No vendor lock-in", "Unlimited retention limits"],
                cons=["High operational overhead", "Must manage storage", "No automatic scaling", "Security patches manual"],
                best_for=["Small teams with DevOps expertise", "Budget-constrained projects", "Learning observability"]
            ),
            # BALANCED - LGTM Stack with object storage
            self._create_option(
                tier="balanced", name="LGTM Stack + Object Storage", provider="kubernetes",
                metrics="Prometheus (VictoriaMetrics for cost)",
                logs="Loki (Grafana Loki)",
                traces="Tempo (Grafana Tempo)",
                alerts="Alertmanager + Grafana OnCall",
                ingestion_methods=["Prometheus scraping", "Fluent Bit", "OpenTelemetry Collector with sampling"],
                integrations=["kube-state-metrics", "cadvisor", "node-exporter"],
                commands=["helm install victoria-metrics victoria-metrics/victoria-metrics-k8s-stack",
                         "helm install loki grafana/loki-stack",
                         "helm install tempo grafana/tempo"],
                cost="$30-100", complexity="Medium",
                pros=["Excellent price-performance", "Object storage reduces costs", "Good community support", "Scalable architecture"],
                cons=["Object storage costs vary", "Still requires maintenance", "Learning curve for Grafana stack"],
                best_for=["Production workloads", "Growing teams", "Best price-quality ratio"]
            ),
            # PREMIUM - Managed observability
            self._create_option(
                tier="premium", name="Fully Managed Observability", provider="kubernetes",
                metrics="Grafana Cloud Mimir/Prometheus",
                logs="Grafana Cloud Loki",
                traces="Grafana Cloud Tempo",
                alerts="Grafana OnCall + PagerDuty",
                ingestion_methods=["Grafana Agent", "Grafana Cloud native integrations", "OpenTelemetry Collector full"],
                integrations=["Grafana Cloud Alloy", "All K8s metrics automatic"],
                commands=["grafana cloud install", "Connect cluster via API"],
                cost="$100-500", complexity="Low",
                pros=["Zero maintenance", "Automatic scaling", "24/7 support included", "SLO features included"],
                cons=["Higher cost at scale", "Vendor lock-in", "Data egress fees"],
                best_for=["Enterprise production", "Teams without Ops resources", "Critical workloads"]
            )
        ]

    # ========== AWS EKS Tiered Options ==========

    def _eks_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """AWS EKS tiered options"""
        return [
            # BUDGET - Self-hosted on EC2
            self._create_option(
                tier="budget", name="Self-Hosted Prometheus + CloudWatch Logs", provider="aws-eks",
                metrics="Prometheus (self-hosted on EC2)",
                logs="CloudWatch Logs (basic)",
                traces="AWS X-Ray (basic)",
                alerts="Alertmanager (self-hosted) + CloudWatch Alarms",
                ingestion_methods=["Prometheus operator", "CloudWatch agent", "AWS Distro for OTel"],
                integrations=["aws-cloudwatch-metrics", "kube-state-metrics"],
                commands=["kubectl install prometheus-operator", "Enable CloudWatch container insights"],
                cost="$20-80", complexity="High",
                pros=["No managed service fees", "Keep metrics in-cluster", "CloudWatch Logs integration"],
                cons=["EC2 costs for Prometheus", "Manual scaling", "Maintenance overhead"],
                best_for=["Cost-sensitive teams", "Existing EC2 infrastructure"]
            ),
            # BALANCED - AMP + CloudWatch
            self._create_option(
                tier="balanced", name="Amazon Managed Service for Prometheus", provider="aws-eks",
                metrics="AMP (Amazon Managed Prometheus)",
                logs="CloudWatch Logs with S3 archive",
                traces="AWS X-Ray with OTel",
                alerts="CloudWatch Alarms + Alertmanager",
                ingestion_methods=["AMP remote write", "CloudWatch agent", "ADOT collector"],
                integrations=["AWS AMP workspace", "CloudWatch Logs Insights", "X-Ray daemon"],
                commands=["aws amp create-workspace", "Enable ADOT add-on on EKS"],
                cost="$50-150", complexity="Medium",
                pros=["No Prometheus maintenance", "AWS native integration", "Scalable", "S3 logs cheap long-term"],
                cons=["AMP costs at scale", "Query API charges", "X-Ray limited tracing"],
                best_for=["Production EKS", "AWS-centric teams", "Balanced cost/maintenance"]
            ),
            # PREMIUM - Datadog/New Relic
            self._create_option(
                tier="premium", name="Datadog / New Relic", provider="aws-eks",
                metrics="Datadog Metrics / New Relic Metrics",
                logs="Datadog Logs / New Relic Logs",
                traces="Datadog APM / New Relic APM",
                alerts="Datadog Monitor / New Relic Alerts + PagerDuty",
                ingestion_methods=["Datadog Agent / New Relic Infrastructure", "Full instrumentation"],
                integrations=["AWS integrations automatic", "All services monitored"],
                commands=["Install Datadog Agent via Helm", "Enable AWS CloudWatch metrics sync"],
                cost="$200-1000+", complexity="Low",
                pros=["All-in-one platform", "Excellent UI", "Auto-instrumentation", "24/7 support"],
                cons=["Expensive at scale", "Per-host pricing", "Vendor lock-in"],
                best_for=["Enterprise", "Teams wanting turnkey", "Rapid deployment"]
            )
        ]

    # ========== GCP GKE Tiered Options ==========

    def _gke_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Google GKE tiered options"""
        return [
            # BUDGET - Self-hosted LGTM
            self._create_option(
                tier="budget", name="Self-Hosted LGTM Stack", provider="gcp-gke",
                metrics="Prometheus (self-hosted on GKE)",
                logs="Loki (to GCS)",
                traces="Tempo (to GCS)",
                alerts="Alertmanager",
                ingestion_methods=["Prometheus scraping", "Fluent Bit", "OTel Collector"],
                integrations=["kube-state-metrics", "cadvisor"],
                commands=["helm install kube-prometheus-stack", "Use GCS for Loki/Tempo storage"],
                cost="<$50", complexity="High",
                pros=["Zero GCP monitoring fees", "GCS cheap storage", "Full control"],
                cons=["Manage Prometheus cluster", "Manual setup", "Maintenance"],
                best_for=["Budget-constrained GKE", "Teams with K8s expertise"]
            ),
            # BALANCED - Google Cloud Operations
            self._create_option(
                tier="balanced", name="Google Cloud Operations (Stackdriver)", provider="gcp-gke",
                metrics="Cloud Monitoring (Prometheus compatible)",
                logs="Cloud Logging with log-based metrics",
                traces="Cloud Trace",
                alerts="Cloud Alerting + Alertmanager export",
                ingestion_methods=["Google Cloud Operations agent", "Auto-instrumentation"],
                integrations=["GKE metrics automatic", "Service mesh metrics"],
                commands=["gcloud container clusters update --enable-cloud-monitoring"],
                cost="$50-200", complexity="Low",
                pros=["Native GCP integration", "Automatic for GKE", "Good UI", "Logs and metrics together"],
                cons=["Log ingestion costs", "Query syntax unique", "Less flexible than Prometheus"],
                best_for=["GKE production", "GCP-native teams", "Moderate cost tolerance"]
            ),
            # PREMIUM - Grafana Cloud + GCP
            self._create_option(
                tier="premium", name="Grafana Cloud + GCP Integration", provider="gcp-gke",
                metrics="Grafana Cloud Mimir",
                logs="Grafana Cloud Loki",
                traces="Grafana Cloud Tempo",
                alerts="Grafana OnCall",
                ingestion_methods=["Grafana Agent", "GCP metrics bridge"],
                integrations=["GCP integration automatic", "Full stack visibility"],
                commands=["Install Grafana Agent", "Connect GCP projects"],
                cost="$150-400", complexity="Low",
                pros=["Best of both worlds", "GCP logs via bridge", "Unified dashboards", "No maintenance"],
                cons=["Multiple services to pay for", "GCP egress charges"],
                best_for=["Multi-cloud environments", "Teams wanting Grafana ecosystem"]
            )
        ]

    # ========== Azure AKS Tiered Options ==========

    def _aks_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Azure AKS tiered options"""
        return [
            # BUDGET - Self-hosted
            self._create_option(
                tier="budget", name="Self-Hosted LGTM", provider="azure-aks",
                metrics="Prometheus (self-hosted)",
                logs="Loki (to Azure Blob)",
                traces="Tempo (to Azure Blob)",
                alerts="Alertmanager",
                ingestion_methods=["Prometheus operator", "Fluent Bit", "OTel"],
                integrations=["kube-state-metrics", "cadvisor"],
                commands=["helm install kube-prometheus-stack"],
                cost="<$40", complexity="High",
                pros=["No Azure Monitor costs", "Blob storage cheap", "Open source"],
                cons=["High maintenance", "Must manage Prometheus", "Self-support"],
                best_for=["Budget AKS", "Open source preference"]
            ),
            # BALANCED - Azure Monitor Managed Prometheus
            self._create_option(
                tier="balanced", name="Azure Monitor + Container Insights", provider="azure-aks",
                metrics="Azure Monitor Managed Prometheus",
                logs="Azure Monitor Logs (Log Analytics)",
                traces="Application Insights",
                alerts="Azure Monitor Alerts + Action Groups",
                ingestion_methods=["Azure Monitor agent", "AMA Metrics", "Dapr tracing"],
                integrations=["Container Insights", "AKS metrics automatic"],
                commands=["az aks enable-addons -a monitoring", "az aks update --enable-azure-monitor-metrics"],
                cost="$60-180", complexity="Low",
                pros=["Native Azure integration", "Container Insights excellent", "Managed Prometheus compatible", "Good UX"],
                cons=["Log Analytics expensive at scale", "Query language (KQL) unique"],
                best_for=["AKS production", "Azure-centric teams"]
            ),
            # PREMIUM - Datadog
            self._create_option(
                tier="premium", name="Datadog", provider="azure-aks",
                metrics="Datadog Metrics",
                logs="Datadog Logs",
                traces="Datadog APM",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog Agent"],
                integrations=["Azure integration automatic"],
                commands=["Install Datadog Agent"],
                cost="$200-800", complexity="Low",
                pros=["Turnkey monitoring", "Excellent dashboards", "Auto-instrumentation"],
                cons=["Expensive", "Per-host pricing"],
                best_for=["Enterprise AKS", "Rapid deployment"]
            )
        ]

    # ========== Hetzner Kubernetes Tiered Options (Best EU Value) ==========

    def _hetzner_k8s_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Hetzner Kubernetes - best value in Europe"""
        return [
            # BUDGET - Pure open source on Hetzner
            self._create_option(
                tier="budget", name="Self-Hosted LGTM on Hetzner", provider="hetzner-k8s",
                metrics="Prometheus (self-hosted on Hetzner VM)",
                logs="Loki (to Hetzner Storage Box)",
                traces="Tempo (to Hetzner Storage Box)",
                alerts="Alertmanager",
                ingestion_methods=["Prometheus scraping", "Fluent Bit", "OTel"],
                integrations=["kube-state-metrics", "hcloud-exporter"],
                commands=["Deploy monitoring on dedicated Hetzner CX22 (~€8/month)",
                         "hcloud volume create --size 10 --name loki-storage"],
                cost="<€20/month", complexity="High",
                pros=["Best value in EU", "Hetzner Storage Box included (free for small projects)", "No egress fees in EU", "Privacy compliant"],
                cons=["Need dedicated monitoring VM", "High availability doubles cost", "Self-managed"],
                best_for=["EU privacy requirements", "Budget-conscious EU startups", "Hetzner enthusiasts"]
            ),
            # BALANCED - Hetzner + Grafana Cloud
            self._create_option(
                tier="balanced", name="Grafana Cloud (EU region)", provider="hetzner-k8s",
                metrics="Grafana Cloud Mimir (EU)",
                logs="Grafana Cloud Loki (EU)",
                traces="Grafana Cloud Tempo (EU)",
                alerts="Grafana OnCall",
                ingestion_methods=["Grafana Agent", "Grafana Alloy"],
                integrations=["Hetzner metrics", "Full observability"],
                commands=["Deploy Grafana Agent on K8s", "Connect to Grafana Cloud EU"],
                cost="€30-100/month", complexity="Low",
                pros=["EU data residency", "No maintenance", "Excellent value", "Hetzner network fast"],
                cons=["External service", "Learning curve"],
                best_for=["Production EU workloads", "Best price-quality in EU"]
            ),
            # PREMIUM - European Datadog/New Relic
            self._create_option(
                tier="premium", name="Datadog EU", provider="hetzner-k8s",
                metrics="Datadog (EU region)",
                logs="Datadog Logs (EU)",
                traces="Datadog APM (EU)",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog Agent"],
                integrations=["Hetzner cloud integration"],
                commands=["Install Datadog Agent"],
                cost="€150-500/month", complexity="Low",
                pros=["Full features", "EU region available", "Support"],
                cons=["Expensive", "Vendor lock-in"],
                best_for=["Enterprise with EU requirements"]
            )
        ]

    # ========== Scaleway Kubernetes Tiered Options ==========

    def _scaleway_k8s_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Scaleway Kubernetes tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Self-Hosted with Scaleway Object Storage",
                metrics="Prometheus (self-hosted)",
                logs="Loki (to Scaleway Object Storage)",
                traces="Tempo (to Scaleway Object Storage)",
                alerts="Alertmanager",
                ingestion_methods=["Prometheus operator", "Fluent Bit", "OTel"],
                integrations=["kube-state-metrics", "Scaleway metrics"],
                commands=["helm install kube-prometheus-stack", "Configure Object Storage bucket"],
                cost="<€25/month", complexity="High",
                pros=["Cheap storage in Paris/Amsterdam", "No egress fees", "EU privacy"],
                cons=["Maintenance overhead"],
                best_for=["Scaleway users", "EU startups"]
            ),
            # BALANCED - Scaleway Managed Services
            self._create_option(
                tier="balanced", name="Scaleway Managed Metrics + Self-Hosted Logs",
                metrics="Scaleway Managed Prometheus (beta)",
                logs="Loki (to Object Storage)",
                traces="Tempo (to Object Storage)",
                alerts="Alertmanager",
                ingestion_methods=["Prometheus operator", "Fluent Bit", "OTel"],
                integrations=["Scaleway metrics"],
                commands=["Enable Managed Metrics in K8s pool"],
                cost="€30-80/month", complexity="Medium",
                pros=["Managed Prometheus", "Cheap log storage", "Good EU value"],
                cons=["Still some self-hosting"],
                best_for=["Scaleway production"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="Grafana Cloud EU",
                metrics="Grafana Cloud Mimir",
                logs="Grafana Cloud Loki",
                traces="Grafana Cloud Tempo",
                alerts="Grafana OnCall",
                ingestion_methods=["Grafana Agent"],
                integrations=["Scaleway metrics"],
                commands=["Connect Grafana Cloud"],
                cost="€40-120/month", complexity="Low",
                pros=["Turnkey", "EU region", "Good value"],
                cons=["External service"],
                best_for=["Production Scaleway K8s"]
            )
        ]

    # ========== OVHcloud Kubernetes Tiered Options ==========

    def _ovh_k8s_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """OVHcloud Kubernetes (Managed Kubernetes) tiered options"""
        return [
            # BUDGET - Self-hosted LGTM on OVHcloud
            self._create_option(
                tier="budget", name="Self-Hosted LGTM on OVHcloud K8s", provider="ovhcloud-k8s",
                metrics="Prometheus (self-hosted on K8s)",
                logs="Loki (to OVH Object Storage)",
                traces="Tempo (to OVH Object Storage)",
                alerts="Alertmanager",
                ingestion_methods=["Prometheus operator", "Fluent Bit", "OTel"],
                integrations=["kube-state-metrics", "OVH metrics"],
                commands=["helm install kube-prometheus-stack", "Configure OVH Object Storage for log storage"],
                cost="<€25/month", complexity="High",
                pros=["OVH storage very cheap", "Good EU coverage", "No egress fees", "EU data residency"],
                cons=["Self-managed K8s monitoring", "Maintenance overhead"],
                best_for=["OVHcloud K8s users", "French market", "EU startups"]
            ),
            # BALANCED - OVHcloud + Grafana Cloud EU
            self._create_option(
                tier="balanced", name="OVHcloud + Grafana Cloud (EU)", provider="ovhcloud-k8s",
                metrics="Grafana Cloud Mimir (EU)",
                logs="Grafana Cloud Loki (EU)",
                traces="Grafana Cloud Tempo (EU)",
                alerts="Grafana OnCall",
                ingestion_methods=["Grafana Agent", "Grafana Alloy"],
                integrations=["OVH metrics", "Full observability"],
                commands=["Deploy Grafana Agent on K8s", "Connect to Grafana Cloud EU region"],
                cost="€30-90/month", complexity="Low",
                pros=["Good EU value with Paris region", "No maintenance", "Turnkey setup"],
                cons=["External service dependency"],
                best_for=["Production OVHcloud K8s", "Best price-quality for EU"]
            ),
            # PREMIUM - Datadog EU
            self._create_option(
                tier="premium", name="OVHcloud + Datadog EU", provider="ovhcloud-k8s",
                metrics="Datadog (EU region)",
                logs="Datadog Logs (EU)",
                traces="Datadog APM (EU)",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog Agent"],
                integrations=["OVHcloud integration", "K8s integration"],
                commands=["Install Datadog Agent on K8s"],
                cost="€100-400/month", complexity="Low",
                pros=["Full enterprise features", "EU region available", "Excellent support"],
                cons=["Expensive", "Vendor lock-in"],
                best_for=["Enterprise OVHcloud K8s"]
            )
        ]

    # ========== Exoscale Kubernetes Tiered Options ==========

    def _exoscale_k8s_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Exoscale Kubernetes tiered options"""
        return [
            # BUDGET - Self-hosted LGTM
            self._create_option(
                tier="budget", name="Self-Hosted LGTM on Exoscale K8s", provider="exoscale-k8s",
                metrics="Prometheus (self-hosted)",
                logs="Loki (to Exoscale Object Storage - POL)",
                traces="Tempo (to Exoscale POL)",
                alerts="Alertmanager",
                ingestion_methods=["Prometheus operator", "Fluent Bit", "OTel"],
                integrations=["kube-state-metrics", "Exoscale metrics"],
                commands=["helm install kube-prometheus-stack", "Configure Exoscale POL bucket"],
                cost="<€25/month", complexity="High",
                pros=["POL storage cheap", "Swiss privacy", "CH data centers", "No egress fees"],
                cons=["Self-managed", "Maintenance overhead"],
                best_for=["Exoscale K8s users", "Swiss market", "Privacy requirements"]
            ),
            # BALANCED - Exoscale + Grafana Cloud
            self._create_option(
                tier="balanced", name="Exoscale + Grafana Cloud (EU)", provider="exoscale-k8s",
                metrics="Grafana Cloud Mimir",
                logs="Grafana Cloud Loki",
                traces="Grafana Cloud Tempo",
                alerts="Grafana OnCall",
                ingestion_methods=["Grafana Agent"],
                integrations=["Exoscale metrics"],
                commands=["Deploy Grafana Agent", "Connect to Grafana Cloud"],
                cost="€30-80/month", complexity="Low",
                pros=["No maintenance", "Good value", "EU support"],
                cons=["External service"],
                best_for=["Production Exoscale K8s"]
            ),
            # PREMIUM - Datadog
            self._create_option(
                tier="premium", name="Exoscale + Datadog", provider="exoscale-k8s",
                metrics="Datadog",
                logs="Datadog Logs",
                traces="Datadog APM",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog Agent"],
                commands=["Install Datadog Agent"],
                cost="€100-400/month", complexity="Low",
                pros=["Full features", "Enterprise support"],
                cons=["Expensive"],
                best_for=["Enterprise Exoscale K8s"]
            )
        ]

    # ========== DigitalOcean Kubernetes Tiered Options ==========

    def _digitalocean_k8s_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """DigitalOcean Kubernetes (DOKS) tiered options"""
        return [
            # BUDGET - Self-hosted LGTM
            self._create_option(
                tier="budget", name="Self-Hosted LGTM on DOKS", provider="digitalocean-k8s",
                metrics="Prometheus (self-hosted on DOKS)",
                logs="Loki (to DO Spaces - S3 compatible)",
                traces="Tempo (to DO Spaces)",
                alerts="Alertmanager",
                ingestion_methods=["Prometheus operator", "Fluent Bit", "OTel"],
                integrations=["kube-state-metrics", "DO metrics"],
                commands=["helm install kube-prometheus-stack", "Create DO Spaces bucket"],
                cost="<$30/month", complexity="High",
                pros=["DO Spaces cheap", "Simple", "Good value"],
                cons=["Self-managed", "Single region mostly"],
                best_for=["DO K8s users", "Small workloads"]
            ),
            # BALANCED - DO + Grafana Cloud
            self._create_option(
                tier="balanced", name="DigitalOcean + Grafana Cloud", provider="digitalocean-k8s",
                metrics="Grafana Cloud Mimir",
                logs="Grafana Cloud Loki",
                traces="Grafana Cloud Tempo",
                alerts="Grafana OnCall",
                ingestion_methods=["Grafana Agent"],
                integrations=["DO metrics"],
                commands=["Deploy Grafana Agent"],
                cost="$40-120/month", complexity="Low",
                pros=["No maintenance", "Good price-quality", "Easy setup"],
                cons=["External service"],
                best_for=["Production DOKS"]
            ),
            # PREMIUM - Datadog
            self._create_option(
                tier="premium", name="DigitalOcean + Datadog", provider="digitalocean-k8s",
                metrics="Datadog",
                logs="Datadog Logs",
                traces="Datadog APM",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog Agent"],
                commands=["Install Datadog Agent"],
                cost="$150-500/month", complexity="Low",
                pros=["Full features", "Excellent DO integration"],
                cons=["Expensive"],
                best_for=["Enterprise DOKS"]
            )
        ]

    # ========== Serverless Tiered Options ==========

    def _lambda_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """AWS Lambda tiered options"""
        return [
            # BUDGET - CloudWatch only
            self._create_option(
                tier="budget", name="CloudWatch Native", provider="aws-lambda",
                metrics="CloudWatch Metrics",
                logs="CloudWatch Logs (standard retention)",
                traces="X-Ray (basic)",
                alerts="CloudWatch Alarms → SNS",
                ingestion_methods=["CloudWatch automatic", "Enable X-Ray in Lambda config"],
                integrations=["Lambda metrics automatic"],
                commands=["aws lambda update-function-configuration --function-name <name> --tracing-config Mode=Active"],
                cost="<$20", complexity="Low",
                pros=["Included with Lambda", "Zero setup", "AWS native"],
                cons=["Limited querying", "Logs expensive at scale", "X-Ray limited"],
                best_for=["Simple Lambda functions", "Low volume"]
            ),
            # BALANCED - CloudWatch + log export
            self._create_option(
                tier="balanced", name="CloudWatch + S3 Export + Honeycomb",
                metrics="CloudWatch Metrics",
                logs="CloudWatch Logs → S3 (via subscription filter)",
                traces="Honeycomb (or X-Ray enhanced)",
                alerts="CloudWatch Alarms + Honeycomb triggers",
                ingestion_methods=["CloudWatch Logs subscription filter to S3"],
                integrations=["Lambda metrics", "S3 for log archival"],
                commands=["aws logs put-subscription-filter", "Export to Honeycomb via firehose"],
                cost="$20-60", complexity="Medium",
                pros=["Cheap long-term logs in S3", "Honeycomb for fast queries", "Best price-quality"],
                cons=["Setup complexity"],
                best_for=["Production Lambda", "Cost optimization"]
            ),
            # PREMIUM - Datadog/New Relic
            self._create_option(
                tier="premium", name="Datadog Serverless",
                metrics="Datadog Metrics",
                logs="Datadog Logs",
                traces="Datadog APM",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog Lambda layer"],
                integrations=["AWS Lambda automatic"],
                commands=["Add Datadog layer to Lambda"],
                cost="$50-200", complexity="Low",
                pros=["Turnkey serverless monitoring", "Auto-tracing", "Great UX"],
                cons=["Expensive"],
                best_for=["Enterprise Lambda", "Complex architectures"]
            )
        ]

    def _cloud_run_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Google Cloud Run tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Cloud Monitoring + Cloud Logging Basic",
                metrics="Cloud Monitoring (free tier)",
                logs="Cloud Logging (basic)",
                traces="Cloud Trace (basic)",
                alerts="Cloud Alerting",
                ingestion_methods=["Google Cloud Operations agent (optional)"],
                integrations=["Cloud Run metrics automatic"],
                commands=["gcloud run services deploy"],
                cost="<$15", complexity="Low",
                pros=["Free monitoring tier generous", "Automatic", "Good for small apps"],
                cons=["Logs get expensive", "Query costs"],
                best_for=["Small Cloud Run apps", "Hobby projects"]
            ),
            # BALANCED - Loki bridge
            self._create_option(
                tier="balanced", name="Cloud Monitoring + Loki Logs",
                metrics="Cloud Monitoring",
                logs="Loki (self-hosted or Grafana Cloud)",
                traces="Cloud Trace",
                alerts="Cloud Alerting",
                ingestion_methods=["Log export to Loki", "Cloud Monitoring native"],
                integrations=["Cloud Run metrics"],
                commands=["Set up log sink to Loki", "Use Cloud Monitoring"],
                cost="$20-50", complexity="Medium",
                pros=["Cheap logs in Loki", "Native metrics", "Good balance"],
                cons=["Two systems to manage"],
                best_for=["Production Cloud Run", "Cost optimization"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="Grafana Cloud",
                metrics="Grafana Cloud",
                logs="Grafana Cloud Loki",
                traces="Grafana Cloud Tempo",
                alerts="Grafana OnCall",
                ingestion_methods=["Grafana Agent"],
                integrations=["GCP logs/metrics bridge"],
                cost="$50-150", complexity="Low",
                pros=["Unified platform", "No maintenance", "Excellent"],
                cons=["Higher cost"],
                best_for=["Production Cloud Run", "Multi-cloud"]
            )
        ]

    # ========== PaaS Tiered Options ==========

    def _heroku_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Heroku tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Heroku Logs + Free Metrics",
                metrics="Heroku Metrics (free tier)",
                logs="Heroku Logplex ( drains to self-hosted Loki)",
                traces="Basic APM (self-instrumented)",
                alerts="Heroku Alerts",
                ingestion_methods=["Log drain to self-hosted Loki"],
                integrations=["Heroku dyno metrics"],
                commands=["heroku drains:add https://loki.example.com/loki/api/v1/push"],
                cost="<$25", complexity="High",
                pros=["Low cost", "Control over logs", "No vendor lock-in for logs"],
                cons=["Self-hosted Loki", "Limited metrics retention"],
                best_for=["Budget Heroku apps", "Privacy needs"]
            ),
            # BALANCED - Papertrail
            self._create_option(
                tier="balanced", name="Heroku + Papertrail/Loki",
                metrics="Heroku Metrics + Librato/New Relic Basic",
                logs="Papertrail or self-hosted Loki",
                traces="APM Basic",
                alerts="Heroku Alerts",
                ingestion_methods=["Log drain", "APM setup"],
                integrations=["Heroku addons"],
                commands=["heroku addons:create papertrail", "or self-host Loki"],
                cost="$25-75", complexity="Medium",
                pros=["Papertrail great for logs", "Reasonable cost", "Easy setup"],
                cons=["Multiple services"],
                best_for=["Production Heroku", "Small teams"]
            ),
            # PREMIUM - Heroku + Datadog
            self._create_option(
                tier="premium", name="Heroku + Datadog",
                metrics="Datadog",
                logs="Datadog Logs (via drain or APM)",
                traces="Datadog APM",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog APM", "Log drain"],
                integrations=["Heroku integration automatic"],
                commands=["heroku addons:create datadog"],
                cost="$75-250", complexity="Low",
                pros=["Turnkey", "Excellent monitoring", "APM included"],
                cons=["Expensive"],
                best_for=["Enterprise Heroku", "Complex apps"]
            )
        ]

    def _vercel_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Vercel tiered options"""
        return [
            # BUDGET - Vercel native
            self._create_option(
                tier="budget", name="Vercel Analytics + Log Drains",
                metrics="Vercel Analytics (free tier)",
                logs="Vercel Logs → self-hosted Loki",
                traces="OpenTelemetry (self-instrumented)",
                alerts="Vercel Notifications",
                ingestion_methods=["Log drain to self-hosted Loki"],
                integrations=["Vercel edge metrics"],
                commands=["Add log drain in Vercel dashboard"],
                cost="<$20", complexity="High",
                pros=["Free Vercel Analytics", "Control logs", "Edge metrics included"],
                cons=["Self-hosted Loki", "Limited traces"],
                best_for=["Vercel hobby projects", "Budget constrained"]
            ),
            # BALANCED - Vercel + Grafana Cloud
            self._create_option(
                tier="balanced", name="Vercel + Grafana Cloud",
                metrics="Vercel Analytics + Grafana Cloud",
                logs="Grafana Cloud Loki (via drain)",
                traces="Grafana Cloud Tempo",
                alerts="Grafana OnCall",
                ingestion_methods=["Log drain", "OTel instrumentation"],
                integrations=["Vercel edge metrics", "Web Vitals"],
                commands=["Configure log drain in Vercel"],
                cost="$20-60", complexity="Medium",
                pros=["Excellent edge monitoring", "Unified dashboard", "Reasonable cost"],
                cons=["Two platforms"],
                best_for=["Production Vercel apps", "E-commerce"]
            ),
            # PREMIUM - Vercel + Datadog
            self._create_option(
                tier="premium", name="Vercel + Datadog",
                metrics="Datadog + Vercel Analytics",
                logs="Datadog Logs",
                traces="Datadog RUM + APM",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog Browser SDK", "APM"],
                integrations=["Vercel integration"],
                commands=["Install Datadog SDK"],
                cost="$75-300", complexity="Low",
                pros=["Full RUM + APM", "Turnkey", "Excellent for frontend"],
                cons=["Expensive"],
                best_for=["Enterprise Vercel", "Customer-facing apps"]
            )
        ]

    def _netlify_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Netlify tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Netlify Functions + Self-Hosted Logs",
                metrics="Netlify Analytics (free)",
                logs="Netlify Logs → self-hosted Loki",
                traces="APM self-instrumented",
                alerts="Netlify Notifications",
                ingestion_methods=["Log drain"],
                commands=["Configure log drain"],
                cost="<$15", complexity="High",
                pros=["Free tier generous", "Full control"],
                cons=["Self-hosted", "Limited APM"],
                best_for=["Netlify hobby sites"]
            ),
            # BALANCED
            self._create_option(
                tier="balanced", name="Netlify + Grafana Cloud",
                metrics="Netlify Analytics + Grafana",
                logs="Grafana Cloud Loki (via drain)",
                traces="Grafana Cloud Tempo",
                alerts="Grafana OnCall",
                ingestion_methods=["Log drain", "OTel"],
                commands=["Set up log drain"],
                cost="$20-50", complexity="Medium",
                pros=["Good balance", "Edge functions monitored"],
                cons=["Setup required"],
                best_for=["Production Netlify"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="Netlify + Datadog",
                metrics="Datadog",
                logs="Datadog Logs",
                traces="Datadog RUM",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog SDK"],
                commands=["Install Datadog"],
                cost="$50-200", complexity="Low",
                pros=["Turnkey RUM monitoring"],
                cons=["Cost"],
                best_for=["Enterprise Netlify"]
            )
        ]

    def _railway_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Railway tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Railway Metrics + Self-Hosted Logs",
                metrics="Railway built-in metrics",
                logs="Self-hosted Loki",
                traces="OpenTelemetry",
                alerts="Railway Notifications",
                ingestion_methods=["Log forwarding"],
                commands=["Set up log forwarder"],
                cost="<$20", complexity="High",
                pros=["Cheap entry", "Good built-in metrics"],
                cons=["Self-hosted logs"],
                best_for=["Railway MVPs"]
            ),
            # BALANCED
            self._create_option(
                tier="balanced", name="Railway + Grafana Cloud",
                metrics="Railway Metrics + Grafana",
                logs="Grafana Cloud Loki",
                traces="Grafana Cloud Tempo",
                alerts="Grafana OnCall",
                ingestion_methods=["Railway log forwarding"],
                commands=["Connect Grafana Cloud"],
                cost="$20-60", complexity="Low",
                pros=["Full observability", "Easy setup"],
                cons=["Cost adds up"],
                best_for=["Production Railway"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="Railway + Datadog",
                metrics="Datadog",
                logs="Datadog Logs",
                traces="Datadog APM",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog agent"],
                commands=["Install Datadog"],
                cost="$50-200", complexity="Low",
                pros=["Turnkey"],
                best_for=["Enterprise Railway"]
            )
        ]

    def _render_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Render tiered options"""
        return self._generic_paas_tiered("Render", ["Render metrics", "Render log drains"])

    def _fly_io_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Fly.io tiered options"""
        return [
            # BUDGET - Fly native
            self._create_option(
                tier="budget", name="Fly.io Metrics + Self-Hosted Logs",
                metrics="flyctl metrics",
                logs="Self-hosted Loki (on Fly.io volume)",
                traces="OTel basic",
                alerts="Fly.io notifications",
                ingestion_methods=["flyctl agent", "Loki on volume"],
                commands=["fly volumes create loki-data", "Deploy Loki with flyctl"],
                cost="<$25", complexity="High",
                pros=["Cheap compute", "Volumes reasonably priced", "Edge network"],
                cons=["Self-hosted logging"],
                best_for=["Fly.io edge apps"]
            ),
            # BALANCED - Fly + Grafana
            self._create_option(
                tier="balanced", name="Fly.io + Grafana Cloud",
                metrics="flyctl metrics + Grafana",
                logs="Grafana Cloud Loki",
                traces="Grafana Cloud Tempo",
                alerts="Grafana OnCall",
                ingestion_methods=["Log forwarding"],
                commands=["Set up log forwarder"],
                cost="$30-80", complexity="Low",
                pros=["Edge monitoring", "Good value"],
                best_for=["Production Fly.io apps"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="Fly.io + Datadog",
                metrics="Datadog",
                logs="Datadog Logs",
                traces="Datadog APM",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog agent"],
                commands=["Install Datadog"],
                cost="$75-250", complexity="Low",
                pros=["Turnkey"],
                best_for=["Enterprise Fly.io"]
            )
        ]

    # ========== VM Tiered Options (European Clouds) ==========

    def _hetzner_vm_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Hetzner VM tiered options - BEST VALUE IN EU"""
        return [
            # BUDGET - All self-hosted on Hetzner
            self._create_option(
                tier="budget", name="Self-Hosted LGTM on Hetzner VM",
                metrics="Prometheus (on CX21 ~€4/mo)",
                logs="Loki (same VM, Storage Box free)",
                traces="Tempo (same VM)",
                alerts="Alertmanager (same VM)",
                ingestion_methods=["node_exporter on all VMs", "Fluent Bit", "OTel"],
                integrations=["hcloud-exporter"],
                commands=["Deploy on dedicated Hetzner VM", "hcloud volume create --size 10 --name monitoring"],
                cost="<€10/month", complexity="High",
                pros=["Incredible value - €10/month for full stack", "No EU egress fees", "Storage Box included free", "Privacy compliant"],
                cons=["Single point of failure", "No HA unless double cost", "Maintenance overhead"],
                best_for=["EU startups", "Hetzner users", "Budget-constrained projects", "Privacy requirements"]
            ),
            # BALANCED - Hetzner VMs + Grafana Cloud
            self._create_option(
                tier="balanced", name="Hetzner Compute + Grafana Cloud",
                metrics="Grafana Cloud Mimir (EU region)",
                logs="Grafana Cloud Loki (EU)",
                traces="Grafana Cloud Tempo (EU)",
                alerts="Grafana OnCall",
                ingestion_methods=["Grafana Agent on each VM"],
                integrations=["hcloud-exporter"],
                commands=["Deploy Grafana Agent", "Connect to Grafana Cloud EU"],
                cost="€25-70/month", complexity="Low",
                pros=["EU data residency", "No monitoring maintenance", "Hetzner compute cheap", "Best price-quality ratio in EU"],
                cons=["External service"],
                best_for=["Production EU infrastructure", "Teams wanting best value"]
            ),
            # PREMIUM - Hetzner + Datadog EU
            self._create_option(
                tier="premium", name="Hetzner + Datadog EU",
                metrics="Datadog (EU region)",
                logs="Datadog Logs (EU)",
                traces="Datadog APM (EU)",
                alerts="Datadog Monitor",
                ingestion_methods=["Datadog Agent"],
                commands=["Install Datadog Agent"],
                cost="€100-400/month", complexity="Low",
                pros=["Full features", "EU region", "Enterprise support"],
                cons=["Expensive"],
                best_for=["Enterprise with EU requirements"]
            )
        ]

    def _scaleway_vm_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Scaleway VM tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Self-Hosted on Scaleway",
                metrics="Prometheus (on DEV1-S ~€8/mo)",
                logs="Loki (to Object Storage)",
                traces="Tempo (to Object Storage)",
                alerts="Alertmanager",
                ingestion_methods=["node_exporter", "Fluent Bit"],
                commands=["Deploy on Scaleway DEV1-S"],
                cost="<€15/month", complexity="High",
                pros=["Good EU value", "Object storage cheap"],
                cons=["Maintenance"],
                best_for=["Scaleway users"]
            ),
            # BALANCED
            self._create_option(
                tier="balanced", name="Scaleway + Grafana Cloud EU",
                metrics="Grafana Cloud",
                logs="Grafana Cloud",
                traces="Grafana Cloud",
                alerts="Grafana OnCall",
                ingestion_methods=["Grafana Agent"],
                cost="€30-80/month", complexity="Low",
                pros=["Paris/Amsterdam regions", "Good value"],
                best_for=["Production Scaleway"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="Scaleway + Datadog EU",
                metrics="Datadog",
                logs="Datadog",
                traces="Datadog APM",
                alerts="Datadog Monitor",
                cost="€100-400/month", complexity="Low",
                pros=["Full features"],
                best_for=["Enterprise"]
            )
        ]

    def _ovh_vm_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """OVHcloud VM tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Self-Hosted LGTM on OVHcloud",
                metrics="Prometheus (on Public Cloud instance)",
                logs="Loki (to OVH Object Storage)",
                traces="Tempo (to OVH Object Storage)",
                alerts="Alertmanager",
                ingestion_methods=["node_exporter", "Fluent Bit"],
                commands=["Deploy on Public Cloud", "Use OVH Logs API"],
                cost="<€20/month", complexity="High",
                pros=["OVH storage very cheap", "Good EU coverage"],
                cons=["Maintenance"],
                best_for=["OVH users", "French market"]
            ),
            # BALANCED
            self._create_option(
                tier="balanced", name="OVHcloud + Grafana Cloud",
                metrics="Grafana Cloud",
                logs="Grafana Cloud",
                traces="Grafana Cloud",
                alerts="Grafana OnCall",
                cost="€30-90/month", complexity="Low",
                pros=["Good EU value", "Paris region"],
                best_for=["Production OVHcloud"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="OVHcloud + Datadog",
                metrics="Datadog",
                logs="Datadog",
                traces="Datadog APM",
                cost="€100-400/month", complexity="Low",
                pros=["Enterprise features"],
                best_for=["Enterprise"]
            )
        ]

    def _exoscale_vm_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Exoscale VM tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Self-Hosted LGTM",
                metrics="Prometheus",
                logs="Loki (to Exoscale POL)",
                traces="Tempo (to POL)",
                alerts="Alertmanager",
                cost="<€20/month", complexity="High",
                pros=["POL storage cheap", "Swiss privacy"],
                best_for=["Exoscale users", "Swiss market"]
            ),
            # BALANCED
            self._create_option(
                tier="balanced", name="Exoscale + Grafana Cloud",
                metrics="Grafana Cloud",
                logs="Grafana Cloud",
                traces="Grafana Cloud",
                cost="€30-80/month", complexity="Low",
                pros=["Good value"],
                best_for=["Production"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="Exoscale + Datadog",
                metrics="Datadog",
                logs="Datadog",
                traces="Datadog APM",
                cost="€100-400/month", complexity="Low",
                best_for=["Enterprise"]
            )
        ]

    def _ionos_vm_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """IONOS VM tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Self-Hosted LGTM",
                metrics="Prometheus",
                logs="Loki",
                traces="Tempo",
                cost="<€20/month", complexity="High",
                best_for=["German market"]
            ),
            # BALANCED
            self._create_option(
                tier="balanced", name="IONOS + Grafana Cloud",
                metrics="Grafana Cloud",
                logs="Grafana Cloud",
                traces="Grafana Cloud",
                cost="€30-80/month", complexity="Low",
                best_for=["Production"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="IONOS + Datadog",
                metrics="Datadog",
                logs="Datadog",
                traces="Datadog APM",
                cost="€100-400/month", complexity="Low",
                best_for=["Enterprise"]
            )
        ]

    def _digitalocean_vm_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """DigitalOcean VM tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Self-Hosted LGTM on DO",
                metrics="Prometheus + do_exporter",
                logs="Loki (to DO Spaces)",
                traces="Tempo (to DO Spaces)",
                alerts="Alertmanager",
                cost="<$25/month", complexity="High",
                pros=["DO Spaces reasonably priced", "do_exporter available"],
                best_for=["DO users"]
            ),
            # BALANCED
            self._create_option(
                tier="balanced", name="DigitalOcean + Grafana Cloud",
                metrics="Grafana Cloud",
                logs="Grafana Cloud",
                traces="Grafana Cloud",
                cost="$30-80/month", complexity="Low",
                pros=["Good integration"],
                best_for=["Production DO"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="DigitalOcean + Datadog",
                metrics="Datadog",
                logs="Datadog",
                traces="Datadog APM",
                cost="$100-400/month", complexity="Low",
                best_for=["Enterprise"]
            )
        ]

    def _vultr_vm_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Vultr VM tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Self-Hosted LGTM on Vultr",
                metrics="Prometheus + vultr_exporter",
                logs="Loki (to Vultr Object Storage)",
                traces="Tempo (to Object Storage)",
                alerts="Alertmanager",
                cost="<$25/month", complexity="High",
                best_for=["Vultr users", "Budget VPS"]
            ),
            # BALANCED
            self._create_option(
                tier="balanced", name="Vultr + Grafana Cloud",
                metrics="Grafana Cloud",
                logs="Grafana Cloud",
                traces="Grafana Cloud",
                cost="$30-80/month", complexity="Low",
                best_for=["Production Vultr"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="Vultr + Datadog",
                metrics="Datadog",
                logs="Datadog",
                traces="Datadog APM",
                cost="$100-400/month", complexity="Low",
                best_for=["Enterprise"]
            )
        ]

    def _linode_vm_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Linode VM tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Self-Hosted LGTM on Linode",
                metrics="Prometheus + linode_exporter",
                logs="Loki (to Linode Object Storage)",
                traces="Tempo (to Object Storage)",
                alerts="Alertmanager",
                cost="<$25/month", complexity="High",
                best_for=["Linode users", "Akamai customers"]
            ),
            # BALANCED
            self._create_option(
                tier="balanced", name="Linode + Grafana Cloud",
                metrics="Grafana Cloud",
                logs="Grafana Cloud",
                traces="Grafana Cloud",
                cost="$30-80/month", complexity="Low",
                best_for=["Production Linode"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="Linode + Datadog",
                metrics="Datadog",
                logs="Datadog",
                traces="Datadog APM",
                cost="$100-400/month", complexity="Low",
                best_for=["Enterprise"]
            )
        ]

    # ========== Docker Compose Tiered Options ==========

    def _docker_compose_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Docker Compose tiered options"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Self-Hosted LGTM in Compose",
                metrics="Prometheus (container)",
                logs="Loki (container, local volume)",
                traces="Tempo (container, local volume)",
                alerts="Alertmanager (container)",
                ingestion_methods=["cAdvisor", "node_exporter on host", "Fluent Bit"],
                integrations=["cAdvisor"],
                commands=["Add monitoring services to docker-compose.yml", "docker-compose up -d prometheus loki tempo"],
                cost="$0", complexity="High",
                pros=["Free", "Full control", "Good for local/dev"],
                cons=["Not production-ready", "No persistence unless configured"],
                best_for=["Local development", "Testing", "Homelabs"]
            ),
            # BALANCED
            self._create_option(
                tier="balanced", name="Docker Compose + Object Storage",
                metrics="Prometheus (container)",
                logs="Loki (container, logs to S3/MinIO)",
                traces="Tempo (container, traces to S3/MinIO)",
                alerts="Alertmanager",
                ingestion_methods=["cAdvisor", "Fluent Bit with S3 output"],
                integrations=["cAdvisor", "S3/MinIO"],
                commands=["Use MinIO for local object storage", "Configure S3 endpoint for production"],
                cost="$10-50", complexity="Medium",
                pros=["Scalable storage", "Production-ready", "Still mostly self-hosted"],
                cons=["Object storage costs", "Some maintenance"],
                best_for=["Small production", "Single-server deployments"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="Grafana Cloud + Docker Compose",
                metrics="Grafana Cloud",
                logs="Grafana Cloud",
                traces="Grafana Cloud",
                alerts="Grafana OnCall",
                ingestion_methods=["Grafana Agent sidecar"],
                cost="$50-150", complexity="Low",
                pros=["No maintenance", "Production ready", "Excellent observability"],
                cons=["External dependency", "Cost"],
                best_for=["Production Docker Compose", "Teams without Ops"]
            )
        ]

    # ========== Generic Fallback ==========

    def _generic_tiered(self, analysis: RepositoryAnalysis) -> List[EventHandlingOption]:
        """Generic tiered options when platform unknown"""
        return [
            # BUDGET
            self._create_option(
                tier="budget", name="Self-Hosted LGTM Stack", provider="generic",
                metrics="Prometheus", logs="Loki", traces="Tempo", alerts="Alertmanager",
                ingestion=["Prometheus scraping", "Fluent Bit", "OTel"],
                integrations=["node_exporter", "app instrumentation"],
                commands=["docker compose -f monitoring-stack.yml up -d"],
                cost="<$50", complexity="High",
                pros=["Open source", "No licensing", "Full control"],
                cons=["Full self-hosting", "High maintenance"],
                best_for=["General use", "Learning", "Self-hosting enthusiasts"]
            ),
            # BALANCED
            self._create_option(
                tier="balanced", name="Grafana Cloud", provider="generic",
                metrics="Grafana Cloud", logs="Grafana Cloud", traces="Grafana Cloud", alerts="Grafana OnCall",
                ingestion=["Grafana Agent", "Grafana Alloy"],
                integrations=["App instrumentation"],
                commands=["Install Grafana Agent", "Connect to Grafana Cloud"],
                cost="$50-150", complexity="Low",
                pros=["No maintenance", "Good value", "Turnkey"],
                cons=["External service", "Learning curve"],
                best_for=["Production", "Multi-cloud", "Best price-quality"]
            ),
            # PREMIUM
            self._create_option(
                tier="premium", name="Datadog or New Relic", provider="generic",
                metrics="Datadog/New Relic", logs="Datadog/New Relic", traces="Datadog/New Relic APM", alerts="Datadog/New Relic",
                ingestion=["Agent installation"],
                integrations=["Full cloud integrations"],
                commands=["Install agent", "Configure dashboards"],
                cost="$200-1000", complexity="Low",
                pros=["Turnkey", "Full features", "Enterprise support"],
                cons=["Expensive", "Vendor lock-in"],
                best_for=["Enterprise", "Fast setup", "No ops team"]
            )
        ]

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
        """Generate event handling setup with tiered options"""
        primary = event_rx.primary
        return {
            "selected_tier": event_rx.selected_tier,
            "primary_option": {
                "name": primary.name,
                "tier": primary.tier,
                "estimated_cost": primary.estimated_monthly_cost,
                "complexity": primary.setup_complexity,
                "metrics": {
                    "source": primary.metrics_source,
                    "ingestion": primary.ingestion_methods[0] if primary.ingestion_methods else "manual"
                },
                "logs": {
                    "source": primary.log_source,
                    "ingestion": primary.ingestion_methods[1] if len(primary.ingestion_methods) > 1 else primary.ingestion_methods[0] if primary.ingestion_methods else "manual"
                },
                "traces": {
                    "source": primary.trace_source,
                    "ingestion": primary.ingestion_methods[2] if len(primary.ingestion_methods) > 2 else primary.ingestion_methods[0] if primary.ingestion_methods else "manual"
                },
                "alerts": {
                    "destination": primary.alert_destination,
                    "integrations": primary.required_integrations
                },
                "setup_commands": primary.setup_commands,
                "pros": primary.pros,
                "cons": primary.cons,
                "best_for": primary.best_for
            },
            "all_options": [
                {
                    "name": opt.name,
                    "tier": opt.tier,
                    "cost": opt.estimated_monthly_cost,
                    "complexity": opt.setup_complexity,
                    "metrics": opt.metrics_source,
                    "logs": opt.log_source,
                    "traces": opt.trace_source,
                    "alerts": opt.alert_destination
                }
                for opt in event_rx.options
            ]
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
        """Generate setup README with tiered options"""
        primary = event_rx.primary

        # Build options comparison table
        options_table = ""
        for i, opt in enumerate(event_rx.options, 1):
            badge = "⭐ RECOMMENDED" if opt.tier == event_rx.selected_tier else ""
            options_table += f"""
### Option {i}: {opt.name} ({opt.tier.upper()}) {badge}

- **Estimated Cost**: {opt.estimated_monthly_cost}
- **Setup Complexity**: {opt.setup_complexity}
- **Metrics**: {opt.metrics_source}
- **Logs**: {opt.log_source}
- **Traces**: {opt.trace_source}
- **Alerts**: {opt.alert_destination}

**Pros**:
{chr(10).join(f'  - {p}' for p in opt.pros)}

**Cons**:
{chr(10).join(f'  - {c}' for c in opt.cons)}

**Best For**: {', '.join(opt.best_for)}

"""

        return f"""# RLC Setup for {analysis.cloud_provider.value.upper()} {analysis.compute_platform.value.upper()}

## Environment Analysis

- **Languages**: {', '.join([l.value for l in analysis.languages])}
- **Frameworks**: {', '.join(analysis.frameworks) if analysis.frameworks else 'None detected'}
- **Compute Platform**: {analysis.compute_platform.value}
- **Cloud Provider**: {analysis.cloud_provider.value}

## Event Handling Options

**Selected Option**: {primary.name} ({primary.tier.upper()})

### All Options (Ranked by Price-Quality Ratio)
{options_table}

## Selected Option Details

### Metrics
- **Source**: {primary.metrics_source}
- **Ingestion**: {primary.ingestion_methods[0] if primary.ingestion_methods else 'manual'}

### Logs
- **Source**: {primary.log_source}
- **Ingestion**: {primary.ingestion_methods[1] if len(primary.ingestion_methods) > 1 else primary.ingestion_methods[0] if primary.ingestion_methods else 'manual'}

### Traces
- **Source**: {primary.trace_source}
- **Ingestion**: {primary.ingestion_methods[2] if len(primary.ingestion_methods) > 2 else primary.ingestion_methods[0] if primary.ingestion_methods else 'manual'}

### Alerts
- **Destination**: {primary.alert_destination}

### Setup Commands
{chr(10).join(f'{i+1}. {cmd}' for i, cmd in enumerate(primary.setup_commands))}

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

2. **Configure event handling**
   Follow the setup commands above for your selected option.

3. **Test the setup**
   ```bash
   python events/ingestion/event-ingester.py --type test --severity low --title "Test event"
   ```

## Changing Option

To change the selected event handling option, re-run the wizard with:
```bash
python tools/wizard/rlc-setup-wizard.py <repo-path> --tier [budget|balanced|premium]
```

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
    parser.add_argument("--tier", choices=["budget", "balanced", "premium"], default="balanced",
                       help="Select price-quality tier (default: balanced)")
    parser.add_argument("--list-options", action="store_true", help="List all event handling options without generating setup")
    parser.add_argument("--show-tier", choices=["budget", "balanced", "premium"],
                       help="Show details for a specific tier")

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
            print(f"❌ Invalid cloud provider: {args.cloud}")
            return

    if args.platform:
        try:
            analysis.compute_platform = ComputePlatform(args.platform.lower())
        except ValueError:
            print(f"❌ Invalid platform: {args.platform}")
            return

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

    # Override tier if specified
    event_rx.selected_tier = args.tier
    primary = next((o for o in event_rx.options if o.tier == args.tier), event_rx.options[0])
    event_rx.primary = primary

    # Show options if requested
    if args.list_options or args.show_tier:
        if args.show_tier:
            options = [o for o in event_rx.options if o.tier == args.show_tier]
        else:
            options = event_rx.options

        print("=" * 70)
        print("EVENT HANDLING OPTIONS (Ranked by Price-Quality Ratio)")
        print("=" * 70)
        print()

        for i, opt in enumerate(options, 1):
            badge = "⭐ DEFAULT" if opt.tier == args.tier else ""
            print(f"{i}. {opt.name} ({opt.tier.upper()}) {badge}")
            print(f"   Cost: {opt.estimated_monthly_cost} | Complexity: {opt.setup_complexity}")
            print(f"   Metrics: {opt.metrics_source}")
            print(f"   Logs: {opt.log_source}")
            print(f"   Traces: {opt.trace_source}")
            print(f"   Alerts: {opt.alert_destination}")
            print()

            if args.show_tier or args.list_options:
                print(f"   ✅ Pros:")
                for pro in opt.pros:
                    print(f"      - {pro}")
                print(f"   ❌ Cons:")
                for con in opt.cons:
                    print(f"      - {con}")
                print(f"   🎯 Best For: {', '.join(opt.best_for)}")
                print()

        if args.list_options:
            print()
            print("To select an option and generate setup:")
            print(f"  python tools/wizard/rlc-setup-wizard.py <repo> --tier [budget|balanced|premium]")
            return

    # Generate prescriptions
    team_prescriber = AgentTeamPrescriber()
    team_rx = team_prescriber.prescribe(analysis)

    # Generate artifacts
    generator = SetupArtifactGenerator()
    artifacts = generator.generate(analysis, event_rx, team_rx, args.output)

    print("=" * 70)
    print(f"SELECTED OPTION: {primary.name} ({primary.tier.upper()})")
    print("=" * 70)
    print()

    print(f"Event Handling Setup:")
    print(f"  Metrics: {primary.metrics_source}")
    print(f"  Logs: {primary.log_source}")
    print(f"  Traces: {primary.trace_source}")
    print(f"  Alerts: {primary.alert_destination}")
    print(f"  Estimated Cost: {primary.estimated_monthly_cost}")
    print(f"  Setup Complexity: {primary.setup_complexity}")
    print()

    print("Agent Team Prescription:")
    print(f"  Core: {len(team_rx.core_agents)} agents")
    print(f"  Observers: {len(team_rx.observer_agents)} agents")
    print(f"  Monitors: {len(team_rx.monitor_agents)} agents")
    print(f"  Alerters: {len(team_rx.alerter_agents)} agents")
    print(f"  Controllers: {len(team_rx.controller_agents)} agents")
    print(f"  Responders: {len(team_rx.responder_agents)} agents")
    print(f"  Optional: {len(team_rx.optional_agents)} agents")
    print(f"  Total: {len(set(team_rx.core_agents + team_rx.observer_agents + team_rx.monitor_agents + team_rx.alerter_agents + team_rx.controller_agents + team_rx.responder_agents))} unique agents")
    print()

    print(f"✅ Setup artifacts generated in: {args.output}")
    print()
    print("Generated files:")
    for name, path in artifacts.items():
        print(f"  {name}: {path}")
    print()

    print("To see all options:")
    print(f"  python tools/wizard/rlc-setup-wizard.py {args.repo_path} --list-options")
    print()
    print("To change tier:")
    print(f"  python tools/wizard/rlc-setup-wizard.py {args.repo_path} --tier [budget|balanced|premium]")


if __name__ == "__main__":
    main()
