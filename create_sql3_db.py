import sqlite3
def create_database(db_path, table_name, columns):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns_definition = ', '.join([f'{col_name} {col_type}' for col_name, col_type in columns.items()])
    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})"
    cursor.execute(query)

    conn.commit()
    conn.close()
    print(f"Table {table_name} created successfully in {db_path}")

db_path = "bodyweight.db"
table_name = "bodyweight"
columns = {
    "date": "TEXT",
    "bodyweight": "REAL"
}

create_database(db_path, table_name, columns)