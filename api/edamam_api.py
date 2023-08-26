# import requests

# url = "https://edamam-food-and-grocery-database.p.rapidapi.com/api/food-database/v2/parser"

# querystring = {"nutrition-type":"cooking","category[0]":"generic-foods","health[0]":"alcohol-free"}

# headers = {
# 	"X-RapidAPI-Key": "5a51ab4956msh2b6ea037dff0438p1a666bjsn43994e5fb554",
# 	"X-RapidAPI-Host": "edamam-food-and-grocery-database.p.rapidapi.com"
# }

# response = requests.get(url, headers=headers, params=querystring)

# print(response.json())

# import requests
# import json

# def get_food_category(food_name, app_id, app_key):
#     url = f"https://api.edamam.com/api/food-database/v2/parser?ingr={food_name}&app_id={app_id}&app_key={app_key}"
#     response = requests.get(url)

#     if response.status_code == 200:
#         food_data = response.json()
#         if 'parsed' in food_data and food_data['parsed']:
#             food_item = food_data['parsed'][0]['food']
#             category_label = food_item.get('categoryLabel', 'Unknown')
#             return category_label
#         else:
#             return "Unknown"
#     else:
#         print(f"Error {response.status_code}: {response.text}")
#         return None

# # Replace these with your Edamam Application ID and API Key
# app_id = "edamam-food-and-grocery-database.p.rapidapi.com"
# app_key = "5a51ab4956msh2b6ea037dff0438p1a666bjsn43994e5fb554"

# food_name = "carrot"
# category = get_food_category(food_name, app_id, app_key)

# if category:
#     print(f"The food '{food_name}' belongs to the category: {category}")
# else:
#     print(f"Unable to classify the food '{food_name}'.")

# import requests

# def get_food_category(food_name, rapidapi_key):
#     url = "https://edamam-food-and-grocery-database.p.rapidapi.com/api/food-database/v2/parser"
#     querystring = {"ingr": food_name}
#     headers = {
#         'x-rapidapi-host': "edamam-food-and-grocery-database.p.rapidapi.com",
#         'x-rapidapi-key': "5a51ab4956msh2b6ea037dff0438p1a666bjsn43994e5fb554"
#     }
#     response = requests.request("GET", url, headers=headers, params=querystring)

#     if response.status_code == 200:
#         food_data = response.json()
#         print(food_data)
#         if 'parsed' in food_data and food_data['parsed']:
#             food_item = food_data['parsed'][0]['food']
#             category_label = food_item.get('categoryLabel', 'Unknown')
#             return category_label
#         else:
#             return "Unknown"
#     else:
#         print(f"Error {response.status_code}: {response.text}")
#         return None

# # Replace this with your RapidAPI Key for Edamam Food and Grocery Database
# rapidapi_key = "YOUR_RAPIDAPI_KEY"

# food_name = "carrot"
# category = get_food_category(food_name, rapidapi_key)

# if category:
#     print(f"The food '{food_name}' belongs to the category: {category}")
# else:
#     print(f"Unable to classify the food '{food_name}'.")

# import requests
# headers = {
#     'x-rapidapi-host': "edamam-food-and-grocery-database.p.rapidapi.com",
#     'x-rapidapi-key': "5a51ab4956msh2b6ea037dff0438p1a666bjsn43994e5fb554" # Replace with your actual RapidAPI key
# }

# url = "https://edamam-food-and-grocery-database.p.rapidapi.com/auto-complete"

# querystring = {"q": "carrot"} # The food item you want to search for


# response = requests.request("GET", url, headers=headers, params=querystring)

# if response.status_code == 200:
#     suggestions = response.json()
#     print("Suggestions for 'carrot':", suggestions)
# else:
#     print(f"Error {response.status_code}: {response.text}")

# import requests
# import json

# url = "https://edamam-food-and-grocery-database.p.rapidapi.com/api/food-database/v2/nutrients"

# headers = {
#     'x-rapidapi-host': "edamam-food-and-grocery-database.p.rapidapi.com",
#     'x-rapidapi-key': "5a51ab4956msh2b6ea037dff0438p1a666bjsn43994e5fb554", # Replace with your actual RapidAPI key
#     'content-type': "application/json"
# }

# # Example payload for a food item (e.g., carrot)
# payload = {
#     "ingredients": [
#         {
#             "quantity": 1,
#             "measureURI": "http://www.edamam.com/ontologies/edamam.owl#Measure_unit",
#             "foodId": "food_bf4za6qbl08zmgat7s8q0bpviq02" # Example foodId for carrot
#         }
#     ]
# }

# response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

# if response.status_code == 200:
#     nutrients = response.json()
#     print("Nutrients for 'carrot':", nutrients)
# else:
#     print(f"Error {response.status_code}: {response.text}")

# import requests

# url = "https://edamam-food-and-grocery-database.p.rapidapi.com/auto-complete"

# querystring = {"q": "apple"}

# headers = {
#     "X-RapidAPI-Key": "5a51ab4956msh2b6ea037dff0438p1a666bjsn43994e5fb554",
#     "X-RapidAPI-Host": "edamam-food-and-grocery-database.p.rapidapi.com"
# }

# response = requests.request("GET", url, headers=headers, params=querystring)

# print(response.json())

# import requests

# url = "https://edamam-food-and-grocery-database.p.rapidapi.com/api/food-database/v2/parser"

# querystring = {"ingr":"apple"}

# headers = {
# 	"X-RapidAPI-Key": "5a51ab4956msh2b6ea037dff0438p1a666bjsn43994e5fb554",
# 	"X-RapidAPI-Host": "edamam-food-and-grocery-database.p.rapidapi.com"
# }

# response = requests.get(url, headers=headers, params=querystring)

# print(response.json())


import requests

url = "https://edamam-food-and-grocery-database.p.rapidapi.com/api/food-database/v2/nutrients"

payload = {
    "ingredients": [
        {
            "quantity": 1,
            "measureURI": "http://www.edamam.com/ontologies/edamam.owl#Measure_gram",
            "qualifiers": [],
            "foodId": "food_a1gb9ubb72c7snbuxr3weagwv0dd",
        }
    ]
}
headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "5a51ab4956msh2b6ea037dff0438p1a666bjsn43994e5fb554",
    "X-RapidAPI-Host": "edamam-food-and-grocery-database.p.rapidapi.com",
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
