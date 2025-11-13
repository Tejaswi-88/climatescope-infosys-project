# ==============================================
# 🌍 5_Continent_Country_Location.py
# ==============================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pytz

# ✅ Access global dataset and filters
from components.data_loader import get_global_data
from components.sidebar_filters import sidebar_location_filters

# -----------------------------
# 📦 Load global dataset once
# -----------------------------
df = get_global_data()

# -----------------------------
# 🌍 Sidebar Filters (shared)
# -----------------------------
df_filtered = sidebar_location_filters(df)

selected_continents = st.session_state.get("continent", [])
selected_countries = st.session_state.get("country", [])
selected_locations = st.session_state.get("location", [])

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

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Sun & Moon | Global Weather Tracker",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="expanded"
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

# -------------------------------
# Header
# -------------------------------
st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B; font-size: 48px; font-family: "Segoe UI", sans-serif;margin-top: -50px;'>
        🌞 Sun & Moon Visuals
    </h1>
""", unsafe_allow_html=True)
st.markdown("""<h6 style=
            'font-size: 16px;
            font-weight: 200;
            color: #A0A0A0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-family: "Segoe UI", sans-serif;
            text-align:center;
            margin-bottom: 20px;
        '>
Explore local Sun & Moon timings and weather details interactively.
</h6>""", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

# -------------------------------
# 📍 Selected Locations Overview
# -------------------------------
styled_header("📍 Selected Locations Overview")

# Keep only unique locations
unique_locations = df_filtered[["iso_alpha", "continent", "country", "location_name", "latitude", "longitude"]].drop_duplicates().reset_index(drop=True)

# Initialize session state for selected location
if "selected_row_idx" not in st.session_state:
    st.session_state.selected_row_idx = None

# Table styling
st.markdown("""
<style>
/* Table row styling */
.row {
    display: flex;
    border-bottom: 1px solid rgba(255,255,255,0.2); /* subtle line */
    padding: 6px 0;
    align-items: center;
}
.row:hover {
    background-color: rgba(255,255,255,0.03);
}

/* Header styling */
.header {
    font-weight: bold;
    color: #FFD700; /* golden header text */
    border-bottom: 2px solid rgba(255,255,255,0.3);
    padding: 6px 0;
}
.col {
    padding: 0 8px;
    flex: 1;
    min-width: 50px;
}
.col-small { flex: 0.5; }
.col-medium { flex: 2; }
</style>
""", unsafe_allow_html=True)

# Column headers
st.markdown('<div class="row header">'
            '<div class="col col-small">ISO</div>'
            '<div class="col col-medium">Continent</div>'
            '<div class="col col-medium">Country</div>'
            '<div class="col col-medium">Location</div>'
            '<div class="col col-medium">Latitude</div>'
            '<div class="col col-medium">Longitude</div>'
            '<div class="col col-small">Select</div>'
            '</div>', unsafe_allow_html=True)

# Render rows
for idx, row in unique_locations.iterrows():
    cols = st.columns([1, 2, 2, 2, 2, 2, 1])
    cols[0].markdown(f"<div class='row col-small'>{row['iso_alpha']}</div>", unsafe_allow_html=True)
    cols[1].markdown(f"<div class='row col-medium'>{row['continent']}</div>", unsafe_allow_html=True)
    cols[2].markdown(f"<div class='row col-medium'>{row['country']}</div>", unsafe_allow_html=True)
    cols[3].markdown(f"<div class='row col-medium'>{row['location_name']}</div>", unsafe_allow_html=True)
    cols[4].markdown(f"<div class='row col-medium'>{row['latitude']}</div>", unsafe_allow_html=True)
    cols[5].markdown(f"<div class='row col-medium'>{row['longitude']}</div>", unsafe_allow_html=True)
    if cols[6].button("Select", key=f"select_{idx}"):
        st.session_state.selected_row_idx = idx

# --------------------------------------
# ✅ Safe row selection handling
# --------------------------------------
idx = st.session_state.get("selected_row_idx", None)

# Validate index: must be integer within range
if (
    idx is None
    or not isinstance(idx, int)
    or idx < 0
    or idx >= len(unique_locations)
):
    st.session_state.selected_row_idx = None
    st.info("Please select a location row to see Sun & Moon details.")
    st.stop()

# ✅ Safe access now
selected_row = unique_locations.iloc[idx]
st.write(f"✅ Selected location: **{selected_row['location_name']}**")



# Close table HTML
st.markdown("</table>", unsafe_allow_html=True)

# Handle row selection
if st.session_state.selected_row_idx is None:
    st.info("Select a location row to see Sun & Moon details.")
    st.stop()

selected_row = unique_locations.iloc[st.session_state.selected_row_idx]
selected_location = selected_row["location_name"]
selected_lat = selected_row["latitude"]
selected_lon = selected_row["longitude"]
tz = df_filtered[df_filtered["location_name"] == selected_location]["timezone"].iloc[0] if "timezone" in df_filtered.columns else "UTC"

# Display selected location info
st.markdown(f"""
<div style="
    background-color: #333;
    color: #F2F2F2;
    padding: 15px;
    border-radius: 8px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
">
    <span><b>Location:</b> {selected_location}</span>
    <span><b>Lat:</b> {selected_lat}</span>
    <span><b>Lon:</b> {selected_lon}</span>
    <span><b>Timezone:</b> {tz}</span>
