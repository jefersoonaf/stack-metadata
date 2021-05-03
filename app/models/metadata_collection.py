from flask import Flask, request
from pymongo import MongoClient

class MetadataCollection():
    def __init__(self):
        self.General = {
            "Identifier": None,
            "Title": None,
            "Catalog_Entry":{
                "Catalogue": None,
                "Entry": None
                },
            "Language": None,
            "Description": None,
            "Keywords": None,
            "Coverage": None,
            "Structure": None,
            "Aggregation_Level": None
        }
        self.Life_Cycle = {
            "Version": None,
            "Status": None,
            "Contribute":{
                "Role": None,
                "Entity": None,
                "Date": None
            }
        }
        self.Meta_metadata = {
            "Identifier": None,
            "Catalog":{
                "Catalog": None,
                "Entry": None
            },
            "Contribute":{
                "Role": None,
                "Entity": None,
                "Date": None
            },
            "Metadata_Scheme": "IEEE LOM",
            "Language": None
        }
        self.Technical = {
            "Format": None,
            "Size": None,
            "Location": None,
            "Requirements":{
                "Type": None,
                "Name": None,
                "Min_version": None,
                "Max_version": None
            },
            "Installation_Remarks": None,
            "Other_platform_requirements": None,
            "Duration": None
        }
        self.Educational = {
            "Interactivity_Type": "Expositivo",
            "Learning_Resource_Type": "Texto Narrativo",
            "Interactivity_Level": "Baixo",
            "Semantic_Density": "Médio",
            "Intended_end_user_role": "Professor",
            "Context": None,
            "Typical_Age_Range": None,
            "Difficulty": None,
            "Typical_learning_Time": None,
            "Description": None,
            "Language": None
        }
        self.Rights = {
            "Cost": None,
            "Copyright_&_other_restrictions": None,
            "Description": None
        }
        self.Relation = {
            "Kind": None,
            "Resource":{
                "Identifier": None,
                "Description": None,
                "Catalog_entry": None
            }
        }
        self.Annotation = {
            "Person": None,
            "Date": None,
            "Description": None
        }
        self.Classification = {
            "Purpose": None,
            "Taxon_path":{
                "Source": None,
                "Taxon":{
                    "ID": "Objetivo Educacional",
                    "Entry": None
                }
            },
            "Description": None,
            "Keywords": None
        }

    def get_as_json(self):
        return self.__dict__
        