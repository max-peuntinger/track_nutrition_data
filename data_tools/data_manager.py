import pandas as pd
import sqlite3


class SQLite3Reader:
    def __init__(self, db_path):
        self.db_path = db_path

    def read_data(self, query):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def read_single_data(self, id, table):
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM {table} WHERE id = {id}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df


class SQLite3Writer:
    def __init__(self, db_path):
        self.db_path = db_path

    def create_data(self, table_name, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        conn.close()

    def update_data(self, table_name, data, row_id):
        set_assignments = [f"{column} = ?" for column in data.keys()]
        set_clause = ", ".join(set_assignments)
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        values = list(data.values()) + [row_id]
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def delete_data(self, table_name, row_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = f"DELETE FROM {table_name} WHERE id = ?"
        cursor.execute(query, (row_id,))
        conn.commit()
        conn.close()
