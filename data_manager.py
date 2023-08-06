import csv
import os
import pandas as pd

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



if __name__ == '__main__':
    # Example Usage with both reader and writer
    FIELD_ORDER = [
        'timestamp',
        'name',
        'calories',
        'serving_size_g',
        'fat_total_g',
        'fat_saturated_g',
        'protein_g',
        'sodium_mg',
        'potassium_mg',
        'cholesterol_mg',
        'carbohydrates_total_g',
        'fiber_g',
        'sugar_g']
    csv_reader = CSVReader("nutrition.csv")
    csv_writer = CSVWriter("nutrition.csv", field_order=FIELD_ORDER)
    data_manager = DataManager(csv_reader, csv_writer)
    df = data_manager.read_data().tail(1)
    # Convert the last row to a dictionary
    last_row_dict = df.iloc[0].to_dict()
    data_manager.write_data(last_row_dict)
