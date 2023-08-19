from datetime import datetime
import pandas as pd
from typing import Optional, Any
import plotly.graph_objects as go
from dash import Dash
from dash.dependencies import Input, Output
from flask import Flask
from flask_bootstrap import Bootstrap
import plotly.express as px
from data_tools.data_processing import filter_data_by_date, time_of_day
from data_tools.data_manager import DataReader
from charts.charts_plotly import create_layout
from routes import register_routes

app = Flask(__name__)
register_routes(app)
Bootstrap(app)
app.secret_key = "your_secret_key"
dash_app = Dash(__name__, server=app, url_base_pathname="/dashboard/")
dash_app.layout = create_layout()


@dash_app.callback(
    Output("calories-bar-chart", "figure"),
    [
        Input("interval-component", "n_intervals"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("time-frame-dropdown", "value"),
    ],
)
def update_graph_live(
    _: Any, start_date: Optional[str], end_date: Optional[str], time_frame: str
) -> go.Figure:
    """
    Updates the calories bar chart on the dashboard in real-time.

    This callback function is triggered by changes in the specified inputs, including the interval component, date picker range, and time frame dropdown.
    It reads the food eaten data from the database, filters and groups the data based on the selected time frame, and constructs a bar chart to represent the total calories consumed during different time intervals of the day.

    Parameters:
        _: Any (Unused parameter, typically representing the interval component)
        start_date: Optional[str] (The start date for filtering the data, in the format "YYYY-MM-DD")
        end_date: Optional[str] (The end date for filtering the data, in the format "YYYY-MM-DD")
        time_frame: str (The selected time frame for grouping the data, being, "daily, "weekly", "monthly")

    Returns:
        go.Figure: A Plotly Figure object representing the bar chart of total calories consumed.

    Note:
        The function handles different time frames ("weekly", "monthly") and ensures that all required columns are present in the grouped data. It also adds text annotations for total calories on the chart.
    """
    datareader = DataReader("data/bodyweight.db")
    df: pd.DataFrame = datareader.read_food_eaten_data()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["timestamp"] = df["timestamp"]

    df["time_of_day"] = df["timestamp"].apply(time_of_day)
    df["date"] = df["timestamp"].dt.date
    df["date"] = pd.to_datetime(df["date"])
    start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    filtered_data_df = filter_data_by_date(df, start_date, end_date)

    grouped = (
        filtered_data_df.groupby(["date", "time_of_day"])["calories"]
        .sum()
        .unstack()
        .fillna(0)
    )

    grouped.index = pd.to_datetime(grouped.index)

    if time_frame == "weekly":
        weekly_totals = grouped.resample("W-MON", closed="left", label="left").sum()
        days_with_data_weekly = grouped.resample(
            "W-MON", closed="left", label="left"
        ).apply(lambda x: x.index.nunique())
        grouped = weekly_totals.divide(days_with_data_weekly, axis=0)
    elif time_frame == "monthly":
        monthly_totals = grouped.resample("M").sum()
        days_with_data_monthly = grouped.resample("M").apply(
            lambda x: x.index.nunique()
        )
        grouped = monthly_totals.divide(days_with_data_monthly, axis=0)

    for col in ["2-12", "12-17", "17-22", "22-2"]:
        if col not in grouped.columns:
            grouped[col] = 0

    grouped = grouped[["2-12", "12-17", "17-22", "22-2"]]
    total_calories_per_day = grouped.sum(axis=1)

    fig = go.Figure(
        data=[
            go.Bar(name="2-12", x=grouped.index, y=grouped["2-12"]),
            go.Bar(name="12-17", x=grouped.index, y=grouped["12-17"]),
            go.Bar(name="17-22", x=grouped.index, y=grouped["17-22"]),
            go.Bar(name="22-2", x=grouped.index, y=grouped["22-2"]),
        ]
    )
    # Add text annotations for total calories
    for i, total_calories in enumerate(total_calories_per_day):
        total_calories_rounded = round(total_calories, 1)
        fig.add_trace(
            go.Scatter(
                x=[grouped.index[i]],
                y=[total_calories],
                text=[f"{total_calories_rounded}"],
                mode="text",
                showlegend=False,
            )
        )
    fig.update_layout(barmode="stack", margin=dict(l=20, r=20, t=20, b=60))
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showline=False, zeroline=False)
    fig.update_yaxes(showline=False, zeroline=False)

    return fig


