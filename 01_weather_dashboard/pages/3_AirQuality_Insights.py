# 3_AirQuality_Insights.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import pycountry_convert as pc

st.set_page_config(page_title="Air Quality Insights", layout="wide")

# ============================
# Load Data
# ============================
@st.cache_data
def load_data():
    df = pd.read_csv("../data/processed/processed_weather_data.csv", parse_dates=["last_updated"])
    df.columns = [col.strip() for col in df.columns]
    return df

df = load_data()

# ============================
# Detect User Country
# ============================
def get_user_country():
    try:
        ip_info = requests.get('https://ipinfo.io').json()
        return ip_info.get('country', None)
    except:
        return None

user_country = get_user_country()
unique_countries = sorted(df['country'].unique())
default_country = user_country if user_country in unique_countries else "India"

# ============================
# Map Country → Continent
# ============================
def country_to_continent(country_name):
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        return {
            'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe', 'NA': 'North America',
            'OC': 'Oceania', 'SA': 'South America', 'AN': 'Antarctica'
        }[continent_code]
    except:
        return "Unknown"

if 'continent' not in df.columns:
    df['continent'] = df['country'].apply(country_to_continent)

# ============================
# Sidebar Filters (Multi-select with Select All)
# ============================
st.sidebar.header("🌐 Air Quality Filters")

# --- Continent ---
continents = sorted(df['continent'].unique())
select_all_cont = st.sidebar.checkbox("Select All Continents", value=True)
if select_all_cont:
    selected_continents = continents
else:
    selected_continents = st.sidebar.multiselect(
        "Select Continent(s)",
        options=continents,
        default=[df[df['country']==default_country]['continent'].values[0]]
    )

# --- Countries ---
countries_in_selected_cont = sorted(df[df['continent'].isin(selected_continents)]['country'].unique())
select_all_countries = st.sidebar.checkbox("Select All Countries", value=True)
if select_all_countries:
    selected_countries = countries_in_selected_cont
else:
    selected_countries = st.sidebar.multiselect(
        "Select Country(s)",
        options=countries_in_selected_cont,
        default=[default_country] if default_country in countries_in_selected_cont else countries_in_selected_cont[:1]
    )

# --- Locations ---
locations_in_selected_countries = sorted(df[df['country'].isin(selected_countries)]['location_name'].unique())
select_all_locations = st.sidebar.checkbox("Select All Locations", value=True)
if select_all_locations:
    selected_locations = locations_in_selected_countries
else:
    selected_locations = st.sidebar.multiselect(
        "Select Location(s)",
        options=locations_in_selected_countries,
        default=[locations_in_selected_countries[0]] if locations_in_selected_countries else []
    )

# AQI filter
aqi_options = {
    1: 'Good (1)', 2: 'Moderate (2)', 3: 'Unhealthy for Sensitive Groups (3)',
    4: 'Unhealthy (4)', 5: 'Very Unhealthy (5)', 6: 'Hazardous (6)'
}
selected_aqi_level = st.sidebar.select_slider(
    "Max Air Quality Index (US EPA)",
    options=list(aqi_options.keys()),
    value=6,
    format_func=lambda x: aqi_options[x]
)

# PM2.5 & PM10 range sliders
pm2_5_range = st.sidebar.slider("PM2.5 Range (µg/m³)", int(df['air_quality_PM2.5'].min()), int(df['air_quality_PM2.5'].max()), (int(df['air_quality_PM2.5'].min()), int(df['air_quality_PM2.5'].max())))
pm10_range = st.sidebar.slider("PM10 Range (µg/m³)", int(df['air_quality_PM10'].min()), int(df['air_quality_PM10'].max()), (int(df['air_quality_PM10'].min()), int(df['air_quality_PM10'].max())))

# ============================
# Filter Data
# ============================
df_filtered = df[
    (df['continent'].isin(selected_continents)) &
    (df['country'].isin(selected_countries)) &
    (df['location_name'].isin(selected_locations)) &
    (df['air_quality_us-epa-index'] <= selected_aqi_level) &
    (df['air_quality_PM2.5'] >= pm2_5_range[0]) & (df['air_quality_PM2.5'] <= pm2_5_range[1]) &
    (df['air_quality_PM10'] >= pm10_range[0]) & (df['air_quality_PM10'] <= pm10_range[1])
]

