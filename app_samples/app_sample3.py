import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- Utility Functions and Data Simulation ---

@st.cache_data
def load_simulated_data():
    """
    Simulates loading and initial processing of the GlobalWeatherRepository data.
    Since the real data is large and complex, this creates a realistic subset.
    """
    np.random.seed(42)
    
    countries = ['USA', 'India', 'Brazil', 'Nigeria', 'Germany', 'Australia']
    locations = {
        'USA': ['New York', 'Los Angeles', 'Chicago'],
        'India': ['Mumbai', 'Delhi', 'Bangalore'],
        'Brazil': ['Rio de Janeiro', 'Sao Paulo'],
        'Nigeria': ['Lagos'],
        'Germany': ['Berlin', 'Munich'],
        'Australia': ['Sydney']
    }
    
    data = []
    
    current_time = datetime.now()
    
    # Generate data for multiple cities
    for country, cities in locations.items():
        for city in cities:
            temp = np.random.uniform(5, 40)
            wind = np.random.uniform(1, 50)
            humidity = np.random.randint(30, 100)
            pressure = np.random.uniform(980, 1040)
            aqi = np.random.randint(1, 7)
            uv = np.random.randint(0, 12)
            
            # Simple simulation of condition based on temperature and humidity
            if temp > 30 and humidity < 60:
                condition = 'Sunny'
            elif temp < 10 or humidity > 85:
                condition = 'Rain'
            elif aqi > 4:
                condition = 'Haze/Smog'
            else:
                condition = np.random.choice(['Partly Cloudy', 'Clear', 'Overcast', 'Light Rain'])
            
            # Simulate a recent update time
            last_updated = current_time - timedelta(minutes=np.random.randint(1, 60))
            
            data.append({
                'country': country,
                'location_name': city,
                'latitude': np.random.uniform(-40, 40) if country != 'Australia' else np.random.uniform(-35, -25),
                'longitude': np.random.uniform(-100, 100),
                'temperature_celsius': round(temp, 1),
                'feels_like_celsius': round(temp * 0.9 + humidity * 0.05, 1),
                'wind_mph': round(wind, 1),
                'humidity': humidity,
                'pressure_mb': round(pressure, 1),
                'precip_mm': round(np.random.uniform(0, 10), 1) if 'Rain' in condition else 0.0,
                'cloud': np.random.randint(0, 100),
                'visibility_km': round(np.random.uniform(5, 15), 1),
                'uv_index': uv,
                'air_quality_us-epa-index': aqi,
                'condition_text': condition,
                'last_updated': last_updated.strftime('%Y-%m-%d %H:%M:%S'),
                'wind_direction': np.random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
            })
            
    df = pd.DataFrame(data)
    
    # Post-processing: convert last_updated to datetime object
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    
    return df

# --- Streamlit App Layout ---

st.set_page_config(
    page_title="Global Weather Dashboard (Daily Snapshot)",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🌍"
)

# Load data and apply general styling
df = load_simulated_data()

st.title("🌍 Global Weather Repository Snapshot")
st.markdown("A real-time overview of weather conditions, air quality, and key metrics across major global locations. Data last synchronized on: **{}**".format(df['last_updated'].max().strftime('%Y-%m-%d %H:%M %Z')))

