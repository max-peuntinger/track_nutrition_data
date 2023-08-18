import sqlite3


def create_database(db_path, table_name, columns):
    """
    Creates a new table in the specified SQLite3 database.

    Args:
        db_path (str): The path to the SQLite3 database file.
        table_name (str): The name of the table to create.
        columns (dict): A dictionary containing the column names and their corresponding types.

    Returns:
        None: The function prints a success message but does not return a value.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns_definition = ", ".join(
        [f"{col_name} {col_type}" for col_name, col_type in columns.items()]
    )
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})"
    cursor.execute(query)

    conn.commit()
    conn.close()
    print(f"Table {table_name} created successfully in {db_path}")


# db_path = "bodyweight.db"
# table_name = "bodyweight"
# columns = {
#     "date": "TEXT",
#     "bodyweight": "REAL"
# }

# db_path = "bodyweight.db"
# table_name = "food_eaten"
# columns = {
#     "timestamp": "TEXT",
#     "name": "TEXT",
#     "calories": "REAL",
#     "serving_size_g": "REAL",
#     "fat_total_g": "REAL",
#     "fat_saturated_g": "REAL",
#     "protein_g": "REAL",
#     "sodium_mg": "REAL",
#     "potassium_mg": "REAL",
#     "cholesterol_mg": "REAL",
#     "carbohydrates_total_g": "REAL",
#     "fiber_g": "REAL",
#     "sugar_g": "REAL",
# }

# create_database(db_path, table_name, columns)
