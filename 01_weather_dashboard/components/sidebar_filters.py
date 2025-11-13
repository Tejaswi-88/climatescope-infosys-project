import streamlit as st
import pandas as pd
import requests
import pycountry_convert as pc

# ============================
# 🌎 Detect User Country & Continent
# ============================
def get_user_country_and_continent():
    """Detect user's country and continent from IP (fallback to India/Asia)."""
    try:
        ip_info = requests.get('https://ipinfo.io', timeout=3).json()
        country_code = ip_info.get('country', None)
        if country_code:
            country_name = pc.country_alpha2_to_country_name(country_code)
            continent_code = pc.country_alpha2_to_continent_code(country_code)
            continent_map = {
                'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe',
                'NA': 'North America', 'OC': 'Oceania',
                'SA': 'South America', 'AN': 'Antarctica'
            }
            continent_name = continent_map.get(continent_code, 'Unknown')
            return country_name, continent_name
    except Exception:
        pass
    return "India", "Asia"  # fallback defaults


# ============================
# 📍 Sidebar Filters (Smart Defaults + Dynamic Select All)
# ============================
def sidebar_location_filters(df: pd.DataFrame):
    """Unified sidebar filter with continent → country → location hierarchy."""
    st.sidebar.header("📍 Global Geographic Filters")

    # Get user defaults
    default_country, default_continent = get_user_country_and_continent()

    # --- Continent Filter ---
    continents = sorted(df['continent'].dropna().unique())
    select_all_cont = st.sidebar.checkbox("🌐 Select All Continents", value=False)
    if select_all_cont:
        selected_continents = continents
    else:
        selected_continents = st.sidebar.multiselect(
            "Select Continent(s)",
            options=continents,
            default=[default_continent] if default_continent in continents else [continents[0]]
        )

    # --- Country Filter ---
    countries_in_selected_cont = sorted(
        df[df['continent'].isin(selected_continents)]['country'].dropna().unique()
    )

    # 🔒 Safe default initialization
    if not countries_in_selected_cont:
        countries_in_selected_cont = sorted(df['country'].dropna().unique())

    select_all_countries = st.sidebar.checkbox("🏳️ Select All Countries", value=False)
    if select_all_countries:
        selected_countries = countries_in_selected_cont
    else:
        selected_countries = st.sidebar.multiselect(
            "Select Country(s)",
            options=countries_in_selected_cont,
            default=[default_country]
            if default_country in countries_in_selected_cont
            else [countries_in_selected_cont[0]]
        )

    # --- Location Filter ---
    locations_in_selected_countries = sorted(
        df[df['country'].isin(selected_countries)]['location_name'].dropna().unique()
    )

    if not locations_in_selected_countries:
        locations_in_selected_countries = sorted(df['location_name'].dropna().unique())

    select_all_locations = st.sidebar.checkbox("📍 Select All Locations", value=True)
    if select_all_locations:
        selected_locations = locations_in_selected_countries
    else:
        selected_locations = st.sidebar.multiselect(
            "Select Location(s)",
            options=locations_in_selected_countries,
            default=locations_in_selected_countries
        )

    # --- Apply Filters Safely ---
    filtered_df = df[
        df['continent'].isin(selected_continents)
        & df['country'].isin(selected_countries)
        & df['location_name'].isin(selected_locations)
    ]

    # --- Persist selections ---
    st.session_state['continent'] = selected_continents
    st.session_state['country'] = selected_countries
    st.session_state['location'] = selected_locations

    st.sidebar.markdown("---")

    return filtered_df
