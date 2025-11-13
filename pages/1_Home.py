import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import altair as alt
import requests
import pycountry_convert as pc

from components.sidebar_filters import sidebar_location_filters

from components.data_loader import get_global_data
df = get_global_data()

# Apply sidebar filters
filtered_df = sidebar_location_filters(df)
df_filtered = filtered_df

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
        margin-bottom:2px;
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


   /* Force visibility and styling of sidebar toggle button */
    button[aria-label="Toggle sidebar"] {
        position: fixed !important;
        top: 16px !important;
        left: 16px !important;
        z-index: 999999 !important;
        background-color: #FF3B3B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 50% !important;
        box-shadow: 0 0 6px rgba(255, 59, 59, 0.6) !important;
        width: 32px !important;
        height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        opacity: 1 !important;
        visibility: visible !important;
        transition: all 0.2s ease !important;
    }
    button[aria-label="Toggle sidebar"]:hover {
        background-color: #FF6666 !important;
        box-shadow: 0 0 8px rgba(255, 102, 102, 0.8) !important;
        transform: scale(1.05) !important;
    }

    
    /* Ensure collapsed sidebar still shows toggle button */
    div[data-testid="collapsedControl"] {
        position: fixed !important;
        top: 16px !important;
        left: 16px !important;
        z-index: 999999 !important;
        background-color: #FF3B3B !important;
        border-radius: 50% !important;
        box-shadow: 0 0 6px rgba(255, 59, 59, 0.6) !important;
        width: 32px !important;
        height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="collapsedControl"]:hover {
        background-color: #FF6666 !important;
        box-shadow: 0 0 8px rgba(255, 102, 102, 0.8) !important;
        transform: scale(1.05) !important;
    }

    /* ========================================================= */
    /* 👇 Fade-in toggle button visibility on hover of sidebar */
    /* ========================================================= */

    /* Hide sidebar toggle button by default */
    button[aria-label="Toggle sidebar"],
    div[data-testid="collapsedControl"] {
        opacity: 0 !important;
        visibility: hidden !important;
        transition: opacity 0.3s ease, visibility 0.3s ease !important;
    }

    /* Show toggle button only when user hovers near sidebar area */
    [data-testid="stSidebar"]:hover button[aria-label="Toggle sidebar"],
    [data-testid="stSidebar"]:hover div[data-testid="collapsedControl"] {
        opacity: 1 !important;
        visibility: visible !important;
    }

    /* Slight scale effect on hover */
    button[aria-label="Toggle sidebar"]:hover,
    div[data-testid="collapsedControl"]:hover {
        transform: scale(1.05) !important;
    }


    </style>
    """,
    unsafe_allow_html=True,
)


# ============================
# Page Configuration
# ============================
st.set_page_config(
    page_title="Global Weather Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔧 Hide Streamlit top-right menu & deploy button
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;} 
        footer {visibility: hidden;} 
        header [data-testid="stHeader"] div:nth-child(2) {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def styled_header(text, level=2, color="rgb(255, 140, 66)", size=32):
    html = f"""
        <h{level} style='
            color: {color};
            font-size: {size}px;
            font-weight: 600;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.6);
            font-family: "Segoe UI", sans-serif;
            margin-top: 10px;
            margin-bottom: 10px;
        '>
            {text}
        </h{level}>
    """
    st.markdown(html, unsafe_allow_html=True)


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
# Main Dashboard Content
# ============================
st.markdown("""
    <div style='
        position: relative;
        top: -50px;
        text-align: center;
        background-color: #1e1e1e;
        border: 2px solid #333333;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        width: 100%;
        margin: auto;
    '>
        <h1 style='
            font-size: 56px;
            font-weight: 700;
            color: #FF4B4B;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-family: "Segoe UI", sans-serif;
            margin-bottom: 10px;
        '>
            Global Weather Tracker
        </h1>
        <h6 style='
            font-size: 16px;
            font-weight: 100;
            color: #A0A0A0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-family: "Segoe UI", sans-serif;
            margin-bottom: 20px;
        '>
            Stay informed with real-time climate insights. Explore temperature, humidity, wind, and air quality trends across regions and filter data based on what matters to you.
        </h6>
    </div>
""", unsafe_allow_html=True)


if df_filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ===========================
# 🎯 KPI Section
# ===========================

# Box style for KPIs
box_style = """
    background-color: #1e1e1e;
    padding: 18px 20px;
    border-radius: 12px;
    border: 2px solid #333333;
    box-shadow: 0 0 12px rgba(0, 0, 0, 0.4);
    color: #e0e0e0;
    text-align: left;
    font-size: 14px;
    margin: auto;
