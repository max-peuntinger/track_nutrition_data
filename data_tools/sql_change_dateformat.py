import sqlite3

def update_timestamp_format(db_path):
    # Connect to the SQLite3 database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to select timestamps from the specific table
    query_select = "SELECT id, timestamp FROM cycling_data"
    cursor.execute(query_select)
    rows = cursor.fetchall()

    # Iterate through the rows and update the timestamp format
    for row in rows:
        row_id, timestamp = row
        # Modify the timestamp to the desired format
        new_timestamp = timestamp.replace(" ", "T") # Example: change "2023-08-21 13:15" to "2023-08-21T13:15"
        # Update the timestamp in the database
        query_update = "UPDATE cycling_data SET timestamp = ? WHERE id = ?"
        cursor.execute(query_update, (new_timestamp, row_id))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Path to your SQLite3 database file
db_path = "data/bodyweight.db"
update_timestamp_format(db_path)
