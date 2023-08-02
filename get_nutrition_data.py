import os
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

def main():
    parser = argparse.ArgumentParser(description='CalorieNinjas API Command Line Tool')
    parser.add_argument('food_item', type=str, help='The food item to get nutrition data for.')
    parser.add_argument('weight', type=str, help='The weight of the food item.')
    parser.add_argument('--test', action='store_true', help='Run in test mode. Does not write to CSV.')

    args = parser.parse_args()
    food_item = args.food_item
    weight = args.weight
    test = args.test

    nutrition_data = get_nutrition_data(food_item, weight)
    if nutrition_data:
        berlin_tz = pytz.timezone('Europe/Berlin')
        berlin_time = datetime.now(berlin_tz)
        res = {}
        res["timestamp"] = berlin_time
        print(f"Nutrition data for {nutrition_data['items'][0]['name']}:")
        for key, value in nutrition_data["items"][0].items():
            if key == "name":
                res[key] = value
                continue
            
            res[key] = float(value) * float(weight[:-1])/100.0

            #print(f"{key}: {float(value) * float(weight[:-1])/100.0}")
    # print(res)
    if not test:
        with open('nutrition.csv', 'a') as f:
            writer = csv.DictWriter(f, fieldnames=res.keys())
            writer.writerow(res)
# timestamp,food_name,food_quantity,calories,fat_total_g,fat_saturated_g,protein_g,sodium_mg,potassium_mg,cholesterol_mg,carbohydrates_total_g,fiber_g,sugar_g


if __name__ == '__main__':
 
    main()
