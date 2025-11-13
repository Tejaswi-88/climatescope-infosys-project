# app.py
import streamlit as st
import pandas as pd
from components.data_loader import get_global_data  # <-- import from your data loader

# ===========================
# 🌍 App Configuration
# ===========================
st.set_page_config(
    page_title="Global Weather Tracker",
    page_icon="🌦️",
    layout="wide"
)

# ===========================
# 📦 Load Global Dataset Once
# ===========================
df = get_global_data()  # Cached loading handled in data_loader.py

# Initialize filters in session state (shared across pages)
for key in ["continent", "country", "location"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ===========================
# ✅ Welcome Section
# ===========================
st.title("🌦️ Global Weather Tracker")
st.write(
    """
    The **Global Weather Tracker** provides an interactive platform to explore, visualize, 
    and analyze global climate and weather data across continents, countries, and locations.
    This multi-page Streamlit app allows users to gain insights into temperature trends, 
    precipitation patterns, and climatic anomalies over time.
    """
)

st.markdown("---")

# ===========================
# 🧠 Project Overview
# ===========================
st.header("🧩 Project Overview")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ⚙️ Technical Stack")
    st.markdown("""
    - **Frontend:** Streamlit (Python-based UI framework)
    - **Data Processing:** Pandas, NumPy
    - **Visualization:** Plotly, Altair, Matplotlib
    - **Backend/Data Source:** Pre-processed CSV files 
    - **Geo Data:** pycountry-convert (for continent-country mapping)
    """)

with col2:
    st.markdown("### 🎯 Project Goals")
    st.markdown("""
    - Build an interactive global weather dashboard  
    - Enable real-time data filtering by **continent**, **country**, and **location**
    - Visualize multi-month and multi-region climate variations  
    - Support data-driven climate insights and reports  
    - Facilitate comparative climate analysis across regions
    """)


st.markdown("---")

# ===========================
# 🔄 Dataflow & Workflow
# ===========================
st.header("🔄 Dataflow & Workflow")

st.markdown("""
1. **Data Loading:**  
   The pre-processed dataset (`.csv file`) is loaded once using `get_global_data()` in `data_loader.py`.  
   Caching ensures efficient reuse across all app pages.

2. **Filtering Logic:**  
   Sidebar filters (Continent → Country → Location) are applied globally using `st.session_state`.

3. **Page Interconnection:**  
   Each page (Home, Trends, Analysis, Reports) uses the shared dataset and applied filters to display relevant insights.

4. **Visualization & Insights:**  
   Users can explore temperature trends, anomalies, precipitation patterns, and more through interactive charts.

5. **Dynamic Interaction:**  
   Visual components update automatically as filters are changed in the sidebar, ensuring seamless data exploration.
""")


# ===========================
# 🚀 Features & Improvements
# ===========================
st.header("🚀 Features & Planned Improvements")

st.markdown("""
### ✅ Current Features
- 🌍 Global dataset integration with continent and country mapping  
- 📅 Month-based weather trend visualization  
- 📈 Interactive charts and summary metrics  
- 📊 Dynamic filtering across pages  
- 💡 Dataset caching for optimized performance  

### 🔧 Upcoming Improvements
- 🧠 AI-driven weather anomaly detection  
- 🕒 Time-series forecasting (ARIMA/LSTM models)  
- 📑 Advanced report generation (PDF/Excel exports)  
- 🗺️ Interactive world map with layered heatmaps  
- 🔍 Search functionality for countries and cities  
- 📡 Integration with live weather APIs for real-time updates  
""")

st.markdown("---")

# ===========================
# 📊 Dataset Summary
# ===========================
st.subheader("📊 Dataset Summary")
st.write(f"**Rows:** {df.shape[0]:,} | **Columns:** {df.shape[1]}")

with st.expander("🔍 Preview Data"):
    st.dataframe(df.head(), use_container_width=True)

st.info(
    "Navigate to other pages (like Home, Trends, or Analysis) using the sidebar — "
    "the dataset and selected filters will be shared automatically across the app."
)
