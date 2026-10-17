
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="GameShield TI",
    page_icon="🛡️",
    layout="wide"
)

st.title("GameShield TI")
st.caption("Gaming Threat Intelligence Platform")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a page",
    ["Overview", "Threat Intelligence", "Investigations"]
)

if page == "Overview":
    st.header("Security Intelligence Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Known Indicators", 0)
    col2.metric("Active Investigations", 0)
    col3.metric("High-Priority Threats", 0)

    st.info(
        "System initialized. Intelligence data "
        "sources have not yet been configured."
    )

elif page == "Threat Intelligence":
    st.header("Threat Intelligence Records")

    st.dataframe(
        pd.DataFrame(
            columns=[
                "Indicator",
                "Type",
                "Source",
                "Confidence"
            ]
        ),
        use_container_width=True
    )

elif page == "Investigations":
    st.header("Active Investigations")

    st.info("No investigations have been created.")
