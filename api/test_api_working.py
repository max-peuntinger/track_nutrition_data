from dotenv import load_dotenv
import os
import requests

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.calorieninjas.com/v1/nutrition"


# def get_food_info_from_api(food_item, weight):
#     print("in func")
headers = {
    "X-Api-Key": API_KEY,
}
params = {
    "query": "1lb brisket and fries",
}

# Make the GET request
response = requests.get(BASE_URL, headers=headers, params=params)

# Print the status code and response
print(f"Status Code: {response.status_code}")
print("Response:")
print(response.json())