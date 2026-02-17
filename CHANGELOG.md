# Changelog

All notable changes to the AI-First RLC Practices framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Rust and WASM language support in RLC Setup Wizard
- WASM observability recommendations for WebAssembly workloads
- Rust-specific observability guidance (tracing, opentelemetry-rust, prometheus-client)
- AI model advisory documentation with per-agent model recommendations
- Tier-based model selection (Budget, Balanced, Premium)
- Open-source model recommendations with local deployment options
- MCP (Model Context Protocol) server integration guidance
- Agent communication protocol documentation
- Model setup script generation
- QUICKSTART.md for new users
- AGENT-INDEX.md with complete agent catalog
- CONTRIBUTING.md with contribution guidelines
- CHANGELOG.md for version tracking

### Changed
- Enhanced RLC Setup Wizard to ask about tier preference
- Construction Agent now configures AI models and MCP servers
- Improved agent model selection with task-specific recommendations
- Better documentation following SDLC patterns

### Fixed
- Tier selection now respects user's --tier choice
- Fixed CloudProvider enum reference (CLOUD_RUN → GCP)
- Fixed RepositoryAnalysis attribute (repo_path → path)

## [0.2.0] - 2025-01-15

### Added
- Event handling module with ingestion, routing, correlation, and state machine
- Core agents: incident-commander, auto-remediator, post-mortem-writer
- Observer agents: metrics-collector, log-aggregator
- Monitor agents: anomaly-detector
- RLC Gates configuration
- Agent communication protocols
- Runbook templates
- Post-mortem templates
- SLO/SLI definition templates
- RLC Setup Wizard with cloud provider detection
- Price-quality tiered event handling (Budget/Balanced/Premium)
- Construction Agent for infrastructure setup

## [0.1.0] - 2025-01-01

### Added
- Initial RLC framework
- Core documentation (README, CLAUDE-CORE, CLAUDE-SETUP)
- Basic agent templates
- Event handling concepts
- RLC Gates concept

---

## Version Release Notes

### 0.2.x Series

Focus: Agent Intelligence and Integration

**Key Features:**
- Open-source AI model recommendations for all agents
- Three-tier deployment model (Budget/Balanced/Premium)
- MCP server integration for tool access
- Comprehensive documentation

**Model Recommendations:**
- **Budget Tier**: 3-4B parameter models (8GB VRAM)
- **Balanced Tier**: 3-7B parameter models (16GB VRAM)
- **Premium Tier**: 3-14B+ parameter models (32GB VRAM)

**Supported Models:**
- Llama 3.2 (3B, 11B)
- Mistral 7B
- Qwen 2.5 (3B, 7B, 14B, 32B)
- Phi-3.5 (3.8B)
- Mixtral 8x7B (46B MoE)

---

## Release Process

### How to Release

1. Update VERSION file
2. Update CHANGELOG.md with release notes
3. Create git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions will create release

### Version Format

- **Major** (0.X.0): Breaking changes, major new features
- **Minor** (0.x.X): New features, backwards compatible
- **Patch** (0.x.x): Bug fixes, documentation updates

---

## Upcoming Releases

### 0.3.0 (Planned)

- Additional agent types (health-checker, threshold-evaluator, pattern-recognizer, alert-router, runbook-executor, recovery-monitor)
- Enhanced MCP server integrations
- Multi-cloud deployment guides
- Performance benchmarking for agents
- AIOps and predictive capabilities

### 1.0.0 (Future)

- Production-ready agents for all categories
- Complete integration with major observability platforms
- Comprehensive runbook library
- Enterprise deployment guides
- SLA/SLO management tools

---

**Note**: This project is in active development. Releases may include breaking changes until 1.0.0.
