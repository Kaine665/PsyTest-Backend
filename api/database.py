from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_URL = "mongodb+srv://Kaine:j877413fxt@clusterpsy.pylcmi3.mongodb.net/?retryWrites=true&w=majority&appName=ClusterPsy"
MONGO_DB = "psy_test"

class MongoDatabase:
    def __init__(self, url=MONGO_URL, db_name=MONGO_DB):
        try:
            self.client = MongoClient(url)
            self.db = self.client[db_name]
        except ConnectionFailure as e:
            print(f"数据库连接失败: {e}")
            self.client = None
            self.db = None

    def get_collection(self, collection_name):
        if self.db:
            return self.db[collection_name]
        return None

    def insert_one(self, collection_name, data):
        col = self.get_collection(collection_name)
        if col:
            return col.insert_one(data)
        return None

    def find(self, collection_name, query={}, projection=None):
        col = self.get_collection(collection_name)
        if col:
            return col.find(query, projection)
        return None

    def find_one(self, collection_name, query={}, projection=None):
        col = self.get_collection(collection_name)
        if col:
            return col.find_one(query, projection)
        return None

    def update_one(self, collection_name, query, update_data, upsert=False):
        col = self.get_collection(collection_name)
        if col:
            return col.update_one(query, {'$set': update_data}, upsert=upsert)
        return None

    def delete_one(self, collection_name, query):
        col = self.get_collection(collection_name)
        if col:
            return col.delete_one(query)
        return None

    def close(self):
        if self.client:
            self.client.close()