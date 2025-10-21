import streamlit as st
import pandas as pd
import plotly.express as px
from components.filters import filter_panel
from components.utils import load_data

# Page config
st.set_page_config(page_title="Station Explorer", page_icon="📍", layout="wide")

# Load data
df = load_data()

# Sidebar filters (reuse component)
filters = filter_panel(df)
filtered_df = df.copy()

# Apply continent, country, and location filters
filtered_df = filtered_df[
    filtered_df["continent"].isin(filters["continent"]) &
    filtered_df["country"].isin(filters["country"]) &
    filtered_df["location_name"].isin(filters["location"])
]

# Additional search box (optional)
search_term = st.sidebar.text_input("🔎 Search station/location", "")
if search_term:
    filtered_df = filtered_df[
        filtered_df["location_name"].str.contains(search_term, case=False, na=False)
        | filtered_df["country"].str.contains(search_term, case=False, na=False)
    ]

# Page title
st.title("📍 Station Explorer")
st.caption("Explore weather station data interactively.")

# Summary KPIs at the top
if not filtered_df.empty:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Avg Temp (°C)", round(filtered_df["temperature_celsius"].mean(), 2))
    col2.metric("Avg Humidity (%)", round(filtered_df["humidity"].mean(), 2))
    col3.metric("Avg Wind (mph)", round(filtered_df["wind_mph"].mean(), 2))
    if "air_quality_us-epa-index" in filtered_df.columns:
        col4.metric("Avg US AQI Index", round(filtered_df["air_quality_us-epa-index"].mean(), 2))
    else:
        col4.metric("Avg US AQI Index", "N/A")
else:
    st.warning("No stations found with these filters.")

# Table
st.subheader("🗃️ Station List")

if filtered_df.empty:
    st.info("No matching records found.")
else:
    # Columns to show in table
    table_cols = [
        "country", "location_name", "latitude", "longitude",
        "last_updated", "temperature_celsius", "humidity", "wind_mph"
    ]
    if "air_quality_us-epa-index" in filtered_df.columns:
        table_cols.append("air_quality_us-epa-index")

    # Sortable and scrollable table
    st.dataframe(
        filtered_df[table_cols]
        .sort_values(["country", "location_name"])
        .reset_index(drop=True),
        use_container_width=True,
    )

# Optional: Select station for detail view
st.subheader("📊 Station Detail View")

selected_station = st.selectbox(
    "Select a station for trend visualization",
    options=["None"] + sorted(filtered_df["location_name"].unique())
)

if selected_station != "None":
    station_data = filtered_df[filtered_df["location_name"] == selected_station]

    st.markdown(f"### 🌤️ {selected_station}")
    col1, col2 = st.columns(2)
    with col1:
        fig_temp = px.line(
            station_data,
            x="last_updated",
            y="temperature_celsius",
            title="Temperature Trend (°C)",
            markers=True
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    with col2:
        fig_hum = px.line(
            station_data,
            x="last_updated",
            y="humidity",
            title="Humidity Trend (%)",
            markers=True
        )
        st.plotly_chart(fig_hum, use_container_width=True)
