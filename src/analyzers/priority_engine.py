
from collections import defaultdict


EVENT_WEIGHTS = {
    "failed_login": 10,
    "suspicious_transaction": 25,
    "account_takeover_signal": 30,
    "unusual_connection": 5,
}


def calculate_case_priority(evidence):
    """
    Calculate an explainable investigation review priority.

    Evidence must contain event_id, event_type,
    indicator_id and source_name.

    Source count is descriptive, not a claim
    of independent corroboration.
    """

    if not evidence:
        return {
            "score": 0,
            "priority": "Low",
            "reasons": ["No supporting evidence available"],
            "source_count": 0,
            "event_count": 0,
        }

    events = {}
    unique_indicators = set()
    sources = set()

    for item in evidence:
        event_id = item["event_id"]
        event_type = item["event_type"]
        indicator_id = item["indicator_id"]
        source_name = item["source_name"]

        # Avoid scoring the same event more than once.
        events[event_id] = event_type
        unique_indicators.add(indicator_id)

        if source_name:
            sources.add(source_name)

    score = 10  # A verified technical match exists.
    reasons = ["At least one exact indicator match"]

    for event_type in events.values():
        weight = EVENT_WEIGHTS.get(event_type, 0)
        score += weight

        if weight:
            reasons.append(
                f"Security event: {event_type} (+{weight})"
            )

    # A small bonus for additional distinct indicators.
    additional = max(0, len(unique_indicators) - 1)
    indicator_bonus = min(additional * 5, 15)

    if indicator_bonus:
        score += indicator_bonus
        reasons.append(
            f"Additional indicators (+{indicator_bonus})"
        )

    score = min(score, 100)

    if score >= 70:
        priority = "Critical"
    elif score >= 40:
        priority = "High"
    elif score >= 20:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "score": score,
        "priority": priority,
        "reasons": reasons,
        "source_count": len(sources),
        "event_count": len(events),
    }
