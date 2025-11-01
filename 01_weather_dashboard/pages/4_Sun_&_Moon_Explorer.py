# ==============================================
# 🌍 5_Continent_Country_Location.py
# ==============================================
# Streamlit page: Continent → Country → Location view with time-based Sun & Moon visuals
# Make sure this file is inside `weather_dashboard/pages/`

import streamlit as st
import pandas as pd
import numpy as np
import requests
import pycountry_convert as pc
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, time as dtime
from dateutil import parser
import pytz

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Continent → Country → Location (Sun & Moon)", layout="wide")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data(ttl=3600)
def load_data(path="../data/processed/processed_weather_data.csv"):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    # Add continent dynamically
    if "country" in df.columns:
        def get_continent(country_name):
            try:
                alpha2 = pc.country_name_to_country_alpha2(country_name)
                cont_code = pc.country_alpha2_to_continent_code(alpha2)
                cont_map = {
                    "AF": "Africa", "AS": "Asia", "EU": "Europe",
                    "NA": "North America", "OC": "Oceania",
                    "SA": "South America", "AN": "Antarctica"
                }
                return cont_map.get(cont_code, "Unknown")
            except:
                return "Unknown"
        df["continent"] = df["country"].apply(get_continent)
    else:
        df["continent"] = "Unknown"

    # Ensure datetime
    if "last_updated" in df.columns:
        def parse_dt(x):
            try:
                return datetime.strptime(str(x).strip(), "%d-%m-%Y %H:%M")
            except:
                try:
                    return parser.parse(str(x))
                except:
                    return pd.NaT
        df["last_updated_dt"] = df["last_updated"].apply(parse_dt)
    return df

df = load_data()

# -------------------------------
# Detect User Country & Continent
# -------------------------------
def get_user_country_and_continent():
    try:
        ip_info = requests.get('https://ipinfo.io').json()
        country_code = ip_info.get('country')
        if country_code:
            country_name = pc.country_alpha2_to_country_name(country_code)
            cont_code = pc.country_alpha2_to_continent_code(country_code)
            cont_map = {
                "AF": "Africa", "AS": "Asia", "EU": "Europe",
                "NA": "North America", "OC": "Oceania",
                "SA": "South America", "AN": "Antarctica"
            }
            cont_name = cont_map.get(cont_code, "Unknown")
            return country_name, cont_name
    except:
        pass
    return "India", "Asia"

default_country, default_continent = get_user_country_and_continent()

# -------------------------------
# Sidebar Filters (same behavior as Air Quality)
# -------------------------------
st.sidebar.header("🌐 Continent → Country → Location Filters")

# --- Continent Selection ---
continents = sorted(df["continent"].unique())
select_all_cont = st.sidebar.checkbox("Select All Continents", value=False)
if select_all_cont:
    selected_continents = continents
else:
    selected_continents = st.sidebar.multiselect(
        "Select Continent(s)",
        options=continents,
        default=[default_continent] if default_continent in continents else [continents[0]]
    )

# --- Country Selection ---
countries_in_selected = sorted(df[df["continent"].isin(selected_continents)]["country"].dropna().unique())
select_all_countries = st.sidebar.checkbox("Select All Countries", value=False)
if select_all_countries:
    selected_countries = countries_in_selected
else:
    selected_countries = st.sidebar.multiselect(
        "Select Country(s)",
        options=countries_in_selected,
        default=[default_country] if default_country in countries_in_selected else [countries_in_selected[0]]
    )

# --- Location Selection ---
locations_in_selected = sorted(df[df["country"].isin(selected_countries)]["location_name"].dropna().unique())
select_all_locations = st.sidebar.checkbox("Select All Locations", value=True)
if select_all_locations:
    selected_locations = locations_in_selected
else:
    selected_locations = st.sidebar.multiselect(
        "Select Location(s)",
        options=locations_in_selected,
        default=locations_in_selected
    )

# Filtered Data
df_filtered = df[
    (df["continent"].isin(selected_continents)) &
    (df["country"].isin(selected_countries)) &
    (df["location_name"].isin(selected_locations))
].copy()

# -------------------------------
# Header
# -------------------------------
st.title("🌞 Continent → Country → Location — Time-based Sun & Moon Visuals")
st.markdown("Use the sidebar to drill down by **Continent → Country → Location**. Then explore local Sun & Moon timings and weather details interactively.")

if df_filtered.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

# -------------------------------
# Location Data Overview
# -------------------------------
st.subheader("📍 Selected Locations Overview")
st.dataframe(df_filtered[["continent", "country", "location_name", "latitude", "longitude"]].drop_duplicates().reset_index(drop=True))

# -------------------------------
# Location Selection for Details
# -------------------------------
locations = df_filtered["location_name"].unique().tolist()
selected_location = st.selectbox("Select a location for detailed Sun & Moon view", options=locations)

loc_data = df_filtered[df_filtered["location_name"] == selected_location]
lat = loc_data["latitude"].iloc[0]
lon = loc_data["longitude"].iloc[0]
tz = loc_data["timezone"].iloc[0] if "timezone" in loc_data.columns else "UTC"
st.markdown(f"**Location:** {selected_location} | **Lat:** {lat} | **Lon:** {lon} | **Timezone:** {tz}")

# -------------------------------
# Available Dates
# -------------------------------
available_dates = pd.to_datetime(loc_data["last_updated_dt"]).dt.date.dropna().unique()
selected_date = st.date_input("Select a date", value=available_dates[0], min_value=min(available_dates), max_value=max(available_dates))

