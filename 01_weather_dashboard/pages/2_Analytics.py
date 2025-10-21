import streamlit as st
import pandas as pd
import plotly.express as px
from components.filters import filter_panel
from components.utils import load_data

# Page config
st.set_page_config(page_title="Analytics & Trends", page_icon="📈", layout="wide")

# Load data
df = load_data()

# Sidebar filters
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
st.title("📈 Weather Analytics & Trends")
st.caption("Analyze temperature, humidity, wind, and air quality trends over time.")

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    # -------------------
    # Time series of Temperature
    # -------------------
    st.subheader("🌡️ Temperature Trends Over Time")
    fig_temp = px.line(
        filtered_df,
        x="last_updated",
        y="temperature_celsius",
        color="country",
        title="Temperature Trend (°C) by Country",
        labels={"temperature_celsius": "Temperature (°C)", "last_updated": "Date"},
        template="plotly_white"
    )
    st.plotly_chart(fig_temp, use_container_width=True)

    # -------------------
    # Humidity Trends
    # -------------------
    st.subheader("💧 Humidity Trends Over Time")
    fig_hum = px.line(
        filtered_df,
        x="last_updated",
        y="humidity",
        color="country",
        title="Humidity Trend (%) by Country",
        labels={"humidity": "Humidity (%)", "last_updated": "Date"},
        template="plotly_white"
    )
    st.plotly_chart(fig_hum, use_container_width=True)

    # -------------------
    # Wind Distribution
    # -------------------
    st.subheader("🌬️ Wind Speed Distribution")
    fig_wind = px.box(
        filtered_df,
        x="country",
        y="wind_mph",
        color="country",
        title="Wind Speed Variation (mph) by Country",
        labels={"wind_mph": "Wind Speed (mph)"},
        template="plotly_white"
    )
    st.plotly_chart(fig_wind, use_container_width=True)

    # -------------------
    # Air Quality Comparison (if available)
    # -------------------
    if "air_quality_us-epa-index" in filtered_df.columns:
        st.subheader("🌫️ Air Quality Comparison")
        fig_aqi = px.bar(
            filtered_df.groupby("country")["air_quality_us-epa-index"].mean().reset_index(),
            x="country",
            y="air_quality_us-epa-index",
            title="Average US AQI by Country",
            color="air_quality_us-epa-index",
            color_continuous_scale="reds",
            template="plotly_white"
        )
        st.plotly_chart(fig_aqi, use_container_width=True)

    # -------------------
    # Optional: correlation heatmap
    # -------------------
    st.subheader("📊 Correlation Heatmap")
    numeric_cols = ["temperature_celsius", "humidity", "wind_mph"]
    if "air_quality_us-epa-index" in filtered_df.columns:
        numeric_cols.append("air_quality_us-epa-index")

    corr = filtered_df[numeric_cols].corr()
    fig_corr = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        title="Correlation between Weather Metrics"
    )
    st.plotly_chart(fig_corr, use_container_width=True)


# -------------------
# Top 4 Metrics Tables
# -------------------
st.markdown("---")
st.subheader("🚨 Extreme Weather Events")

# Only consider rows with numeric values
df_temp = filtered_df.dropna(subset=["temperature_celsius"])
df_aqi = filtered_df.dropna(subset=["air_quality_us-epa-index"]) if "air_quality_us-epa-index" in filtered_df.columns else pd.DataFrame()

# Compute top locations
top_hot = df_temp.nlargest(5, "temperature_celsius")[["location_name", "country", "temperature_celsius"]].copy()
top_cold = df_temp.nsmallest(5, "temperature_celsius")[["location_name", "country", "temperature_celsius"]].copy()

if not df_aqi.empty:
    top_danger = df_aqi.nlargest(5, "air_quality_us-epa-index")[["location_name", "country", "air_quality_us-epa-index"]].copy()
    top_safe = df_aqi.nsmallest(5, "air_quality_us-epa-index")[["location_name", "country", "air_quality_us-epa-index"]].copy()
else:
    top_danger = pd.DataFrame(columns=["location_name", "country", "air_quality_us-epa-index"])
    top_safe = pd.DataFrame(columns=["location_name", "country", "air_quality_us-epa-index"])

# Format S.No and values
def format_table(df, value_col, value_name):
    df = df.reset_index(drop=True)
    df.insert(0, "S.No", range(1, len(df)+1))
    if value_col in df.columns:
        df[value_col] = df[value_col].round(2)
        df = df.rename(columns={value_col: value_name})
    return df

top_hot = format_table(top_hot, "temperature_celsius", "Temperature (°C)")
top_cold = format_table(top_cold, "temperature_celsius", "Temperature (°C)")
top_danger = format_table(top_danger, "air_quality_us-epa-index", "AQI (Air Quality Index)")
top_safe = format_table(top_safe, "air_quality_us-epa-index", "AQI (Air Quality Index)")

# First row: Top Hot and Top Cold
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.markdown("**🔥 Top 5 Hottest Locations**")
    st.table(top_hot)
with row1_col2:
    st.markdown("**❄️ Top 5 Coldest Locations**")
    st.table(top_cold)

# Second row: Top Dangerous AQI and Top Safe AQI
row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.markdown("**😷 Top 5 Most Polluted Locations**")
    st.table(top_danger)
with row2_col2:
    st.markdown("**✅ Top 5 Most Non-Polluted Locations**")
    st.table(top_safe)