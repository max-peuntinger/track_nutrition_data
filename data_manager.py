import csv
import os
import pandas as pd
import sqlite3

class DataManager:
    def __init__(self, reader=None, writer=None):
        self.reader = reader
        self.writer = writer

    def read_data(self):
        if self.reader:
            return self.reader.read_data()
        return None
    
    def write_data(self, data):
        if self.writer:
            self.writer.write_data(data)
        return None
    
class CSVReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_data(self):
        return pd.read_csv(self.file_path)

class CSVWriter:
    def __init__(self, file_path, field_order):
        self.file_path = file_path
        self.field_order = field_order

    def write_data(self, data):
        # Check if the file already exists
        write_header = not os.path.exists(self.file_path)

        # Open the file in append mode
        with open(self.file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.field_order)

            # Write the header if the file is new
            if write_header:
                writer.writeheader()

            # Write the data as a row
            writer.writerow(data)

class SQLite3Reader:
    def __init__(self, db_path):
        self.db_path = db_path

    def read_data(self, query):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    

class SQLite3Writer:
    def __init__(self, db_path):
        self.db_path = db_path

    def create_data(self, table_name, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        conn.close()

    def update_data(self, table_name, data, row_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query =f"UPDATE {table_name} SET {set_column} WHERE id = ?"
        cursor.execute(query, tuple(data.value()) + (row_id,))
        conn.commit()
        conn.close()

    def delete_data(self, table_name, row_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = f"DELETE FROM {table_name} WHERE id = ?"
        cursor.execute(query, (row_id,))
        conn.commit()
        conn.close()
