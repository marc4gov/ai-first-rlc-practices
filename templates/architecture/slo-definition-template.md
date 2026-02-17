# Service Level Objective (SLO) Definition: [Service Name]

**Service**: [Service Name]
**Version**: 1.0
**Last Updated**: [Date]
**Owner**: [Team/Owner]

## Overview

[Brief description of what this service does and why SLOs matter]

## SLI Definitions

### SLI 1: [Availability / Success Rate]

**Description**: [What this measures]
**Measurement**: [How it's calculated]
**Unit**: [Percentage]

**Query**:
```promql
# Prometheus query example
sum(rate(http_requests_total{status!~"5.."}[5m])) /
sum(rate(http_requests_total[5m]))
```

**Data Source**: [Where data comes from]

### SLI 2: [Latency]

**Description**: [What this measures]
**Measurement**: [Percentile]
**Unit**: [Milliseconds/Seconds]

**Query**:
```promql
# Prometheus query example
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

**Percentiles Tracked**:
- p50: [Target value]
- p95: [Target value]
- p99: [Target value]

### SLI 3: [Throughput / Quality Metric]

**Description**: [What this measures]
**Measurement**: [How it's calculated]
**Unit**: [Requests per second / Other]

**Query**:
```promql
# Prometheus query example
sum(rate(service_requests_total[5m]))
```

## SLO Targets

| SLI | Target | Measurement Window | Rolling/Calendar |
|-----|--------|-------------------|------------------|
| [Availability] | [99.9%] | 30 days | Rolling |
| [Latency p95] | [< 200ms] | 30 days | Rolling |
| [Latency p99] | [< 500ms] | 30 days | Rolling |
| [Quality] | [99%] | Calendar month | Calendar |

## Error Budget Calculation

### Budget per Period

| Period | Budget | Allowable Downtime | Notes |
|--------|--------|-------------------|-------|
| Day | [0.1%] | [86.4 seconds] | |
| Week | [0.1%] | [10.1 minutes] | |
| Month (30 days) | [0.1%] | [43.2 minutes] | |
| Quarter (90 days) | [0.1%] | [129.6 minutes] | |

### Current Budget Status

| Period | Budget | Used | Remaining | Status |
|--------|--------|------|-----------|--------|
| Today | [0.1%] | [%] | [%] | [OK/Warning/Burned] |
| This Week | [0.1%] | [%] | [%] | [OK/Warning/Burned] |
| This Month | [0.1%] | [%] | [%] | [OK/Warning/Burned] |

## Error Budget Policy

### When Budget is Healthy (> 50% remaining)
- ✅ Normal feature development allowed
- ✅ Standard deployment cadence
- ✅ Capacity planning work

### When Budget is Depleting (25-50% remaining)
- ⚠️ Increase testing rigor
- ⚠️ Add monitoring for new features
- ⚠️ Consider reliability in architecture reviews
- ⚠️ Reduce deployment frequency for high-risk changes

### When Budget is Critical (10-25% remaining)
- 🚨 Feature freeze for risky changes
- 🚨 Reliability-focused sprint required
- 🚨 All deployments require SRE review
- 🚨 Prioritize incident prevention work

### When Budget is Burned (< 10% or exhausted)
- 🛑 Complete feature freeze
- 🛑 Only critical fixes and reliability work allowed
- 🛑 Post-mortem for all incidents required
- 🛑 Executive review of reliability plan

### Budget Recovery Criteria

Budget is considered recovered when:
- [ ] 30-day rolling SLO returns to target
- [ ] No SLO breaches in past 7 days
- [ ] Error budget > 50% remaining
- [ ] No critical reliability debt identified

## Alerting Policy

### Critical Alerts (Page Immediately)
| Condition | Threshold | Window | Alert Name |
|-----------|-----------|--------|------------|
| [Burn rate] | [14.4x] | [1 hour] | [SLO-burn-critical] |
| [SLO breach] | [Impending] | [5 hours] | [SLO-breach-warning] |

### Warning Alerts (Create Ticket)
| Condition | Threshold | Window | Alert Name |
|-----------|-----------|--------|------------|
| [Elevated burn rate] | [6x] | [6 hours] | [SLO-burn-elevated] |
| [Trend warning] | [1x sustained] | [3 days] | [SLO-trend-warning] |

### Multi-Window, Multi-Burn-Rate Alerting

Following Google SRE methodology:

| Window | Burn Rate | Action | Alert Type |
|--------|-----------|--------|------------|
| 1 hour | 14.4x | Page | Critical |
| 6 hours | 6x | Page | High |
| 3 days | 1x | Ticket | Warning |

## Exclusions and Caveats

### Planned Maintenance
- [Description of what's excluded]
- [How maintenance is tracked]
- [Notification requirements]

### Force Majeure
- [Events beyond control]
- [How these are handled]

### Measurement Limitations
- [Known gaps in measurement]
- [Data quality issues]
- [Edge cases not covered]

## Dependencies

### Upstream Dependencies
| Service | SLO | Impact if degraded |
|---------|-----|-------------------|
| [Service 1] | [99.9%] | [Our SLO cannot exceed theirs] |
| [Service 2] | [99.95%] | [Our SLO cannot exceed theirs] |

### Downstream Consumers
| Service | Their Requirements | Our Commitment |
|---------|-------------------|----------------|
| [Service 1] | [99.9%] | [We meet this] |
| [Service 2] | [99.5%] | [We exceed this] |

## Reporting

### Dashboard Links
- [SLO Dashboard]: [URL]
- [Error Budget Dashboard]: [URL]
- [SLO Burn Rate]: [URL]

### Regular Reports
- **Weekly**: [What's reported, who receives it]
- **Monthly**: [What's reported, who receives it]
- **Quarterly**: [What's reported, who receives it]

## Change History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| [Date] | 1.0 | Initial SLO definition | [Name] |

---

## Appendix: SLO Calculation Examples

### Rolling Window Calculation
```
For a 30-day rolling SLO:
1. Collect all requests over the past 30 days
2. Count "good" requests (met success criteria)
3. Divide good by total
4. Compare to target (e.g., 99.9%)

Example:
- Total requests: 1,000,000,000
- Good requests: 999,000,000
- SLO achieved: 99.9%
- Target: 99.9%
- Status: ✅ Meeting target
```

### Error Budget Calculation
```
Error Budget = 100% - SLO Target

For 99.9% SLO:
- Error Budget = 100% - 99.9% = 0.1%

In time (30 days = 43,200 minutes):
- Error Budget = 43,200 × 0.001 = 43.2 minutes

If you've used 20 minutes of downtime:
- Budget Remaining = 43.2 - 20 = 23.2 minutes
- Budget Remaining % = 23.2 / 43.2 = 53.7%
```

### Burn Rate Calculation
```
Burn Rate = Current Error Rate / Error Budget Rate

Example:
- SLO: 99.9% (0.1% error budget)
- Current error rate: 1.44%
- Burn Rate = 1.44% / 0.1% = 14.4x

At 14.4x burn rate:
- Entire 30-day budget consumed in: 30 / 14.4 = 2.08 days
- Time to exhaust = 2.08 days if trend continues
```

---

**Remember**: SLOs are agreements with users about service quality. Set targets based on what users need and what you can deliver, not arbitrary numbers. And always protect your error budget—it's the limit of how unreliable you're allowed to be.