if df_filtered.empty:
    st.warning("No data found for selected filters.")
    st.stop()

# ============================
# KPI Metrics Table with Safe/Danger Filter
# ============================
st.title("🌬️ Air Quality Insights")
st.subheader("Key Metrics for Selected Locations")

# Define safe limits
safe_limits = {'PM2.5': 35, 'PM10': 50}  # µg/m³

# Safe/Danger filter on main page
status_filter = st.radio(
    "Filter by Air Quality Status:",
    ["All", "Safe ✅", "Danger ⚠️"],
    horizontal=True
)

# Prepare table
metrics_list = []
for loc in selected_locations:
    loc_df = df_filtered[df_filtered['location_name'] == loc]
    avg_aqi = loc_df['air_quality_us-epa-index'].mean()
    avg_pm25 = loc_df['air_quality_PM2.5'].mean()
    avg_pm10 = loc_df['air_quality_PM10'].mean()
    avg_humidity = loc_df['humidity'].mean()

    pm25_status = "Safe ✅" if avg_pm25 <= safe_limits['PM2.5'] else "Danger ⚠️"
    pm10_status = "Safe ✅" if avg_pm10 <= safe_limits['PM10'] else "Danger ⚠️"

    # Apply status filter
    if status_filter == "All" or status_filter in [pm25_status, pm10_status]:
        metrics_list.append({
            "Location": loc,
            "Avg AQI": f"{avg_aqi:.2f}",
            "PM2.5 (µg/m³)": f"{avg_pm25:.2f}",
            "PM2.5 Status": pm25_status,
            "PM10 (µg/m³)": f"{avg_pm10:.2f}",
            "PM10 Status": pm10_status,
            "Humidity (%)": f"{avg_humidity:.2f}"
        })

metrics_df = pd.DataFrame(metrics_list)

# Display table
st.dataframe(metrics_df, use_container_width=True)



# ============================
# PM2.5 and PM10 Value Ranges by Air Quality Category
# ============================
st.markdown("### 🌫️ PM2.5 and PM10 Value Ranges by Air Quality Category")
st.markdown("""
These ranges are based on India's National Air Quality Index (NAQI), which is also aligned with global standards.
""")

naqi_ranges = [
    {"AQI Category": "Good", "PM2.5 (µg/m³)": "0 – 30", "PM10 (µg/m³)": "0 – 50", 
     "Health Impact": "Minimal impact"},
    {"AQI Category": "Satisfactory", "PM2.5 (µg/m³)": "31 – 60", "PM10 (µg/m³)": "51 – 100", 
     "Health Impact": "Minor breathing discomfort to sensitive people"},
    {"AQI Category": "Moderately Polluted", "PM2.5 (µg/m³)": "61 – 90", "PM10 (µg/m³)": "101 – 250", 
     "Health Impact": "Breathing discomfort to people with lung disease"},
    {"AQI Category": "Poor", "PM2.5 (µg/m³)": "91 – 120", "PM10 (µg/m³)": "251 – 350", 
     "Health Impact": "Breathing discomfort on prolonged exposure"},
    {"AQI Category": "Very Poor", "PM2.5 (µg/m³)": "121 – 250", "PM10 (µg/m³)": "351 – 430", 
     "Health Impact": "Respiratory illness on prolonged exposure"},
    {"AQI Category": "Severe", "PM2.5 (µg/m³)": ">250", "PM10 (µg/m³)": ">430", 
     "Health Impact": "Serious health impacts, even on healthy individuals"}
]

naqi_df = pd.DataFrame(naqi_ranges)
st.table(naqi_df)

st.markdown("""
**Sources**:  
- <a href="https://www.airquality.cpcb.gov.in/ccr_docs/About_AQI.pdf" target="_blank">CPCB Air Quality Index</a>  
- <a href="https://safar.tropmet.res.in/AQI-47-12-Details" target="_blank">SAFAR India</a>  
- <a href="https://smartairfilters.com/en/blog/global-air-quality-standards-pm2-5-pm10/" target="_blank">Smart Air Global Standards</a>
""", unsafe_allow_html=True)



