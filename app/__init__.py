from flask import Flask
from app.models.database import Database

database = Database("meta_v1")

#app = Flask(__name__, template_folder='../templates', static_folder='../static') 
app = Flask(__name__) 

from app import routes