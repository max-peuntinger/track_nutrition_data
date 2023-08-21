from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from data_tools.data_manager import DataReader
import pandas as pd


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
    df = pd.read_csv("data/biking.csv")
    print(df.columns) 
    df['duration_in_min'] = df['duration_in_s'].fillna(0) / 60
    return df


def create_cycling_chart():
    df = preprocess_cycling_data()
    fig = px.bar(df, x="timestamp", y="duration_in_min")
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title="",             # Hide x-axis label
            showline=False        # Hide x-axis line
        ),
        yaxis=dict(
            title="",             # Hide y-axis label
            showline=False        # Hide y-axis line
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
