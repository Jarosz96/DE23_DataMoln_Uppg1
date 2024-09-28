import json
from azure.storage.queue import QueueServiceClient
from dotenv import load_dotenv
import os

# Import .env variables to define your Azure Queue connection string, name and path to JSON file
load_dotenv()
connection_string = os.getenv("CONNECTION_STRING")
queue_name = os.getenv("QUEUE_NAME")
json_file_path = os.getenv("JSON_FILE_PATH")

# Connect to the queue service and access the specified queue.
queue_service_client = QueueServiceClient.from_connection_string(conn_str=connection_string)
queue_client = queue_service_client.get_queue_client(queue=queue_name)

with open(json_file_path, 'r') as file:
    json_data = json.load(file)

# Convert JSON data to str and send message to Azure Queue
message = json.dumps(json_data)
queue_client.send_message(message)