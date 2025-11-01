import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry_convert as pc
import requests

# ==========================
# Page config
# ==========================
st.set_page_config(page_title="Analytics & Trends", page_icon="📈", layout="wide")

# ==========================
# Load data
# ==========================
@st.cache_data
def load_data():
    df = pd.read_csv("../data/processed/processed_weather_data.csv", parse_dates=["last_updated"])
    df.columns = [col.strip() for col in df.columns]

    # --- Add continent column dynamically ---
    if 'country' in df.columns:
        def get_continent(country_name):
            try:
                country_alpha2 = pc.country_name_to_country_alpha2(country_name)
                continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
                continent_map = {
                    'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe',
                    'NA': 'North America', 'OC': 'Oceania',
                    'SA': 'South America', 'AN': 'Antarctica'
                }
                return continent_map.get(continent_code, 'Unknown')
            except:
                return 'Unknown'
        df['continent'] = df['country'].apply(get_continent)
    else:
        df['continent'] = 'Unknown'

    return df


df = load_data()

# ==========================
# Detect User Country and Set Defaults
# ==========================
def get_user_country_and_continent():
    try:
        ip_info = requests.get('https://ipinfo.io').json()
        country_code = ip_info.get('country', None)
        if country_code:
            country_name = pc.country_alpha2_to_country_name(country_code)
            continent_code = pc.country_alpha2_to_continent_code(country_code)
            continent_map = {
                'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe', 'NA': 'North America',
                'OC': 'Oceania', 'SA': 'South America', 'AN': 'Antarctica'
            }
            continent_name = continent_map.get(continent_code, 'Unknown')
            return country_name, continent_name
    except:
        pass
    return "India", "Asia"  # fallback

default_country, default_continent = get_user_country_and_continent()

# ==========================
# Sidebar Filters (Like Air Quality)
# ==========================
st.sidebar.header("🌍 Weather Analytics Filters")

# --- Continent Filter ---
continents = sorted(df['continent'].unique())
select_all_cont = st.sidebar.checkbox("Select All Continents", value=False)
if select_all_cont:
    selected_continents = continents
else:
    selected_continents = st.sidebar.multiselect(
        "Select Continent(s)",
        options=continents,
        default=[default_continent] if default_continent in continents else [continents[0]]
    )

# --- Country Filter ---
countries_in_selected_cont = sorted(df[df['continent'].isin(selected_continents)]['country'].unique())
select_all_countries = st.sidebar.checkbox("Select All Countries", value=False)
if select_all_countries:
    selected_countries = countries_in_selected_cont
else:
    selected_countries = st.sidebar.multiselect(
        "Select Country(s)",
        options=countries_in_selected_cont,
        default=[default_country] if default_country in countries_in_selected_cont else [countries_in_selected_cont[0]]
    )

# --- Location Filter ---
locations_in_selected_countries = sorted(df[df['country'].isin(selected_countries)]['location_name'].unique())
select_all_locations = st.sidebar.checkbox("Select All Locations", value=True)
if select_all_locations:
    selected_locations = locations_in_selected_countries
else:
    selected_locations = st.sidebar.multiselect(
        "Select Location(s)",
        options=locations_in_selected_countries,
        default=locations_in_selected_countries
    )

# --- Filtered data ---
filtered_df = df[
    df["continent"].isin(selected_continents) &
    df["country"].isin(selected_countries) &
    df["location_name"].isin(selected_locations)
]

# ==========================
# ✅ Numeric Filters (Keep as-is)
# ==========================

# Temperature
temp_min, temp_max = st.sidebar.slider(
    "🌡️ Temperature Range (°C)", float(df["temperature_celsius"].min()), float(df["temperature_celsius"].max()),
    (float(df["temperature_celsius"].min()), float(df["temperature_celsius"].max()))
)
filtered_df = filtered_df[
    (filtered_df["temperature_celsius"] >= temp_min) &
    (filtered_df["temperature_celsius"] <= temp_max)
]

