import streamlit as st
import pycountry_convert as pc

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

def filter_panel(df, default_country="India"):
    st.sidebar.header("🌐 Weather Filters")

    # Add continent column if missing
    if 'continent' not in df.columns:
        df['continent'] = df['country'].apply(country_to_continent)

    # --- Continent Filter ---
    continents = sorted(df['continent'].dropna().unique())
    select_all_cont = st.sidebar.checkbox("Select All Continents", value=True)
    if select_all_cont:
        selected_continents = continents
    else:
        selected_continents = st.sidebar.multiselect(
            "Select Continent(s)",
            options=continents,
            default=[df[df['country'] == default_country]['continent'].values[0]]
        )

    # --- Country Filter ---
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

    # --- Location Filter ---
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

    # --- Temperature Filter ---
    tmin, tmax = int(df['temperature_celsius'].min()), int(df['temperature_celsius'].max())
    temp_min, temp_max = st.sidebar.slider("🌡️ Temperature (°C)", tmin, tmax, (tmin, tmax))

    # --- Humidity Filter ---
    hmin, hmax = int(df['humidity'].min()), int(df['humidity'].max())
    humidity_min, humidity_max = st.sidebar.slider("💧 Humidity (%)", hmin, hmax, (hmin, hmax))

    # --- Wind Filter ---
    wmin, wmax = int(df['wind_mph'].min()), int(df['wind_mph'].max())
    wind_min, wind_max = st.sidebar.slider("🌬️ Wind Speed (mph)", wmin, wmax, (wmin, wmax))

    return {
        "continent": selected_continents,
        "country": selected_countries,
        "location": selected_locations,
        "temp_min": temp_min,
        "temp_max": temp_max,
        "humidity_min": humidity_min,
        "humidity_max": humidity_max,
        "wind_min": wind_min,
        "wind_max": wind_max
    }
