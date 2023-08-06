import csv

class DataWriter:
    def __init__(self, filename='nutrition.csv', field_order=None):
        self.file_name = filename
        self.field_order = field_order

    def write_to_csv(self, data):
        with open(self.file_name, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.field_order)
            writer.writerow(data)
