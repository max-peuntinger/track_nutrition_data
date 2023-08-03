from flask import Flask, request, render_template

import os
import sys
import argparse
import csv
from datetime import datetime
import requests
import pytz
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from the environment variable
API_KEY = os.getenv('API_KEY')

# CalorieNinjas API base URL
BASE_URL = 'https://api.calorieninjas.com/v1/nutrition'

app = Flask(__name__)

class InvalidArgumentNumberException(Exception):
    pass


# Function to fetch nutrition data for a given food item
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
    data["timestamp"] = berlin_time
    print(f"Nutrition data for {nutrition_data['items'][0]['name']}:")
    for key, value in nutrition_data["items"][0].items():
        if key == "name":
            data[key] = value
            continue  
        data[key] = float(value) * float(weight[:-1])/100.0
    print(f"{data}")
    return data


def write_to_csv(data, f, writer=None):
    fieldnames = data.keys()
    if writer is None:
        # Initialize writer if it hasn't been initialized yet
        writer = csv.DictWriter(f, fieldnames=fieldnames)
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
            with open('nutrition.csv', 'a', newline='') as f:
                writer = write_to_csv(data, f)
        return 'Data saved successfully!'
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