</div>
""", unsafe_allow_html=True)


# -------------------------------
# 🗓️ Available Dates Fix
# -------------------------------
# Filter df_filtered for the selected location
loc_data = df_filtered[df_filtered["location_name"] == selected_location].copy()

if loc_data.empty:
    st.warning("No data found for the selected location.")
    st.stop()

# Convert datetime column
if "last_updated_dt" in loc_data.columns:
    loc_data["datetime"] = pd.to_datetime(loc_data["last_updated_dt"], errors="coerce")
elif "last_updated" in loc_data.columns:
    loc_data["datetime"] = pd.to_datetime(loc_data["last_updated"], errors="coerce")
else:
    st.error("❌ No datetime column found in the dataset.")
    st.stop()

loc_data = loc_data.dropna(subset=["datetime"])
available_dates = loc_data["datetime"].dt.date.dropna().unique()

if len(available_dates) == 0:
    st.warning("No valid date entries found for this location.")
    st.stop()


# -------------------------------
# 🗓️ Available Dates & Times
# -------------------------------

# Detect proper datetime column
if "last_updated_dt" in loc_data.columns:
    datetime_col = "last_updated_dt"
elif "last_updated" in loc_data.columns:
    datetime_col = "last_updated"
else:
    st.error("❌ No valid datetime column found in dataset.")
    st.stop()

# Convert safely
loc_data["datetime"] = pd.to_datetime(loc_data[datetime_col], errors="coerce")
loc_data = loc_data.dropna(subset=["datetime"])

# Available Dates
available_dates = sorted(loc_data["datetime"].dt.date.dropna().unique().tolist())

if not available_dates:
    st.warning("⚠️ No available dates for this location.")
    st.stop()

selected_date = st.date_input(
    "📅 Select a Date",
    value=available_dates[0],
    min_value=min(available_dates),
    max_value=max(available_dates),
)

# Filter day data
loc_day_data = loc_data[loc_data["datetime"].dt.date == selected_date]
if loc_day_data.empty:
    st.warning("⚠️ No data available for the selected date.")
    st.stop()

# Extract times
times = sorted(loc_day_data["datetime"].dt.time.dropna().unique().tolist())

# Time selection
st.subheader("🕓 Select a Time")
cols = st.columns(6)
selected_time = None
for i, t in enumerate(times):
    if cols[i % 6].button(str(t)):
        selected_time = t
        st.session_state["selected_time"] = t  # persist selection

# Restore previously selected time
if not selected_time and "selected_time" in st.session_state:
    selected_time = st.session_state["selected_time"]

if not selected_time:
    st.info("Please select a time slot to visualize Sun & Moon details.")
    st.stop()

# Combine selection
selected_dt = datetime.combine(selected_date, selected_time)

# Get row for selected datetime
row = loc_day_data[
    pd.to_datetime(loc_day_data["datetime"]) == pd.to_datetime(selected_dt)
]

if row.empty:
    st.warning("Please select a time slot to visualize Sun & Moon details.")
    st.stop()

row = row.iloc[0]

# -------------------------------
# 🌤️ Weather Snapshot + Sun/Moon
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
    st.header("🌙 Moon Illumination ")
    sunrise = row.get("sunrise", "—")
    sunset = row.get("sunset", "—")
    moonrise = row.get("moonrise", "—")
    moonset = row.get("moonset", "—")
    moon_phase = row.get("moon_phase", "—")
    moon_illum = row.get("moon_illumination", "—")

    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=float(moon_illum) if str(moon_illum).replace('.', '', 1).isdigit() else 0,
        number={'suffix': "%"},
        title={"text": f"Moon Illumination<br>{moon_phase}"}
    ))
    fig.update_layout(height=300, margin={"t": 20, "b": 20})
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# 🌅 Sun & 🌙 Moon Details
# -------------------------------
st.markdown("---")
st.markdown("### 🌅 Sun & 🌙 Moon Details for Selected Location & Time")

col_sun, col_moon = st.columns(2)

# 🌞 SUN VISUAL
with col_sun:
    st.subheader("Sun Status ☀️")
    try:
        selected_dt = pd.to_datetime(row.get('last_updated'), errors='coerce')
        sunrise_dt = pd.to_datetime(f"{selected_dt.date()} {sunrise}", errors='coerce')
        sunset_dt = pd.to_datetime(f"{selected_dt.date()} {sunset}", errors='coerce')

        total = (sunset_dt - sunrise_dt).total_seconds()
        elapsed = (selected_dt - sunrise_dt).total_seconds()
        progress = max(0, min(1, elapsed / total)) if total > 0 else 0

        fig_sun = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progress * 100,
            title={
                'text': f"Day Progress: {int(progress * 100)}%<br>🌅 {sunrise_dt.strftime('%H:%M')} | 🌇 {sunset_dt.strftime('%H:%M')}",
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
        fig_sun.update_layout(height=300, margin={'t': 20, 'b': 20, 'l': 20, 'r': 20}, template="plotly_dark")
        st.plotly_chart(fig_sun, use_container_width=True)
    except Exception as e:
        st.info("☀️ Sun data unavailable for this slot.")

# 🌙 MOON VISUAL
with col_moon:
    st.subheader("Moon Phase 🌔")
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
    fig_moon.add_annotation(text=f"{int(illum)}%", x=0.5, y=0.5, font_size=20, showarrow=False)
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
