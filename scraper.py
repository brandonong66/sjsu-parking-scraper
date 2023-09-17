from bs4 import BeautifulSoup
import requests
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


URL = 'https://sjsuparkingstatus.sjsu.edu/'


def fetch_parking_data():
    try:
        response = requests.get(URL, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        garages = soup.select('.garage h2.garage__name')
        capacities = soup.select('.garage__fullness')

        parking_data = {garage.text.strip(): int(''.join(filter(str.isdigit, capacity.text)))
                        for garage, capacity in zip(garages, capacities)}
        return parking_data
    except requests.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        return None
    except AttributeError as e:
        print(f"Error parsing HTML: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def insert_to_db(parking_data):
    if not parking_data:
        print("No data to insert into database")
        return

    db_conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        passwd=DB_PASSWORD,
        database=DB_NAME,
    )
    db_cursor = db_conn.cursor()

    try:
        
        placeholders = ', '.join(['(%s, %s)'] * len(parking_data))
        query = f"INSERT INTO parking (garage_name, capacity) VALUES {placeholders}"
        values = [item for sublist in parking_data.items() for item in sublist]

        db_cursor.execute(query, values)
        db_conn.commit()
        print(
            f"Successfully inserted data into database")
    except mysql.connector.Error as e:
        print(f"Error inserting data into database: {e}")
        db_conn.rollback()
    finally:
        db_cursor.close()
        db_conn.close()

def lambda_handler(event, context):
    parking_data = fetch_parking_data()
    insert_to_db(parking_data)