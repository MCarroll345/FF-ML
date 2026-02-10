from dotenv import dotenv_values
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

config = dotenv_values(".env")

client = MongoClient("mongodb+srv://MCarroll123:eebee261202@fitfinder.uzlpzrs.mongodb.net/?retryWrites=true&w=majority&appName=FitFinder", server_api=ServerApi('1'))
db = client.clothes


