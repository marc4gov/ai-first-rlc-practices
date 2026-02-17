# [Service Name] - [Failure Mode] Runbook

**Runbook ID**: RB-YYYYMMDD-001
**Service**: [Service Name]
**Failure Mode**: [What can go wrong]
**Severity**: [Typical SEV level when this occurs]
**Owner**: [Team/Responsible Party]
**Last Updated**: [Date]

## Overview

[Brief description of this failure mode and when to use this runbook]

## Trigger Conditions

This runbook is triggered when:
- [Alert/condition that triggers this runbook]
- [Additional conditions]
- [Monitoring dashboards to check]

## Symptoms

### What You'll See
- [User-visible symptoms]
- [Alert patterns]
- [Dashboard indicators]

### What to Check First
1. [Critical health check]
2. [Most likely failure point]
3. [Secondary indicator]

## Detection and Verification

### Confirm the Issue
```bash
# Commands to verify the issue is occurring
[Command 1]
[Command 2]
```

### Dashboard Links
- [Primary dashboard]: [URL]
- [Secondary dashboard]: [URL]
- [Related service dashboard]: [URL]

## Diagnosis Steps

### Step 1: [First diagnostic area]
**Check**: [What to check]
**Command**: [Commands to run]
**Expected**: [What normal looks like]
**If Abnormal**: [What it means]

### Step 2: [Second diagnostic area]
**Check**: [What to check]
**Command**: [Commands to run]
**Expected**: [What normal looks like]
**If Abnormal**: [What it means]

### Step 3: [Third diagnostic area - root cause]
**Check**: [What to check]
**Command**: [Commands to run]
**Expected**: [What normal looks like]
**If Abnormal**: [What it means]

## Mitigation Procedures

### Immediate Actions (Do These First)

#### Action 1: [Most common fix]
```bash
[Commands to execute]
```
**Expected Result**: [What should happen]
**Verification**: [How to confirm it worked]
**Rollback**: [How to undo if it makes things worse]

#### Action 2: [Secondary fix]
```bash
[Commands to execute]
``]
**Expected Result**: [What should happen]
**Verification**: [How to confirm it worked]

### Escalation Criteria

Escalate immediately if:
- [Condition requiring escalation]
- [Another condition]
- [Time threshold: e.g., no improvement after 15 minutes]

**Escalation Path**:
1. [First escalation]: [Role/Person] - [Contact method]
2. [Second escalation]: [Role/Person] - [Contact method]
3. [Management escalation]: [Role/Person] - [Contact method]

## Recovery Verification

### Health Checks
- [ ] [Health check 1]: [Command/URL]
- [ ] [Health check 2]: [Command/URL]
- [ ] [Health check 3]: [Command/URL]

### Metrics to Monitor
- [Metric 1]: [Expected value after recovery]
- [Metric 2]: [Expected value after recovery]
- [Metric 3]: [Expected value after recovery]

### Duration Monitoring
Monitor for [X] minutes to ensure stability:
- [ ] [X] minutes elapsed
- [ ] No regression detected
- [ ] SLO compliance verified

## Resolution

### When to Declare Resolved
Declare resolution when ALL of:
- [ ] All health checks passing
- [ ] Metrics returned to baseline
- [ ] No customer complaints in [X] minutes
- [ ] SLO compliance verified

### Post-Incident Actions
- [ ] Update incident timeline
- [ ] Document any deviations from this runbook
- [ ] Flag runbook for update if procedures were unclear
- [ ] Create improvement tickets for gaps discovered

## Prevention

### Long-term Fixes Required
- [ ] [Fix 1]: [Link to ticket]
- [ ] [Fix 2]: [Link to ticket]
- [ ] [Fix 3]: [Link to ticket]

### Monitoring Gaps Identified
- [ ] [Gap 1]: [What to add]
- [ ] [Gap 2]: [What to add]

### Related Runbooks
- [Related runbook 1]: [Link]
- [Related runbook 2]: [Link]

## Appendix

### Useful Commands
```bash
# [Purpose]
[command]

# [Purpose]
[command]
```

### Reference Links
- [Architecture documentation]: [Link]
- [Service documentation]: [Link]
- [Runplaybooks directory]: [Link]
- [On-call schedule]: [Link]

### Runbook History
| Date | Change | Author |
|------|--------|--------|
| [Date] | [Change description] | [Author] |
| [Date] | [Change description] | [Author] |

---

**Remember**: This runbook is a living document. Update it when:
- Procedures change
- New symptoms are discovered
- Fix steps don't work as documented
- New tools or commands become available
