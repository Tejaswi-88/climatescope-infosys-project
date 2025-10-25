import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import os
import altair as alt
import requests

# ============================
# Load Data
# ============================
@st.cache_data
def load_data():
    #df = pd.read_csv("../data/processed/normalized_weather_data.csv", parse_dates=["last_updated"])
    df = pd.read_csv("../data/processed/processed_weather_data.csv", parse_dates=["last_updated"])
    df.columns = [col.strip() for col in df.columns]
    return df

df = load_data()

# ============================
# Detect User Country (optional default)
# ============================
def get_user_country():
    try:
        ip_info = requests.get('https://ipinfo.io').json()
        return ip_info.get('country', None)
    except:
        return None

user_country = get_user_country()
unique_countries = sorted(df['country'].unique())
default_countries = [user_country] if user_country in unique_countries else ["India"]


# ============================
# Dashboard Theme Config
# ============================
themes = {
    "🌞 Light": {
        "background": "#F5F5F5",         # Soft light gray
        "text": "#070606",               # Deep charcoal for contrast
        "plotly_template": "plotly_white",
        "altair_scheme": "category10",
        "color_scale": px.colors.sequential.Plasma,
        "color_discrete" : px.colors.qualitative.G10
    },
    "🌙 Dark": {
        "background": "#121212",         # True dark mode
        "text": "#E0E0E0",               # Light gray for readability
        "plotly_template": "plotly_dark",
        "altair_scheme": "dark2",
        "color_scale": px.colors.sequential.Viridis,
        "color_discrete" : px.colors.qualitative.Prism
    },
    "🌊 Ocean Blue": {
        "background": "#0F1C2E",         # Deep navy blue
        "text": "#A9CCE3",               # Soft aqua blue
        "plotly_template": "seaborn",
        "altair_scheme": "blues",
        "color_scale": px.colors.sequential.Blues,
        "color_discrete" : px.colors.qualitative.Dark24
    },
    "🌅 Sunset": {
        "background": "#2C1B1B",         # Warm dusk brown
        "text": "#F39C12",               # Sunset orange
        "plotly_template": "ggplot2",
        "altair_scheme": "redyellowblue",
        "color_scale": px.colors.sequential.Sunset,
        "color_discrete" : px.colors.qualitative.Set1
    },
    "🌿 Nature": {
        "background": "#1B3B2F",         # Forest green
        "text": "#A9DFBF",               # Light mint green
        "plotly_template": "simple_white",
        "altair_scheme": "greenblue",
        "color_scale": px.colors.sequential.Greens,
        "color_discrete" : px.colors.qualitative.Set2
    },
    "⚪ Monochrome": {
        "background": "#2C2C2C",         # Neutral dark gray
        "text": "#CCCCCC",               # Soft light gray
        "plotly_template": "plotly",
        "altair_scheme": "greys",
        "color_scale": px.colors.sequential.Greys,
        "color_discrete" : px.colors.qualitative.Safe
    }
}


# ============================
# Sidebar Filters
# ============================
st.title("🌍 Global Weather Repository Snapshot")

with st.sidebar:
    st.header("Dashboard Controls")
    selected_theme = st.selectbox("Select Color Theme", list(themes.keys()), index=1)
    theme = themes[selected_theme]

    st.markdown("---")
    st.header("📊 Dashboard Filters")

    
    selected_countries = st.multiselect(
        "Select Countries to View",
        options=unique_countries,
        default=default_countries,
        key="country_filter"
    )

    # Air Quality Filter
    aqi_options = {
        1: 'Good (1)', 2: 'Moderate (2)', 3: 'Unhealthy for Sensitive Groups (3)',
        4: 'Unhealthy (4)', 5: 'Very Unhealthy (5)', 6: 'Hazardous (6)'
    }
    selected_aqi_level = st.select_slider(
        "Filter by Max Air Quality Index (US EPA)",
        options=list(aqi_options.keys()),
        value=6,
        format_func=lambda x: aqi_options[x]
    )

    # Temperature Range Filter
    min_temp, max_temp = int(df['temperature_celsius'].min()), int(df['temperature_celsius'].max())
    temp_range = st.slider(
        "Temperature Range (°C)",
        min_value=min_temp,
        max_value=max_temp,
        value=(min_temp, max_temp),
        step=1
    )

