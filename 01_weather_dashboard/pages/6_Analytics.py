import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry_convert as pc
import requests

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



# ==========================
# Page config
# ==========================
st.set_page_config(page_title="Analytics & Trends", page_icon="📈", layout="wide")



# Numeric Filters
temp_min, temp_max = st.sidebar.slider(
    "🌡️ Temperature Range (°C)",
    float(df["temperature_celsius"].min()), float(df["temperature_celsius"].max()),
    (float(df["temperature_celsius"].min()), float(df["temperature_celsius"].max()))
)

humidity_min, humidity_max = st.sidebar.slider(
    "💧 Humidity Range (%)",
    float(df["humidity"].min()), float(df["humidity"].max()),
    (float(df["humidity"].min()), float(df["humidity"].max()))
)

wind_min, wind_max = st.sidebar.slider(
    "🌬️ Wind Speed (mph)",
    float(df["wind_mph"].min()), float(df["wind_mph"].max()),
    (float(df["wind_mph"].min()), float(df["wind_mph"].max()))
)

# ==========================
# Filtered DataFrame
# ==========================
filtered_df = df[
    df['continent'].isin(selected_continents) &
    df['country'].isin(selected_countries) &
    df['location_name'].isin(selected_locations) &
    (df['temperature_celsius'] >= temp_min) &
    (df['temperature_celsius'] <= temp_max) &
    (df['humidity'] >= humidity_min) &
    (df['humidity'] <= humidity_max) &
    (df['wind_mph'] >= wind_min) &
    (df['wind_mph'] <= wind_max)
]

filtered_df['last_updated'] = pd.to_datetime(filtered_df['last_updated'], errors='coerce')

# ==========================
# Page Content Header
# ==========================
st.markdown("""
    <h1 style='text-align: center; color: #FF4B4B; font-size: 48px; font-family: "Segoe UI", sans-serif;margin-top: -50px;'>
        📈 Weather Analytics & Trends
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
Analyze temperature, humidity, wind, UV, and air quality trends over time.
</h6>""", unsafe_allow_html=True)


# ==========================
# Main Dashboard Radio Buttons
# ==========================
st.markdown("### Dashboard Controls")

col1, col2 = st.columns(2) 

with col1:
    agg_level = st.radio(
        "Aggregation Level",
        ["Continent", "Country", "Location"],
        index=1  # Default = "Country"
    )

with col2:
    time_aggregation = st.radio(
        "Time Aggregation",
        ["Yearly", "Monthly", "Weekly", "Daily"],
        index=2  # Default = "Weekly"
    )


# ==========================
# Prepare Data for Plotting
# ==========================
if filtered_df.empty:
    st.warning("No data available for the selected filters.")
else:
    df_plot = filtered_df.copy()

    # Determine group column based on aggregation level
    if agg_level == "Continent":
        group_col = 'continent'
    elif agg_level == "Country":
        group_col = 'country'
    else:
        group_col = 'location_name'

    # Time aggregation
    if time_aggregation == "Daily":
        df_plot['time_period'] = df_plot['last_updated'].dt.date
    elif time_aggregation == "Weekly":
        df_plot['time_period'] = df_plot['last_updated'].dt.to_period("W").apply(lambda r: r.start_time)
    elif time_aggregation == "Monthly":
        df_plot['time_period'] = df_plot['last_updated'].dt.to_period("M").apply(lambda r: r.start_time)
    elif time_aggregation == "Yearly":
        df_plot['time_period'] = df_plot['last_updated'].dt.year


    numeric_cols = df_plot.select_dtypes(include='number').columns.tolist()

    df_agg = df_plot.groupby(
        ['time_period', group_col], as_index=False
    )[numeric_cols].mean()

    # ==========================
    # Plot Graphs
    # ==========================
    styled_header("🌡️ Temperature Trend")
    fig_temp = px.line(
        df_agg,
        x='time_period',
        y='temperature_celsius',
        color=group_col,
        title=f"Temperature Trend ({agg_level}, {time_aggregation})",
        template="plotly_white"
    )
    st.plotly_chart(fig_temp, use_container_width=True)

    styled_header("💧 Humidity Trend")
    fig_hum = px.line(
        df_agg,
        x='time_period',
        y='humidity',
        color=group_col,
        title=f"Humidity Trend ({agg_level}, {time_aggregation})",
        template="plotly_white"
    )
    st.plotly_chart(fig_hum, use_container_width=True)

    styled_header("🌬️ Wind Speed Trend")
    fig_wind = px.line(
        df_agg,
        x='time_period',
        y='wind_mph',
        color=group_col,
        title=f"Wind Speed Trend ({agg_level}, {time_aggregation})",
        template="plotly_white"
    )
    st.plotly_chart(fig_wind, use_container_width=True)


# ==========================
# Extreme Weather Tables with Multi-select & Display Mode
# ==========================
st.markdown("---")
styled_header("🚨 Extreme Weather Events")

# -------------------
# User settings
# -------------------
top_n = st.slider(
    "Select number of rows to display in top/least metrics:",
    min_value=3, max_value=20, value=5, step=1
)

