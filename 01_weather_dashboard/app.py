import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import altair as alt
import requests
import pycountry_convert as pc

# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Global Weather & Air Quality Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# Theme & Styling
# ============================
THEME = {
    "background": "#0F1116",
    "text": "#FAFAFA",
    "primary": "#5E5CE6",
    "plotly_template": "plotly_dark",
    "altair_scheme": "dark",
    "color_scale": px.colors.sequential.Cividis_r,
    "color_discrete": px.colors.qualitative.Pastel
}

# Apply global styles
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {THEME['background']};
            color: {THEME['text']};
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {THEME['text']};
        }}
        .st-emotion-cache-16txtl3 {{
            padding-top: 2rem;
        }}
        .st-emotion-cache-1v0mbdj {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
    </style>
""", unsafe_allow_html=True)


# ============================
# Utility Functions
# ============================
def get_continent_from_country(country_name):
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        continent_name = pc.convert_continent_code_to_continent_name(continent_code)
        return continent_name
    except:
        return 'Other'

def apply_plotly_theme(fig):
    fig.update_layout(
        template=THEME['plotly_template'],
        paper_bgcolor=THEME['background'],
        plot_bgcolor=THEME['background'],
        font_color=THEME['text'],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

# ============================
# Data Loading & Caching
# ============================
@st.cache_data
def load_and_process_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "../data/processed/processed_weather_data.csv")

    try:
        df = pd.read_csv(csv_path, parse_dates=["last_updated"])
    except FileNotFoundError:
        st.error(f"""
            **ERROR: Data file not found.**
            Please ensure `processed_weather_data.csv` is in the same directory as `app.py`.
            *Directory Searched:* `{script_dir}`
        """)
        st.stop()

    df.columns = [col.strip() for col in df.columns]
    df['continent'] = df['country'].apply(get_continent_from_country)
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df.dropna(subset=['latitude', 'longitude'], inplace=True)
    return df

df = load_and_process_data()


# ============================
# User Location Detection
# ============================
@st.cache_data
def get_user_location():
    try:
        ip_info = requests.get('https://ipinfo.io', timeout=5).json()
        country_code = ip_info.get('country')
        user_country = pc.country_alpha2_to_country_name(country_code)
        user_continent = get_continent_from_country(user_country)
        return user_continent, user_country
    except Exception:
        return "North America", "United States"

user_continent, user_country = get_user_location()

# ============================
# Sidebar & Filters
# ============================
with st.sidebar:
    st.markdown("<h1 style='font-size: 24px;'>🌍 Dashboard Controls</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📍 Global Geographic Filters")
    st.info("Dashboard defaults to your location. Add or remove locations below.")

    unique_continents = sorted(df['continent'].unique())
    selected_continents = st.multiselect(
        "Continents",
        options=unique_continents,
        default=[user_continent] if user_continent in unique_continents else []
    )

    if selected_continents:
        countries_in_selected_continents = sorted(df[df['continent'].isin(selected_continents)]['country'].unique())
        default_country = [user_country] if user_country in countries_in_selected_continents else []
        selected_countries = st.multiselect(
            "Countries",
            options=countries_in_selected_continents,
            default=default_country
        )
    else:
        selected_countries = []

    st.markdown("---")
    st.markdown("### 🌡️ Global Weather Filters")

    aqi_options = {1: 'Good', 2: 'Moderate', 3: 'Unhealthy (SG)', 4: 'Unhealthy', 5: 'Very Unhealthy', 6: 'Hazardous'}
    selected_aqi_level = st.select_slider("Max Air Quality Index (US EPA)", options=list(aqi_options.keys()), value=6, format_func=lambda x: aqi_options[x])

    min_temp, max_temp = int(df['temperature_celsius'].min()), int(df['temperature_celsius'].max())
    temp_range = st.slider("Temperature Range (°C)", min_value=min_temp, max_value=max_temp, value=(min_temp, max_temp))

# ============================
# Main Dashboard Content
# ============================
st.markdown("<h1 style='text-align: center; font-size: 48px;'>Global Weather & Air Quality Dashboard</h1>", unsafe_allow_html=True)

if not selected_countries:
    st.warning("Please select at least one country in the sidebar to view data.")
    st.stop()

df_filtered = df[
    (df['country'].isin(selected_countries)) &
    (df['air_quality_us-epa-index'] <= selected_aqi_level) &
    (df['temperature_celsius'].between(temp_range[0], temp_range[1]))
]

if df_filtered.empty:
    st.warning("No data available for the selected filters. Please broaden your criteria.")
    st.stop()

# ============================
# KPI Metrics
# ============================
st.markdown("### Key Global Indicators (Filtered)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

avg_temp = df_filtered['temperature_celsius'].mean()
kpi1.metric(label="Avg. Temperature", value=f"{avg_temp:.1f} °C", delta=f"{df_filtered['feels_like_celsius'].mean() - avg_temp:.1f} °C feels like diff")

max_wind = df_filtered['wind_mph'].max()
kpi2.metric(label="Max Wind Speed", value=f"{max_wind:.1f} MPH", delta=f"{df_filtered['wind_mph'].mean():.1f} MPH avg")

avg_humidity = df_filtered['humidity'].mean()
kpi3.metric(label="Avg. Humidity", value=f"{avg_humidity:.1f} %", delta=f"{df_filtered['precip_mm'].sum():.1f} mm total precip")

avg_aqi = df_filtered['air_quality_us-epa-index'].mean()
kpi4.metric(label="Avg. Air Quality Index", value=f"{avg_aqi:.2f}", delta=f"{len(df_filtered)} locations")

st.markdown("<hr style='border: 1px solid rgba(255, 255, 255, 0.1);'>", unsafe_allow_html=True)


# ============================
# Global Map Visualization
# ============================
st.subheader("Global Weather & Air Quality Map")

map_fig = px.scatter_geo(
    df_filtered,
    lat='latitude',
    lon='longitude',
    color='temperature_celsius',
    hover_name='location_name',
    size='humidity',
    projection='natural earth',
    color_continuous_scale=THEME['color_scale'],
    custom_data=['country', 'humidity', 'wind_mph', 'air_quality_us-epa-index']
)

map_fig.update_layout(
    height=600,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    geo=dict(bgcolor='rgba(0,0,0,0)', landcolor='#2A2A2A', showcountries=True, countrycolor="rgba(255, 255, 255, 0.2)")
)
map_fig.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>Country: %{customdata[0]}<br>Temperature: %{marker.color:.1f}°C<br>Humidity: %{customdata[1]:.0f}%<br>Wind Speed: %{customdata[2]:.1f} MPH<br>AQI: %{customdata[3]:.0f}<extra></extra>"
)

st.plotly_chart(apply_plotly_theme(map_fig), use_container_width=True)


# ============================
# Detailed Analysis Tabs (WITH SUB-FILTERS RESTORED)
# ============================
st.markdown("<hr style='border: 1px solid rgba(255, 255, 255, 0.1);'>", unsafe_allow_html=True)
st.subheader("Detailed Trend Analysis")

# --- Define 6 Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌡️ Temperature",
    "💧 Humidity",
    "☀️ UV Index",
    "💨 Wind & Pressure",
    "😷 Air Quality",
    "☀️ Astronomical Data"
])

# --- TAB 1: Temperature ---
with tab1:
    st.markdown("##### Filter Countries and Locations for this Tab")
    tab1_countries = st.multiselect(
        "Select countries:",
        options=selected_countries,
        default=selected_countries,
        key="tab1_country_filter"
    )
    tab1_df = df_filtered[df_filtered['country'].isin(tab1_countries)]
    
    tab1_locations = st.multiselect(
        "Select locations:",
        options=tab1_df['location_name'].unique(),
        default=tab1_df['location_name'].unique(),
        key="tab1_location_filter"
    )
    tab1_df = tab1_df[tab1_df['location_name'].isin(tab1_locations)]
    
    if tab1_df.empty:
        st.warning("No data for the selected countries/locations in this tab.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            temp_fig = px.scatter(
                tab1_df,
                x='temperature_celsius',
                y='feels_like_celsius',
                color='humidity',
                title='Actual vs. Feels Like Temperature',
                color_continuous_scale=THEME['color_scale'],
                hover_name='location_name'
            )
            st.plotly_chart(apply_plotly_theme(temp_fig), use_container_width=True)
        with col2:
            temp_time_fig = px.line(
                tab1_df,
                x='last_updated',
                y='temperature_celsius',
                color='country',
                title='Temperature Over Time',
                color_discrete_sequence=THEME['color_discrete']
            )
            st.plotly_chart(apply_plotly_theme(temp_time_fig), use_container_width=True)

# --- TAB 2: Humidity ---
with tab2:
    st.markdown("##### Filter Countries and Locations for this Tab")
    tab2_countries = st.multiselect(
        "Select countries:",
        options=selected_countries,
        default=selected_countries,
        key="tab2_country_filter"
    )
    tab2_df = df_filtered[df_filtered['country'].isin(tab2_countries)]
    
    tab2_locations = st.multiselect(
        "Select locations:",
        options=tab2_df['location_name'].unique(),
        default=tab2_df['location_name'].unique(),
        key="tab2_location_filter"
    )
    tab2_df = tab2_df[tab2_df['location_name'].isin(tab2_locations)]
    
    if tab2_df.empty:
        st.warning("No data for the selected countries/locations in this tab.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            humidity_chart = alt.Chart(tab2_df).mark_boxplot(extent="min-max").encode(
                x=alt.X('country:N', title=None, axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('humidity:Q', title='Humidity (%)'),
                color=alt.Color('country:N', legend=None)
            ).properties(title='Humidity Distribution by Country', background='transparent').configure_view(stroke=None)
            st.altair_chart(humidity_chart, use_container_width=True, theme="streamlit")
        with col2:
            humidity_time_fig = px.line(
                tab2_df,
                x='last_updated',
                y='humidity',
                color='country',
                title='Humidity Over Time',
                color_discrete_sequence=THEME['color_discrete']
            )
            st.plotly_chart(apply_plotly_theme(humidity_time_fig), use_container_width=True)

# --- TAB 3: UV Index ---
with tab3:
    st.markdown("##### Filter Countries and Locations for this Tab")
    tab3_countries = st.multiselect(
        "Select countries:",
        options=selected_countries,
        default=selected_countries,
        key="tab3_country_filter"
    )
    tab3_df = df_filtered[df_filtered['country'].isin(tab3_countries)]
    
    tab3_locations = st.multiselect(
        "Select locations:",
        options=tab3_df['location_name'].unique(),
        default=tab3_df['location_name'].unique(),
        key="tab3_location_filter"
    )
    tab3_df = tab3_df[tab3_df['location_name'].isin(tab3_locations)]
    
    if tab3_df.empty:
        st.warning("No data for the selected countries/locations in this tab.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            uv_hist = px.histogram(
                tab3_df,
                x='uv_index',
                nbins=20,
                color='country',
                title='UV Index Distribution',
                color_discrete_sequence=THEME['color_discrete']
            )
            st.plotly_chart(apply_plotly_theme(uv_hist), use_container_width=True)
        with col2:
            uv_fig = px.line(
                tab3_df,
                x='last_updated',
                y='uv_index',
                color='country',
                title='UV Index Over Time',
                color_discrete_sequence=THEME['color_discrete']
            )
            st.plotly_chart(apply_plotly_theme(uv_fig), use_container_width=True)

# --- TAB 4: Wind & Pressure ---
with tab4:
    st.markdown("##### Filter Countries and Locations for this Tab")
    tab4_countries = st.multiselect(
        "Select countries:",
        options=selected_countries,
        default=selected_countries,
        key="tab4_country_filter"
    )
    tab4_df = df_filtered[df_filtered['country'].isin(tab4_countries)]
    
    tab4_locations = st.multiselect(
        "Select locations:",
        options=tab4_df['location_name'].unique(),
        default=tab4_df['location_name'].unique(),
        key="tab4_location_filter"
    )
    tab4_df = tab4_df[tab4_df['location_name'].isin(tab4_locations)]
    
    if tab4_df.empty:
        st.warning("No data for the selected countries/locations in this tab.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            wind_fig = px.bar_polar(
                tab4_df, r="wind_mph", theta="wind_direction", color="wind_mph",
                title="Wind Speed & Direction", color_continuous_scale=THEME['color_scale']
            )
            st.plotly_chart(apply_plotly_theme(wind_fig), use_container_width=True)
        with col2:
            press_fig = px.scatter(
                tab4_df,
                x='pressure_mb', y='cloud', color='continent',
                title='Atmospheric Pressure vs. Cloud Cover',
                color_discrete_sequence=THEME['color_discrete'],
                hover_name='location_name'
            )
            st.plotly_chart(apply_plotly_theme(press_fig), use_container_width=True)

# --- TAB 5: Air Quality ---
with tab5:
    st.markdown("##### Filter Countries and Locations for this Tab")
    tab5_countries = st.multiselect(
        "Select countries:",
        options=selected_countries,
        default=selected_countries,
        key="tab5_country_filter"
    )
    tab5_df = df_filtered[df_filtered['country'].isin(tab5_countries)]
    
    tab5_locations = st.multiselect(
        "Select locations:",
        options=tab5_df['location_name'].unique(),
        default=tab5_df['location_name'].unique(),
        key="tab5_location_filter"
    )
    tab5_df = tab5_df[tab5_df['location_name'].isin(tab5_locations)]
    
    if tab5_df.empty:
        st.warning("No data for the selected countries/locations in this tab.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            tab5_df['AQI_Category'] = tab5_df['air_quality_us-epa-index'].map(aqi_options)
            aqi_counts = tab5_df['AQI_Category'].value_counts().reset_index()
            aqi_fig = px.pie(
                aqi_counts,
                values='count', names='AQI_Category',
                title='Air Quality Index Distribution',
                hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu_r
            )
            st.plotly_chart(apply_plotly_theme(aqi_fig), use_container_width=True)
        with col2:
            pollution_fig = px.scatter(
                tab5_df.dropna(subset=['air_quality_PM2.5', 'air_quality_PM10']),
                x='air_quality_PM2.5', y='air_quality_PM10',
                color='continent', size='air_quality_us-epa-index',
                title='Particulate Matter (PM2.5 vs PM10)',
                hover_name='location_name', color_discrete_sequence=THEME['color_discrete']
            )
            st.plotly_chart(apply_plotly_theme(pollution_fig), use_container_width=True)

# --- TAB 6: Astronomical Data ---
with tab6:
    st.markdown("##### Filter Countries and Locations for this Tab")
    tab6_countries = st.multiselect(
        "Select countries:",
        options=selected_countries,
        default=selected_countries,
        key="tab6_country_filter"
    )
    tab6_df = df_filtered[df_filtered['country'].isin(tab6_countries)]
    
    tab6_locations = st.multiselect(
        "Select locations:",
        options=tab6_df['location_name'].unique(),
        default=tab6_df['location_name'].unique(),
        key="tab6_location_filter"
    )
    tab6_df = tab6_df[tab6_df['location_name'].isin(tab6_locations)]
    
    if tab6_df.empty:
        st.warning("No data for the selected countries/locations in this tab.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            illumination_fig = px.box(
                tab6_df, y='moon_illumination', x='country', color='country',
                title='Moon Illumination (%) by Country', color_discrete_sequence=THEME['color_discrete']
            )
            st.plotly_chart(apply_plotly_theme(illumination_fig), use_container_width=True)
        with col2:
            moon_phase_counts = tab6_df['moon_phase'].value_counts().reset_index()
            moon_phase_fig = px.pie(
                moon_phase_counts, values='count', names='moon_phase',
                title='Moon Phase Distribution', hole=0.4, color_discrete_sequence=THEME['color_discrete']
            )
            st.plotly_chart(apply_plotly_theme(moon_phase_fig), use_container_width=True)

# ============================
# Raw Data Table
# ============================
with st.expander("View Raw Filtered Data"):
    st.dataframe(df_filtered.drop(columns=['AQI_Category'], errors='ignore'), use_container_width=True)