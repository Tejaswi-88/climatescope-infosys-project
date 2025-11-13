# app.py
import streamlit as st
import pandas as pd
from components.data_loader import get_global_data

# ===========================
# 🌍 App Configuration
# ===========================
st.set_page_config(
    page_title="Global Weather Tracker",
    page_icon="🌦️",
    layout="wide"
)

# ===========================
# 🎨 Custom Styles
# ===========================
st.markdown(
    """
    <style>
    /* Page background */
    .main {
        background-color: #0E1117;
        color: #FFFFFF;
        font-family: "Segoe UI", sans-serif;
    }

    /* Center page title */
    .main h1 {
        text-align: center;
        color: #FF4B4B;
        text-shadow: 1px 1px 5px rgba(0,0,0,0.5);
    }

    /* Subtitles */
    .main h2, .main h3 {
        color: #FF6666;
        margin-top: 25px;
    }

    /* Info box */
    .stInfo {
        background-color: #1C1F26;
        border-left: 4px solid #FF6F00;
        padding: 15px 20px;
        border-radius: 6px;
        color: #FFFFFF;
    }

    /* Expander style */
    .stExpander {
        background-color: #121519;
        border-radius: 8px;
        padding: 10px;
        color: #FFFFFF;
    }

    /* Dataframe table */
    .stDataFrame div[data-testid="stDataFrame"] {
        background-color: #121519;
        color: #FFFFFF;
    }

    /* Markdown links */
    a {
        color: #FF6666;
        text-decoration: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===========================
# 📦 Load Global Dataset
# ===========================
df = get_global_data()  # cached loader

# ===========================
# ✅ Landing Page Header
# ===========================
st.title("🌦️ Global Weather Tracker")
st.markdown(
    """
Welcome to **ClimateScope**, a comprehensive platform for global weather exploration, trend analysis, and climate insights.

This platform allows you to:
- Filter data by continent, country, and location using the sidebar.
- Analyze key metrics like temperature, humidity, wind, UV, precipitation, visibility, and air quality.
- Explore historical and current trends across different timeframes (daily, weekly, monthly, yearly).

"""
)

st.markdown("---")

# ===========================
# 🧰 Technology Stack
# ===========================
st.subheader("🧰 Technology Stack")
st.markdown(
"""
- **Frontend & Visualization:** Streamlit, Plotly, Altair
- **Backend & Data Handling:** Python, Pandas, NumPy
- **Data Storage:** CSV / Processed weather datasets
- **APIs:** Public weather data sources
- **Machine Learning / Analytics:** Optional for predictive insights
"""
)

# ===========================
# 🔄 Project Flow
# ===========================
st.subheader("🔄 Project Flow / How it Works")
st.markdown("""
1. **Data Loading:** Weather datasets are loaded once globally and cached for efficiency.
2. **Sidebar Filtering:** Users select continents, countries, or locations to filter data.
3. **Dashboard Views:** Aggregation by continent/country/location, and time aggregation by daily/weekly/monthly/yearly.
4. **Trend Analysis:** Visualizations of temperature, humidity, wind speed, UV index, precipitation, visibility, and air quality.
5. **Extreme Events & Forecasts:** Identify hotspots and critical conditions per location.
6. **Cross-Page Sharing:** Data is shared across all pages to ensure consistent views and filters.
""")

# ===========================
# 🏠 Page Descriptions
# ===========================
st.subheader("📄 Pages & Features")

st.markdown("""
- **Home – Global Weather Insights:** Overview of global data, summary metrics, and dataset preview.
- **Weather Trend Analysis:** Detailed trends of temperature, humidity, wind, UV, and air quality.
- **Air Quality Insights:** Explore AQI trends and identify polluted regions.
- **Sun & Moon Explorer:** Sunrise, sunset, moonrise, and moon phases by location.
- **Analytics:** Interactive dashboards with selectable aggregation and timeframes.
- **Crop Suitability:** Identify crops suitable for locations based on climate conditions.
""")

# ===========================
# ⭐ Key Features
# ===========================
st.subheader("⭐ Key Features Implemented")
st.markdown("""
- Interactive filters for **continent, country, and location**.
- **Dynamic aggregation**: daily, weekly, monthly, yearly.
- **Visualizations:** Line charts, trend analysis, choropleth maps.
- **Extreme event tables** for temperature, UV, wind, precipitation, visibility, and AQI.
- **Responsive design:** All charts and tables are interactive and adaptive.
- **Centralized data caching:** Fast performance across pages.
""")

# ===========================
# 🔍 Dataset Preview
# ===========================
with st.expander("🔍 Preview Weather Dataset"):
    st.dataframe(df.head(10), use_container_width=True)

st.info(
    """
Navigate through the sidebar pages to explore each feature:

- Home
- Trends & Analytics
- Extreme Events
- Forecasts
- Crop Suitability
"""
)
