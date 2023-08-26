import sqlite3

def create_cycling_table():
    conn = sqlite3.connect('data/bodyweight.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE cycling (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        calories INTEGER NOT NULL,
        duration INTEGER NOT NULL,
        name_of_session TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_cycling_table()
    print("Table created successfully.")
