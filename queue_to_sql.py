import pyodbc
import json
from azure.storage.queue import QueueServiceClient
from dotenv import load_dotenv
import os

# Connectrion details for SQL server
load_dotenv()
server = os.getenv('SERVER')
database = os.getenv('DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('PASSWORD')
driver = os.getenv('DRIVER')
connection_string = os.getenv('CONNECTION_STRING')
queue_name = os.getenv('QUEUE_NAME')

# Connect to the database
conn = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
cursor = conn.cursor()

# Connect to the queue and retrieve messages to process.
queue_service_client = QueueServiceClient.from_connection_string(conn_str=connection_string)
queue_client = queue_service_client.get_queue_client(queue=queue_name)
messages = queue_client.receive_messages()

# Checks for messages to process
insert_data = []
for message in messages:
    data = json.loads(message.content)

    for person in data:
        insert_data.append((
            person.get('ar'),
            person.get('kon'),
            person.get('folkmangd'),
            person.get('levande_fodda'),
            person.get('doda'),
            person.get('gifta'),
            person.get('ogifta'),
            person.get('skilda')
        ))

if insert_data:
    cursor.executemany('''
        INSERT INTO dbo.population_data (year, gender_code, total_population, births, deaths, unmarried_population, married_population, divorced_population)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', insert_data)

    conn.commit()

    # Clear Asure Queue to prevent duplicate data since JSON file is writing new data and not appendeing
    queue_client.clear_messages()


cursor.close()
conn.close()