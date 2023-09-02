from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


 # db intitialized here
app = Flask(__name__)
app.config["SECRET_KEY"] = '162f7c7a3564f15ff5716druc'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Real.db'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nawqqlzjedutde:ecd99368e9056bbfa253c106a707db2cb8b1360e257a1d560d82e42f695691ba@ec2-107-21-67-46.compute-1.amazonaws.com:5432/d9l6uoj2g6gklc'  
db  = SQLAlchemy(app)
app.app_context().push()

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category ='info'


import route, models

