import streamlit as st

def set_page_style():
    """
    Apply custom CSS and page styling for consistent look & feel.
    """
    st.markdown(
        """
    <style>
    /* Main background */
    .reportview-container {
        background-color: #f5f5f5;
    }
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #ffffff;
    }
    /* Card titles and text */
    .stMetricValue, .stMetricLabel {
        color: #333333;
    }
    /* Remove default padding for wide layout */
    .main .block-container {
        padding-top: 1rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
        unsafe_allow_html=True
    )
