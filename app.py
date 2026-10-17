

import pandas as pd
import streamlit as st

from src.database.queries import (
    get_dashboard_metrics,
    get_threat_indicators,
    get_investigations,
)

from src.analyzers.correlation import correlate_ip_indicators

from src.analyzers.case_scoring import get_scored_cases

from src.analyzers.case_generator import (
    get_automated_cases,
    get_case_evidence,
)


from src.analyzers.case_management import (
    update_case,
    add_case_note,
    get_case_notes,
    get_case_audit_history,
)

from src.reports.report_generator import (
    generate_case_report,
)


st.set_page_config(
    page_title="GameShield TI",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ GameShield TI")
st.caption("Gaming Threat Intelligence Platform")

st.info(
    "DEVELOPMENT ENVIRONMENT — Includes synthetic "
    "investigation data and externally sourced OTX indicators. "
    "Listed indicators are not independently verified."
)


st.sidebar.title("Navigation")


page = st.sidebar.radio(
    "Select a page",
    [
        "Overview",
        "Threat Intelligence",
        "Investigations",
        "Correlations",
    ],
)


if st.sidebar.button("Refresh Data"):
    st.rerun()


try:
    if page == "Overview":

        st.header("Security Intelligence Overview")

        metrics = get_dashboard_metrics()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Known Indicators",
            metrics["indicators"]
        )

        col2.metric(
            "Active Investigations",
            metrics["investigations"]
        )

        col3.metric(
            "High-Confidence Indicators",
            metrics["high_confidence"]
        )

        st.divider()

        st.subheader("Intelligence Summary")

        indicators = get_threat_indicators()

        if indicators:
            df = pd.DataFrame(indicators)

            st.bar_chart(
                df["confidence"].value_counts()
                .sort_index()
                .rename_axis("Confidence Score")
            )
        else:
            st.info("No threat intelligence records found.")


    elif page == "Threat Intelligence":

        st.header("Threat Intelligence Records")

        indicators = get_threat_indicators()

        if indicators:
            df = pd.DataFrame(indicators)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                f"Displaying {len(df)} threat indicators."
            )

        else:
            st.info("No intelligence records available.")


    

    elif page == "Correlations":

        st.header("Threat Intelligence Correlations")

        st.caption(
            "Matching intelligence indicators against "
            "simulated multiplayer security events."
        )

        matches = correlate_ip_indicators()

        if matches:
            df = pd.DataFrame(matches)

            st.metric("Total Matches", len(df))

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

            st.warning(
                "These matches represent investigative leads. "
                "Synthetic events do not indicate real malicious activity."
            )

        else:
            st.info("No matching indicators found.")

    
    elif page == "Investigations":

        st.header("Investigation Cases")

        # SECTION 1: Existing investigations
        st.subheader("Existing Investigations")

        investigations = get_investigations()

        if investigations:
            df = pd.DataFrame(investigations)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                f"Displaying {len(df)} investigations."
            )

        else:
            st.info("No investigations have been created.")

        # SECTION 2: Automatically generated cases
        st.divider()

        st.subheader("Automatically Generated Cases")

        auto_cases = get_automated_cases()

        if auto_cases:
            cases_df = pd.DataFrame(auto_cases)

            st.metric(
                "Automated Cases",
                len(cases_df)
            )

            st.dataframe(
                cases_df,
                use_container_width=True,
                hide_index=True,
            )

            st.divider()

            st.subheader("Investigation Evidence Viewer")

            case_options = {
                f"Case {case['case_id']} — {case['title']}":
                case["case_id"]
                for case in auto_cases
            }

            selected_label = st.selectbox(
                "Select an investigation",
                options=list(case_options.keys()),
            )

            selected_case_id = case_options[selected_label]

            evidence = get_case_evidence(selected_case_id)

            if evidence:
                evidence_df = pd.DataFrame(evidence)

                st.metric(
                    "Evidence Records",
                    len(evidence_df)
                )

                st.dataframe(
                    evidence_df,
                    use_container_width=True,
                    hide_index=True,
                )

                st.info(
                    "Evidence identifies an indicator match. "
                    "It does not independently prove "
                    "malicious activity."
                )

            else:
                st.info(
                    "No evidence has been attached "
                    "to this investigation."
                )


        else:
            st.info(
                "No automatically generated cases found."
            )

        st.divider()

        st.subheader("Investigation Priority Analysis")

        st.caption(
            "Calculated review priorities based on "
            "the evidence currently attached to each case."
        )

        scored_cases = get_scored_cases()

        if scored_cases:
            summary = pd.DataFrame([
                {
                    "Case ID": case["case_id"],
                    "Title": case["title"],
                    "Assigned Priority": case["priority"],
                    "Recommended Priority":
                        case["recommended_priority"],
                    "Score": case["calculated_score"],
                    "Evidence Records": case["evidence_count"],
                    "Sources": case["source_count"],
                }
                for case in scored_cases
            ])

            st.dataframe(
                summary,
                use_container_width=True,
                hide_index=True,
            )

            st.subheader("Scoring Explanation")

            selected_case = st.selectbox(
                "Choose a case to review its score",
                options=scored_cases,
                format_func=lambda case:
                    f"Case {case['case_id']} - {case['title']}",
                key="priority_case_selector",
            )

            st.metric(
                "Calculated Review Score",
                selected_case["calculated_score"],
            )

            st.write(
                "Recommended priority:",
                selected_case["recommended_priority"],
            )

            st.write("Reasons:")

            for reason in selected_case["scoring_reasons"]:
                st.write(f"- {reason}")

            st.info(
                "This is a rule-based review recommendation, "
                "not a verified threat severity assessment. "
                "Existing case priorities are unchanged."
            )

        else:
            st.info("No automated cases available to score.")


        st.divider()
        st.subheader("Analyst Case Management")

        st.caption(
            "Update investigation status, assign priority, "
            "and document investigative findings."
        )

        if auto_cases:

            case_lookup = {
                case["case_id"]: case
                for case in auto_cases
            }

            selected_id = st.selectbox(
                "Select a case to manage",
                options=list(case_lookup.keys()),
                format_func=lambda case_id:
                    f"Case {case_id} - "
                    f"{case_lookup[case_id]['title']}",
                key="management_case_selector",
            )

            current_case = case_lookup[selected_id]

            st.markdown("#### Update Investigation")

            with st.form(
                f"update_case_form_{selected_id}"
            ):

                status = st.selectbox(
                    "Investigation Status",
                    [
                        "Open",
                        "In Progress",
                        "Closed",
                    ],
                    index=[
                        "Open",
                        "In Progress",
                        "Closed",
                    ].index(current_case["status"]),
                )

                priority = st.selectbox(
                    "Assigned Priority",
                    [
                        "Low",
                        "Medium",
                        "High",
                        "Critical",
                    ],
                    index=[
                        "Low",
                        "Medium",
                        "High",
                        "Critical",
                    ].index(current_case["priority"]),
                )

                save_changes = st.form_submit_button(
                    "Save Investigation Changes"
                )

            if save_changes:
                updated = update_case(
                    selected_id,
                    status,
                    priority,
                )

                if updated:
                    st.success(
                        "Investigation updated successfully."
                    )
                    st.rerun()
                else:
                    st.error("Investigation not found.")

            st.divider()
            st.markdown("#### Add Investigation Note")

            with st.form(
                f"case_note_form_{selected_id}",
                clear_on_submit=True,
            ):

                author = st.text_input(
                    "Analyst Name",
                    max_chars=100,
                )

                note_text = st.text_area(
                    "Investigation Note",
                    height=150,
                    placeholder=(
                        "Document your investigation "
                        "findings and next steps..."
                    ),
                )

                save_note = st.form_submit_button(
                    "Save Investigation Note"
                )

            if save_note:
                try:
                    add_case_note(
                        selected_id,
                        author,
                        note_text,
                    )

                    st.success(
                        "Investigation note saved."
                    )
                    st.rerun()

                except ValueError as error:
                    st.error(str(error))

            st.divider()
            st.markdown("#### Investigation Notes History")

            notes = get_case_notes(selected_id)

            if notes:
                notes_df = pd.DataFrame(notes)

                st.dataframe(
                    notes_df,
                    use_container_width=True,
                    hide_index=True,
                )

            else:
                st.info(
                    "No notes have been recorded "
                    "for this investigation."
                )

            # ============================================
            # SECTION 6: AUDIT HISTORY
            # ============================================

            st.divider()

            st.subheader("Investigation Audit History")

            audit_history = get_case_audit_history(
                selected_id
            )

            if audit_history:
                audit_df = pd.DataFrame(audit_history)

                st.dataframe(
                    audit_df,
                    use_container_width=True,
                    hide_index=True,
                )

                st.caption(
                    "Audit records show changes recorded "
                    "since logging was introduced."
                )

            else:
                st.info(
                    "No audit history has been recorded "
                    "for this investigation."
                )

            st.divider()

            st.subheader("Investigation Report")

            report_text = generate_case_report(
                selected_id
            )

            st.download_button(
                label="Download Investigation Report",
                data=report_text,
                file_name=(
                    f"gameshield_case_{selected_id}.md"
                ),
                mime="text/markdown",
                key=f"download_report_{selected_id}",
            )

            st.caption(
                "The report includes case details, "
                "supporting evidence, analyst notes, "
                "review scoring, and audit history."
            )

        else:
            st.info(
                "No automated cases available for management."
            )



except Exception:
    import logging

    logging.exception(
        "GameShield TI encountered an application error."
    )

    st.error(
        "An application error occurred. "
        "Please check the application logs "
        "or contact the administrator."
    )