@dash_app.callback(
    Output("macronutrients-stacked-bar-chart", "figure"),
    [
        Input("interval-component", "n_intervals"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    ],
)
def update_macronutrients_chart(
    _: Any, start_date: Optional[str], end_date: Optional[str]
) -> go.Figure:
    datareader = DataReader("data/bodyweight.db")
    df: pd.DataFrame = datareader.read_food_eaten_data()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["date"] = df["timestamp"].dt.date
    df["date"] = pd.to_datetime(df["date"])
    start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    filtered_data_df = filter_data_by_date(df, start_date, end_date)

    grouped = filtered_data_df.groupby("date").agg(
        carbs=pd.NamedAgg(column="carbohydrates_total_g", aggfunc="sum"),
        fats=pd.NamedAgg(column="fat_total_g", aggfunc="sum"),
        proteins=pd.NamedAgg(column="protein_g", aggfunc="sum"),
    )

    grouped["total"] = grouped["carbs"] + grouped["fats"] + grouped["proteins"]
    grouped["carbs"] = grouped["carbs"] / grouped["total"] * 100
    grouped["fats"] = grouped["fats"] / grouped["total"] * 100
    grouped["proteins"] = grouped["proteins"] / grouped["total"] * 100

    fig = go.Figure(
        data=[
            go.Bar(name="Carbs", x=grouped.index, y=grouped["carbs"]),
            go.Bar(name="Fats", x=grouped.index, y=grouped["fats"]),
            go.Bar(name="Proteins", x=grouped.index, y=grouped["proteins"]),
        ]
    )
    fig.update_layout(barmode="stack", margin=dict(l=20, r=20, t=20, b=60))
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showline=False, zeroline=False)
    fig.update_yaxes(showline=False, zeroline=False)

    return fig


@dash_app.callback(
    Output("weight-line-chart", "figure"),
    [
        Input("interval-component", "n_intervals"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
        Input("time-frame-dropdown", "value"),
    ],
)
def update_weight_chart(
    _: Any, start_date: Optional[str], end_date: Optional[str], time_frame: str
) -> go.Figure:
    """
    Updates the weight line chart on the dashboard in real-time.

    This callback function is triggered by changes in the specified inputs, including the interval component, date picker range, and time frame dropdown.
    It reads the bodyweight data from the database, filters and groups the data based on the selected time frame, and constructs a line chart to represent the average bodyweight over time.

    Parameters:
        _: Any (Unused parameter, typically representing the interval component)
        start_date: Optional[str] (The start date for filtering the data, in the format "YYYY-MM-DD")
        end_date: Optional[str] (The end date for filtering the data, in the format "YYYY-MM-DD")
        time_frame: str (The selected time frame for grouping the data, being, "daily", "weekly", "monthly")

    Returns:
        go.Figure: A Plotly Figure object representing the line chart of average bodyweight.

    Note:
        The function handles different time frames ("daily", "weekly", "monthly") and groups the data accordingly. The line chart provides a visual representation of bodyweight trends over the selected period.
    """
    datareader = DataReader("data/bodyweight.db")
    weight_data = datareader.read_bodyweight_data()
    weight_data["date"] = pd.to_datetime(weight_data["date"])
    start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    filtered_weight_data = filter_data_by_date(weight_data, start_date, end_date)

    if time_frame == "weekly":
        filtered_weight_data["week_start"] = (
            filtered_weight_data["date"].dt.to_period("W").dt.start_time
        )
        grouped_data = (
            filtered_weight_data.groupby("week_start")["bodyweight"]
            .mean()
            .reset_index()
        )
        grouped_data["date"] = grouped_data["week_start"]
    elif time_frame == "monthly":
        grouped_data = (
            filtered_weight_data.groupby(
                [filtered_weight_data["date"].dt.to_period("M")]
            )["bodyweight"]
            .mean()
            .reset_index()
        )
        grouped_data["date"] = grouped_data["date"].dt.to_timestamp()
    else:
        grouped_data = filtered_weight_data

    fig = px.line(grouped_data, x="date", y="bodyweight")
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=0))
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showline=False, zeroline=False)
    fig.update_yaxes(showline=False, zeroline=False)
    return fig


if __name__ == "__main__":
    app.run(debug=True)
