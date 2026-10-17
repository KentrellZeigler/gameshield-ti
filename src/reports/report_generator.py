
from datetime import datetime, timezone

from src.analyzers.case_generator import (
    get_automated_cases,
    get_case_evidence,
)
from src.analyzers.case_management import (
    get_case_notes,
    get_case_audit_history,
)
from src.analyzers.priority_engine import (
    calculate_case_priority,
)


def safe_text(value):
    """Render untrusted text safely in report lines."""
    if value is None:
        return "Not recorded"

    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def generate_case_report(case_id, conn=None):
    """Generate a Markdown report for one investigation."""

    cases = get_automated_cases(conn)

    case = next(
        (item for item in cases
         if item["case_id"] == case_id),
        None,
    )

    if case is None:
        raise ValueError("Investigation case not found.")

    evidence = get_case_evidence(case_id, conn)
    notes = get_case_notes(case_id, conn)
    history = get_case_audit_history(case_id, conn)

    assessment = calculate_case_priority(evidence)

    generated_at = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )

    lines = [
        "# GameShield TI — Investigation Report",
        "",
        f"**Case ID:** {case_id}",
        f"**Title:** {safe_text(case['title'])}",
        f"**Status:** {safe_text(case['status'])}",
        f"**Assigned Priority:** {safe_text(case['priority'])}",
        f"**Generated At (UTC):** {generated_at}",
        "",
        "## Investigation Priority Analysis",
        "",
        f"**Review Score:** {assessment['score']}/100",
        f"**Recommended Priority:** {assessment['priority']}",
        "",
        "### Scoring Reasons",
        "",
    ]

    for reason in assessment["reasons"]:
        lines.append(f"- {safe_text(reason)}")

    lines.extend([
        "",
        "## Supporting Evidence",
        "",
        "| Event ID | Event Type | Source IP | "
        "Indicator | Intelligence Source |",
        "|---|---|---|---|---|",
    ])

    for item in evidence:
        lines.append(
            f"| {item['event_id']} "
            f"| {safe_text(item['event_type'])} "
            f"| {safe_text(item['source_ip'])} "
            f"| {safe_text(item['indicator_value'])} "
            f"| {safe_text(item['source_name'])} |"
        )

    if not evidence:
        lines.append("| — | No evidence | — | — | — |")

    lines.extend([
        "",
        "## Analyst Notes",
        "",
    ])

    if notes:
        for note in notes:
            lines.extend([
                f"### Note {note['note_id']}",
                "",
                f"**Author:** {safe_text(note['author'])}",
                f"**Created:** {note['created_at']}",
                "",
                safe_text(note["note_text"]),
                "",
            ])
    else:
        lines.append("No analyst notes recorded.")

    lines.extend([
        "",
        "## Audit History",
        "",
        "| Timestamp | Actor | Action | Previous | New |",
        "|---|---|---|---|---|",
    ])

    for item in history:
        lines.append(
            f"| {item['created_at']} "
            f"| {safe_text(item['actor'])} "
            f"| {safe_text(item['action'])} "
            f"| {safe_text(item['old_value'])} "
            f"| {safe_text(item['new_value'])} |"
        )

    if not history:
        lines.append("| — | — | No history recorded | — | — |")

    lines.extend([
        "",
        "## Assessment Limitations",
        "",
        "- This platform is a development environment.",
        "- Game-security events used here are synthetic.",
        "- A matching indicator is not proof of malicious activity.",
        "- Review scores use experimental, rule-based weights.",
        "- Analyst identities are not authenticated.",
        "- Historical actions before audit logging are unavailable.",
        "- This report is not a forensically verified record.",
        "",
    ])

    return "\n".join(lines)
