from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from data_manager import CSVReader


csv_reader = CSVReader("weight.csv")
weight_data = csv_reader.read_data()

# Create a line chart
fig = px.line(weight_data, x='date', y='bodyweight', title='Weight Over Time')

def create_layout():
    layout = html.Div([
        dbc.Container([
            html.H1('Calories per Day'),
            dcc.Graph(id='calories-bar-chart'),
            html.H1("Weight Over Time"),
            dcc.Graph(id='weight-line-chart', figure=fig),
            dcc.Interval(
                id='interval-component',
                interval=1*1000,  # in milliseconds
                n_intervals=0
            )
        ])
    ])

    return layout
