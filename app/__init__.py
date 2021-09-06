from flask import Flask
from app.models.database import Database
from flask_login import LoginManager
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import logging
import datetime
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE = os.getenv("DATABASE")
SECRET_KEY = os.getenv("SECRET_KEY")
USERNAME_EMAIL = os.getenv("USERNAME_EMAIL")
PASSWORD_EMAIL = os.getenv("PASSWORD_EMAIL")
#### Limite diário de busca padrão na API para novos usuários ####
SEARCH_LIMIT = 20

database = Database(DATABASE)

#agendador de tarefas
def job_function():
    list_users_db = database.filter_by("users", {"role": "standard"})
    for user in list_users_db:
        user_temp = user
        user['search_limit'] = SEARCH_LIMIT
        database.update("users", user_temp, user)
    scheduler.reschedule_job('1', trigger='cron', hour=00, minute=00, second=10)

job_defaults = {
    'coalesce': False,
    'max_instances': 1
}

scheduler = BackgroundScheduler(job_defaults=job_defaults, timezone=pytz.timezone('America/Sao_Paulo'))
scheduler.add_job(job_function, 'cron', hour=datetime.datetime.now().hour, minute=datetime.datetime.now().minute, second=datetime.datetime.now().second+10, id="1")
scheduler.start()
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


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
    MAIL_USERNAME = USERNAME_EMAIL,
    MAIL_DEFAULT_SENDER = USERNAME_EMAIL,
    MAIL_PASSWORD = PASSWORD_EMAIL
)

mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)

from app.controllers import routes