# Humidity
humidity_min, humidity_max = st.sidebar.slider(
    "💧 Humidity Range (%)", float(df["humidity"].min()), float(df["humidity"].max()),
    (float(df["humidity"].min()), float(df["humidity"].max()))
)
filtered_df = filtered_df[
    (filtered_df["humidity"] >= humidity_min) &
    (filtered_df["humidity"] <= humidity_max)
]

# Wind Speed
wind_min, wind_max = st.sidebar.slider(
    "🌬️ Wind Speed (mph)", float(df["wind_mph"].min()), float(df["wind_mph"].max()),
    (float(df["wind_mph"].min()), float(df["wind_mph"].max()))
)
filtered_df = filtered_df[
    (filtered_df["wind_mph"] >= wind_min) &
    (filtered_df["wind_mph"] <= wind_max)
]


# ===============================
# Sidebar Filters (Continue after Wind)
# ===============================
st.sidebar.markdown("---")
st.sidebar.subheader("🌦️ Additional Weather Filters")

filters = {}

# UV Index Filter
if "uv_index" in df.columns:
    uv_min, uv_max = float(df["uv_index"].min()), float(df["uv_index"].max())
    filters["uv_min"], filters["uv_max"] = st.sidebar.slider(
        "UV Index Range",
        min_value=uv_min,
        max_value=uv_max,
        value=(uv_min, uv_max),
        step=0.1
    )

# Precipitation Filter
if "precip_mm" in df.columns:
    precip_min, precip_max = float(df["precip_mm"].min()), float(df["precip_mm"].max())
    filters["precip_min"], filters["precip_max"] = st.sidebar.slider(
        "Precipitation (mm) Range",
        min_value=precip_min,
        max_value=precip_max,
        value=(precip_min, precip_max),
        step=0.1
    )

# Visibility Filter
if "visibility_km" in df.columns:
    visibility_min, visibility_max = float(df["visibility_km"].min()), float(df["visibility_km"].max())
    filters["visibility_min"], filters["visibility_max"] = st.sidebar.slider(
        "Visibility (km) Range",
        min_value=visibility_min,
        max_value=visibility_max,
        value=(visibility_min, visibility_max),
        step=0.1
    )

# Air Quality Index Filter
if "air_quality_us-epa-index" in df.columns:
    air_min, air_max = int(df["air_quality_us-epa-index"].min()), int(df["air_quality_us-epa-index"].max())
    filters["air_quality_us-epa_min"], filters["air_quality_us-epa_max"] = st.sidebar.slider(
        "Air Quality Index (US EPA)",
        min_value=air_min,
        max_value=air_max,
        value=(air_min, air_max),
        step=1
    )

# ===============================
# Apply filters to DataFrame
# ===============================
# Start with already location-filtered dataframe
# (not resetting to df.copy())
# This ensures all filters work together
# ===============================
# Apply new filters to filtered_df (not df)
if "uv_index" in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df["uv_index"] >= filters["uv_min"]) &
        (filtered_df["uv_index"] <= filters["uv_max"])
    ]

if "precip_mm" in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df["precip_mm"] >= filters["precip_min"]) &
        (filtered_df["precip_mm"] <= filters["precip_max"])
    ]

if "visibility_km" in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df["visibility_km"] >= filters["visibility_min"]) &
        (filtered_df["visibility_km"] <= filters["visibility_max"])
    ]

if "air_quality_us-epa-index" in filtered_df.columns:
    filtered_df = filtered_df[
        (filtered_df["air_quality_us-epa-index"] >= filters["air_quality_us-epa_min"]) &
        (filtered_df["air_quality_us-epa-index"] <= filters["air_quality_us-epa_max"])
    ]



