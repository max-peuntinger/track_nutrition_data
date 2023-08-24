from dotenv import load_dotenv
import os
import requests

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.calorieninjas.com/v1/nutrition"


def get_food_info_from_api(food_item, weight):
    headers = {
        "X-Api-Key": API_KEY,
    }
    params = {
        "query": f"{food_item} {weight}",
    }
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Problem with FoodNinja API at https://api-ninjas.com/api/nutrition")
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print("Problem with FoodNinja API at https://api-ninjas.com/api/nutrition")
        print(f"Error: {e}")
        return None
