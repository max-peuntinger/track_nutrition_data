import unittest
import sys
from io import StringIO
import get_nutrition_data
import os
import csv


class TestGetNutritionDataResults(unittest.TestCase):
    def test_apple_has_correct_name(self):
        result = get_nutrition_data.get_nutrition_data('apple', '100g')
        self.assertEqual(result['items'][0]['name'], 'apple')

    def test_apple_has_correct_weight(self):
        result = get_nutrition_data.get_nutrition_data('apple', '100g')
        self.assertEqual(result['items'][0]['serving_size_g'], 100)

    def test_apple_has_correct_calories(self):
        result = get_nutrition_data.get_nutrition_data('apple', '100g')
        self.assertEqual(result['items'][0]['calories'], 53.0)


class TestCommandLineArguments(unittest.TestCase):
    def test_missing_weight(self):
        # Replace sys.argv
        sys.argv = ['get_nutrition_data.py', 'apple']

        # Redirect stderr to check error output
        stderr = StringIO()
        sys.stderr = stderr

        with self.assertRaises(get_nutrition_data.InvalidArgumentNumberException):
            get_nutrition_data.main()

        # Check error output
        self.assertIn('Error, please provide a pair of food and weight', stderr.getvalue())

    def test_test_flag_prevents_csv_writing(self):
        # Get the last modification time of the csv file
        csv_last_modified = os.path.getmtime('nutrition.csv') if os.path.exists('nutrition.csv') else 0

        # Replace sys.argv
        sys.argv = ['get_nutrition_data.py', 'apple', '100g', '--test']

        get_nutrition_data.main()

        # Get the current last modification time of the csv file
        csv_current_last_modified = os.path.getmtime('nutrition.csv') if os.path.exists('nutrition.csv') else 0

        # Check that the csv file was not modified
        self.assertEqual(csv_last_modified, csv_current_last_modified)

class TestParseArguments(unittest.TestCase):
    def test_correct_arguments(self):
        sys.argv = ['get_nutrition_data', 'apple', '100g']
        pairs, test = get_nutrition_data.parse_arguments()
        self.assertEqual(pairs, [('apple', '100g')])
        self.assertFalse(test)

    def test_incorrect_arguments(self):
        sys.argv = ['get_nutrition_data', 'apple']
        stderr = StringIO()
        sys.stderr = stderr
        with self.assertRaises(get_nutrition_data.InvalidArgumentNumberException):
                               get_nutrition_data.parse_arguments()
        self.assertIn('Error, please provide a pair of food and weight', stderr.getvalue())

class TestProcessNutritionData(unittest.TestCase):
    def setUp(self) -> None:
        self.data = {
             'items': [{
                  'name': 'apple',
                  'calories': '53.0',
                  'serving_size_g': 100,
             }],
        }

    def test_process_nutrition_data(self):
        result = get_nutrition_data.process_nutrition_data('apple', '100g', self.data)
        self.assertIn('timestamp', result)
        self.assertEqual(result['name'], 'apple')
        self.assertEqual(result['calories'], 53.0)
        self.assertEqual(result['serving_size_g'], 100)

class TestWriteToCsv(unittest.TestCase):
    def setUp(self):
        self.data = {
            'timestamp': '2023-08-03 15:00:00',
            'name': 'apple',
            'calories': 53.0,
            'serving_size_g': 100.0,
        }
        if os.path.exists('test_nutrition.csv'):
            os.remove('test_nutrition.csv')
        with open('nutrition_test.csv', 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['timestamp', 'name', 'calories', 'serving_size_g'])


        
    def tearDown(self):
        if os.path.exists('test_nutrition.csv'):
            os.remove('test_nutrition.csv')

def test_write_to_csv(self):
    # Run the function
    get_nutrition_data.write_to_csv(self.data, 'nutrition_test.csv')

    # Check the output
    with open('nutrition_test.csv', 'r') as f:
        reader = csv.reader(f)
        lines = list(reader)

    expected_data = [
        ['timestamp', 'name', 'calories', 'serving_size_g'],
        ['2023-08-03 15:00:00', 'apple', '53.0', '100.0']
    ]

    # Convert the expected data to match the type of data read from the CSV
    expected_data = [[str(item) for item in sublist] for sublist in expected_data]

    self.assertEqual(lines, expected_data)


if __name__ == '__main__':
    unittest.main()
