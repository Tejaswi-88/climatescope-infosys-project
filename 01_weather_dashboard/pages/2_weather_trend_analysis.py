import streamlit as st 
import pandas as pd
import pycountry_convert as pc
import plotly.express as px
import requests

# ============================
# Page Config
# ============================
st.set_page_config(page_title="Weather Condition Analysis", layout="wide")
st.title("🌤️ Global Weather Condition Analysis Dashboard")
st.markdown("Explore weather conditions across time, geography, and atmospheric features.")

# ============================
# Helper Functions
# ============================

def country_to_continent(country_name):
    """Map country to continent."""
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        return {
            'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe', 'NA': 'North America',
            'OC': 'Oceania', 'SA': 'South America', 'AN': 'Antarctica'
        }[continent_code]
    except:
        return "Unknown"


def get_user_country_and_continent():
    """Detect user location using IP (fallback: India, Asia)."""
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
    return "India", "Asia"

# ============================
# Load Data
# ============================
@st.cache_data
def load_data():
    df = pd.read_csv("../data/processed/processed_weather_data.csv", parse_dates=["last_updated"])
    df["continent"] = df["country"].apply(country_to_continent)
    df["Year"] = df["last_updated"].dt.year
    df["Month"] = df["last_updated"].dt.month_name()
    df["Day"] = df["last_updated"].dt.day
    return df

df = load_data()
default_country, default_continent = get_user_country_and_continent()

# ============================
# Sidebar Filters
# ============================

st.sidebar.header("🌎 Weather Filters")

# --- Continent Filter ---
continents = sorted(df["continent"].dropna().unique())
select_all_cont = st.sidebar.checkbox("Select All Continents", value=False)
if select_all_cont:
    selected_continents = continents
else:
    selected_continents = st.sidebar.multiselect(
        "🌍 Select Continent(s)",
        options=continents,
        default=[default_continent] if default_continent in continents else [continents[0]],
    )

# --- Country Filter ---
countries = sorted(df[df["continent"].isin(selected_continents)]["country"].unique())
select_all_countries = st.sidebar.checkbox("Select All Countries", value=False)
if select_all_countries:
    selected_countries = countries
else:
    selected_countries = st.sidebar.multiselect(
        "🏳️ Select Country(s)",
        options=countries,
        default=[default_country] if default_country in countries else [countries[0]],
    )

# --- Location Filter ---
locations = sorted(df[df["country"].isin(selected_countries)]["location_name"].unique())
select_all_locations = st.sidebar.checkbox("Select All Locations", value=True)
if select_all_locations:
    selected_locations = locations
else:
    selected_locations = st.sidebar.multiselect(
        "📍 Select Location(s)",
        options=locations,
        default=locations,
    )

# --- Year Filter ---
years = sorted(df["Year"].unique())
selected_years = st.sidebar.multiselect(
    "📆 Select Year(s)", 
    options=years,
    default=[max(years)] if years else None,   # Default to latest year only
)

# --- Month Filter (dependent on selected year) ---
if selected_years:
    months = sorted(df[df["Year"].isin(selected_years)]["Month"].unique().tolist())
else:
    months = sorted(df["Month"].unique().tolist())

selected_months = st.sidebar.multiselect(
    "🗓️ Select Month(s)", 
    options=months,
    default=None,   # No month selected by default
)

# --- Day Filter (dependent on selected months) ---
if selected_months:
    days = sorted(df[df["Month"].isin(selected_months)]["Day"].unique().tolist())
else:
    days = sorted(df["Day"].unique().tolist())

selected_days = st.sidebar.multiselect(
    "📅 Select Day(s)", 
    options=days,
    default=None,   # No day selected by default
)

# ============================
# Apply Filters
# ============================

df_filtered = df[
    (df["continent"].isin(selected_continents)) &
    (df["country"].isin(selected_countries)) &
    (df["location_name"].isin(selected_locations)) &
    (df["Year"].isin(selected_years)) &
    (df["Month"].isin(selected_months) if selected_months else True) &
    (df["Day"].isin(selected_days) if selected_days else True)
]

# ============================
# Weather Condition Analysis
# ============================

st.subheader("🌦️ Weather Condition Overview")

if df_filtered.empty:
    st.warning("No data available for the selected filters.")
else:
    # --- Frequency of Weather Conditions ---
    condition_counts = df_filtered["condition_text"].value_counts().reset_index()
    condition_counts.columns = ["Condition", "Count"]

    fig_count = px.bar(
        condition_counts,
        x="Condition",
        y="Count",
        title="🌦️ Frequency of Weather Conditions",
        color="Count",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_count, use_container_width=True)

    # --- Most and Least Common Conditions ---
    most_common = condition_counts.iloc[0]
    least_common = condition_counts.iloc[-1]
    st.markdown(f"**Most Observed:** {most_common['Condition']} ({most_common['Count']} times)")
    st.markdown(f"**Least Observed:** {least_common['Condition']} ({least_common['Count']} times)")

    # --- Weather Trends Over Time ---
    st.subheader("⏳ Weather Condition Trends Over Time")
    time_trend = df_filtered.groupby(["Year", "Month", "condition_text"]).size().reset_index(name="Count")
    fig_trend = px.line(
        time_trend,
        x="Month",
        y="Count",
        color="condition_text",
        line_group="Year",
        markers=True,
        title="Monthly Weather Trends by Condition",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # --- Scatter Plot ---
    st.subheader("🌡️ Weather Conditions vs Temperature & Humidity")
    fig_feat = px.scatter(
        df_filtered,
        x="temperature_celsius",
        y="humidity",
        size="uv_index",
        color="condition_text",
        hover_data=["country", "location_name", "temperature_celsius", "humidity", "uv_index"],
        title="Humidity vs Temperature (Bubble Size = UV Index)",
        size_max=30,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_feat, use_container_width=True)

    # --- Sample Table ---
    st.subheader("📋 Filtered Data Sample")
    st.dataframe(df_filtered.sample(min(100, len(df_filtered))), use_container_width=True)
