# Incident Post-Mortem: [Incident Title]

**Incident ID**: INC-YYYYMMDD-XXX
**Date**: [Date of incident]
**Duration**: [Start time] to [End time] ([Total duration])
**Severity**: [SEV0/SEV1/SEV2/SEV3/SEV4]
**Incident Commander**: [Name]
**Author**: [Name]
**Status**: [Draft/Final]

## Executive Summary

[2-3 sentence summary of what happened, impact, and resolution]

## Timeline

| Time (UTC) | Duration | Description | Owner |
|------------|----------|-------------|-------|
| [HH:MM] | [0 min] | [Event detected/trigger] | [Who/what] |
| [HH:MM] | [+X min] | [What happened] | [Who/what] |
| [HH:MM] | [+X min] | [What happened] | [Who/what] |
| [HH:MM] | [+X min] | [Resolution] | [Who/what] |
| [HH:MM] | [+X min] | [Incident closed] | [Who/what] |

## Impact Assessment

### Customer Impact
- **Affected Services**: [List services]
- **Affected Customers**: [All/Specific regions/Specific customers]
- **User-Visible Symptoms**: [What customers experienced]
- **Duration of Impact**: [How long customers were affected]

### Business Impact
- **Revenue Impact**: [Estimated if applicable]
- **SLA Impact**: [Yes/No - details if yes]
- **Compliance Impact**: [Yes/No - details if yes]
- **Stakeholder Notifications**: [Who was notified]

## Root Cause Analysis

### The Problem
[Description of the actual root cause]

### How It Happened
[Step-by-step explanation of the chain of events that led to the incident]

### Why It Happened
[Deeper analysis of why the root cause existed]

### Contributing Factors
- [Factor 1]: [Description]
- [Factor 2]: [Description]
- [Factor 3]: [Description]

### 5 Whys Analysis
1. Why did [incident] happen?
   → [Answer 1]
2. Why did [Answer 1] happen?
   → [Answer 2]
3. Why did [Answer 2] happen?
   → [Answer 3]
4. Why did [Answer 3] happen?
   → [Answer 4]
5. Why did [Answer 4] happen?
   → [Root cause]

## What Went Well

- [ ] [Good thing 1]: [Description of what worked well]
- [ ] [Good thing 2]: [Description of what worked well]
- [ ] [Good thing 3]: [Description of what worked well]

## What Could Be Improved

- [ ] [Improvement area 1]: [Description of what didn't go well]
- [ ] [Improvement area 2]: [Description of what didn't go well]
- [ ] [Improvement area 3]: [Description of what didn't go well]

## Action Items

### Preventive Actions (Prevent Recurrence)
| ID | Action | Owner | Priority | Due Date | Status |
|----|--------|-------|----------|----------|--------|
| ACT-1 | [Description] | [Owner] | P0/P1/P2/P3 | [Date] | Open/Done |
| ACT-2 | [Description] | [Owner] | P0/P1/P2/P3 | [Date] | Open/Done |

### Detection Improvements
| ID | Action | Owner | Priority | Due Date | Status |
|----|--------|-------|----------|----------|--------|
| ACT-3 | [Description] | [Owner] | P0/P1/P2/P3 | [Date] | Open/Done |
| ACT-4 | [Description] | [Owner] | P0/P1/P2/P3 | [Date] | Open/Done |

### Process Improvements
| ID | Action | Owner | Priority | Due Date | Status |
|----|--------|-------|----------|----------|--------|
| ACT-5 | [Description] | [Owner] | P0/P1/P2/P3 | [Date] | Open/Done |
| ACT-6 | [Description] | [Owner] | P0/P1/P2/P3 | [Date] | Open/Done |

## Resolution Summary

### What Fixed It
[Description of the actual fix that resolved the incident]

### Verification Steps
- [ ] [Verification step 1]: [Result]
- [ ] [Verification step 2]: [Result]
- [ ] [Verification step 3]: [Result]

## Metrics and Graphs

### Key Metrics During Incident
| Metric | Before | During | After |
|--------|--------|--------|-------|
| [Metric 1] | [Value] | [Value] | [Value] |
| [Metric 2] | [Value] | [Value] | [Value] |
| [Metric 3] | [Value] | [Value] | [Value] |

### Dashboard Snapshots
- [Link to dashboard with annotated timeline]
- [Link to relevant graphs]

## Appendix

### Logs and Traces
- [Link to relevant log queries]
- [Link to relevant traces]

### Related Documents
- [Related incident 1]: [Link]
- [Related incident 2]: [Link]
- [Architecture doc]: [Link]
- [Runbook]: [Link]

### Review and Approval

| Role | Name | Approval |
|------|------|----------|
| Incident Commander | [Name] | [Signature/Date] |
| Technical Lead | [Name] | [Signature/Date] |
| Manager | [Name] | [Signature/Date] |

---

## Notes

[Additional context, nuance, or information that doesn't fit elsewhere]

---

**Blameless Post-Mortem Culture Reminder**: This document focuses on systems and processes, not individuals. The goal is learning and improvement, not blame.
