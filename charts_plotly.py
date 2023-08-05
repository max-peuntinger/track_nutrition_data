from dash import dcc, html
import dash_bootstrap_components as dbc

def create_layout():
    layout = html.Div([
        dbc.Container([
            html.H1("Calories per Day"),
            dcc.Graph(id='calories-bar-chart'),
            dcc.Interval(
                id='interval-component',
                interval=1*1000,  # in milliseconds
                n_intervals=0
            )
        ])
    ])

    return layout