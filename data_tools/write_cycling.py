import sqlite3
import csv

# Path to the CSV file
csv_file_path = 'data/biking.csv'

# Connect to the SQLite database
conn = sqlite3.connect('data/bodyweight.db')
cursor = conn.cursor()

# Open the CSV file
with open(csv_file_path, 'r') as file:
    reader = csv.DictReader(file)

    # Iterate through the rows in the CSV file
    for row in reader:
        # Extract the required fields
        timestamp = row['timestamp']
        calories = row['calories']
        duration_in_s = row['duration_in_s']
        name = row['name']

        # Transform duration_in_s into minutes
        duration = int(duration_in_s) / 60

        # Insert the data into the cycling_data table
        cursor.execute("""
            INSERT INTO cycling_data (timestamp, calories, duration, name_of_session)
            VALUES (?, ?, ?, ?)
        """, (timestamp, calories, duration, name))

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Data inserted successfully.")
