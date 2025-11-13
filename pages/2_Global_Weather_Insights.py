import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import pycountry_convert as pc

# ✅ Access the globally loaded data
from components.data_loader import get_global_data
df = get_global_data()

from components.sidebar_filters import sidebar_location_filters, get_user_country_and_continent
default_country, default_continent = get_user_country_and_continent()

# ✅ Use shared sidebar filter
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


# AQI filter
aqi_options = {
    1: 'Good (1)', 2: 'Moderate (2)', 3: 'Unhealthy for Sensitive Groups (3)',
    4: 'Unhealthy (4)', 5: 'Very Unhealthy (5)', 6: 'Hazardous (6)'
}
selected_aqi_level = st.sidebar.select_slider(
    "Max Air Quality Index",
    options=list(aqi_options.keys()),
    value=6,
    format_func=lambda x: aqi_options[x]
)

# Dynamic ranges for weather parameters
st.sidebar.markdown("### Adjust Weather Parameter Ranges")
temp_range = st.sidebar.slider("Temperature (°C)", float(df['temperature_celsius'].min()), float(df['temperature_celsius'].max()), (float(df['temperature_celsius'].min()), float(df['temperature_celsius'].max())), 0.01)
precip_range = st.sidebar.slider("Precipitation (mm)", float(df['precip_mm'].min()), float(df['precip_mm'].max()), (float(df['precip_mm'].min()), float(df['precip_mm'].max())), 0.01)
wind_range = st.sidebar.slider("Wind Speed (mph)", float(df['wind_mph'].min()), float(df['wind_mph'].max()), (float(df['wind_mph'].min()), float(df['wind_mph'].max())), 0.01)
uv_range = st.sidebar.slider("UV Index", float(df['uv_index'].min()), float(df['uv_index'].max()), (float(df['uv_index'].min()), float(df['uv_index'].max())), 0.01)
humidity_range = st.sidebar.slider("Humidity (%)", float(df['humidity'].min()), float(df['humidity'].max()), (float(df['humidity'].min()), float(df['humidity'].max())), 0.01)


# =========================
# Filter Data
# =========================
df_filtered = df[
    (df['country'].isin(selected_countries)) &
    (df['air_quality_us-epa-index'] <= selected_aqi_level) &
    (df['temperature_celsius'] >= temp_range[0]) & (df['temperature_celsius'] <= temp_range[1]) &
    (df['precip_mm'] >= precip_range[0]) & (df['precip_mm'] <= precip_range[1]) &
    (df['wind_mph'] >= wind_range[0]) & (df['wind_mph'] <= wind_range[1]) &
    (df['uv_index'] >= uv_range[0]) & (df['uv_index'] <= uv_range[1]) &
    (df['humidity'] >= humidity_range[0]) & (df['humidity'] <= humidity_range[1])
]

df_filtered['latitude'] = pd.to_numeric(df_filtered['latitude'], errors='coerce')
df_filtered['longitude'] = pd.to_numeric(df_filtered['longitude'], errors='coerce')
df_filtered = df_filtered.dropna(subset=['latitude', 'longitude'])

if df_filtered.empty:
    st.warning("No data found for selected filters.")
    st.stop()


# =========================
# Weather Overview Tabs with Sub-filter and Graph Selection
# =========================
#
#Bar	Clear comparison of averages across locations
#Box	Shows spread, outliers, and variability
#Scatter	Reveals relationships between metrics
#Line	Tracks changes over time

# ===============================
# 📊 Weather Overview by Selected Locations
# ===============================
st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B; width:100%; font-size: 48px; font-family: "Segoe UI", sans-serif;margin-top: -50px;'>
        📊 Weather Overview
    </h1>
