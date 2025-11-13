import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# -------------------------------
# 📂 Load Data
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("../data/processed/normalized_weather_data.csv", parse_dates=["last_updated"])
    # Ensure column names are clean
    df.columns = [col.strip() for col in df.columns]
    return df

df = load_data()

# -------------------------------
# Load CSS from file
# -------------------------------
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------------------
# 🧭 Sidebar Filters
# -------------------------------
st.sidebar.header("🌍 Global Weather Filters")

# Country filter
countries = df["country"].dropna().unique()

# Add a "Select All" checkbox
select_all = st.sidebar.checkbox("Select All Countries", value=True)

if select_all:
    selected_country = sorted(countries)
else:
    selected_country = st.sidebar.multiselect("Select Country", sorted(countries))


# Date range filter
min_date = df["last_updated"].min()
max_date = df["last_updated"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Parameter selection
parameters = ["temperature_celsius", "humidity", "uv_index", "precip_mm", "pressure_mb"]
selected_parameter = st.sidebar.selectbox("Select Parameter", parameters)

# Optional air quality filter
show_aqi = st.sidebar.checkbox("Show Air Quality Index", value=False)

# -------------------------------
# 🧼 Filter Data Based on Selection
# -------------------------------
mask = (
    df["country"].isin(selected_country) &
    (df["last_updated"].dt.date >= date_range[0]) &
    (df["last_updated"].dt.date <= date_range[1])
)
filtered_df = df[mask]

# -------------------------------
# 🧠 Dashboard Title
# -------------------------------
st.set_page_config(page_title="Global Weather Dashboard", layout="wide")
st.title("🌦️ Global Weather Data Dashboard")
st.markdown(f"Showing weather insights from **{date_range[0]}** to **{date_range[1]}**")

# -------------------------------
# 📌 KPI Cards
# -------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Temp (°C)", f"{filtered_df['temperature_celsius'].mean():.2f}")
col2.metric("Avg Humidity (%)", f"{filtered_df['humidity'].mean():.2f}")
col3.metric("Avg Pressure (mb)", f"{filtered_df['pressure_mb'].mean():.2f}")
col4.metric("Avg UV Index", f"{filtered_df['uv_index'].mean():.2f}")

# -------------------------------
# 🗺️ Global Map Visualization
# -------------------------------
# 🗺️ Global Map Visualization
st.subheader("🌍 Weather Map")

# ✅ Handle negative values for bubble size
size_col = filtered_df[selected_parameter]
min_val = size_col.min()
if min_val <= 0:
    size_col = size_col + abs(min_val) + 1   # shift all values to positive

fig_map = px.scatter_geo(
    filtered_df,
    lat="latitude",
    lon="longitude",
    color=selected_parameter,
    size=size_col,                          # ✅ use shifted positive values
    hover_name="location_name",
    projection="natural earth",
    title=f"Global Distribution of {selected_parameter}",
    color_continuous_scale="RdYlBu_r",
    size_max=20                             # optional: controls max bubble size
)

st.plotly_chart(fig_map, use_container_width=True)

# -------------------------------
# 📈 Trend Analysis
# -------------------------------
st.subheader(f"📈 {selected_parameter.replace('_', ' ').title()} Trends Over Time")

fig_trend = px.line(
    filtered_df,
    x="last_updated",
    y=selected_parameter,
    color="country",
    markers=True,
    title=f"Trend of {selected_parameter} by Country"
)
fig_trend.update_layout(xaxis_title="Date", yaxis_title=selected_parameter)
st.plotly_chart(fig_trend, use_container_width=True)

# -------------------------------
# 🆚 Comparison by Country
# -------------------------------
st.subheader("🆚 Country Comparison")
avg_param = (
    filtered_df.groupby("country")[selected_parameter]
    .mean()
    .reset_index()
    .sort_values(by=selected_parameter, ascending=False)
)

fig_bar = px.bar(
    avg_param,
    x="country",
    y=selected_parameter,
    title=f"Average {selected_parameter} by Country",
    color="country"
)
st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------
# 🌫️ Optional: Air Quality Index
# -------------------------------
if show_aqi:
    st.subheader("🌫️ Air Quality Index (PM2.5)")
    fig_aqi = px.scatter_geo(
        filtered_df,
        lat="latitude",
        lon="longitude",
        color="air_quality_PM2.5",
        hover_name="location_name",
        size="air_quality_PM2.5",
        projection="natural earth",
        title="PM2.5 Distribution",
        color_continuous_scale="OrRd"
    )
    st.plotly_chart(fig_aqi, use_container_width=True)

# -------------------------------
# 📥 Download Section
# -------------------------------
st.sidebar.subheader("📥 Export Data")
st.sidebar.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_weather_data.csv",
    mime="text/csv",
)

# -------------------------------
# 📝 Footer
# -------------------------------
st.markdown("---")
st.caption("📊 Built with Streamlit & Plotly | Global Weather Repository Dataset | © 2025")

