from flask import Flask, request
from pymongo import MongoClient

class LearningObject():
    def __init__(self, learning_object_item, name_site, api_site):
        self.general = {
            "identifier": [str(api_site), learning_object_item["question_id"]],
            "title": learning_object_item["title"],
            "catalog_entry":{
                "catalogue": learning_object_item["tags"],
                "entry": learning_object_item["link"]
            },
            "language": None,
            "description":{
                "question": learning_object_item["body"],
                "answers": learning_object_item["answers"]  
            },
            "keywords": learning_object_item["tags"],
            "coverage": None,
            "structure": ["linear", "Hireárquico"],
            "aggregation_level": "2"
        }
        try:
            self.life_cycle = {
            "version": None,
            "status": "Revisado",
            "contribute":{
                "role": "Autor",
                "entity": "{}-{}".format(str(learning_object_item["owner"]["user_id"]), str(learning_object_item["owner"]["display_name"])),
                "date": learning_object_item["creation_date"]
            }
        }
        except:
            self.life_cycle = {
                "version": None,
                "status": "Revisado",
                "contribute":{
                    "role": "Autor",
                    "entity": "{}-{}".format("0", str(learning_object_item["owner"]["display_name"])),
                    "date": learning_object_item["creation_date"]
                }
            }
        try:
            self.meta_metadata = {
                "identifier": [str(api_site), learning_object_item["question_id"]],
                "catalog":{
                    "catalog": learning_object_item["tags"],
                    "entry": learning_object_item["link"]
                },
                "contribute":{
                    "role": "Autor",
                    "entity": "{}-{}".format(str(learning_object_item["owner"]["user_id"]), str(learning_object_item["owner"]["display_name"])),
                    "date": learning_object_item["creation_date"]
                },
                "metadata_scheme": "IEEE LOM",
                "language": None
            }
        except:
            self.meta_metadata = {
                "identifier": [str(api_site), learning_object_item["question_id"]],
                "catalog":{
                    "catalog": learning_object_item["tags"],
                    "entry": learning_object_item["link"]
                },
                "contribute":{
                    "role": "Autor",
                    "entity": "{}-{}".format("0", str(learning_object_item["owner"]["display_name"])),
                    "date": learning_object_item["creation_date"]
                },
                "metadata_scheme": "IEEE LOM",
                "language": None
            }
        self.technical = {
            "format": "text/html",
            "size": None,
            "location": learning_object_item["link"],
            "requirements":{
                "type": "Operating System",
                "name": "Linux",
                "min_version": None,
                "max_version": None
            },
            "installation_remarks": None,
            "other_platform_requirements": None,
            "duration": None
        }
        self.educational = {
            "interactivity_type": "Expositivo",
            "learning_resource_type": "Texto Narrativo",
            "interactivity_level": "Baixo",
            "semantic_density": "Médio",
            "intended_end_user_role": "Professor",
            "context": "Todos",
            "typical_age_range": "12+",
            "difficulty": "Fácil",
            "typical_learning_time": None,
            "description": None,
            "language": None
        }
        self.rights = {
            "cost": "Não",
            "copyright_&_other_restrictions": "Não",
            "description": "Acesso Público"
        }
        self.relation = {
            "kind": None,
            "resource":{
                "identifier": None,
                "description": None,
                "catalog_entry": None
            }
        }
        self.annotation = {
            "person": None,
            "date": None,
            "description": None
        }
        self.classification = {
            "purpose": "Objetivo Educacional",
            "taxon_path":{
                "source": name_site,
                "taxon":{
                    "id": "url",
                    "entry": learning_object_item["link"]
                }
            },
            "description":{
                "question": learning_object_item["body"],
                "answers": learning_object_item["answers"],
            },
            "keywords": learning_object_item["tags"]
    }

    def get_as_json(self):
        return self.__dict__
        