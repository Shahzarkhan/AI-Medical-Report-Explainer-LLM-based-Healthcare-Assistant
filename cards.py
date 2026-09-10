import streamlit as st


def show_dashboard_cards(score, risk, abnormal, normal):

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🟢 Health Score",
            value=f"{score}/100"
        )

    with col2:
        st.metric(
            label="⚠️ Risk Level",
            value=risk
        )

    with col3:
        st.metric(
            label="🔴 Abnormal Tests",
            value=abnormal
        )

    with col4:
        st.metric(
            label="✅ Normal Tests",
            value=normal
        )

    st.divider()