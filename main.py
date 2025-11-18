import streamlit as st
from data_loader import (
    fetch_data,
    fetch_sessions,
    fetch_laps,
    fetch_stints,
    fetch_drivers,
    fetch_pit_stops,
    fetch_results
)
from data_processor import(
    process_laps_data,
    process_pit_stops_data,
    process_stints_data,
    process_driver_position,
    process_results_data,
    build_driver_colormap
)
from visualiser import(
    plot_lap_times,
    plot_tyre_strategy
)


st.set_page_config(page_title="F1 Dashboard", page_icon="🏎️", layout="wide")
st.title("🏎️ Formula 1 Dashboard")

col1, col2 = st.columns(2)

with col1:
    years = [2023,2024,2025]
    selected_year = st.selectbox("Select Year", years)

    meetings = fetch_data("meetings", {"year": selected_year})
    
    if meetings.empty:
        st.error("No meetings found for this year.")
        st.stop()

    countries = sorted(meetings["country_name"].dropna().unique())
    selected_country = st.selectbox("Select Country", countries)

    filtered_meetings = meetings[meetings["country_name"] == selected_country].copy()
    filtered_meetings["label"] = filtered_meetings["meeting_name"] + ' - ' + filtered_meetings["location"]
    filtered_meetings = filtered_meetings.sort_values(by="meeting_name", ascending=False)

with col2:
    selected_meeting = st.selectbox("Select Grand Prix", filtered_meetings["label"], disabled=True)
    
    # Find selected meeting key
    selected_meeting_key = filtered_meetings.loc[
        filtered_meetings["label"] == selected_meeting, "meeting_key"
    ].values[0]

    sessions = fetch_sessions(selected_meeting_key)
    selected_session = st.selectbox("Select Session", sessions["session_name"])
    
    # Find selected session key
    selected_session_key = sessions.loc[
        sessions["session_name"] == selected_session, "session_key"
    ].values[0]



# Load data
results_df = fetch_results(selected_session_key)
driver_df = fetch_drivers(selected_session_key)
laps_df = fetch_laps(selected_session_key)
stints_df = fetch_stints(selected_session_key)


# Prepare driver info
results_info = results_df[["driver_number", "position", "number_of_laps"]]
driver_df = driver_df.merge(results_info, on="driver_number", how="left")

driver_color_map = build_driver_colormap(driver_df)

driver_info = driver_df[["driver_number", "name_acronym", "position", "number_of_laps"]]
processed_driver_info = process_driver_position(driver_info)

driver_results_info = driver_df[["driver_number", "headshot_url", "full_name", "team_name", "position", "number_of_laps"]]
processed_driver_results = process_driver_position(driver_results_info)

session_results = results_df[[
    "driver_number", "duration", "dnf", "dns", "dsq", "gap_to_leader"
    ]]
session_results = session_results.merge(processed_driver_results, on="driver_number", how="left")

processed_session_results = process_results_data(session_results, selected_session)


# Table with results
with st.expander(f"Session Results for {selected_session} at {selected_country} {selected_year}",
                 expanded=True):
    # if selected_session == "Race":
    with st.container(horizontal_alignment='center'):
        st.data_editor(
            processed_session_results,
            disabled=True,
            hide_index=True,
            # width=800,
            row_height=70,
            column_order=(
                "position", "driver_number", "headshot_url",
                "full_name", "team_name", "number_of_laps", "gap_to_leader"
                ),
            column_config={
                "headshot_url": st.column_config.ImageColumn("Photo")
            }
        )
    # else:
    #     st.warning("No result available for this session")
     



# Lap time chart
with st.expander(f"📈 Lap Time Chart for {selected_session} at {selected_country} {selected_year}",
                 expanded=True):
    processed_laps = process_laps_data(laps_df).merge(processed_driver_info, on="driver_number", how="left")

    if processed_laps.empty:
        st.warning("No lap time data found.")
    else:
        fig = plot_lap_times(processed_laps, driver_color_map)
        st.plotly_chart(fig, width='stretch')


# Tyre strategy plot
with st.expander(f"🛠️ Tyre Strategy for {selected_session} at {selected_country} {selected_year}",
                 expanded=True):
    processed_stints = process_stints_data(stints_df).merge(processed_driver_info, on="driver_number", how="left")

    if processed_stints.empty:
        st.warning("No stints data found.")
    else:
        fig = plot_tyre_strategy(processed_stints, driver_color_map)
        st.plotly_chart(fig, width='stretch')
