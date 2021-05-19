from flask import Flask
from app.models.database import Database
from flask_login import LoginManager
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

database = Database("meta_v1")

#app = Flask(__name__, template_folder='../templates', static_folder='../static') 
#FLASK_APP=run.py
app = Flask('app') 
app.config.update(
    SECRET_KEY = SECRET_KEY
)

#app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

login_manager = LoginManager()
login_manager.init_app(app)

from app import routes