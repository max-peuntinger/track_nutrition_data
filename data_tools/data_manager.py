import pandas as pd
import sqlite3
import pandas as pd

class _SQLite3Reader:
    def __init__(self, db_path):
        self.db_path = db_path

    def read_data(self, query):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def read_single_data(self, id, table):
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM {table} WHERE id = {id} LIMIT 1"
        df = pd.read_sql(query, conn)
        conn.close()
        return df

class DataReaderInterface:
    def read_food_eaten_data(self) -> pd.DataFrame:
        pass

    def read_bodyweight_data(self) -> pd.DataFrame:
        pass

    def read_single_bodyweight_entry(self, id: int) -> pd.DataFrame:
        pass

class DataReader(DataReaderInterface):
    def __init__(self, db_name: str):
        self.sql_reader = _SQLite3Reader(db_name)

    def read_food_eaten_data(self) -> pd.DataFrame:
        query = "SELECT * FROM food_eaten ORDER BY timestamp DESC"
        return self.sql_reader.read_data(query)

    def read_bodyweight_data(self) -> pd.DataFrame:
        query = "SELECT * FROM bodyweight ORDER BY date DESC"
        return self.sql_reader.read_data(query)
    
    def read_single_bodyweight_entry(self, id: int) -> pd.DataFrame:
            return self.sql_reader.read_single_data(id=id, table="bodyweight")
    
    def read_single_food_entry(self, id: int) -> pd.DataFrame:
            return self.sql_reader.read_single_data(id=id, table="food_eaten")

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