# ============================
# Global Theme Styling
# ============================
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        h1, h2, h3, h4, h5, h6, p, label {{
            color: {theme['text']} !important;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {theme['background']};
        }}
        div[data-testid="stMetricValue"], div[data-testid="stMetricDelta"] {{
            color: {theme['text']} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)


# ============================
# Apply Main Filters
# ============================
df_filtered = df[
    (df['country'].isin(selected_countries)) &
    (df['air_quality_us-epa-index'] <= selected_aqi_level) &
    (df['temperature_celsius'] >= temp_range[0]) &
    (df['temperature_celsius'] <= temp_range[1])
]

df_filtered['latitude'] = pd.to_numeric(df_filtered['latitude'], errors='coerce')
df_filtered['longitude'] = pd.to_numeric(df_filtered['longitude'], errors='coerce')
df_filtered = df_filtered.dropna(subset=['latitude', 'longitude'])

if df_filtered.empty:
    st.error("No data found for the selected filter combination. Please adjust the controls.")
    st.stop()

# ============================
# KPI Metrics
# ============================
st.markdown("---")
st.subheader("Key Global Indicators (Filtered Data)")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
avg_temp = df_filtered['temperature_celsius'].mean()
kpi1.metric(
    label="Avg. Temperature (C)",
    value=f"{avg_temp:.1f} °C",
    delta=f"{df_filtered['feels_like_celsius'].mean() - avg_temp:.1f} Feels Like Diff",
    delta_color='off'
)

max_wind = df_filtered['wind_mph'].max()
kpi2.metric(
    label="Max Wind Gust (MPH)",
    value=f"{max_wind:.1f} MPH",
    delta=f"{df_filtered['wind_mph'].mean():.1f} Avg Wind",
    delta_color='off'
)

avg_humidity = df_filtered['humidity'].mean()
kpi3.metric(
    label="Avg. Humidity (%)",
    value=f"{avg_humidity:.1f} %",
    delta=f"{df_filtered['precip_mm'].sum():.1f} mm Total Precip",
    delta_color='off'
)

avg_aqi = df_filtered['air_quality_us-epa-index'].mean()
kpi4.metric(
    label="Avg. Air Quality Index",
    value=f"{avg_aqi:.2f}",
    delta=f"{len(df_filtered)} Locations",
    delta_color='off'
)


def apply_plotly_theme(fig):
    fig.update_layout(
        template=theme['plotly_template'],
        paper_bgcolor=theme['background'],
        plot_bgcolor=theme['background'],
        font_color=theme['text']
    )
    return fig


# ============================
# Global Map Visualization
# ============================
st.markdown("---")
st.subheader("Global Weather & Air Quality Map")

df_filtered['humidity_scaled'] = df_filtered['humidity'] - df_filtered['humidity'].min() + 1

map_fig = px.scatter_geo(
    df_filtered,
    lat='latitude',
    lon='longitude',
    color='temperature_celsius',
    hover_name='location_name',
    size='humidity_scaled',
    #color_continuous_scale=px.colors.sequential.Plasma,
    color_continuous_scale=theme['color_scale'],
    title='Global Temperature Distribution & Humidity',
    height=550,
    template=theme['plotly_template'],
    hover_data={
        'temperature_celsius': ':.2f',
        'humidity': ':.2f',
        'wind_mph': ':.2f',
        'uv_index': ':.2f',
        'air_quality_us-epa-index': ':.2f'
    }
)
map_fig.update_traces(
    hovertemplate=
    "Country: %{hovertext}<br>" +
    "Temperature: %{customdata[0]:.2f} °C<br>" +
    "Humidity: %{customdata[1]:.2f} %<br>" +
    "Wind Speed: %{customdata[2]:.2f} mph<br>" +
    "UV Index: %{customdata[3]:.2f}<br>" +
    "AQI: %{customdata[4]:.2f}<extra></extra>"
)
map_fig.update_geos(lataxis_range=[-60, 90], lonaxis_range=[-180, 180], showland=True, landcolor="lightgray")
map_fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

st.plotly_chart(apply_plotly_theme(map_fig), use_container_width=True)



# ============================
# Tabs + Secondary Filters
# ============================
st.markdown("---")
st.subheader("Detailed Trend Analysis")
tab1, tab2, tab3, tab4 = st.tabs([
    "🌡️ Temperature & Humidity Trends",
    "💨 Wind & Pressure",
    "😷 Air Quality Breakdown",
    "🌙 Astronomical Data"
])



# ---------- TAB 1 ----------
with tab1:
    tab1_countries = st.multiselect(
        "🌍 Secondary Country Filter (Tab 1)",
        options=selected_countries,
        default=selected_countries,
        key="tab1_country_filter"
    )
    tab1_df = df_filtered[df_filtered['country'].isin(tab1_countries)]
    if tab1_df.empty:
        st.warning("No data for the selected countries in this tab.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            temp_fig = px.scatter(
                tab1_df,
                x='temperature_celsius',
                y='feels_like_celsius',
                color='humidity',
                hover_name='location_name',
                title='Actual vs. Feels Like Temperature by Humidity',
                color_continuous_scale=theme['color_scale'],
                template=theme['plotly_template'],
                hover_data={
                    'temperature_celsius': ':.2f',
                    'feels_like_celsius': ':.2f',
                    'humidity': ':.2f'
                }
            )
            temp_fig.update_traces(
                hovertemplate=
                "Country: %{hovertext}<br>" +
                "Temperature: %{x:.2f} °C<br>" +
                "Feels Like: %{y:.2f} °C<br>" +
                "Humidity: %{marker.color:.2f} %<extra></extra>"
            )
            st.plotly_chart(apply_plotly_theme(temp_fig), use_container_width=True)


        with col2:
            brush = alt.selection_interval(encodings=['y'])
            humidity_chart = alt.Chart(tab1_df).mark_boxplot(extent="min-max").encode(
                x=alt.X('country', title=None),
                y=alt.Y('humidity', title='Humidity (%)'),
                color=alt.Color(
                        'country',
                        legend=None,
                        scale=alt.Scale(scheme=theme['altair_scheme']) 
                    )
            ).properties(
                title='Humidity Distribution',
                background=theme['background']
            ).configure_view(
                stroke=None 
            )#.configure_title(
              #  color=theme['text']
            #).configure_axis(
             #   labelColor=theme['text'],
              #  titleColor=theme['text']
            #)
            st.altair_chart(humidity_chart, use_container_width=True)

# ---------- TAB 2 ----------
with tab2:
    tab2_countries = st.multiselect(
        "🌍 Secondary Country Filter (Tab 2)",
        options=selected_countries,
        default=selected_countries,
        key="tab2_country_filter"
    )
    tab2_df = df_filtered[df_filtered['country'].isin(tab2_countries)]
    if tab2_df.empty:
        st.warning("No data for the selected countries in this tab.")
    else:
        col3, col4 = st.columns(2)
        with col3:
            wind_fig = px.bar_polar(
                tab2_df,
                r="wind_mph",
                theta="wind_direction",
                color="wind_mph",
                color_continuous_scale=theme['color_scale'],
                template=theme['plotly_template'],
                title="Wind Speed by Direction",
                hover_data={'wind_mph': ':.2f'}
            )
            wind_fig.update_traces(
                hovertemplate=
                "Direction: %{theta}<br>" +
                "Wind Speed: %{r:.2f} mph<extra></extra>"
            )
            wind_fig.update_layout(
                    paper_bgcolor=theme['background'],
                    plot_bgcolor=theme['background'],
                    font_color=theme['text'],
                    polar=dict(
                        bgcolor='rgba(0,0,0,0)'  # Transparent circle background
                    )
            )
            st.plotly_chart(apply_plotly_theme(wind_fig), use_container_width=True)


        with col4:
            press_fig = px.scatter(
                tab2_df,
                x='pressure_mb',
                y='cloud',
                color='country',
                hover_name='location_name',
                title='Atmospheric Pressure vs. Cloud Cover (%)',
                color_discrete_sequence=theme['color_discrete'],
                hover_data={
                    'pressure_mb': ':.2f',
                    'cloud': ':.2f'
                }
            )
            press_fig.update_traces(
                hovertemplate="Country: %{hovertext}<br>Pressure: %{x:.2f} mb<br>Cloud: %{y:.2f} %<extra></extra>"
            )
            st.plotly_chart(apply_plotly_theme(press_fig), use_container_width=True)


# ---------- TAB 3 ----------
with tab3:
    tab3_countries = st.multiselect(
        "🌍 Secondary Country Filter (Tab 3)",
        options=selected_countries,
        default=selected_countries,
        key="tab3_country_filter"
    )
    tab3_df = df_filtered[df_filtered['country'].isin(tab3_countries)]
    tab3_df['AQI_Category'] = tab3_df['air_quality_us-epa-index'].map(aqi_options)
    tab3_df['AQI_Category'].fillna("Unknown", inplace=True) 
    if tab3_df.empty:
        st.warning("No data for the selected countries in this tab.")
    else:
        col5, col6 = st.columns(2)
        with col5:
            tab3_df['AQI_Category'] = tab3_df['air_quality_us-epa-index'].map(aqi_options)
            aqi_counts = tab3_df.groupby('AQI_Category')['location_name'].count().reset_index()
            aqi_counts.columns = ['AQI_Category', 'Count']

            if aqi_counts.empty:
                title='Air Quality Index Distribution',
                st.warning("No AQI data available for selected countries.")
            else:
                aqi_fig = px.pie(
                    aqi_counts,
                    values='Count',
                    names='AQI_Category',
                    title='Air Quality Index Distribution',
                    template=theme['plotly_template'],
                    hole=0.4,
                    color_discrete_sequence=theme['color_discrete']
                )
                st.plotly_chart(apply_plotly_theme(aqi_fig), use_container_width=True)


        with col6:
            tab3_df['aqi_size'] = tab3_df['air_quality_us-epa-index'].clip(lower=1)
            df_pollution = tab3_df.dropna(subset=['air_quality_PM2.5', 'air_quality_PM10'])
            pollution_fig = px.scatter(
                df_pollution,
                x='air_quality_PM2.5',
                y='air_quality_PM10',
                color='country',
                size='aqi_size',
                hover_name='location_name',
                title='Particulate Matter Comparison (PM2.5 vs PM10)',
                color_discrete_sequence=theme['color_discrete'],
            )
            st.plotly_chart(apply_plotly_theme(pollution_fig), use_container_width=True)


# ---------- TAB 4 ----------
with tab4:
    tab4_countries = st.multiselect(
        "🌍 Secondary Country Filter (Tab 4)",
        options=selected_countries,
        default=selected_countries,
        key="tab4_country_filter"
    )
    tab4_df = df_filtered[df_filtered['country'].isin(tab4_countries)]
    
    if tab4_df.empty:
        st.warning("No data for the selected countries in this tab.")
    else:
        st.markdown("### ☀️ Sunrise & Sunset Times Visualization")

        # Convert times to datetime for plotting
        tab4_df['sunrise_dt'] = pd.to_datetime(tab4_df['sunrise'], errors='coerce')
        tab4_df['sunset_dt'] = pd.to_datetime(tab4_df['sunset'], errors='coerce')

        # Create a Gantt-style timeline for sunrise/sunset
        sun_chart = alt.Chart(tab4_df).mark_bar(size=10).encode(
            x=alt.X('sunrise_dt:T', title='Time'),
            x2='sunset_dt:T',
            y=alt.Y('location_name:N', sort='-x', title='Location'),
            color=alt.Color('country:N', legend=alt.Legend(title='Country')),
            tooltip=['location_name', 'country', 'sunrise', 'sunset']
        ).properties(
            width='container',
            height=400,
            title='Daylight Duration (Sunrise to Sunset)',
            background=theme['background']
        ).configure_view(
            stroke=None  
        ).configure_title(
            color=theme['text']
        ).configure_axis(
            labelColor=theme['text'],
            titleColor=theme['text']
        )
        st.altair_chart(sun_chart, use_container_width=True)

        st.markdown("### 🌕 Moon Illumination by Country")
        illumination_fig = px.box(
            tab4_df,
            y='moon_illumination',
            x='country',
            color='country',
            title='Moon Illumination (%)',
            template=theme['plotly_template']
        )
        st.plotly_chart(apply_plotly_theme(illumination_fig), use_container_width=True)


        st.markdown("### 🌓 Moon Phase Distribution")
        moon_phase_counts = tab4_df.groupby('moon_phase')['location_name'].count().reset_index()
        moon_phase_counts.columns = ['Moon Phase', 'Count']

        moon_phase_fig = px.pie(
            moon_phase_counts,
            values='Count',
            names='Moon Phase',
            title='Moon Phase Distribution',
            hole=0.4,
            template=theme['plotly_template']
        )
        moon_phase_fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(apply_plotly_theme(moon_phase_fig), use_container_width=True)



# ============================
# Raw Data Table
# ============================
st.markdown("---")
with st.expander("View Raw Filtered Data Table"):
    st.dataframe(df_filtered.drop(columns=['AQI_Category'], errors='ignore'), use_container_width=True)
