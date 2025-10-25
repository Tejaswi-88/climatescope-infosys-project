# dashboard/utils/viz_utils.py
import plotly.express as px
import plotly.graph_objects as go

def create_animated_weather_map(df):
    """Create animated map showing weather changes over time"""
    if 'last_updated' not in df.columns:
        return None
    
    fig = px.scatter_geo(
        df,
        lat='latitude',
        lon='longitude',
        color='temperature_celsius',
        size='wind_mph',
        animation_frame=df['last_updated'].dt.date,
        title="Animated Global Weather Changes",
        color_continuous_scale="Viridis"
    )
    return fig