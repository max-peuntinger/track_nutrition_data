from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go


from charts_plotly import create_layout
from data_manager import DataManager, CSVReader
# from data_manager import data_manager_reader

def create_layout():
    # Define your Dash layout here
    layout = html.Div([
        html.H1("Nutrition Dashboard"),
        dcc.Graph(id='calories-bar-chart'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000,  # Update every 1 second
            n_intervals=0
        ),
        # Add more Dash components as needed
    ])
    return layout

def update_graph_live(n):
    # Load the data
    df = data_manager_reader.read_data()

    # Convert timestamp to datetime format in UTC
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    # Subtract 2 hours from each timestamp to make 00:00 to 02:00 as previous day
    df["timestamp"] = df["timestamp"] - pd.DateOffset(hours=2)

    # Define function to categorize time of day
    def time_of_day(t):
        if 2 <= t.hour < 12:
            return '2-12'
        elif 12 <= t.hour < 17:
            return '12-17'
        elif 17 <= t.hour < 22:
            return '17-22'
        else:
            return '22-2'  # now this includes 00:00 to 02:00 as it is part of the previous day for my day/night cycle

    # Apply function to timestamp
    df["time_of_day"] = df["timestamp"].apply(time_of_day)

    # Extract the date from the timestamp
    df["date"] = df["timestamp"].dt.date

    # Group by date and time of day and sum calories
    grouped = df.groupby(["date", "time_of_day"])["calories"].sum().unstack().fillna(0)

    # Check if the columns exist, if not add them with default value of 0
    for col in ['2-12', '12-17', '17-22', '22-2']:
        if col not in grouped.columns:
            grouped[col] = 0

    # Order the columns
    grouped = grouped[['2-12', '12-17', '17-22', '22-2']]

    # Calculate total calories for each day
    total_calories_per_day = grouped.sum(axis=1)

    # Create the bar chart
    fig = go.Figure(data=[
        go.Bar(name='2-12', x=grouped.index, y=grouped['2-12']),
        go.Bar(name='12-17', x=grouped.index, y=grouped['12-17']),
        go.Bar(name='17-22', x=grouped.index, y=grouped['17-22']),
        go.Bar(name='22-2', x=grouped.index, y=grouped['22-2'])
    ])

    # Add text annotations for total calories
    for i, total_calories in enumerate(total_calories_per_day):
        total_calories_rounded = round(total_calories, 1)  # Round to 1 digit after the decimal point
        fig.add_trace(go.Scatter(
            x=[grouped.index[i]],
            y=[total_calories],
            text=[f"{total_calories_rounded}"],
            mode="text",
            showlegend=False
        ))

    # Change the bar mode
    fig.update_layout(barmode='stack')

    return fig

