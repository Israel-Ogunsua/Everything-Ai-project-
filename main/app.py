from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


 # db intitialized here
app = Flask(__name__)
app.config["SECRET_KEY"] = '162f7c7a3564f15ff5716druc'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Real.db'  
 
db  = SQLAlchemy(app)
app.app_context().push()

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category ='info'


import route, models