# ============================
# Multi-location Pollutant Comparison (Bar chart with values)
# ============================
st.markdown("### 📊 Multi-location Pollutant Comparison")
pollutant_rename_map = {
    'air_quality_PM2.5': 'PM2.5',
    'air_quality_PM10': 'PM10',
    'air_quality_Nitrogen_dioxide': 'NO₂ (Nitrogen Dioxide)',
    'air_quality_Sulphur_dioxide': 'SO₂ (Sulphur Dioxide)',
    'air_quality_Carbon_Monoxide': 'CO (Carbon Monoxide)',
    'air_quality_Ozone': 'O₃ (Ozone)'
}


pollutant_cols = ['air_quality_PM2.5','air_quality_PM10','air_quality_Nitrogen_dioxide','air_quality_Sulphur_dioxide','air_quality_Carbon_Monoxide','air_quality_Ozone']
comparison_df = df_filtered.groupby('location_name')[pollutant_cols].mean().reset_index()
comparison_df = comparison_df.rename(columns=pollutant_rename_map)

# Bar chart with values displayed inside bars
short_pollutants = list(pollutant_rename_map.values())

melted_df = comparison_df.melt(id_vars='location_name', 
                               value_vars=short_pollutants, 
                               var_name='Pollutant', 
                               value_name='Value')

bar_fig = px.bar(
    melted_df,
    x='location_name',
    y='Value',
    color='Pollutant',
    text_auto=".2f",
    custom_data=['Pollutant'],
    title="Average Pollutant Levels per Location"
)

bar_fig.update_traces(
    hovertemplate='<b>Location:</b> %{x}<br><b>Pollutant:</b> %{customdata[0]}<br><b>Value:</b> %{y:.2f} µg/m³<br><extra></extra>'
)
st.plotly_chart(bar_fig, use_container_width=True)

# ============================
# AQI & PM Trends
# ============================
st.markdown("### 📈 AQI & Particulate Matter Trends")

# Ensure datetime
df_filtered['last_updated'] = pd.to_datetime(df_filtered['last_updated'])

# Drop rows with NaN in relevant columns
trend_df = df_filtered[['last_updated','air_quality_us-epa-index','air_quality_PM2.5','air_quality_PM10']].dropna()

trend_fig = px.line(
    trend_df.melt(id_vars='last_updated', 
                  value_vars=['air_quality_us-epa-index','air_quality_PM2.5','air_quality_PM10'],
                  var_name='Metric', value_name='Value'),
    x='last_updated',
    y='Value',
    color='Metric',
    labels={"Value":"Concentration / Index","last_updated":"Date"},
    title="AQI & PM Trends",
    markers=True
)
st.plotly_chart(trend_fig, use_container_width=True)


# ============================
# AQI Category Pie
# ============================
st.markdown("### 🥧 AQI Category Distribution")
df_filtered['AQI_Category'] = df_filtered['air_quality_us-epa-index'].map(aqi_options)
aqi_counts = df_filtered.groupby('AQI_Category')['location_name'].count().reset_index()
aqi_counts.columns = ['AQI_Category','Count']

pie_fig = px.pie(
    aqi_counts,
    values='Count',
    names='AQI_Category',
    title="AQI Category Distribution",
    hole=0.4
)
pie_fig.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(pie_fig, use_container_width=True)

# ============================
# Correlation Heatmap
# ============================
st.markdown("### 🔥 Correlation Analysis")
corr_cols = ['air_quality_us-epa-index','air_quality_PM2.5','air_quality_PM10','temperature_celsius','humidity','wind_mph','uv_index']
corr = df_filtered[corr_cols].corr()
fig, ax = plt.subplots(figsize=(8,6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap='OrRd', ax=ax)
st.pyplot(fig)

# ============================
# Raw Data
# ============================
st.markdown("---")
with st.expander("View Raw Filtered Air Quality Data"):
    st.dataframe(df_filtered.reset_index(drop=True), use_container_width=True)
