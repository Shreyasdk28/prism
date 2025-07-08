from pymongo import MongoClient
import os

class MongoDBClient:
    def __init__(self):
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(mongo_uri)
        self.db = self.client["shopping_ai"]  # or any db name

    def insert_output(self, collection_name, data):
        collection = self.db[collection_name]
        return collection.insert_one(data)