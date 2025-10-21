# 5_Continent_Country_Location.py
# Streamlit page: Continent -> Country -> Location view with date/time selection and dynamic Sun/Moon visuals
# Place this file in weather_dashboard/pages/

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, time as dtime
import pytz
from dateutil import parser

# import the filter panel you provided
from components.filters import filter_panel

st.set_page_config(page_title="Continent → Country → Location (Sun & Moon)", layout="wide")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data(ttl=3600)
def load_data(path="../data/processed/processed_weather_data.csv"):
    df = pd.read_csv(path)
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    # Ensure types
    if 'latitude' in df.columns:
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    if 'longitude' in df.columns:
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    # parse last_updated into datetime
    if 'last_updated' in df.columns:
        def try_parse(x):
            try:
                return datetime.strptime(str(x).strip(), "%d-%m-%Y %H:%M")
            except Exception:
                try:
                    return parser.parse(str(x))
                except Exception:
                    return pd.NaT
        df['last_updated_dt'] = df['last_updated'].apply(try_parse)
    else:
        df['last_updated_dt'] = pd.NaT
    return df

# -------------------------------
# Helper Functions
# -------------------------------
def parse_local_time_string(timestr, ref_date, tz_str):
    """Parse a local time string like '4:50 AM' into a timezone-aware datetime for a given reference date."""
    try:
        if pd.isna(timestr) or pd.isna(tz_str) or pd.isna(ref_date):
            return None
        t = datetime.strptime(str(timestr).strip(), "%I:%M %p").time()
        tz = pytz.timezone(tz_str)
        dt_local = datetime.combine(ref_date.date(), t)
        return tz.localize(dt_local)
    except Exception:
        return None

# -------------------------------
# Load & Filter Data
# -------------------------------
df = load_data()
filters = filter_panel(df)

# Apply filters
df_filtered = df[
    (df['country'].isin(filters['country'])) &
    (df['location_name'].isin(filters['location'])) &
    (df['temperature_celsius'] >= filters['temp_min']) &
    (df['temperature_celsius'] <= filters['temp_max']) &
    (df['humidity'] >= filters['humidity_min']) &
    (df['humidity'] <= filters['humidity_max']) &
    (df['wind_mph'] >= filters['wind_min']) &
    (df['wind_mph'] <= filters['wind_max'])
].copy()

# -------------------------------
# Header & Location Selection
# -------------------------------
st.title("Continent → Country → Location — Time-based Sun & Moon Visuals")
st.markdown("Select a continent → country → location from the sidebar filters. Then pick an available date/time for that location to see sun/moon and weather conditions.")

# Show filtered locations
st.subheader("Selected locations")
st.dataframe(df_filtered[['continent','country','location_name','latitude','longitude']].drop_duplicates().reset_index(drop=True))

locs = df_filtered['location_name'].dropna().unique().tolist()
if not locs:
    st.warning("No locations match the current filters. Adjust filters to see data.")
    st.stop()

selected_location = st.selectbox("Choose location for details", options=locs)

loc_rows = df_filtered[df_filtered['location_name'] == selected_location]
if loc_rows.empty:
    st.error("No data rows for this location after applying filters.")
    st.stop()

lat = loc_rows['latitude'].iloc[0]
lon = loc_rows['longitude'].iloc[0]
tz = loc_rows['timezone'].iloc[0] if 'timezone' in loc_rows.columns else None
st.markdown(f"**Location:** {selected_location} — **Lat:** {lat} — **Lon:** {lon} — **Timezone:** {tz}")

# -------------------------------
# Hourly Date & Time Selection
# -------------------------------
available_times = loc_rows[['last_updated','last_updated_dt']].dropna().drop_duplicates().sort_values('last_updated_dt')

available_dates = pd.to_datetime(available_times['last_updated_dt']).dt.date.drop_duplicates().sort_values()
selected_date = st.date_input("Select date", value=available_dates.iloc[0], min_value=available_dates.min(), max_value=available_dates.max())

times_for_date = available_times[pd.to_datetime(available_times['last_updated_dt']).dt.date == selected_date]
available_hours = sorted(pd.to_datetime(times_for_date['last_updated_dt']).dt.time.unique())