""", unsafe_allow_html=True)

with st.expander("📘 What Each Graph Type Shows", expanded=False):
    st.markdown("""
    <div style="
        background-color: #1a1a1a;
        padding: 15px 18px;
        border-radius: 10px;
        color: #bbbbbb;
        font-size: 13px;
        line-height: 1.6;
    ">
    • <b>Bar Chart</b> — Compares <i>average values</i> (like temperature or humidity) across locations.<br>
    • <b>Line Chart</b> — Tracks how a metric <i>changes over time</i> for each location.<br>
    • <b>Box Plot</b> — Reveals <i>data spread, variability</i>, and <i>outliers</i>.<br>
    • <b>Scatter Plot</b> — Displays <i>relationships between two metrics</i> (e.g., temperature vs humidity).<br>
    </div>
    """, unsafe_allow_html=True)

metric_map = {
    "Temperature": "temperature_celsius",
    "Humidity": "humidity",
    "Wind Speed": "wind_mph",
    "UV Index": "uv_index"
}
graph_options = ["Bar", "Line", "Box", "Scatter"]

tabs = st.tabs(list(metric_map.keys()))

for tab_name, tab in zip(metric_map.keys(), tabs):
    with tab:
        # --- Filter Locations ---
        sub_locations = st.multiselect(
            f"Filter Locations for {tab_name}",
            options=df_filtered['location_name'].unique(),
            default=df_filtered['location_name'].unique(),
            key=f"sub_{tab_name}_location"
        )
        df_tab = df_filtered[df_filtered['location_name'].isin(sub_locations)]

        # --- Select Graph Type ---
        graph_selected = st.selectbox(
            f"Select Graph Type for {tab_name}",
            graph_options,
            key=f"{tab_name}_graph"
        )

        col = metric_map[tab_name]

        # --- Scatter-specific filter (appears only when Scatter is chosen) ---
        if graph_selected == "Scatter":
            other_choices = [m for m in metric_map.keys() if m != tab_name]
            selected_other = st.selectbox(
                f"Select comparison metric for {tab_name} (Y-axis):",
                options=other_choices,
                key=f"{tab_name}_other_metric"
            )
            other_col = metric_map[selected_other]
        else:
            other_col = None

        # --- Plot Function ---
        def plot_metric(df_plot, col, graph_type, other_col=None):
            if df_plot.empty:
                st.warning("No data for selected locations")
                return None

            color_scales = {
                "temperature_celsius": "Reds",
                "humidity": "Blues",
                "wind_mph": "Greens",
                "uv_index": "solar"
            }
            units = {
                "temperature_celsius": "°C",
                "humidity": "%",
                "wind_mph": "mph",
                "uv_index": "UV"
            }
            display_names = {
                "temperature_celsius": "Temperature",
                "humidity": "Humidity",
                "wind_mph": "Wind Speed",
                "uv_index": "UV Index"
            }

            scale = color_scales.get(col, "Plasma")
            unit = units.get(col, "")
            display_name = display_names.get(col, col)

            if graph_type == "Line":
                df_plot['last_updated'] = pd.to_datetime(df_plot['last_updated'], errors='coerce')
                df_plot = df_plot.dropna(subset=['last_updated'])
                fig = px.line(
                    df_plot,
                    x='last_updated',
                    y=col,
                    color='location_name',
                    markers=True,
                    hover_data=['country'],
                    title=f"{display_name} Trend Over Time by Location"
                )

            elif graph_type == "Bar":
                df_avg = (
                    df_plot.groupby(['country', 'location_name'])[col]
                    .mean()
                    .reset_index()
                )
                df_avg[col] = df_avg[col].round(2)
                fig = px.bar(
                    df_avg,
                    x='location_name',
                    y=col,
                    color=col,
                    color_continuous_scale=scale,
                    title=f"Average {display_name} by Location",
                    hover_data={'country': True, 'location_name': True, col: ':.2f'}
                )

            elif graph_type == "Box":
                fig = px.box(
                    df_plot,
                    x='location_name',
                    y=col,
                    color='location_name',
                    title=f"{display_name} Distribution by Location"
                )

            elif graph_type == "Scatter" and other_col:
                other_display = display_names.get(other_col, other_col)
                fig = px.scatter(
                    df_plot,
                    x=col,
                    y=other_col,
                    color='location_name',
                    hover_data=['country'],
                    title=f"{display_name} vs {other_display} by Location"
                )
                fig.update_layout(
                    xaxis_title=f"{display_name} ({units[col]})",
                    yaxis_title=f"{other_display} ({units[other_col]})"
                )
            else:
                st.warning("Please select a metric to compare.")
                return None

            fig.update_layout(height=450)
            return fig

        fig = plot_metric(df_tab, col, graph_selected, other_col)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        

       # --- Dynamic Summary Section (Smart Version) ---
        if not df_tab.empty and fig is not None:
            metric_display = tab_name
            num_locations = len(sub_locations)
            num_points = len(df_tab)
            avg_value = df_tab[col].mean().round(2)
            min_value = df_tab[col].min().round(2)
            max_value = df_tab[col].max().round(2)
            graph_type = graph_selected

            # Default base description
            summary_text = ""
            quick_insight = ""

            # ---- Graph-Type Specific Explanations ----
            if graph_type == "Bar":
                df_avg = df_tab.groupby('location_name')[col].mean().round(2)
                top_location = df_avg.idxmax()
                top_value = df_avg.max()
                bottom_location = df_avg.idxmin()
                bottom_value = df_avg.min()
                summary_text = (
                    f"This bar chart compares <b>{metric_display}</b> averages across "
                    f"<b>{num_locations}</b> selected location(s). It helps identify which region "
                    f"has the highest and lowest average {metric_display.lower()}."
                )
                quick_insight = (
                    f"🔹 The highest average {metric_display.lower()} is <b>{top_value}</b> "
                    f"at <b>{top_location}</b>, while the lowest is <b>{bottom_value}</b> "
                    f"at <b>{bottom_location}</b>.<br>"
                    f"🔹 Overall mean: <span style='color:#FFD700;'>{avg_value}</span> units."
                )

            elif graph_type == "Line":
                df_tab['last_updated'] = pd.to_datetime(df_tab['last_updated'], errors='coerce')
                trend_text = "temporal patterns, seasonal changes, or sudden fluctuations"
                summary_text = (
                    f"This line chart tracks how <b>{metric_display}</b> values change over time "
                    f"across <b>{num_locations}</b> location(s). It highlights {trend_text} "
                    f"in your selected dataset."
                )
                latest_values = (
                    df_tab.sort_values('last_updated')
                    .groupby('location_name')[col]
                    .last()
                    .round(2)
                )
                latest_display = "<br>".join([f"🔹 <b>{loc}:</b> {val}" for loc, val in latest_values.items()])
                quick_insight = (
                    f"The average <b>{metric_display}</b> across all data is "
                    f"<span style='color:#FFD700;'>{avg_value}</span> units.<br>"
                    f"Here are the latest readings:<br>{latest_display}"
                )

            elif graph_type == "Box":
                summary_text = (
                    f"This box plot reveals the <b>data spread</b>, <b>variability</b>, and "
                    f"<b>outliers</b> of <b>{metric_display}</b> across the selected "
                    f"{num_locations} location(s). It’s ideal for detecting uneven distributions."
                )
                spread = (max_value - min_value).round(2)
                quick_insight = (
                    f"🔹 Overall range: <b>{min_value}</b> – <b>{max_value}</b> units "
                    f"(<b>spread:</b> {spread}).<br>"
                    f"🔹 Mean value: <span style='color:#FFD700;'>{avg_value}</span> units."
                )

            elif graph_type == "Scatter" and other_col:
                other_display = [k for k, v in metric_map.items() if v == other_col][0]
                corr = df_tab[[col, other_col]].corr().iloc[0, 1].round(2)
                trend_type = (
                    "positive" if corr > 0.3 else "negative" if corr < -0.3 else "weak or no"
                )
                summary_text = (
                    f"This scatter plot visualizes the <b>relationship</b> between "
                    f"<b>{metric_display}</b> and <b>{other_display}</b> across selected locations."
                )
                quick_insight = (
                    f"🔹 The correlation between <b>{metric_display}</b> and <b>{other_display}</b> "
                    f"is <b>{corr}</b> ({trend_type} correlation).<br>"
                    f"🔹 Average {metric_display.lower()}: <span style='color:#FFD700;'>{avg_value}</span> units."
                )

            else:
                summary_text = (
                    f"This visualization shows <b>{metric_display}</b> patterns "
                    f"across selected locations."
                )
                quick_insight = (
                    f"Average value: <span style='color:#FFD700;'>{avg_value}</span> units."
                )

            # ---- Render Styled Summary ----
            st.markdown(
                f"""
                <div style="
                    background-color: #1a1a1a;
                    border-left: 4px solid #4caf50;
                    padding: 18px 20px;
                    border-radius: 10px;
                    color: #e0e0e0;
                    font-size: 14px;
                    margin-top: 15px;
                    line-height: 1.7;
                ">
                <h4 style="color:#76ff03;">📊 Analysis Summary</h4>
                <b>🗂 Selected Metric:</b> {metric_display}<br>
                <b>📈 Graph Type:</b> {graph_type}<br>
                <b>📍 Locations Displayed:</b> {num_locations}<br>
                <b>📊 Total Data Points:</b> {num_points}<br><br>

                <b>🔍 Analysis Summary:</b><br>{summary_text}<br><br>
                <b>📌 Quick Insight:</b><br>{quick_insight}
                </div>
                """,
                unsafe_allow_html=True
            )





# =========================
# 🎯 Styled KPI Cards (Dark Theme)
# =========================

st.markdown("## 🔹 Key Metrics")

# --- Styles ---
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

label_style = "font-weight: bold; color: #FFD700; font-size: 16px;"
value_style = "font-size: 30px; font-weight: light; color: #ffffff;"

# --- KPI Calculations ---
avg_temp = df_filtered['temperature_celsius'].mean()
avg_humidity = df_filtered['humidity'].mean()
avg_wind = df_filtered['wind_mph'].mean()
avg_uv = df_filtered['uv_index'].mean()

# --- Layout ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div style="{box_style}">
            <div style="{label_style}">Avg. Temperature</div>
            <div style="{value_style}">{avg_temp:.2f} °C</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="{box_style}">
            <div style="{label_style}">Avg. Humidity</div>
            <div style="{value_style}">{avg_humidity:.2f} %</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style="{box_style}">
            <div style="{label_style}">Avg. Wind Speed</div>
            <div style="{value_style}">{avg_wind:.2f} mph</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div style="{box_style}">
            <div style="{label_style}">Avg. UV Index</div>
            <div style="{value_style}">{avg_uv:.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


