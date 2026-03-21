from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
db = client.clothes


