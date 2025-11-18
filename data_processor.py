import pandas as pd
import streamlit as st


def process_laps_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare lap data for visualisation

    -Drops laps and sectors without duration
    -Sorts by driver number and lap number

    Args:
        df (pd.DataFrame): Raw lap data from API.

    Returns:
        pd.DataFrame: Cleaned and sorted lap data.
    """
    if df.empty:
        return df
    
    df = df.dropna(subset=[
        "duration_sector_1",
        "duration_sector_2",
        "duration_sector_3",
        "lap_duration"
    ]).copy()

    df["driver_number"] = df["driver_number"].astype(str)
    df["lap_number"] = pd.to_numeric(df["lap_number"], errors="coerce")
    df = df.sort_values(["driver_number", "lap_number"])

    return df

def process_stints_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare stint data for visualisation

    -Sorts by driver number and stint number
    -Fills missing compound values
    -Adds lap_count column

    Args:
        df (pd.DataFrame): Raw stint data from API.

    Returns:
        pd.DataFrame: Cleaned and sorted stint data.
    """
    if df.empty:
        return df
    
    df = df.copy()
    df = df.sort_values(["driver_number", "stint_number"])
    df["compound"] = df["compound"].fillna("Unknown")
    df["lap_count"] = df["lap_end"] - df["lap_start"] + 1
    df["driver_number"] = df["driver_number"].astype(str)

    return df

def process_pit_stops_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare pit stop data for visualisation

    -Drops pit stops without duration
    -Sorts by driver number and lap number

    Args:
        df (pd.DataFrame): Raw pit stop data from API.

    Returns:
        pd.DataFrame: Cleaned and sorted pit stop data.
    """
    if df.empty:
        return df

    df = df.copy()
    df = df[df["pit_duration"].notna()]
    df = df.sort_values(["driver_number", "lap_number"])

    return df

def process_driver_position(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare driver position data

    -Sorts by position and number of laps
    -Replaces missing values with proper finish position

    Args:
        df (pd.DataFrame): Driver position data.

    Returns:
        pd.DataFrame: Cleaned and sorted driver position data.
    """

    if df.empty:
        return df
    
    df = df.copy()
    df = df.sort_values(["position", "number_of_laps"], ascending=[True, False])

    max_position = int(df["position"].max(skipna=True) + 1)
    missing = df["position"].isna().sum()

    df.loc[df["position"].isna(), "position"] = range(max_position, max_position + missing)

    return df


def build_driver_colormap(df: pd.DataFrame) -> dict:
    """
    Create a dictionary that maps driver acronyms to their team color.

    Args:
        driver_df (pd.DataFrame): Driver and team data.

    Returns:
        dict: Dictionary mapping name_acronym to team_colour.
    """
    if df.empty:
        return {}
    
    df = df.copy()

    # Format team colors to always start with '#' for valid CSS color input
    df["team_colour"] = df["team_colour"].apply(
        lambda x: f"#{x}" if not str(x).startswith("#") else x
    )

    return dict(zip(df["name_acronym"], df["team_colour"]))

def process_results_data(df: pd.DataFrame, session_type: str) -> pd.DataFrame:
    """
    Clean and prepare session results data for visualisation

    -Divide operations based on session_type
    -Update position and gap_to_leader based on flags (dnf, dns, dsq)
    -Format position to display as int
    -Replace leader's gap_to_leader with formatted duration
    -Format gap_to_leader's value to include '+' and 's'

    Args:
        df (pd.DataFrame): Session results data.

    Returns:
        pd.DataFrame: Cleaned and formatted session results data.
    """
    if df.empty:
        return df

    df = df.copy()
    
    df["gap_to_leader"] = df["gap_to_leader"].astype("object")
    df["position"] = df["position"].astype("object")
    df["duration"] = df["duration"].astype("object")

    mask_leader = df["gap_to_leader"] == 0

    if session_type in ("Race", "Sprint"):
        for flag in ["dnf", "dns", "dsq"]:
            df.loc[df[flag], ["gap_to_leader", "position"]] = flag.upper()

        df["position"] = df["position"].apply(
            lambda x: int(x) if isinstance(x, (int, float)) and not pd.isna(x) else x
        )
        
        df.loc[mask_leader, "duration"] = df.loc[mask_leader, "duration"].apply(format_race_time)
        df.loc[mask_leader, "gap_to_leader"] = df.loc[mask_leader, "duration"]

        mask_numeric = pd.to_numeric(df["gap_to_leader"], errors="coerce").notna()
        df.loc[mask_numeric & ~mask_leader, "gap_to_leader"] = df.loc[  
            mask_numeric & ~mask_leader, "gap_to_leader"
        ].apply(lambda x: f"+{x:.3f}s")

    elif session_type in ("Qualifying", "Sprint Shootout", "Sprint Qualifying"):
        pass

    else:
        df.loc[mask_leader, "duration"] = df.loc[mask_leader, "duration"].apply(format_lap_time)
        df.loc[mask_leader, "gap_to_leader"] = df.loc[mask_leader, "duration"]

        mask_numeric = pd.to_numeric(df["gap_to_leader"], errors="coerce").notna()
        df.loc[mask_numeric & ~mask_leader, "gap_to_leader"] = df.loc[  
            mask_numeric & ~mask_leader, "gap_to_leader"
        ].apply(lambda x: f"+{x:.3f}s")

    return df



def format_lap_time(seconds):
    minutes = int(seconds // 60)
    sec = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    return f"{minutes:02}:{sec:02}.{millis:03}"


def format_race_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    sec = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)

    return f"{hours}:{minutes:02}:{sec:02}.{millis:03}"

def format_seconds_to_mmss(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)

    return f"{minutes:02}:{secs:02}"
