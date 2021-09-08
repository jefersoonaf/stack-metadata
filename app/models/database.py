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
    
    def sort(self, collection_name, order, limit):
        return list(self.database[str(collection_name)].find().sort("_id",order).limit(limit))

    def update(self, collection_name, db_instance, instance):
        instance = dict(instance)
        self.database[str(collection_name)].update_one({"_id": db_instance["_id"]}, {"$set": instance})
    
    def update_all(self, collection_name, field, where, update):
        self.database[str(collection_name)].update_many({f"{field}": where}, {"$set": {f"{field}": update}})

    def delete(self, collection_name, instance):
        self.database[str(collection_name)].delete_one({"_id": instance["_id"]})
        
    def search_advanced(self, collection_name, search, site, date_start, date_end, order, type_search):
        query = {}
        if type_search == "Título":
            query = {"general.title": {"$regex": f".*{search}.*", 
                                       "$options": "is"}, 
                     "general.identifier.0": f"{site}", 
                     "meta_metadata.contribute.date": {"$gt": date_start, 
                                                       "$lt": date_end}}
        elif type_search == "Descrição":
            query = {"general.description.question": {"$regex": f".*{search}.*", 
                                       "$options": "is"}, 
                     "general.identifier.0": f"{site}", 
                     "meta_metadata.contribute.date": {"$gt": date_start, 
                                                       "$lt": date_end}}
        elif type_search == "Autor":
            query = {"life_cycle.contribute.entity": {"$regex": f".*{search}.*", 
                                       "$options": "is"}, 
                     "general.identifier.0": f"{site}", 
                     "meta_metadata.contribute.date": {"$gt": date_start, 
                                                       "$lt": date_end}}
        else: #Idioma
            query = {"general.language": {"$regex": f".*{search}.*", 
                                       "$options": "is"}, 
                     "general.identifier.0": f"{site}", 
                     "meta_metadata.contribute.date": {"$gt": date_start, 
                                                       "$lt": date_end}}
            
        return list(self.database[str(collection_name)].find(query).sort("meta_metadata.contribute.date", 1 if order == "Crescente" else -1))
            
        """if site != None and "":
            query = {"$and": [{"general.identifier": site},{"general.title": {"$regex": f".*{search}.*", "$options": "is"}}]}
        return self.filter_by("learning_objects", query)"""
        