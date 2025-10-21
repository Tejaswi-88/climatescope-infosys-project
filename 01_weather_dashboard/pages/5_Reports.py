import streamlit as st
import pandas as pd
import plotly.express as px
from components.filters import filter_panel
from components.utils import load_data

# Page config
st.set_page_config(page_title="Reports & Insights", page_icon="📝", layout="wide")

# Load data
df = load_data()

# Sidebar filters (reuse)
filters = filter_panel(df)
filtered_df = df.copy()

# Apply filters
filtered_df = filtered_df[
    filtered_df["continent"].isin(filters["continent"]) &
    filtered_df["country"].isin(filters["country"]) &
    filtered_df["location_name"].isin(filters["location"])
]

# Temperature filter
filtered_df = filtered_df[
    (filtered_df["temperature_celsius"] >= filters["temp_min"]) &
    (filtered_df["temperature_celsius"] <= filters["temp_max"])
]

# Humidity filter
filtered_df = filtered_df[
    (filtered_df["humidity"] >= filters["humidity_min"]) &
    (filtered_df["humidity"] <= filters["humidity_max"])
]

# Wind filter
filtered_df = filtered_df[
    (filtered_df["wind_mph"] >= filters["wind_min"]) &
    (filtered_df["wind_mph"] <= filters["wind_max"])
]

# Page content
st.title("📝 Reports & Key Insights")
st.caption("Quick overview of extreme conditions, top stations, and notable findings.")

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    # -------------------
    # KPI Cards
    # -------------------
    st.subheader("🌡️ Key Metrics")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Hottest Station", 
                filtered_df.loc[filtered_df["temperature_celsius"].idxmax()]["location_name"])
    col2.metric("Coldest Station", 
                filtered_df.loc[filtered_df["temperature_celsius"].idxmin()]["location_name"])
    col3.metric("Highest Humidity", 
                filtered_df.loc[filtered_df["humidity"].idxmax()]["location_name"])
    col4.metric("Highest Wind Speed", 
                filtered_df.loc[filtered_df["wind_mph"].idxmax()]["location_name"])

    # -------------------
    # Top 10 Hottest / Coldest Stations
    # -------------------
    st.subheader("🔥 Top 10 Hottest Stations")
    top_hot = filtered_df.sort_values("temperature_celsius", ascending=False).head(10)
    st.dataframe(top_hot[["country", "location_name", "temperature_celsius", "humidity", "wind_mph"]])

    st.subheader("❄️ Top 10 Coldest Stations")
    top_cold = filtered_df.sort_values("temperature_celsius").head(10)
    st.dataframe(top_cold[["country", "location_name", "temperature_celsius", "humidity", "wind_mph"]])

    # -------------------
    # Top 10 Windy Stations
    # -------------------
    st.subheader("💨 Top 10 Windy Stations")
    top_wind = filtered_df.sort_values("wind_mph", ascending=False).head(10)
    st.dataframe(top_wind[["country", "location_name", "temperature_celsius", "humidity", "wind_mph"]])

    # -------------------
    # Optional: Air Quality Insights
    # -------------------
    if "air_quality_us-epa-index" in filtered_df.columns:
        st.subheader("🌫️ Top 10 Worst Air Quality (US AQI)")
        top_aqi = filtered_df.sort_values("air_quality_us-epa-index", ascending=False).head(10)
        st.dataframe(top_aqi[["country", "location_name", "air_quality_us-epa-index"]])

        fig_aqi = px.bar(
            top_aqi,
            x="location_name",
            y="air_quality_us-epa-index",
            color="air_quality_us-epa-index",
            title="Top 10 Worst AQI Stations",
            color_continuous_scale="reds"
        )
        st.plotly_chart(fig_aqi, use_container_width=True)

    # -------------------
    # Download filtered data
    # -------------------
    st.subheader("📥 Download Filtered Data")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="filtered_weather_data.csv",
        mime="text/csv"
    )
