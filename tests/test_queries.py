
from src.database.queries import (
    get_dashboard_metrics,
    get_threat_indicators,
    get_investigations,
)


def test_dashboard_metrics():
    metrics = get_dashboard_metrics()

    assert metrics["indicators"] >= 5
    assert metrics["investigations"] >= 2
    assert metrics["high_confidence"] >= 3


def test_threat_indicators():
    indicators = get_threat_indicators()

    assert len(indicators) >= 5
    assert "indicator_value" in indicators[0]
    assert "confidence" in indicators[0]


def test_investigations():
    investigations = get_investigations()

    assert len(investigations) >= 2
    assert "title" in investigations[0]
    assert "status" in investigations[0]
