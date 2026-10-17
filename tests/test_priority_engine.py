
import pytest

from src.analyzers.priority_engine import (
    calculate_case_priority,
)


def make_evidence(
    event_type="failed_login",
    indicator_id=1,
    source="Test Source",
):
    return {
        "event_id": 1,
        "event_type": event_type,
        "indicator_id": indicator_id,
        "source_name": source,
    }


def test_empty_evidence():
    result = calculate_case_priority([])

    assert result["score"] == 0
    assert result["priority"] == "Low"


def test_failed_login():
    evidence = [make_evidence()]

    result = calculate_case_priority(evidence)

    assert result["score"] == 20
    assert result["priority"] == "Medium"
    assert result["event_count"] == 1


def test_suspicious_transaction():
    evidence = [
        make_evidence(
            event_type="suspicious_transaction"
        )
    ]

    result = calculate_case_priority(evidence)

    assert result["score"] == 35
    assert result["priority"] == "Medium"


def test_duplicate_source_does_not_double_score():
    evidence = [
        make_evidence(source="Source A"),
        make_evidence(source="Source B"),
    ]

    result = calculate_case_priority(evidence)

    assert result["score"] == 20
    assert result["source_count"] == 2
    assert result["event_count"] == 1


def test_additional_indicator():
    evidence = [
        make_evidence(indicator_id=1),
        make_evidence(indicator_id=2),
    ]

    result = calculate_case_priority(evidence)

    assert result["score"] == 25
    assert result["priority"] == "Medium"


def test_multiple_security_events():
    evidence = [
        make_evidence(),
        {
            "event_id": 2,
            "event_type": "account_takeover_signal",
            "indicator_id": 2,
            "source_name": "Test Source",
        },
    ]

    result = calculate_case_priority(evidence)

    assert result["score"] == 55
    assert result["priority"] == "High"
    assert result["event_count"] == 2