cols = st.columns(6)
selected_time = None
for i, t in enumerate(available_hours):
    col = cols[i % 6]
    if col.button(str(t)):
        selected_time = t

if selected_time is None:
    st.warning("Please select an available time slot.")
    st.stop()

selected_last_updated_dt = datetime.combine(selected_date, selected_time)
selected_last_updated_str = selected_last_updated_dt.strftime("%d-%m-%Y %H:%M")
row = loc_rows[pd.to_datetime(loc_rows['last_updated_dt']) == pd.to_datetime(selected_last_updated_dt)].iloc[0]

# -------------------------------
# Parse Times & Day/Night
# -------------------------------
try:
    sel_dt_naive = selected_last_updated_dt
except Exception:
    sel_dt_naive = None

if sel_dt_naive and tz:
    try:
        sel_tz = pytz.timezone(tz)
        selected_dt = sel_tz.localize(sel_dt_naive)
    except Exception:
        selected_dt = pytz.utc.localize(sel_dt_naive)
else:
    selected_dt = None

sunrise_dt = parse_local_time_string(row.get('sunrise', ''), sel_dt_naive, tz)
sunset_dt = parse_local_time_string(row.get('sunset', ''), sel_dt_naive, tz)
moonrise_dt = parse_local_time_string(row.get('moonrise', ''), sel_dt_naive, tz)
moonset_dt = parse_local_time_string(row.get('moonset', ''), sel_dt_naive, tz)

is_day = False
if selected_dt and sunrise_dt and sunset_dt:
    is_day = (selected_dt >= sunrise_dt) and (selected_dt <= sunset_dt)

# -------------------------------
# Condition Grouping
# -------------------------------
condition_map = {
    "Sunny/Clear": ["sunny", "clear"],
    "Partly Cloudy": ["partly cloudy", "patchy clouds"],
    "Cloudy/Overcast": ["overcast", "cloudy"],
    "Rainy": ["light rain","moderate rain","heavy rain","drizzle","patchy rain","patchy light rain","moderate or heavy rain shower"],
    "Thunderstorm": ["thundery outbreaks possible","moderate or heavy rain with thunder","patchy light rain with thunder","patchy light rain in area with thunder"],
    "Mist/Fog": ["fog","mist","freezing fog","haze"],
    "Snow/Sleet": ["moderate or heavy snow showers","light sleet","blizzard","moderate snow","light snow","light sleet showers","light freezing rain","heavy snow","blowing snow","patchy heavy snow","light snow showers","moderate or heavy sleet","patchy light snow","patchy moderate snow","freezing drizzle","moderate or heavy snow in area with thunder","patchy snow nearby","patchy snow possible","patchy light snow in area with thunder"],
    "Other": []
}

def group_condition(cond_text):
    for k, v in condition_map.items():
        if str(cond_text).lower() in v:
            return k
    return "Other"

loc_rows['condition_group'] = loc_rows['condition_text'].apply(group_condition)

# -------------------------------
# Main Weather Snapshot
# -------------------------------
st.markdown("---")
col1, col2 = st.columns([1,2])
with col1:
    st.header("Weather Snapshot")
    st.subheader(f"{row['condition_text'].title()}")
    st.write(f"**Temperature:** {row.get('temperature_celsius', '—')} °C")
    st.write(f"**Feels like:** {row.get('feels_like_celsius', '—')} °C")
    st.write(f"**Humidity:** {row.get('humidity', '—')} %")
    st.write(f"**Wind:** {row.get('wind_mph', '—')} mph ({row.get('wind_direction','—')})")
    st.write(f"**Visibility:** {row.get('visibility_km','—')} km")
    st.write(f"**Pressure:** {row.get('pressure_mb','—')} mb")
    st.write(f"**Last updated:** {selected_last_updated_str} ({tz})")

with col2:
    st.header("Sun & Moon — Big Visuals")
    emoji = "☀️" if is_day else "🌙"
    st.markdown(f"<div style='font-size:120px; text-align:center'>{emoji}</div>", unsafe_allow_html=True)

