import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_API_URL")


def fetch_data(endpoint, params=None):
    """
    Fetch data from the OpenF1 API and return it as a DataFrame.

    Args:
        endpoint (str): API endpoint (e.g., "meetings", "sessions").
        params (dict): Optional query parameters for the API.

    Returns:
        pd.DataFrame: DataFrame containing the API response data.

    Notes:
        Using `requests.get(url, params=params)` sometimes causes issues with
        formatting, so we manually prepare the full URL using `requests.Request`.
    """
    
    if params is None:
        params ={}

    url = f"{BASE_URL}{endpoint}"
    full_url = requests.Request('GET', url, params=params).prepare().url
    response = requests.get(full_url)
    response.raise_for_status()
    
    return pd.DataFrame(response.json())


@st.cache_data
def fetch_sessions(meeting_key):
    # Returns all session types (FP1, Qualifying, Race) for a specific Grand Prix.
    df = fetch_data("sessions", {"meeting_key": meeting_key})

    return pd.DataFrame(df.drop_duplicates())


@st.cache_data
def fetch_laps(session_key):
    # Retrieves lap timing data for a given session
    return fetch_data("laps" , {"session_key": session_key})


@st.cache_data
def fetch_stints(session_key):
    # Retrieves tire stint data for a given session
    return fetch_data("stints" , {"session_key": session_key})


@st.cache_data
def fetch_pit_stops(session_key):
    # Retrieves pit stop data for a given session
    return fetch_data("pit" , {"session_key": session_key})


@st.cache_data
def fetch_drivers(session_key):
    # Retrieves driver data for a given session
    return fetch_data("drivers" , {"session_key": session_key})

@st.cache_data
def fetch_results(session_key):
    # Retrieves results data for a given session
    return fetch_data("session_result", {"session_key": session_key})