# ==========================
# Page content
# ==========================
st.title("📈 Weather Analytics & Trends")
st.caption("Analyze temperature, humidity, wind, UV, and air quality trends over time.")

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
    # Correlation heatmap
    # -------------------
    st.subheader("📊 Correlation Heatmap")
    numeric_cols = ["temperature_celsius", "humidity", "wind_mph"]
    if "air_quality_us-epa-index" in filtered_df.columns:
        numeric_cols.append("air_quality_us-epa-index")
    if "uv_index" in filtered_df.columns:
        numeric_cols.append("uv_index")
    if "precip_mm" in filtered_df.columns:
        numeric_cols.append("precip_mm")
    if "visibility_km" in filtered_df.columns:
        numeric_cols.append("visibility_km")

    corr = filtered_df[numeric_cols].corr()
    fig_corr = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        title="Correlation between Weather Metrics"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# ==========================
# Extreme Weather Tables with Multi-select
# ==========================
st.markdown("---")
st.subheader("🚨 Extreme Weather Events")

# -------------------
# User settings
# -------------------
top_n = st.slider("Select number of rows to display in top/least metrics:", min_value=3, max_value=20, value=5, step=1)
highlight_country = st.selectbox("Highlight rows for country:", options=["All"] + sorted(filtered_df['country'].unique()))
highlight_location = st.selectbox("Highlight rows for location:", options=["All"] + sorted(filtered_df['location_name'].unique()))

# -------------------
# Helper functions
# -------------------
def format_table(df, value_col, value_name):
    df = df.reset_index(drop=True)
    df.insert(0, "S.No", range(1, len(df)+1))
    if value_col in df.columns:
        df[value_col] = df[value_col].round(2)
        df = df.rename(columns={value_col: value_name})
    return df

def safe_top(df, col, n, ascending=False):
    if col not in df.columns:
        return pd.DataFrame()
    agg_df = df.groupby(['location_name','country'], as_index=False)[col].mean()
    return agg_df.nlargest(n, col) if not ascending else agg_df.nsmallest(n, col)

def highlight_rows(row):
    if (highlight_country != "All" and row['country'] == highlight_country) or \
       (highlight_location != "All" and row['location_name'] == highlight_location):
        return ['background-color: yellow']*len(row)
    else:
        return ['']*len(row)

# -------------------
# Define all metrics and multi-select options
# -------------------
tabs = {
    "All Extremes": ["temperature_celsius","uv_index","humidity","precip_mm","wind_mph","visibility_km","air_quality_us-epa-index"],
    "Hottest / Coldest": ["temperature_celsius"],
    "Highest / Lowest UV": ["uv_index"],
    "Most / Least Humid": ["humidity"],
    "Rainiest / Driest": ["precip_mm"],
    "Windiest / Calmest": ["wind_mph"],
    "Most / Least Visible": ["visibility_km"],
    "Most / Least Polluted": ["air_quality_us-epa-index"]
}

selected_tabs = st.multiselect("Select Extreme Categories to display:", options=list(tabs.keys()), default=["All Extremes"])

# -------------------
# Display tables for selected tabs
# -------------------
for selected_tab in selected_tabs:
    for metric_name, col_name in [
        ("Temperature (°C)", "temperature_celsius"),
        ("UV Index", "uv_index"),
        ("Humidity (%)", "humidity"),
        ("Precipitation (mm)", "precip_mm"),
        ("Wind Speed (mph)", "wind_mph"),
        ("Visibility (km)", "visibility_km"),
        ("AQI (Air Quality Index)", "air_quality_us-epa-index")
    ]:
        if col_name not in tabs[selected_tab] and selected_tab != "All Extremes":
            continue
        top_df = safe_top(filtered_df, col_name, top_n, ascending=False)
        least_df = safe_top(filtered_df, col_name, top_n, ascending=True)

        top_df = format_table(top_df[['location_name','country',col_name]], col_name, metric_name)
        least_df = format_table(least_df[['location_name','country',col_name]], col_name, metric_name)

        st.markdown(f"### 🔝 Top {top_n} {metric_name} Locations")
        st.dataframe(top_df.style.apply(highlight_rows, axis=1))
        st.markdown(f"### 🔽 Bottom {top_n} {metric_name} Locations")
        st.dataframe(least_df.style.apply(highlight_rows, axis=1))