loc_day_data = loc_data[pd.to_datetime(loc_data["last_updated_dt"]).dt.date == selected_date]
times = sorted(pd.to_datetime(loc_day_data["last_updated_dt"]).dt.time.unique())

st.markdown("### Select a Time")
cols = st.columns(6)
selected_time = None
for i, t in enumerate(times):
    if cols[i % 6].button(str(t)):
        selected_time = t

if not selected_time:
    st.info("Please select a time slot to visualize Sun & Moon details.")
    st.stop()

selected_dt = datetime.combine(selected_date, selected_time)
row = loc_day_data[pd.to_datetime(loc_day_data["last_updated_dt"]) == pd.to_datetime(selected_dt)].iloc[0]

# -------------------------------
# Sun & Moon Visuals
# -------------------------------
st.markdown("---")
col1, col2 = st.columns([1, 2])

with col1:
    st.header("🌤️ Weather Snapshot")
    st.write(f"**Condition:** {row.get('condition_text', '—').title()}")
    st.write(f"**Temperature:** {row.get('temperature_celsius', '—')} °C")
    st.write(f"**Humidity:** {row.get('humidity', '—')} %")
    st.write(f"**Wind:** {row.get('wind_mph', '—')} mph ({row.get('wind_direction','—')})")
    st.write(f"**Visibility:** {row.get('visibility_km','—')} km")
    st.write(f"**Pressure:** {row.get('pressure_mb','—')} mb")
    st.write(f"**Last Updated:** {row.get('last_updated','—')}")

with col2:
    st.header("☀️🌙 Sun & Moon Visual")
    sunrise = row.get("sunrise", "—")
    sunset = row.get("sunset", "—")
    moonrise = row.get("moonrise", "—")
    moonset = row.get("moonset", "—")
    moon_phase = row.get("moon_phase", "—")
    moon_illum = row.get("moon_illumination", "—")

    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=float(moon_illum) if str(moon_illum).replace('.','',1).isdigit() else 0,
        number={'suffix': "%"},
        title={"text": f"Moon Illumination<br>{moon_phase}"}
    ))
    fig.update_layout(height=300, margin={"t": 20, "b": 20})
    st.plotly_chart(fig, use_container_width=True)


# ============================
# 🌅 Sun & 🌙 Moon Visuals (Selected Slot)
# ============================

st.markdown("---")
st.markdown("### 🌅 Sun & 🌙 Moon Details for Selected Location & Time")

col_sun, col_moon = st.columns(2)

# -------------------------------
# 🌞 SUN VISUAL
# -------------------------------
with col_sun:
    st.subheader("Sun Status ☀️")

    sunrise_dt, sunset_dt, selected_dt = None, None, None
    try:
        sunrise_dt = pd.to_datetime(sunrise)
        sunset_dt = pd.to_datetime(sunset)
        selected_dt = pd.to_datetime(row.get('last_updated'))
    except Exception:
        pass

    if sunrise_dt is not None and sunset_dt is not None:
        total = (sunset_dt - sunrise_dt).total_seconds()
        elapsed = (selected_dt - sunrise_dt).total_seconds() if selected_dt else 0
        progress = max(0, min(1, elapsed / total)) if total > 0 else 0

        fig_sun = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progress * 100,
            title={
                'text': f"Day Progress: {int(progress * 100)}%<br>🌅 {sunrise} | 🌇 {sunset}",
                'font': {'size': 14}
            },
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'thickness': 0.3, 'color': '#FFD54F'},
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(255,223,99,0.3)'},
                    {'range': [50, 100], 'color': 'rgba(255,180,0,0.3)'}
                ]
            }
        ))

        fig_sun.update_layout(
            height=300,
            margin={'t': 20, 'b': 20, 'l': 20, 'r': 20},
            template="plotly_dark"
        )
        st.plotly_chart(fig_sun, use_container_width=True)
    else:
        st.info("☀️ Sun data unavailable for this slot.")

# -------------------------------
# 🌙 MOON VISUAL
# -------------------------------
with col_moon:
    st.subheader("Moon Phase 🌔")

    illum = 0
    try:
        illum = float(moon_illum) if str(moon_illum).replace('.', '', 1).isdigit() else 0
    except:
        illum = 0
    dark = 100 - illum

    fig_moon = go.Figure(go.Pie(
        labels=['Illuminated', 'Dark'],
        values=[illum, dark],
        hole=0.6,
        sort=False,
        textinfo='none'
    ))

    fig_moon.update_layout(
        title=f"{moon_phase} · Illumination {illum:.1f}%",
        height=300,
        showlegend=False,
        margin={'t': 30, 'b': 10, 'l': 10, 'r': 10},
        template="plotly_dark"
    )

    fig_moon.add_annotation(
        text=f"{int(illum)}%",
        x=0.5,
        y=0.5,
        font_size=20,
        showarrow=False
    )

    st.plotly_chart(fig_moon, use_container_width=True)



# -------------------------------
# Summary Table
# -------------------------------
st.markdown("---")
st.subheader("🌅 Sun & Moon Timings")
st.table(pd.DataFrame({
    "Sunrise": [sunrise],
    "Sunset": [sunset],
    "Moonrise": [moonrise],
    "Moonset": [moonset],
    "Moon Phase": [moon_phase],
    "Moon Illumination (%)": [moon_illum]
}))
