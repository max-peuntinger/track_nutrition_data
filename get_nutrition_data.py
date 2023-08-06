import os
import sys
import argparse
import csv
from datetime import datetime
import requests
import pytz
from dotenv import load_dotenv

import plotly.graph_objects as go
from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

from charts_plotly import create_layout

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment variable
API_KEY = os.getenv('API_KEY')

# CalorieNinjas API base URL
BASE_URL = 'https://api.calorieninjas.com/v1/nutrition'

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
    df = pd.read_csv("nutrition.csv")

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


def parse_arguments():
    parser = argparse.ArgumentParser(description='CalorieNinjas API Command Line Tool')
    parser.add_argument('items', nargs='+', help='Pairs of food items and weights to get nutrition data for.')
    parser.add_argument('--test', action='store_true', help='Run in test mode. Does not write to CSV.')

    args = parser.parse_args()
    if len(args.items) % 2 != 0:
        sys.stderr.write("Error, please provide a pair of food and weight")
        raise InvalidArgumentNumberException
    pairs = [(args.items[i], args.items[i+1]) for i in range(0, len(args.items), 2)]
    return pairs, args.test


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
    print(f"{data}")
    return data

def get_nutrition_data(food_item, weight):
    headers = {
        'X-Api-Key': API_KEY,
    }
    params = {
        'query': f"{food_item} {weight}",
    }
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None



def write_to_csv(data, f, field_order, writer=None):
    if writer is None:
        # Initialize writer if it hasn't been initialized yet
        writer = csv.DictWriter(f, fieldnames=field_order)
    writer.writerow(data)
    print("added")
    return writer


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        food_item = request.form.get('food_item')
        weight = request.form.get('weight')
        nutrition_data = get_nutrition_data(food_item, weight)
        if nutrition_data:
            data = process_nutrition_data(food_item, weight, nutrition_data)
            session['data_to_save'] = data
            return redirect(url_for('confirm'))
        return render_template('index.html')
        return 'Data saved successfully!'
    return render_template('index.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    print(session['data_to_save'])
    if 'data_to_save' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        print(session['data_to_save'])
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
            'sugar_g']
        if 'confirm' in request.form:
            with open('nutrition.csv', 'a',) as f:
                writer = write_to_csv(session['data_to_save'], f, FIELD_ORDER)
            session.pop('data_to_save', None)
            flash('Data saved successfully!', 'success')
            return redirect(url_for('index'))
            #return 'Data saved successfully!'
        else:
            session.pop('data_to_save', None)
            flash('Data saving cancelled', 'info')
            return redirect(url_for('index'))
            # return 'Data saving cancelled'
    else:
        return render_template('confirm.html', data=session['data_to_save'])

@app.route('/dashboard', methods=['GET'])
def dashboard():
    dash_app.layout = create_layout()
    return dash_app.index()

# Create the Dash layout
dash_app.layout = create_layout()

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


if __name__ == '__main__':
    app.run(debug=True)
