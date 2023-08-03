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


if __name__ == '__main__':
    unittest.main()
