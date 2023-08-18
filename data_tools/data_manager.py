import pandas as pd
import sqlite3
from typing import Dict


class _SQLite3Reader:
    """A private class to read data from an SQLite3 database.

    Args:
        db_path (str): The path to the SQLite3 database file.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def read_data(self, query: str):
        """Reads data from the database using a custom SQL query.

        Args:
            query (str): The SQL query to execute.

        Returns:
            pd.DataFrame: The result of the query as a DataFrame.
        """
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def read_single_data(self, id: int, table: str):
        """Reads a single row from the specified table using the given ID.

        Args:
            id (int): The ID of the row to read.
            table (str): The name of the table to read from.

        Returns:
            pd.DataFrame: The result of the query as a DataFrame.
        """
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM {table} WHERE id = {id} LIMIT 1"
        df = pd.read_sql(query, conn)
        conn.close()
        return df


class DataReaderInterface:
    """An interface for reading different types of data."""

    def read_food_eaten_data(self) -> pd.DataFrame:
        """Reads food eaten data.

        Returns:
            pd.DataFrame: The food eaten data as a DataFrame.
        """
        pass

    def read_bodyweight_data(self) -> pd.DataFrame:
        """Reads bodyweight data.

        Returns:
            pd.DataFrame: The bodyweight data as a DataFrame.
        """
        pass

    def read_single_bodyweight_entry(self, id: int) -> pd.DataFrame:
        """Reads a single bodyweight entry.

        Args:
            id (int): The ID of the bodyweight entry to read.

        Returns:
            pd.DataFrame: The bodyweight entry as a DataFrame.
        """
        pass


class DataReader(DataReaderInterface):
    """A class that implements the DataReaderInterface using an SQLite3 database. For docstrings of functions see interface.

    Args:
        db_name (str): The name of the SQLite3 database file.
    """

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
    """A class to write data to an SQLite3 database.

    Args:
        db_path (str): The path to the SQLite3 database file.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_data(self, table_name: str, data: Dict[str, any]) -> None:
        """Inserts a new row into the specified table.

        Args:
            table_name (str): The name of the table to insert into.
            data (dict): A dictionary containing the data to insert.

        Returns:
            None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        conn.close()

    def update_data(self, table_name: str, data: Dict[str, any], row_id: int) -> None:
        """Updates a row in the specified table.

        Args:
            table_name (str): The name of the table to update.
            data (dict): A dictionary containing the new data.
            row_id (int): The ID of the row to update.

        Returns:
            None
        """
        set_assignments = [f"{column} = ?" for column in data.keys()]
        set_clause = ", ".join(set_assignments)
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        values = list(data.values()) + [row_id]
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def delete_data(self, table_name: str, row_id: int) -> None:
        """Deletes a row from the specified table.

        Args:
            table_name (str): The name of the table to delete from.
            row_id (int): The ID of the row to delete.

        Returns:
            None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = f"DELETE FROM {table_name} WHERE id = ?"
        cursor.execute(query, (row_id,))
        conn.commit()
        conn.close()
