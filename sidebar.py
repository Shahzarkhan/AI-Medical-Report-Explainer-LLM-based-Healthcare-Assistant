import streamlit as st

def show_sidebar():

    with st.sidebar:

        st.title("🏥 Dashboard")

        st.success("🟢 AI System Online")

        st.markdown("---")

        st.markdown("### Features")

        page = st.radio(
            "",
            [
                "📄 AI Medical Report",
                "📊 Compare Reports"
            ]
        )

        st.markdown("---")

        st.info("Developed by Shahzar Khan 🚀")

    return page