"""

label_style = "font-weight: bold; color: #FFD700; font-size: 16px;"   # green label
value_style = "font-size: 30px; font-weight: light; color: #ffffff;"
delta_style = "font-size: 13px; font-weight: 500;"

# --- Helper function for delta color & arrow ---
def format_delta(delta_value, unit=""):
    if delta_value > 0:
        return f"<span style='color:#00c853;'>▲ {delta_value:.1f}{unit}</span>"
    elif delta_value < 0:
        return f"<span style='color:#ff5252;'>▼ {delta_value:.1f}{unit}</span>"
    else:
        return f"<span style='color:#bbbbbb;'>– 0{unit}</span>"


# Sample data
avg_temp = df_filtered['temperature_celsius'].mean()
feels_diff = df_filtered['feels_like_celsius'].mean() - avg_temp

max_wind = df_filtered['wind_mph'].max()
avg_wind = df_filtered['wind_mph'].mean()

avg_humidity = df_filtered['humidity'].mean()
total_precip = df_filtered['precip_mm'].sum()

avg_aqi = df_filtered['air_quality_us-epa-index'].mean()
location_count = len(df_filtered)

# Layout for KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_html = format_delta(df_filtered['feels_like_celsius'].mean() - avg_temp, " °C")
    st.markdown(
        f"""
        <div style="{box_style}">
            <div style="{label_style}">Avg. Temperature</div>
            <div style="{value_style}">{avg_temp:.1f} °C</div>
            <div style="{delta_style}">{delta_html} feels like diff</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    delta_html = format_delta(max_wind - avg_wind, " MPH")
    st.markdown(
        f"""
        <div style="{box_style}">
            <div style="{label_style}">Max Wind Speed</div>
            <div style="{value_style}">{max_wind:.1f} MPH</div>
            <div style="{delta_style}">{delta_html} vs avg</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    delta_html = format_delta(avg_humidity - 50, " %")
    st.markdown(
        f"""
        <div style="{box_style}">
            <div style="{label_style}">Avg. Humidity</div>
            <div style="{value_style}">{avg_humidity:.1f} %</div>
            <div style="{delta_style}">{delta_html} | {total_precip:.1f} mm total</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    delta_html = format_delta(50 - avg_aqi, "")
    st.markdown(
        f"""
        <div style="{box_style}">
            <div style="{label_style}">Avg. Air Quality Index</div>
            <div style="{value_style}">{avg_aqi:.2f}</div>
            <div style="{delta_style}">{delta_html} | {location_count} locations</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================
# Global Map Visualization
# ============================
styled_header("World Weather Map")


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
styled_header("Detailed Trend Analysis", level=3, size=28)

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
            temp_fig.update_layout(
                title={
                    'text': 'Actual vs. Feels Like Temperature',
                    'font': {
                        'color': "#F0F0F0",
                        'family': 'Segoe UI, sans-serif'
                    },
                    'x': 0.5,  # center align
                    'xanchor': 'center'
                }
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
            temp_time_fig.update_layout(
                title={
                    'text': 'Actual vs. Feels Like Temperature',
                    'font': {
                        'color': "#F0F0F0",
                        'family': 'Segoe UI, sans-serif'
                    },
                    'x': 0.5,  # center align
                    'xanchor': 'center'
                }
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
        col1, col2 = st.columns(2, gap="medium")  # Optional: adjust gap

        with col1:
            humidity_chart = alt.Chart(tab2_df).mark_boxplot(extent="min-max").encode(
                x=alt.X('country:N', title=None, axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('humidity:Q', title='Humidity (%)'),
                color=alt.Color('country:N', legend=None)
            ).properties(
                title='Humidity Distribution by Country',
                background='transparent',
                height=400  # Ensure consistent height
            ).configure_title(
                font='Segoe UI',
                color='#F0F0F0',
                anchor='middle',
                fontWeight='bold',
                offset=10  # Adjust spacing below title
            ).configure_view(
                stroke=None
            )

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
            humidity_time_fig.update_layout(
                height=400,  # Match Altair chart height
                title={
                    'text': 'Humidity Over Time',
                    'font': {
                        'color': "#F0F0F0",
                        'family': 'Segoe UI, sans-serif',
                    },
                    'x': 0.5,
                    'xanchor': 'center'
                },
                margin=dict(t=60, b=40)  # Adjust top/bottom spacing
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
            uv_hist.update_layout(
                title={
                    'text': 'UV Index Distribution',
                    'font': {
                        'color': "#F0F0F0",
                        'family': 'Segoe UI, sans-serif'
                    },
                    'x': 0.5,  # center align
                    'xanchor': 'center'
                }
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
            uv_fig.update_layout(
                title={
                    'text': 'UV Index Over Time',
                    'font': {
                        'color': "#F0F0F0",
                        'family': 'Segoe UI, sans-serif'
                    },
                    'x': 0.5,  # center align
                    'xanchor': 'center'
                }
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
            wind_fig.update_layout(
                title={
                    'text': 'Wind Speed & Direction',
                    'font': {
                        'color': "#F0F0F0",
                        'family': 'Segoe UI, sans-serif'
                    },
                    'x': 0.5,  # center align
                    'xanchor': 'center'
                }
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
            press_fig.update_layout(
                title={
                    'text': 'Atmospheric Pressure vs. Cloud Cover',
                    'font': {
                        'color': "#F0F0F0",
                        'family': 'Segoe UI, sans-serif'
                    },
                    'x': 0.5,  # center align
                    'xanchor': 'center'
                }
            )
            st.plotly_chart(apply_plotly_theme(press_fig), use_container_width=True)

# --- TAB 5: Air Quality ---
with tab5:

    # =========================
    # 🌫️ AQI Category Mapping
    # =========================
    aqi_options = {
        1: "Good",
        2: "Moderate",
        3: "Unhealthy for Sensitive Groups",
        4: "Unhealthy",
        5: "Very Unhealthy",
        6: "Hazardous"
    }
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
            aqi_fig.update_layout(
                title={
                    'text': 'Air Quality Index Distribution',
                    'font': {
                        'color': "#F0F0F0",
                        'family': 'Segoe UI, sans-serif'
                    },
                    'x': 0.5,  # center align
                    'xanchor': 'center'
                }
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
            pollution_fig.update_layout(
                title={
                    'text': 'Particulate Matter (PM2.5 vs PM10)',
                    'font': {
                        'color': "#F0F0F0",
                        'family': 'Segoe UI, sans-serif'
                    },
                    'x': 0.5,  # center align
                    'xanchor': 'center'
                }
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
            illumination_fig.update_layout(
                title={
                    'text': 'Moon Illumination (%) by Country',
                    'font': {
                        'color': "#F0F0F0",
                        'family': 'Segoe UI, sans-serif'
                    },
                    'x': 0.5,  # center align
                    'xanchor': 'center'
                }
            )
            st.plotly_chart(apply_plotly_theme(illumination_fig), use_container_width=True)
        with col2:
            moon_phase_counts = tab6_df['moon_phase'].value_counts().reset_index()
            moon_phase_fig = px.pie(
                moon_phase_counts, values='count', names='moon_phase',
                title='Moon Phase Distribution', hole=0.4, color_discrete_sequence=THEME['color_discrete']
            )
            moon_phase_fig.update_layout(
                title={
                    'text': 'Moon Phase Distributionr',
                    'font': {
                        'color': "#F0F0F0",
                        'family': 'Segoe UI, sans-serif'
                    },
                    'x': 0.5,  # center align
                    'xanchor': 'center'
                }
            )
            st.plotly_chart(apply_plotly_theme(moon_phase_fig), use_container_width=True)

# ============================
# Raw Data Table
# ============================
with st.expander("View Raw Filtered Data"):
    st.dataframe(df_filtered.drop(columns=['AQI_Category'], errors='ignore'), use_container_width=True)



# ============================
# 🔧 Sidebar Toggle Button Fix
# ============================
st.markdown("""
    <style>
    /* Always keep the sidebar toggle visible */
    [data-testid="stSidebarCollapsedControl"] {
        position: fixed !important;
        top: 20px !important;
        left: 20px !important;
        z-index: 9999 !important;
        background-color: #ff4b4b !important; /* red button */
        color: white !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.3) !important;
    }

    /* When sidebar is expanded */
    [data-testid="stSidebarCollapsedControl"] svg {
        stroke: white !important;
        width: 18px !important;
        height: 18px !important;
    }

    /* Ensure it's clickable when collapsed */
    [data-testid="stSidebarCollapsedControl"]:hover {
        background-color: #ff0000 !important;
        cursor: pointer !important;
    }

    /* Fix overlay issues */
    section[data-testid="stSidebar"] {
        z-index: 1000 !important;
    }
    </style>
""", unsafe_allow_html=True)

