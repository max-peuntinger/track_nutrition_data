from dotenv import load_dotenv
import os
import requests
import logging
from decorators import log_execution_time

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.calorieninjas.com/v1/nutrition"

if not API_KEY:
    logging.error("API_KEY not found in environment variables.")

@log_execution_time
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
            logging.info(f"Foodninja API returned:\n{data} for {params}")
            return data
        else:
            error_message = f"Problem with FoodNinja API at https://api-ninjas.com/api/nutrition. Error: {response.status_code} - {response.text}"
            logging.error(error_message)
            return None
    except requests.exceptions.RequestException as e:
        error_message = ("Problem with FoodNinja API at https://api-ninjas.com/api/nutrition")
        logging.error(error_message)
        return None
