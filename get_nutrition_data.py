from datetime import datetime
import pytz
import plotly.graph_objects as go
from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from dash import Dash
from dash.dependencies import Input, Output
import pandas as pd
from foodninja_api import get_food_info_from_api
from data_manager import DataManager, CSVReader, CSVWriter
from charts_plotly import create_layout
import plotly.express as px

csv_reader = CSVReader("nutrition.csv")
data_manager_reader = DataManager(reader=csv_reader)
app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'your_secret_key'  # Replace 'your_secret_key' with a complex unique string
# Create a new Dash app
dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/')
dash_app.layout = create_layout()

@dash_app.callback(
    Output('calories-bar-chart', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
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
    fig.update_layout(barmode='stack', margin=dict(l=20, r=20, t=20, b=60))
    fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(showline=False, zeroline=False)
    fig.update_yaxes(showline=False, zeroline=False)

    return fig

# Define the callback
@dash_app.callback(
    Output('weight-line-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_weight_chart(n_intervals):
    # Read the weight data
    csv_reader = CSVReader("weight.csv")
    weight_data = csv_reader.read_data()
    fig = px.line(weight_data, x='date', y='bodyweight') 
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=0))
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="")
    fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(showline=False, zeroline=False)
    fig.update_yaxes(showline=False, zeroline=False)
    return fig


def process_nutrition_data(food_item, weight, nutrition_data):
    berlin_tz = pytz.timezone('Europe/Berlin')
    berlin_time = datetime.now(berlin_tz)
    data = {}
    data["timestamp"] = berlin_time.isoformat()
    for key, value in nutrition_data["items"][0].items():
        if key == "name":
            data[key] = value
            continue  
        data[key] = float(value) * float(weight)/100.0
    return data


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'food_item' in request.form:
            food_item = request.form.get('food_item')
            weight = request.form.get('weight')
            nutrition_data = get_food_info_from_api(food_item, weight)
            if nutrition_data:
                data = process_nutrition_data(food_item, weight, nutrition_data)
                session['data_to_save'] = data
                FIELD_ORDER = [
                    'timestamp',
                    'name',
                    'calories',
                    'serving_size_g',
                    'fat_total_g',
                    'fat_saturated_g',
                    'protein_g',
                    'sodium_mg',
                    'potassium_mg',
                    'cholesterol_mg',
                    'carbohydrates_total_g',
                    'fiber_g',
                    'sugar_g'
                    ]
                csv_writer = CSVWriter("nutrition.csv", FIELD_ORDER)
                data_manager_writer = DataManager(writer=csv_writer)
                data_manager_writer.write_data(session['data_to_save'])
                flash('Data saved successfully!', 'success')
        elif 'bodyweight' in request.form:
            weight_data = {}
            weight_data['date'] = request.form.get('date')
            weight_data['bodyweight'] = request.form.get('bodyweight')
            csv_writer = CSVWriter("weight.csv", ['date', 'bodyweight'])
            data_manager_writer = DataManager(writer=csv_writer)
            data_manager_writer.write_data(weight_data)
            flash('Data saved successfully!', 'success')
        else:
            flash('Aborted entry!', 'failure')
        session.pop('data_to_save', None)
        return redirect('/')
    return render_template('index.html', data=session.get('data_to_save'))


@app.route('/dashboard', methods=['GET'])
def dashboard():
    dash_app.layout = create_layout()
    return dash_app.index()

if __name__ == '__main__':
    app.run(debug=True)
