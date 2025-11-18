import streamlit as st
import pandas as pd
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_API_URL")

@st.cache_data(ttl=3600)
def fetch_data(endpoint, params=None):
    """
    Fetch data from the OpenF1 API and return it as a DataFrame.

    Args:
        endpoint (str): API endpoint (e.g., "meetings", "sessions").
        params (dict): Optional query parameters for the API.

    Returns:
        pd.DataFrame: DataFrame containing the API response data.

    Notes:
        Using retry and timeout increases stability and resilience
        and fixes occasional API errors.
    """
    
    if params is None:
        params ={}

    url = f"{BASE_URL}{endpoint}"

    last_exc = None
    for _ in range(2): # Retry
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            return pd.DataFrame(r.json())
        except Exception as e:
            last_exc = e
            time.sleep(0.3) # Timeout 0.3s

    st.error(f"API error: {last_exc}")
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_sessions(meeting_key):
    # Returns all session types (FP1, Qualifying, Race) for a specific Grand Prix.
    df = fetch_data("sessions", {"meeting_key": meeting_key})

    return pd.DataFrame(df.drop_duplicates())


@st.cache_data(ttl=3600)
def fetch_laps(session_key):
    # Retrieves lap timing data for a given session
    df = fetch_data("laps" , {"session_key": session_key})

    if not df.empty:
        df["driver_number"] = df["driver_number"].astype(str)
    
    return df


@st.cache_data(ttl=3600)
def fetch_stints(session_key):
    # Retrieves tire stint data for a given session
    df = fetch_data("stints" , {"session_key": session_key})

    if not df.empty:
        df["driver_number"] = df["driver_number"].astype(str)
    
    return df


@st.cache_data(ttl=3600)
def fetch_pit_stops(session_key):
    # Retrieves pit stop data for a given session
    df = fetch_data("pit" , {"session_key": session_key})

    if not df.empty:
        df["driver_number"] = df["driver_number"].astype(str)
    
    return df


@st.cache_data(ttl=3600)
def fetch_drivers(session_key):
    # Retrieves driver data for a given session
    df = fetch_data("drivers" , {"session_key": session_key})

    if not df.empty:
        df["driver_number"] = df["driver_number"].astype(str)
    
    return df

@st.cache_data(ttl=3600)
def fetch_results(session_key):
    # Retrieves results data for a given session
    df = fetch_data("session_result" , {"session_key": session_key})

    if not df.empty:
        df["driver_number"] = df["driver_number"].astype(str)
    
    return df