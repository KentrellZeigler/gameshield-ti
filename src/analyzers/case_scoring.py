
from src.analyzers.case_generator import (
    get_automated_cases,
    get_case_evidence,
)
from src.analyzers.priority_engine import (
    calculate_case_priority,
)


def get_scored_cases(conn=None):
    """
    Retrieve automated cases with calculated
    priority recommendations.

    Does not modify database records.
    """
    cases = get_automated_cases(conn)
    scored_cases = []

    for case in cases:
        evidence = get_case_evidence(case["case_id"], conn)

        assessment = calculate_case_priority(evidence)

        scored_cases.append({
            **case,
            "calculated_score": assessment["score"],
            "recommended_priority": assessment["priority"],
            "evidence_count": len(evidence),
            "source_count": assessment["source_count"],
            "event_count": assessment["event_count"],
            "scoring_reasons": assessment["reasons"],
        })

    return scored_cases
