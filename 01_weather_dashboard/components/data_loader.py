# components/data_loader.py
import streamlit as st
import pandas as pd
from pathlib import Path

# ==========================
# 📂 Data Path
# ==========================
DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "climatescope_final_weather.csv"

# ==========================
# 🧠 Global Data Loader
# ==========================
@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(DATA_PATH)

    # --- 🕓 Standardize Date Columns ---
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
        df["Year"] = df["last_updated"].dt.year
        df["Month"] = df["last_updated"].dt.month
        df["Day"] = df["last_updated"].dt.day
    elif "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["Year"] = df["date"].dt.year
        df["Month"] = df["date"].dt.month
        df["Day"] = df["date"].dt.day

    return df

# ==========================
# 🌍 Retrieve Global Data (Shared Across Pages)
# ==========================
def get_global_data():
    """Ensures the global dataset is available and returns it (cached + session-aware)."""
    if "global_data" not in st.session_state:
        with st.spinner("Loading data…"):
            st.session_state["global_data"] = load_data()

    return st.session_state["global_data"]


# ===============================
# 🎨 Styled Sidebar Navigation
# ===============================
st.markdown(
    """
    <style>
    /* Sidebar background with subtle gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000000, #1A1A1A);
        color: #F2F2F2;
        box-shadow: 0 0 15px rgba(255,0,0,0.2);
    }

    /* NAV header - bold red */
    [data-testid="stSidebarNav"]::before {
        content: "🧭 NAVIGATION";
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #FF3B3B !important;
        margin-bottom: 2px;
        display: block;
        margin: 6px 8px 4px 8px !important;
        letter-spacing: 0.6px;
    }

    /* Remove default top spacing from nav list */
    [data-testid="stSidebarNav"] ul:first-of-type {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Hide original app label */
    [data-testid="stSidebarNav"] ul li:first-child div {
        visibility: hidden !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
    }

    /* Nav items */
    [data-testid="stSidebarNav"] ul li div {
        margin: 3px 6px !important;
        padding: 6px 10px !important;
        border-radius: 8px;
        font-size: 15.5px !important;
        background: rgba(255,255,255,0.02) !important;
        color: #F2F2F2 !important;
    }

    /* Reduce list container padding */
    [data-testid="stSidebarNav"] ul {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Hover + active states */
    [data-testid="stSidebarNav"] ul li div:hover {
        background: rgba(255,59,59,0.15) !important;
        color: #FF6666 !important;
        transform: translateX(4px);
    }
    [data-testid="stSidebarNav"] ul li div[data-selected="true"] {
        background: rgba(255,59,59,0.2) !important;
        border-left: 3px solid #FF3B3B !important;
        color: #FF3B3B !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)