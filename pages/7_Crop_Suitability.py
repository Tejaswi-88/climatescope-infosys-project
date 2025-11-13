import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ✅ Import global dataset and filters
from components.data_loader import get_global_data
from components.sidebar_filters import sidebar_location_filters

# -----------------------------
# 📦 Load global dataset once
# -----------------------------
df = get_global_data()
df['last_updated'] = pd.to_datetime(df['last_updated'])
df['month'] = df['last_updated'].dt.strftime("%B")

# -----------------------------
# 🌍 Sidebar Filters (shared)
# -----------------------------
df_filtered = sidebar_location_filters(df)

selected_continents = st.session_state.get("continent", [])
selected_countries = st.session_state.get("country", [])
selected_locations = st.session_state.get("location", [])

# Filter by location/continent/country
df_filtered = df_filtered[
    (df_filtered["continent"].isin(selected_continents)) &
    (df_filtered["country"].isin(selected_countries)) &
    (df_filtered["location_name"].isin(selected_locations))
]

if df_filtered.empty:
    st.warning("No weather data available for the selected filters.")
    st.stop()


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

def styled_header(text, level=2, color="rgb(255, 140, 66)", size=30):
    html = f"""
        <h{level} style='
            color: {color};
            font-size: {size}px;
            font-weight: 600;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
            font-family: "Segoe UI", sans-serif;
            margin-top: 10px;
            margin-bottom: 0px;
        '>
            {text}
        </h{level}>
    """
    st.markdown(html, unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B; font-size: 48px; font-family: "Segoe UI", sans-serif;margin-top: -50px;'>
        🌾 Crop Sustainability
    </h1>
""", unsafe_allow_html=True)
# -----------------------------
# 🗓 Month Filter on Main Dashboard
# -----------------------------
month_order = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

months_in_data = [m for m in month_order if m in df_filtered['month'].unique()]
current_month = datetime.now().strftime("%B")
default_month = [current_month] if current_month in months_in_data else [months_in_data[0]] if months_in_data else ["January"]

selected_months = st.multiselect(
    "🗓 Select Month(s)",
    options=months_in_data or month_order,
    default=default_month
)

# -----------------------------
# Weather label functions
# -----------------------------
def temp_label(temp):
    if temp < 10: return "❄️ Cold"
    elif temp < 20: return "🌤️ Cool"
    elif temp < 30: return "☀️ Moderate"
    elif temp < 37: return "🔥 Hot"
    else: return "🌡️ Very Hot"

def humidity_label(humidity):
    if humidity < 30: return "💨 Dry"
    elif humidity < 60: return "🌿 Comfortable"
    else: return "💧 Humid"

def rainfall_label(rain):
    if rain < 50: return "🌵 Low Rain"
    elif rain < 150: return "🌦️ Moderate Rain"
    else: return "🌧️ Heavy Rain"

def uv_label(uv):
    if uv < 3: return "🟢 Low"
    elif uv < 6: return "🟡 Moderate"
    elif uv < 8: return "🟠 High"
    else: return "🔴 Very High"

def wind_label(wind):
    if wind < 5: return "🍃 Calm"
    elif wind < 15: return "🌬️ Breezy"
    elif wind < 25: return "💨 Windy"
    else: return "🌪️ Strong Wind"

# -----------------------------
# Crop Database & scoring
# -----------------------------
# --- Global Crop Database (extended to 30+ crops)
CROP_DATABASE = {
    "Rice": {"temp": (20, 35), "rain": (100, 250), "humidity": (60, 90), "uv": (5, 9), "desc": "Thrives in warm, humid regions — ideal for tropical Asia."},
    "Wheat": {"temp": (10, 25), "rain": (50, 100), "humidity": (40, 60), "uv": (3, 8), "desc": "Prefers cool to moderate climates — grown in India’s Rabi season."},
    "Maize": {"temp": (18, 30), "rain": (50, 150), "humidity": (40, 70), "uv": (5, 10), "desc": "Requires moderate temperature and rainfall — suited for tropical climates."},
    "Soybean": {"temp": (15, 30), "rain": (50, 150), "humidity": (40, 80), "uv": (4, 9), "desc": "Grows well in moderately warm and moist climates."},
    "Sugarcane": {"temp": (20, 35), "rain": (100, 250), "humidity": (60, 90), "uv": (6, 10), "desc": "Thrives under high temperature and humidity with abundant sunlight."},
    "Cotton": {"temp": (21, 32), "rain": (50, 120), "humidity": (30, 70), "uv": (6, 10), "desc": "Favors hot and dry climates with moderate rainfall."},
    "Barley": {"temp": (10, 25), "rain": (30, 80), "humidity": (30, 60), "uv": (3, 8), "desc": "Suited for cool and dry regions — common in Europe."},
    "Millet": {"temp": (25, 35), "rain": (30, 100), "humidity": (30, 50), "uv": (6, 10), "desc": "Tolerates heat and low rainfall — great for semi-arid regions."},
    "Sorghum": {"temp": (25, 35), "rain": (30, 100), "humidity": (30, 60), "uv": (6, 10), "desc": "Resistant to drought and heat — grown across Africa and India."},
    "Groundnut": {"temp": (20, 30), "rain": (50, 100), "humidity": (30, 60), "uv": (5, 9), "desc": "Prefers sandy soil and warm, moderately dry conditions."},
    "Potato": {"temp": (10, 25), "rain": (50, 120), "humidity": (40, 70), "uv": (3, 8), "desc": "Needs cool temperatures — ideal for temperate zones."},
    "Tomato": {"temp": (20, 30), "rain": (50, 100), "humidity": (40, 70), "uv": (4, 9), "desc": "Prefers warm, moderately humid conditions with good sunlight."},
    "Banana": {"temp": (25, 35), "rain": (100, 250), "humidity": (60, 90), "uv": (6, 10), "desc": "Loves hot and humid conditions — tropical fruit crop."},
    "Coffee": {"temp": (18, 28), "rain": (100, 200), "humidity": (60, 80), "uv": (4, 8), "desc": "Requires moderate warmth, rainfall, and shaded conditions."},
    "Tea": {"temp": (18, 30), "rain": (100, 200), "humidity": (60, 90), "uv": (3, 8), "desc": "Thrives in warm, humid, and cloudy regions."},
    "Cocoa": {"temp": (20, 32), "rain": (150, 250), "humidity": (70, 90), "uv": (4, 8), "desc": "Grows best in humid tropical climates."},
    "Peas": {"temp": (10, 25), "rain": (40, 80), "humidity": (40, 60), "uv": (3, 8), "desc": "Cool-season crop — ideal for temperate climates."},
    "Carrot": {"temp": (15, 25), "rain": (40, 80), "humidity": (40, 60), "uv": (3, 8), "desc": "Grows well in cool climates with moderate rainfall."},
    "Onion": {"temp": (15, 30), "rain": (40, 80), "humidity": (40, 60), "uv": (4, 9), "desc": "Adapts to diverse climates — moderate temperature preferred."},
    "Cassava": {"temp": (25, 35), "rain": (80, 200), "humidity": (50, 80), "uv": (6, 10), "desc": "Heat-tolerant and drought-resistant staple crop."},
    "Sunflower": {"temp": (20, 30), "rain": (40, 100), "humidity": (40, 70), "uv": (5, 10), "desc": "Requires warm, sunny climate — moderately dry regions."},
    "Lentil": {"temp": (10, 30), "rain": (30, 80), "humidity": (30, 60), "uv": (4, 8), "desc": "Prefers dry, cool weather — thrives in semi-arid zones."},
    "Chickpea": {"temp": (10, 30), "rain": (30, 80), "humidity": (30, 60), "uv": (4, 8), "desc": "Tolerant to dry and cool climates — common in Mediterranean."},
    "Coconut": {"temp": (22, 35), "rain": (100, 250), "humidity": (60, 90), "uv": (6, 10), "desc": "Ideal for humid tropical coastal regions."},
    "Pineapple": {"temp": (22, 35), "rain": (100, 200), "humidity": (60, 90), "uv": (6, 10), "desc": "Tropical fruit that loves warmth and moderate rain."},
    "Apple": {"temp": (5, 25), "rain": (50, 120), "humidity": (40, 70), "uv": (3, 8), "desc": "Requires cool temperatures — hill regions."},
    "Mango": {"temp": (24, 35), "rain": (75, 250), "humidity": (50, 80), "uv": (6, 10), "desc": "Requires warm and humid climate — popular tropical fruit."},
    "Papaya": {"temp": (22, 35), "rain": (100, 200), "humidity": (60, 90), "uv": (6, 10), "desc": "Warm and humid conditions — sensitive to frost."},
    "Barley": {"temp": (8, 25), "rain": (30, 100), "humidity": (40, 70), "uv": (3, 8), "desc": "Best for cooler regions — high adaptability."}
}

def match_score(temp, humidity, rain, uv, crop_data):
    score = 0
    if crop_data["temp"][0] <= temp <= crop_data["temp"][1]: score += 2
    if crop_data["humidity"][0] <= humidity <= crop_data["humidity"][1]: score += 2
    if crop_data["rain"][0] <= rain <= crop_data["rain"][1]: score += 2
    if crop_data["uv"][0] <= uv <= crop_data["uv"][1]: score += 1
    return score

# -----------------------------
# 🌾 Crop Recommendations per location & month
# -----------------------------
st.markdown("<br><h4 style='color:#FFD700;'>🌾 Crop Recommendations</h4>", unsafe_allow_html=True)

for loc in selected_locations:
    df_loc = df_filtered[df_filtered["location_name"] == loc]
    if df_loc.empty:
        st.warning(f"No data for {loc}")
        continue

    # Location container
    st.markdown(f"<div style='background-color:#2b2b2b; padding:10px; border-radius:12px; margin-bottom:10px; border: 2px solid #444;'>"
                f"<h3 style='color:#FFD700;'>📍 {loc}</h3></div>", unsafe_allow_html=True)

    for month in selected_months:
        df_month = df_loc[df_loc['month'] == month]
        if df_month.empty:
            st.info(f"{month}: No weather data")
            continue

        loc_temp = df_month['temperature_celsius'].mean()
        loc_humidity = df_month['humidity'].mean()
        loc_rain = df_month['precip_mm'].mean()
        loc_uv = df_month['uv_index'].mean()
        loc_wind = df_month['wind_mph'].mean()

        st.markdown(f"<h5 style='color:#4caf50;'>{month}</h5>", unsafe_allow_html=True)

        # Use Streamlit columns for KPIs (safe rendering)
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Avg Temp (°C)", f"{loc_temp:.1f}", temp_label(loc_temp))
        col2.metric("Humidity (%)", f"{loc_humidity:.1f}", humidity_label(loc_humidity))
        col3.metric("Rainfall (mm)", f"{loc_rain:.1f}", rainfall_label(loc_rain))
        col4.metric("UV Index", f"{loc_uv:.1f}", uv_label(loc_uv))
        col5.metric("Wind (mph)", f"{loc_wind:.1f}", wind_label(loc_wind))

        # Crop recommendations
        ranked = []
        for crop, data in CROP_DATABASE.items():
            score = match_score(loc_temp, loc_humidity, loc_rain, loc_uv, data)
            ranked.append((crop, score, data["desc"]))
        ranked = sorted(ranked, key=lambda x: x[1], reverse=True)[:3]

        explanation = (f"Suitable crops for this environment:")

        st.markdown(
            f"<div style='background-color:#1c1c1c; padding:12px; border-radius:10px; margin-bottom:12px;'>"
            f"<p style='color:#ccc; font-size:13px;'>{explanation}</p>"
            + "".join([f"<b>{i+1}. {crop}</b> — {desc}<br>" for i, (crop, _, desc) in enumerate(ranked)])
            + "</div>",
            unsafe_allow_html=True
        )
