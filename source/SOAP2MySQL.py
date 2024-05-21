import argparse
import json
import os
import sys
import MySQLdb
from zeep import Client

def load_config(config_path):
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.path.dirname(__file__), config_path)

    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the configuration file: {config_path}")
        sys.exit(1)

def connect_to_database(config):
    try:
        return MySQLdb.connect(
            host=config['host'],
            user=config['user'],
            passwd=config['passwd'],
            db=config['db']
        )
    except MySQLdb.Error as err:
        print(f"Database connection error: {err}")
        sys.exit(1)

def create_cursor(connection):
    try:
        return connection.cursor()
    except MySQLdb.Error as err:
        print(f"Error creating cursor: {err}")
        connection.close()
        sys.exit(1)

def create_table(cursor, table_name, columns):
    try:
        create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        cursor.execute(create_query)
    except MySQLdb.Error as err:
        print(f"Error creating table: {err}")
        cursor.close()
        connection.close()
        sys.exit(1)

def insert_data(cursor, table_name, columns, data):
    try:
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE Name = VALUES(Name)"
        cursor.executemany(insert_query, data)
    except MySQLdb.Error as err:
        print(f"Error inserting data: {err}")
        cursor.close()
        connection.close()
        sys.exit(1)

def query_data(cursor, table_name, columns):
    try:
        select_query = f"SELECT {', '.join(columns)} FROM {table_name} ORDER BY Name ASC LIMIT 10"
        cursor.execute(select_query)
        results = cursor.fetchall()
        for row in results:
            print(row)
    except MySQLdb.Error as err:
        print(f"Error querying data: {err}")
        cursor.close()
        connection.close()
        sys.exit(1)

def commit_transaction(connection):
    try:
        connection.commit()
    except MySQLdb.Error as err:
        print(f"Error committing transaction: {err}")
        cursor.close()
        connection.close()
        sys.exit(1)

if __name__ == "__main__":
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process database configuration file location.")
    parser.add_argument('--config', type=str, default='db_config.json', 
                        help='Path to the JSON configuration file. Default is db_config.json in the same directory as the script.')

    # Parse arguments
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Request data from SOAP services
    try:
        client = Client('http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL')
        response = client.service.ListOfCountryNamesByCode()
    except Exception as e:
        print(f"Error fetching data from SOAP service: {e}")
        sys.exit(1)

    # Unpack ISOCode and Name and replace '&' with 'and'
    data = [(obj.sISOCode, obj.sName.replace('&', 'and')) for obj in response]

    # Connect to the MySQL server
    connection = connect_to_database(config)
    cursor = create_cursor(connection)

    # Define table name and column names
    table_name = "country_names"
    columns = ["ISOCODE VARCHAR(3) PRIMARY KEY", "Name VARCHAR(255)"]

    # Create table
    create_table(cursor, table_name, columns)

    # Insert data into the table
    insert_data(cursor, table_name, [col.split()[0] for col in columns], data)

    # Query the first 10 countries in alphabetical order
    query_data(cursor, table_name, [col.split()[0] for col in columns])

    # Commit the transaction
    commit_transaction(connection)

    # Close cursor and connection
    cursor.close()
    connection.close()