highlight_country = st.selectbox(
    "Highlight rows for country:",
    options=["All"] + sorted(filtered_df['country'].unique())
)

highlight_location = st.selectbox(
    "Highlight rows for location:",
    options=["All"] + sorted(filtered_df['location_name'].unique())
)

# -------------------
# Display Mode
# -------------------
display_mode = st.radio(
    "📊 Display Mode:",
    options=["Tables Only", "Maps Only", "Both"],
    index=2
)

# -------------------
# Helper functions
# -------------------
def format_table(df, value_col, value_name):
    df = df.reset_index(drop=True)
    df.insert(0, "S.No", range(1, len(df)+1))
    if value_col in df.columns:
        df[value_col] = df[value_col].round(2)
        df = df.rename(columns={value_col: value_name})
    return df

def safe_top(df, col, n, ascending=False):
    if col not in df.columns:
        return pd.DataFrame()
    agg_df = df.groupby(['location_name','country'], as_index=False)[col].mean()
    return agg_df.nlargest(n, col) if not ascending else agg_df.nsmallest(n, col)

def highlight_rows(row):
    if (highlight_country != "All" and row['country'] == highlight_country) or \
       (highlight_location != "All" and row['location_name'] == highlight_location):
        return ['background-color: yellow']*len(row)
    else:
        return ['']*len(row)

# -------------------
# Define all metrics and multi-select options
# -------------------
tabs = {
    "All Extremes": ["temperature_celsius","uv_index","humidity","precip_mm","wind_mph","visibility_km","air_quality_us-epa-index"],
    "Hottest / Coldest": ["temperature_celsius"],
    "Highest / Lowest UV": ["uv_index"],
    "Most / Least Humid": ["humidity"],
    "Rainiest / Driest": ["precip_mm"],
    "Windiest / Calmest": ["wind_mph"],
    "Most / Least Visible": ["visibility_km"],
    "Most / Least Polluted": ["air_quality_us-epa-index"]
}

selected_tabs = st.multiselect(
    "Select Extreme Categories to display:",
    options=list(tabs.keys()),
    default=["All Extremes"]
)

# -------------------
# Metric color scales
# -------------------
metric_colors = {
    "temperature_celsius": "Reds",        
    "humidity": "Blues",                  
    "precip_mm": "Greens",               
    "uv_index": "Purples",                
    "wind_mph": "Oranges",               
    "visibility_km": "Greys",             
    "air_quality_us-epa-index": "Inferno" 
}
# -------------------
# Display tables and/or maps for selected tabs
# -------------------
for selected_tab in selected_tabs:
    for metric_name, col_name in [
        ("Temperature (°C)", "temperature_celsius"),
        ("UV Index", "uv_index"),
        ("Humidity (%)", "humidity"),
        ("Precipitation (mm)", "precip_mm"),
        ("Wind Speed (mph)", "wind_mph"),
        ("Visibility (km)", "visibility_km"),
        ("AQI (Air Quality Index)", "air_quality_us-epa-index")
    ]:
        # Skip metrics not in selected tab (unless All Extremes)
        if col_name not in tabs[selected_tab] and selected_tab != "All Extremes":
            continue

        # -------------------
        # Top / Least tables
        # -------------------
        if display_mode in ["Tables Only", "Both"]:
            top_df = safe_top(filtered_df, col_name, top_n, ascending=False)
            least_df = safe_top(filtered_df, col_name, top_n, ascending=True)

            top_df = format_table(top_df[['location_name','country',col_name]], col_name, metric_name)
            least_df = format_table(least_df[['location_name','country',col_name]], col_name, metric_name)

            st.markdown(f"### 🔝 Top {top_n} {metric_name} Locations")
            st.dataframe(top_df.style.apply(highlight_rows, axis=1))
            st.markdown(f"### 🔽 Bottom {top_n} {metric_name} Locations")
            st.dataframe(least_df.style.apply(highlight_rows, axis=1))

        # -------------------
        # Choropleth Map
        # -------------------
        if display_mode in ["Maps Only", "Both"] and col_name in filtered_df.columns:
            # Aggregate by country
            map_df = filtered_df.groupby('country', as_index=False)[col_name].mean()

            # Create choropleth map
            fig_map = px.choropleth(
                map_df,
                locations='country',
                locationmode='country names',
                color=col_name,
                color_continuous_scale=metric_colors.get(col_name, 'Viridis'),
                title=f"🌎 Global {metric_name} Distribution",
                labels={col_name: metric_name},
                projection='natural earth',
            )

            # Update layout for transparent background
            fig_map.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)', 
                geo=dict(
                    bgcolor='rgba(0,0,0,0)',
                    lakecolor='rgba(0,0,0,0)',
                    showcoastlines=True,
                    coastlinecolor='rgba(255,255,255,0.2)',
                    showland=True,
                    landcolor='#2A2A2A',
                    showcountries=True,
                    countrycolor='rgba(255, 255, 255, 0.2)',
                ),
                coloraxis_colorbar=dict(
                    title=metric_name,
                    tickfont=dict(color='white'),
                ),
                title_font=dict(color='white')
            )

            st.plotly_chart(fig_map, use_container_width=True)