# 1. SIDEBAR FILTERING
with st.sidebar:
    st.header("Dashboard Controls")
    
    # Country Filter
    unique_countries = sorted(df['country'].unique().tolist())
    selected_countries = st.multiselect(
        "Select Countries to View",
        options=unique_countries,
        default=unique_countries[:3],
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

# Apply filters
df_filtered = df[
    (df['country'].isin(selected_countries)) &
    (df['air_quality_us-epa-index'] <= selected_aqi_level) &
    (df['temperature_celsius'] >= temp_range[0]) &
    (df['temperature_celsius'] <= temp_range[1])
]

# Check if data exists after filtering
if df_filtered.empty:
    st.error("No data found for the selected filter combination. Please adjust the controls.")
    st.stop()


# 2. KEY METRICS (KPIs)
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

# 3. GLOBAL MAP VISUALIZATION
st.markdown("---")
st.subheader("Global Weather & Air Quality Map")

# Use Plotly for interactive map
map_fig = px.scatter_geo(
    df_filtered,
    lat='latitude',
    lon='longitude',
    color='temperature_celsius',
    hover_name='location_name',
    size='humidity',
    color_continuous_scale=px.colors.sequential.Plasma,
    title='Global Temperature Distribution & Humidity',
    height=550,
    template='plotly_dark'
)
map_fig.update_geos(
    lataxis_range=[-60, 90], 
    lonaxis_range=[-180, 180], 
    showland=True, 
    landcolor="lightgray"
)
map_fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

st.plotly_chart(map_fig, use_container_width=True)


# 4. TABBED VISUALIZATIONS (Good UI/UX)
st.markdown("---")
st.subheader("Detailed Trend Analysis")
tab1, tab2, tab3 = st.tabs(["🌡️ Temperature & Humidity Trends", "💨 Wind & Pressure", "😷 Air Quality Breakdown"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Temperature vs. Feels Like (°C)")
        temp_fig = px.scatter(
            df_filtered,
            x='temperature_celsius',
            y='feels_like_celsius',
            color='humidity',
            hover_name='location_name',
            title='Actual vs. Feels Like Temperature by Humidity',
            color_continuous_scale=px.colors.sequential.Sunset,
            template='plotly_white'
        )
        st.plotly_chart(temp_fig, use_container_width=True)

    with col2:
        st.markdown("##### Humidity Distribution by Country")
        # Use Altair for a different aesthetic
        import altair as alt
        humidity_chart = alt.Chart(df_filtered).mark_boxplot(extent="min-max").encode(
            x=alt.X('country', title=None),
            y=alt.Y('humidity', title='Humidity (%)'),
            color=alt.Color('country', legend=None)
        ).properties(
            title='Humidity Distribution'
        )
        st.altair_chart(humidity_chart, use_container_width=True)


with tab2:
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("##### Wind Speed & Direction Polar Chart")
        wind_fig = px.bar_polar(
            df_filtered,
            r="wind_mph",
            theta="wind_direction",
            color="wind_mph",
            color_continuous_scale=px.colors.sequential.Agsunset,
            template='plotly_dark',
            title="Wind Speed by Direction"
        )
        st.plotly_chart(wind_fig, use_container_width=True)

    with col4:
        st.markdown("##### Pressure vs. Cloud Cover")
        press_fig = px.scatter(
            df_filtered,
            x='pressure_mb',
            y='cloud',
            color='country',
            hover_name='location_name',
            title='Atmospheric Pressure vs. Cloud Cover (%)'
        )
        st.plotly_chart(press_fig, use_container_width=True)

with tab3:
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("##### Air Quality (US EPA Index) Count")
        # Create a categorical index description
        df_filtered['AQI_Category'] = df_filtered['air_quality_us-epa-index'].map(aqi_options)
        
        aqi_counts = df_filtered.groupby('AQI_Category')['location_name'].count().reset_index()
        aqi_counts.columns = ['AQI_Category', 'Count']
        
        aqi_fig = px.pie(
            aqi_counts,
            values='Count',
            names='AQI_Category',
            title='Air Quality Index Distribution',
            template='plotly_dark',
            hole=0.4
        )
        st.plotly_chart(aqi_fig, use_container_width=True)
        
    with col6:
        st.markdown("##### Current Weather Condition Breakdown")
        condition_counts = df_filtered.groupby('condition_text')['location_name'].count().reset_index()
        condition_counts.columns = ['Condition', 'Count']
        
        condition_fig = px.bar(
            condition_counts,
            x='Condition',
            y='Count',
            color='Condition',
            title='Locations by Weather Condition',
            template='plotly_white'
        )
        st.plotly_chart(condition_fig, use_container_width=True)
        
# 5. RAW DATA TABLE
st.markdown("---")
with st.expander("View Raw Filtered Data Table"):
    st.dataframe(df_filtered, width="stretch")
