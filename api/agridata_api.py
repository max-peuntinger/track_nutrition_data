import requests

# Replace {varietyCode} with the specific code you want to query, or remove it if you want to get all varieties
url = "https://agridata.ec.europa.eu/extensions/FruitVeg-Api/v1/varieties/POM"

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",  # Example User-Agent header
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    varieties = response.json()
    for variety in varieties:
        print(f"Variety: {variety['variety']}")
        print(f"Product Name: {variety['productName']}")
        print(f"Product Code: {variety['productCode']}")
        print(f"Product Group Code: {variety['productGroupCode']}")
        print()
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
