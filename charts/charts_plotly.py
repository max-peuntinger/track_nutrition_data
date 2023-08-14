from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from data_tools.data_manager import SQLite3Reader

sql3reader = SQLite3Reader("data/bodyweight.db")
bodyweight_data = sql3reader.read_data("SELECT * FROM bodyweight")
# Create a line chart
fig = px.line(bodyweight_data, x='date', y='bodyweight')
fig.update_layout(yaxis=dict(range=[0, None]))

def create_layout():
    layout = html.Div([
        dbc.Container([
            html.Div([
                html.Div([
                    html.H4('Calories per Day'),
                    dcc.Graph(id='calories-bar-chart'),
                ], style={'width': '50%', 'height': '400px', 'display': 'inline-block'}),
                html.Div([
                    html.H4("Weight Over Time"),
                    dcc.Graph(id='weight-line-chart', figure=fig),
                ], style={'width': '50%', 'height': '400px', 'display': 'inline-block'}),
            ]),
            dcc.Interval(
                id='interval-component',
                interval=1*1000,  # in milliseconds
                n_intervals=0
            )
        ])
    ])
    return layout
