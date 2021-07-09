from flask import Flask
from app.models.database import Database
from flask_login import LoginManager
from flask_mail import Mail
import os
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
PASSWORD_EMAIL = os.getenv("PASSWORD_EMAIL")

database = Database("meta_v2")

#app = Flask(__name__, template_folder='../templates', static_folder='../static') 
#FLASK_APP=run.py
app = Flask('app') 
app.config.update(
    SECRET_KEY = SECRET_KEY,
    DEBUG = True,
    #configuração do email
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME = 'noreply.stackmetadata@gmail.com',
    MAIL_DEFAULT_SENDER = 'noreply.stackmetadata@gmail.com',
    MAIL_PASSWORD = PASSWORD_EMAIL
)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)

from app.controllers import routes