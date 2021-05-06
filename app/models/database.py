from pymongo import MongoClient
from bson.objectid import ObjectId


class Database(object):
    def __init__(self, database_name):
        self.client = MongoClient('localhost', 27017)
        self.database = self.client[str(database_name)]

    @property
    def is_online(self):
        return bool(self.server_status['ok'])

    @property
    def stats(self):
        return self.database.command("dbstats")

    @property
    def server_status(self):
        return self.database.command("serverStatus")

    @property
    def collections(self):
        return self.database.collection_names()
    
    def create(self, collection_name, instance):
        self.database[str(collection_name)].insert(instance.get_as_json())

    def read_one(self, collection_name, instance_id):
        return self.database[str(collection_name)].find_one({"_id": ObjectId(instance_id)})
    
    def filter_by(self, collection_name, filter_options):
        return list(self.database[str(collection_name)].find(filter_options))
    
    def list(self, collection_name):
        return list(self.database[str(collection_name)].find())

    def update(self, collection_name, instance):
        instance = dict(instance)
        self.database[str(collection_name)].update_one({"_id": instance["_id"]}, {"$set": instance})

    def delete(self, collection_name, instance):
        self.database[str(collection_name)].delete_one({"_id": instance["_id"]})