from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from data_tools.data_manager import DataReader
import pandas as pd
from typing import Optional

data_reader = DataReader("data/bodyweight.db")
bodyweight_data = data_reader.read_bodyweight_data()
fig = px.line(bodyweight_data, x="date", y="bodyweight")
fig.update_layout(yaxis=dict(range=[0, None]))


def create_stacked_bar_chart():
    df = data_reader.read_daily_macros()
    df['total'] = df['carbs'] + df['fats'] + df['proteins']
    df['carbs'] = df['carbs'] / df['total'] * 100
    df['fats'] = df['fats'] / df['total'] * 100
    df['proteins'] = df['proteins'] / df['total'] * 100
    df_melted = df.melt(id_vars='date', value_vars=['carbs', 'fats', 'proteins'], var_name='category', value_name='percentage')
    return px.bar(df_melted, x='date', y='percentage', color='category', title='Daily Macronutrient Distribution', labels={'percentage': 'Percentage (%)'})


def preprocess_cycling_data():
    data_reader = DataReader(db_name="data/bodyweight.db")
    cycling_data = data_reader.read_cycling_data()
    return cycling_data


def create_cycling_chart(start_date: Optional[str] = None, end_date: Optional[str] = None, time_frame: str = "daily"):
    df = preprocess_cycling_data()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    start_date = pd.to_datetime(start_date) if start_date else None
    end_date = pd.to_datetime(end_date) if end_date else None
    if start_date:
        df = df[df['timestamp'] >= start_date]
    if end_date:
        df = df[df['timestamp'] <= end_date]

    if time_frame == "weekly":
        df['week_start'] = df['timestamp'].dt.to_period('W').dt.start_time
        grouped_data = df.groupby('week_start')['duration'].mean().reset_index()
        grouped_data['timestamp'] = grouped_data['week_start']
    elif time_frame == "monthly":
        grouped_data = df.groupby(df['timestamp'].dt.to_period('M'))['duration'].mean().reset_index()
        grouped_data['timestamp'] = grouped_data['timestamp'].dt.to_timestamp()
    else:
        grouped_data = df

    fig = px.bar(grouped_data, x="timestamp", y="duration")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title="",
            showline=False
        ),
        yaxis=dict(
            title="",
            showline=False
        )
    )
    return fig


fig_cycling = create_cycling_chart()


def create_layout():
    fig_macronutrients = create_stacked_bar_chart()
    layout = html.Div(
        [
            dbc.Container(
                [
                    html.Div(
                        [
                            dcc.DatePickerRange(
                                id="date-picker-range",
                                start_date_placeholder_text="Start Date",
                                end_date_placeholder_text="End Date",
                            )
                        ],
                        style={"display": "block", "text-align": "left"},
                    ),
                    dcc.Dropdown(
                        id="time-frame-dropdown",
                        options=[
                            {"label": "Daily", "value": "daily"},
                            {"label": "Weekly", "value": "weekly"},
                            {"label": "Monthly", "value": "monthly"},
                        ],
                        value="daily",  # default value
                    ),
                    html.Div(
                        [
                            html.H4("Calories per Day"),
                            dcc.Graph(id="calories-bar-chart"),
                        ],
                        style={
                            "width": "50%",
                            "height": "400px",
                            "display": "inline-block",
                            "margin-bottom": "100px"
                        },
                    ),
                    html.Div(
                        [
                            html.H4("Weight Over Time"),
                            dcc.Graph(id="weight-line-chart", figure=fig),
                        ],
                        style={
                            "width": "50%",
                            "height": "400px",
                            "display": "inline-block",
                            "margin-bottom": "100px"
                        },
                    ),
                    html.Div(
                        [
                            html.H4("Share of Macronutrients per day"),
                            dcc.Graph(id='macronutrients-stacked-bar-chart', figure=fig_macronutrients),
                        ],
                        style={
                            "width": "50%",
                            "height": "400px",
                            "display": "inline-block",
                            "margin-bottom": "100px"
                        }
                    ),
                    html.Div(
                        [
                            html.H4("Cycling Duration per Day"),
                            dcc.Graph(id='cycling-line-chart', figure=fig_cycling),
                        ],
                        style={
                            "width": "50%",
                            "height": "400px",
                            "display": "inline-block",
                            "margin-bottom": "100px"
                        }
                    )
               
                ]
            ),
            dcc.Interval(
                id="interval-component",
                interval=1 * 1000,  # in milliseconds
                n_intervals=0,
            ),
        ]
    )

    return layout
