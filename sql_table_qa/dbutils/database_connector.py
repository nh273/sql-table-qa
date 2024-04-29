import os
import sqlite3
import sqlparse
import sqlglot
import json
import inspect

from CONSTANTS import ROOT_DIR, GLOBAL_CONNECTION


class DatabaseConnector:
    """
    A class representing a SQL database connector.
    We hard code this class to access the Chinook dataset for this exercise
    but in a real-world scenario, we would likely have
    different classes with a common interface
    that can connect to different data sources.
    """

    def __init__(self):
        """
        Initializes a new instance of the DatabaseConnector class.
        """
        self.database_name = "Chinook"
        self.sql_flavor = "sqlite"
        self.connection = GLOBAL_CONNECTION
        self.database_schema = {
            "Album": {
                "desc": "Stores album related data",
                "columns": {
                    "AlbumId": {"dtype": "INTEGER", "desc": "Primary key of the album table."},
                    "Title": {"dtype": "NVARCHAR(160)", "desc": "Title of the album."},
                    "ArtistId": {"dtype": "INTEGER", "desc": "Foreign key that references the Artist table."}
                }
            },
            "Artist": {
                "desc": "Stores artist related data",
                "columns": {
                    "ArtistId": {"dtype": "INTEGER", "desc": "Primary key of the artist table."},
                    "Name": {"dtype": "NVARCHAR(120)", "desc": "Name of the artist."}
                }
            },
            "Customer": {
                "desc": "Stores customer related data",
                "columns": {
                    "CustomerId": {"dtype": "INTEGER", "desc": "Primary key of the customer table."},
                    "FirstName": {"dtype": "NVARCHAR(40)", "desc": "First name of the customer."},
                    "LastName": {"dtype": "NVARCHAR(20)", "desc": "Last name of the customer."},
                    "Company": {"dtype": "NVARCHAR(80)", "desc": "Customer's company, if any."},
                    "Address": {"dtype": "NVARCHAR(70)", "desc": "Customer's address."},
                    "City": {"dtype": "NVARCHAR(40)", "desc": "City of the customer."},
                    "State": {"dtype": "NVARCHAR(40)", "desc": "State of the customer."},
                    "Country": {"dtype": "NVARCHAR(40)", "desc": "Country of the customer."},
                    "PostalCode": {"dtype": "NVARCHAR(10)", "desc": "Postal code of the customer."},
                    "Phone": {"dtype": "NVARCHAR(24)", "desc": "Phone number of the customer."},
                    "Fax": {"dtype": "NVARCHAR(24)", "desc": "Fax number of the customer."},
                    "Email": {"dtype": "NVARCHAR(60)", "desc": "Email address of the customer."},
                    "SupportRepId": {"dtype": "INTEGER", "desc": "Foreign key that references the Support Employee."}
                }
            },
            "Employee": {
                "desc": "Stores employee related data",
                "columns": {
                    "EmployeeId": {"dtype": "INTEGER", "desc": "Primary key of the employee table."},
                    "LastName": {"dtype": "NVARCHAR(20)", "desc": "Last name of the employee."},
                    "FirstName": {"dtype": "NVARCHAR(20)", "desc": "First name of the employee."},
                    "Title": {"dtype": "NVARCHAR(30)", "desc": "Title of the employee."},
                    "ReportsTo": {"dtype": "INTEGER", "desc": "Reports to which superior (EmployeeId)."},
                    "BirthDate": {"dtype": "DATETIME", "desc": "Birth date of the employee."},
                    "HireDate": {"dtype": "DATETIME", "desc": "Hire date of the employee."},
                    "Address": {"dtype": "NVARCHAR(70)", "desc": "Address of the employee."},
                    "City": {"dtype": "NVARCHAR(40)", "desc": "City of the employee."},
                    "State": {"dtype": "NVARCHAR(40)", "desc": "State of the employee."},
                    "Country": {"dtype": "NVARCHAR(40)", "desc": "Country of the employee."},
                    "PostalCode": {"dtype": "NVARCHAR(10)", "desc": "Postal code of the employee."},
                    "Phone": {"dtype": "NVARCHAR(24)", "desc": "Phone number of the employee."},
                    "Fax": {"dtype": "NVARCHAR(24)", "desc": "Fax number of the employee."},
                    "Email": {"dtype": "NVARCHAR(60)", "desc": "Email address of the employee."}
                }
            },
            "Genre": {
                "desc": "Stores different musical genre types",
                "columns": {
                    "GenreId": {"dtype": "INTEGER", "desc": "Primary key of the genre table."},
                    "Name": {"dtype": "NVARCHAR(120)", "desc": "Name of the genre."}
                }
            },
            "MediaType": {
                "desc": "Stores types of media formats available",
                "columns": {
                    "MediaTypeId": {"dtype": "INTEGER", "desc": "Primary key of the media type table."},
                    "Name": {"dtype": "NVARCHAR(120)", "desc": "Name of the media type."}
                }
            },
            "Playlist": {
                "desc": "Stores playlist data",
                "columns": {
                    "PlaylistId": {"dtype": "INTEGER", "desc": "Primary key of the playlist table."},
                    "Name": {"dtype": "NVARCHAR(120)", "desc": "Name of the playlist."}
                }
            },
            "PlaylistTrack": {
                "desc": "Associative table linking playlists to tracks",
                "columns": {
                    "PlaylistId": {"dtype": "INTEGER", "desc": "Foreign key referencing playlists."},
                    "TrackId": {"dtype": "INTEGER", "desc": "Foreign key referencing tracks."}
                }
            },
            "Track": {
                "desc": "Stores detailed information about each music track",
                "columns": {
                    "TrackId": {"dtype": "INTEGER", "desc": "Primary key of the track table."},
                    "Name": {"dtype": "NVARCHAR(200)", "desc": "Name of the track."},
                    "AlbumId": {"dtype": "INTEGER", "desc": "Foreign key that references the Album table."},
                    "MediaTypeId": {"dtype": "INTEGER", "desc": "Foreign key that references the MediaType table."},
                    "GenreId": {"dtype": "INTEGER", "desc": "Foreign key that references the Genre table."},
                    "Composer": {"dtype": "NVARCHAR(220)", "desc": "Composer of the track."},
                    "Milliseconds": {"dtype": "INTEGER", "desc": "Length of the track in milliseconds."},
                    "Bytes": {"dtype": "INTEGER", "desc": "File size of the track in bytes."},
                    "UnitPrice": {"dtype": "NUMERIC(10,2)", "desc": "Price of the track."}
                }
            },
            "Invoice": {
                "desc": "Stores invoice data for customer purchases",
                "columns": {
                    "InvoiceId": {"dtype": "INTEGER", "desc": "Primary key of the invoice table."},
                    "CustomerId": {"dtype": "INTEGER", "desc": "Foreign key that references the Customer table."},
                    "InvoiceDate": {"dtype": "DATETIME", "desc": "Date of the invoice."},
                    "BillingAddress": {"dtype": "NVARCHAR(70)", "desc": "Billing address."},
                    "BillingCity": {"dtype": "NVARCHAR(40)", "desc": "Billing city."},
                    "BillingState": {"dtype": "NVARCHAR(40)", "desc": "Billing state."},
                    "BillingCountry": {"dtype": "NVARCHAR(40)", "desc": "Billing country."},
                    "BillingPostalCode": {"dtype": "NVARCHAR(10)", "desc": "Billing postal code."},
                    "Total": {"dtype": "NUMERIC(10,2)", "desc": "Total amount of the invoice."}
                }
            },
            "InvoiceLine": {
                "desc": "Stores line items of an invoice",
                "columns": {
                    "InvoiceLineId": {"dtype": "INTEGER", "desc": "Primary key of the invoice line table."},
                    "InvoiceId": {"dtype": "INTEGER", "desc": "Foreign key that references the Invoice table."},
                    "TrackId": {"dtype": "INTEGER", "desc": "Foreign key that references the Track table."},
                    "UnitPrice": {"dtype": "NUMERIC(10,2)", "desc": "Price per unit."},
                    "Quantity": {"dtype": "INTEGER", "desc": "Quantity of the item."}
                }
            }
        }

    def execute_sql(self, sql: str) -> list:
        """
        Executes an SQL statement on the Chinook database and get back the results.

        Args:
        sql (str): The SQL statement to execute.

        Returns:
        list: A list of tuples representing the result of the SQL query.
        """
        if self._is_modifying_sql(sql):
            raise ValueError("Modifying SQL statements are not allowed.")
        cursor = self.connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result

    def _is_modifying_sql(self, sql: str) -> bool:
        """
        Checks if an SQL statement is a modifying statement.

        Args:
        sql (str): The SQL statement to check.

        Returns:
        bool: True if the SQL statement is a modifying statement, False otherwise.
        """
        parsed = sqlparse.parse(sql)
        for statement in parsed:
            if statement.get_type() in ('INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE'):
                return True
        return False

    def validate_sql(self, sql: str) -> bool:
        """
        Validates an SQL statement.

        Args:
        sql (str): The SQL statement to validate.

        Returns:
        bool: True if the SQL statement is valid, False otherwise.
        """
        try:
            parsed = sqlglot.transpile(sql)
            if parsed:  # If the SQL statement is parsed successfully, it's valid
                return True
            else:
                return False
        except sqlglot.errors.ParseError as e:  # If parsing fails, the SQL is invalid
            return False

    def get_table_schema(self, table_name: str) -> dict:
        """
        Returns the schema of a specific table in the Chinook dataset.

        Args:
        table_name (str): The name of the table whose schema is to be returned.

        Returns:
        dict: A dictionary containing column names and data types of the table.
        """
        return self.database_schema.get(table_name, f"No schema found for table: {table_name}")

    def get_table_names_and_description(self) -> list:
        """
        Returns the name and description of all tables in the Chinook dataset.

        Returns:
        list: A list of table names and descriptions tuples.
        """
        table_info = []
        for table_name, table_data in self.database_schema.items():
            desc = table_data['desc']
            table_info.append((table_name, desc))
        return table_info

    @staticmethod
    def get_methods_info() -> dict:
        """Extracts and returns information about all public methods of this class as a Python dict."""
        methods_info = {}
        for name, func in inspect.getmembers(DatabaseConnector, predicate=inspect.isfunction):
            if not name.startswith('_'):
                methods_info[name] = {
                    "name": name,
                    "signature": str(inspect.signature(func)),
                    "docstring": inspect.getdoc(func)
                }
        return methods_info

    @staticmethod
    def convert_python_type_to_openai_type(python_type: str) -> str:
        """Converts a Python type to an OpenAI type."""
        if python_type == "str":
            return "string"
        else:
            return python_type

    @staticmethod
    def create_open_ai_assistant_tools() -> dict:
        """Extracts and returns information about all public methods of this class as a list
        of dictionaries specifying OpenAI Assistant tools.
        in this format:
        {
            "tool_name": "execute_sql",
            "description": "Executes an SQL statement on the Chinook database and get back the results.",
            "schema": {
                arg: arg type
            }
        }
        """
        tools = []
        for name, func in inspect.getmembers(DatabaseConnector, predicate=inspect.isfunction):
            if not name.startswith('_'):
                sig = inspect.signature(func)
                params = {
                    param.name: {
                        "type": DatabaseConnector   .convert_python_type_to_openai_type(param.annotation.__name__) if param.annotation != inspect._empty else "Any",
                        "description": param.annotation.__doc__ if param.annotation != inspect._empty else "No further description provided."
                    }
                    for param in sig.parameters.values() if param.name != "self"
                }
                tools.append({
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": inspect.getdoc(func) or "No further description provided.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                **params
                            }
                        }
                    }
                })
        return tools

    @ staticmethod
    def get_methods_info_string() -> str:
        """Extracts and returns information about all public methods of this class as a JSON string."""
        return json.dumps(DatabaseConnector.get_methods_info(), indent=4)
