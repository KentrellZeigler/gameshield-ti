
from unittest.mock import patch

from src.analyzers.case_scoring import get_scored_cases


def test_scored_case():
    sample_cases = [
        {
            "case_id": 1,
            "title": "Test Investigation",
            "priority": "Medium",
            "status": "Open",
        }
    ]

    sample_evidence = [
        {
            "event_id": 1,
            "event_type": "failed_login",
            "indicator_id": 1,
            "source_name": "Test Source",
        }
    ]

    with (
        patch(
            "src.analyzers.case_scoring.get_automated_cases",
            return_value=sample_cases,
        ),
        patch(
            "src.analyzers.case_scoring.get_case_evidence",
            return_value=sample_evidence,
        ),
    ):
        results = get_scored_cases()

    assert len(results) == 1
    assert results[0]["calculated_score"] == 20
    assert results[0]["recommended_priority"] == "Medium"
    assert results[0]["evidence_count"] == 1
    assert results[0]["source_count"] == 1
    assert results[0]["priority"] == "Medium"


def test_no_cases():
    with patch(
        "src.analyzers.case_scoring.get_automated_cases",
        return_value=[],
    ):
        assert get_scored_cases() == []
