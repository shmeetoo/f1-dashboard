import streamlit as st
from data_loarder import (
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
    available_years = [2023,2024,2025]
    selected_year = st.selectbox("Select Year", available_years)

    all_meetings = fetch_data("meetings", {"year": selected_year})
    
    if all_meetings.empty:
        st.error("No meetings found for this year.")
        st.stop()

    available_countries = sorted(all_meetings["country_name"].dropna().unique())
    selected_country = st.selectbox("Select Country", available_countries)

    filtered_meetings = all_meetings[all_meetings["country_name"] == selected_country].copy()
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



# Create and process auxiliary DataFrames
results_df = fetch_results(selected_session_key)
results_info = results_df[["driver_number", "position", "number_of_laps"]]
# results_info

driver_df = fetch_drivers(selected_session_key)
driver_df = driver_df.merge(results_info, on="driver_number", how="left")
driver_df["driver_number"] = driver_df["driver_number"].astype(str)
# driver_df

driver_color_map = build_driver_colormap(driver_df)

driver_info = driver_df[["driver_number", "name_acronym", "position", "number_of_laps"]]
processed_driver_info = process_driver_position(driver_info)
# processed_driver_info

driver_info_results = driver_df[["driver_number", "headshot_url", "full_name", "team_name", "position", "number_of_laps"]]
processed_driver_info_results = process_driver_position(driver_info_results)

session_results = results_df[[
    "driver_number", "duration", "dnf", "dns", "dsq", "gap_to_leader"
    ]]

session_results["driver_number"] = session_results["driver_number"].astype(str)
session_results = session_results.merge(processed_driver_info_results, on="driver_number", how="left")
# session_results["duration"] = [format_lap_time(val) for val in session_results["duration"]]

tmp = process_results_data(session_results, selected_session)
# selected_session
# tmp
# Table with results
with st.expander(f"Session Results for {selected_session} at {selected_country} {selected_year}",
                 expanded=True):
    
    # if selected_session == "Race":
    with st.container(horizontal_alignment='center'):

        st.data_editor(
            tmp,
            disabled=tmp,
            hide_index=True,
            # width=800,
            row_height=70,
            column_order=(
                "position", "driver_number", "headshot_url", "full_name", "team_name", "number_of_laps", "gap_to_leader"
                ),
            column_config={
                "headshot_url": st.column_config.ImageColumn(
                    "Photo",
                )
            }
        )
    # else:
    #     st.warning("No result available for this session")
     



# # Lap time chart
with st.expander(f"📈 Lap Time Chart for {selected_session} at {selected_country} {selected_year}",
                 expanded=True):

    lap_df = fetch_laps(selected_session_key)
    processed_df = process_laps_data(lap_df)

    processed_df["driver_number"] = processed_df["driver_number"].astype(str)
    processed_df = processed_df.merge(processed_driver_info, on="driver_number", how="left")


    if processed_df.empty:
        st.warning("No lap time data found.")
    else:
        fig = plot_lap_times(processed_df, driver_color_map)
        st.plotly_chart(fig, width='stretch')


# Tyre strategy plot
with st.expander(f"🛠️ Tyre Strategy for {selected_session} at {selected_country} {selected_year}",
                 expanded=True):
        
    stints_df = fetch_stints(selected_session_key)
    processed_stints = process_stints_data(stints_df)

    processed_stints["driver_number"] = processed_stints["driver_number"].astype(str)
    processed_stints = processed_stints.merge(processed_driver_info, on="driver_number", how="left")


    if processed_stints.empty:
        st.warning("No stints data found.")
    else:
        fig = plot_tyre_strategy(processed_stints, driver_color_map)
        st.plotly_chart(fig, width='stretch')

# processed_stints