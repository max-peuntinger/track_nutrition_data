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

    def write_data(self, table_name, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        print(query)
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        conn.close()


if __name__ == '__main__':

    # sql3writer = SQLite3Writer("bodyweight.db")
    # #
    # sql3writer.write_data(
    #     "bodyweight",
    #     {
    #         # 'date': '2023-08-02', 
    #         # 'bodyweight': '85.5',
    #         # 'date': '2023-08-03', 
    #         # 'bodyweight': '85.2',
    #         # 'date': '2023-08-04', 
    #         # 'bodyweight': '84.2',
    #         # 'date': '2023-08-05', 
    #         # 'bodyweight': '83.9',
    #         # 'date': '2023-08-06', 
    #         # 'bodyweight': '83.7',
    #         # 'date': '2023-08-07', 
    #         # 'bodyweight': '83.1',
    #         # 'date': '2023-08-08', 
    #         # 'bodyweight': '83.2',
    #         # 'date': '2023-08-08', 
    #         # 'bodyweight': '83.3',
    #         'date': '2023-08-10', 
    #         'bodyweight': '82.9',

    #     }
    # )

    sql3reader = SQLite3Reader("bodyweight.db")
    # data_manager = DataManager()
    data = sql3reader.read_data("SELECT * FROM bodyweight")
    print(data)

    # example usage db bodyweight

    # Example Usage with both reader and writer

    # FIELD_ORDER = [
    #     'timestamp',
    #     'name',
    #     'calories',
    #     'serving_size_g',
    #     'fat_total_g',
    #     'fat_saturated_g',
    #     'protein_g',
    #     'sodium_mg',
    #     'potassium_mg',
    #     'cholesterol_mg',
    #     'carbohydrates_total_g',
    #     'fiber_g',
    #     'sugar_g']
    # csv_reader = CSVReader("nutrition.csv")
    # csv_writer = CSVWriter("nutrition.csv", field_order=FIELD_ORDER)
    # data_manager = DataManager(csv_reader, csv_writer)
    # df = data_manager.read_data().tail(1)
    # # Convert the last row to a dictionary
    # last_row_dict = df.iloc[0].to_dict()
    # data_manager.write_data(last_row_dict)
