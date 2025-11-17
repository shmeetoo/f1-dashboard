import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from data_processor import(
    format_lap_time,
    format_seconds_to_mmss
)


def plot_lap_times(lap_time_df: pd.DataFrame, color_map: dict):

    if lap_time_df.empty:
        st.warning("No lap data available for this session.")
        return None
    
    lap_time_df["formatted_lap_time"] = lap_time_df["lap_duration"].apply(format_lap_time)
    lap_time_df["is_pit_out_lap"] = lap_time_df["is_pit_out_lap"].fillna(False).astype(bool)
    
    fig = go.Figure()


    for driver in lap_time_df["name_acronym"].unique():
        driver_data = lap_time_df[lap_time_df["name_acronym"] == driver].copy()
        driver_data = driver_data.sort_values(["lap_number"])

        hover_texts = [
            f"<b>{driver}: {row['driver_number']}</b><br>"
            f"Lap: {row['lap_number']}<br>"
            f"Lap Time: {row['formatted_lap_time']}"
            + ("<br>🔧 PIT" if row['is_pit_out_lap'] else "")
            for _, row in driver_data.iterrows()
        ]

        fig.add_trace(go.Scatter(
            x=driver_data["lap_number"],
            y=driver_data["lap_duration"],
            mode="lines+markers",
            name=driver,
            marker=dict(color=color_map.get(driver, "gray")),
            line=dict(color=color_map.get(driver, "gray")),
            hoverinfo="text",
            hovertext=hover_texts,
            legendrank=driver_data["position"].values[0]
        ))


    fig.update_layout(
        title="Lap Times by Driver",
        xaxis_title="Lap",
        yaxis_title="Lap Time (MM:SS)",
        hovermode="closest",
        height=600
    )

    tick_values = sorted(lap_time_df["lap_duration"].dropna().unique())
    tick_values = [round(val, 0) for val in tick_values if 60 <= val <= 180]
    tick_values = sorted(set(tick_values))[::5]

    fig.update_yaxes(
        tickvals = tick_values,
        ticktext = [format_seconds_to_mmss(val) for val in tick_values]
    )

    return fig


COMPOUND_COLORS = {
    "SOFT": "red",
    "MEDIUM": "yellow",
    "HARD": "white",
    "WET": "blue",
    "INTERMEDIATE": "green",
    "Unknown": "gray"
}


def plot_tyre_strategy(stints_df: pd.DataFrame, color_map: dict):

    if stints_df.empty:
        st.warning("No tyre data available for this session.")
        return None

    stints_df = stints_df.sort_values("position", ascending=False)


    fig = go.Figure()

    for _, row in stints_df.iterrows():
        compound = row["compound"].upper()
        acronym = row["name_acronym"]

        fig.add_trace(go.Bar(
            x=[row["lap_count"]],
            y=[acronym],
            base=row["lap_start"],
            orientation="h",
            marker=dict(color = COMPOUND_COLORS.get(compound, "gray")),
            hovertemplate=(
                f"{acronym}: {row['driver_number']}<br>"
                f"Compound: {compound}<br>"
                f"Laps: {row['lap_count']:.0f}<br>"
                f"Start Lap: {row['lap_start']:.0f}<br>"
                f"End Lap: {row['lap_end']:.0f}"
            ),
            name="",
            showlegend=False
        ))


    y_labels = stints_df["name_acronym"].unique()

    for acronym in y_labels:
        fig.add_annotation(
            x=-3,
            y=acronym,
            xref="x",
            yref="y",
            text=f"<b>{acronym}</b>",
            showarrow=False,
            font=dict(
                color=color_map.get(acronym, "#AAA"),
                size=12
            ),
            align="right"
        )

    fig.update_layout(
        title="Tire Strategy by Driver",
        xaxis_title="Lap Number",
        yaxis_title="",
        barmode="stack",
        height=600,
        margin=dict(l=120), 
    )

    fig.update_yaxes(showticklabels=False)

    return fig

    