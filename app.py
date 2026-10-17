

import pandas as pd
import streamlit as st

from src.database.queries import (
    get_dashboard_metrics,
    get_threat_indicators,
    get_investigations,
)

st.set_page_config(
    page_title="GameShield TI",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ GameShield TI")
st.caption("Gaming Threat Intelligence Platform")
st.warning("DEMO ENVIRONMENT — All threat data is synthetic.")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a page",
    [
        "Overview",
        "Threat Intelligence",
        "Investigations",
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


    elif page == "Investigations":

        st.header("Investigation Cases")

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

except Exception:
    st.error(
        "Unable to retrieve data from PostgreSQL. "
        "Verify that the database server is running "
        "and check the application terminal for errors."
    )
    st.exception(__import__("sys").exc_info()[1])