# -------------------------------
# Sun & Moon Side-by-Side
# -------------------------------
st.markdown("---")
st.subheader("Sun & Moon Visuals")
col_sun, col_moon = st.columns(2)

with col_sun:
    st.header("Sun")
    if is_day and sunrise_dt and sunset_dt:
        total = (sunset_dt - sunrise_dt).total_seconds()
        elapsed = (selected_dt - sunrise_dt).total_seconds() if selected_dt else 0
        progress = max(0, min(1, elapsed/total)) if total>0 else 0
        fig_sun = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progress*100,
            title={'text':f"Day progress: {int(progress*100)}%\nSunrise {row.get('sunrise','—')} · Sunset {row.get('sunset','—')}", 'font':{'size':14}},
            gauge={'axis':{'range':[0,100]}, 'bar':{'thickness':0.3}, 'steps':[{'range':[0,50],'color':'rgba(255,223,99,0.3)'},{'range':[50,100],'color':'rgba(255,180,0,0.3)'}]}
        ))
        fig_sun.update_layout(height=300, margin={'t':20,'b':20,'l':20,'r':20})
        st.plotly_chart(fig_sun, use_container_width=True)

with col_moon:
    st.header("Moon")
    try:
        illum = float(row.get('moon_illumination', np.nan))
    except Exception:
        illum = 0
    illum = 0 if np.isnan(illum) else illum
    dark = 100-illum
    fig_moon = go.Figure(go.Pie(labels=['Illuminated','Dark'], values=[illum,dark], hole=0.6, sort=False, textinfo='none'))
    fig_moon.update_layout(title=f"{row.get('moon_phase','—').title()} · Illumination {illum}%", height=300, showlegend=False, margin={'t':30,'b':10,'l':10,'r':10})
    fig_moon.add_annotation(text=f"{int(illum)}%", x=0.5, y=0.5, font_size=20, showarrow=False)
    st.plotly_chart(fig_moon, use_container_width=True)

# -------------------------------
# Condition Timeline
# -------------------------------
st.markdown("---")
st.subheader("Condition timeline (selected location)")
cond_timeline = loc_rows[loc_rows['last_updated_dt'].dt.date == selected_date]
if not cond_timeline.empty:
    fig_cond = px.timeline(
        cond_timeline,
        x_start='last_updated_dt',
        x_end=cond_timeline['last_updated_dt'] + pd.Timedelta(minutes=45),
        y=['condition_group']*len(cond_timeline),
        color='condition_group',
        labels={'condition_group':'Condition'},
        title=f"Weather conditions on {selected_date}"
    )
    fig_cond.update_yaxes(showticklabels=False)
    st.plotly_chart(fig_cond, use_container_width=True)
else:
    st.info("No hourly condition data available for this date.")

# -------------------------------
# Sun/Moon Timings Table
# -------------------------------
st.markdown("---")
st.subheader("Sun & Moon timings around selected date")
timing_table = pd.DataFrame({
    'sunrise': [row.get('sunrise','')],
    'sunset': [row.get('sunset','')],
    'moonrise': [row.get('moonrise','')],
    'moonset': [row.get('moonset','')],
    'moon_phase': [row.get('moon_phase','')],
    'moon_illumination': [row.get('moon_illumination','')]
})
st.table(timing_table)

# -------------------------------
# Map & Export
# -------------------------------
st.markdown("---")
st.subheader("Location map")
if not np.isnan(lat) and not np.isnan(lon):
    st.map(pd.DataFrame({'lat':[lat],'lon':[lon]}))

st.markdown("---")
st.subheader("Export")
csv = pd.DataFrame([row]).to_csv(index=False)
st.download_button(label="Download selected datapoint as CSV", data=csv, file_name=f"{selected_location}_{selected_last_updated_str}.csv", mime='text/csv')

st.markdown("---")
st.caption("Notes:\n- Sidebar filters: continent → country → location (filter_panel).\n- Day/night detection uses the selected timestamp localized to timezone.\n- Moon illustration is a donut showing illumination percentage.\n- Condition timeline groups weather conditions into categories like Sunny, Rainy, Cloudy, Mist, Snow.")
