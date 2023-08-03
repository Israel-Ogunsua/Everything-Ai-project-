from main import app, login_manager, db
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(70), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable = False, unique= True)
    password = db.Column(db.String(225), nullable = False)
    archives = db.relationship('Archive', backref='author', lazy=True)

    def __repr__(self):
        return f'User({self.username},{self.email}, {self.password},{self.posts} )'


class Archive(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    title  = title = db.Column(db.String(1000))
    discription = db.Column(db.String(2550))
    timePosted = db.Column(db.DateTime, default=datetime.now)
    archived_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'User({self.title},{self.discription})'

