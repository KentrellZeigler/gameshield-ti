
# Case Study: Synthetic Multiplayer Authentication Investigation

## Executive Summary

This case study demonstrates how GameShield TI correlates
a simulated game-security event against stored threat
intelligence and organizes the result for analyst review.

All game events, accounts, and associated investigative
findings in this case study are synthetic.

## Investigation Objective

Determine whether a simulated authentication event
matches an intelligence indicator and whether the
available evidence warrants further investigation.

## Initial Evidence

- Simulated account: SIM_PLAYER_001
- Event type: failed_login
- Source IP: 192.0.2.10
- Intelligence source: GameShield Synthetic Lab
- Correlation method: Exact IPv4 match

192.0.2.10 is a documentation-reserved address and
does not represent real malicious infrastructure.

## Investigative Methodology

### 1. Intelligence Collection

The platform maintains source-attributed threat
indicators in PostgreSQL.

### 2. Security Event Analysis

Synthetic authentication activity is stored as
structured security events.

### 3. Indicator Correlation

The correlation engine compares the event's source IP
against the stored IPv4 indicators.

PostgreSQL's host() function normalizes INET values
for exact comparison.

### 4. Case Creation

The platform generates an automated investigation case
when the security event matches a stored indicator.

### 5. Evidence Preservation

The matching indicator and related event are attached
to the case with a source reference.

### 6. Review Priority Assessment

The experimental priority engine assigns:

- Exact indicator match: 10 points
- Failed login event: 10 points
- Total review score: 20
- Recommended priority: Medium

The recommendation is for analyst review and is
not a confirmed malicious activity severity rating.

## Findings

The simulated failed-login event matched a synthetic
intelligence indicator.

The system created an investigative lead and retained
the associated evidence.

This finding does not establish that an actual account
was compromised or that a real attacker was involved.

## Limitations

- Event data is simulated.
- Intelligence is synthetic in this case study.
- No confirmed attacker attribution.
- No real game infrastructure was assessed.
- Review-priority weights are not empirically calibrated.

## Recommended Next Steps

In a properly authorized real-world investigation:

1. Review additional authentication events.
2. Compare the activity against account history.
3. Evaluate the reputation and freshness of indicators.
4. Examine relevant authorized security telemetry.
5. Document corroborating or contradictory evidence.
6. Escalate only when findings support further action.

## Skills Demonstrated

- Threat intelligence correlation
- SQL investigation queries
- IP address normalization
- Evidence management
- Security event analysis
- Automated case creation
- Explainable investigation scoring
- Investigative report writing
```
