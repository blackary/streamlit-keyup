import pandas as pd
import streamlit as st
from st_keyup import st_keyup


@st.experimental_singleton
def get_cities() -> pd.DataFrame:
    url = "https://raw.githubusercontent.com/grammakov/USA-cities-and-states/master/us_cities_states_counties.csv"
    return pd.read_csv(url, sep="|")


cities = get_cities()

debounce = st.checkbox("Add 0.5s debounce?")

name = st_keyup("Enter city name", debounce=500 if debounce else None)

if name:
    filtered = cities[cities.City.str.lower().str.contains(name.lower(), na=False)]
else:
    filtered = cities

st.write(len(filtered), "cities found")
st.write(filtered)
