from app import app, db, login_manager
from  datetime import datetime
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,  UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    imagefile = db.Column(db.String(30), default="default.jpg", nullable=False)
    password = db.Column(db.String(70), nullable=False)
    chat = db.relationship('ChatPost', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}', {self.id})"
    

class ChatPost(db.Model,  UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), default="New Chat", nullable=False)
    time_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content_me = db.Column(db.String(120), nullable=False)  # Fixed column name
    content_ai = db.Column(db.String(200), nullable=False)  # Fixed column name
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, content_me, content_ai, user_id):
        self.content_me = content_me
        self.content_ai = content_ai
        self.user_id = user_id

    def __repr__(self):
        return f"ChatPost('{self.title}', {self.content_me}', '{self.content_ai}', '{self.user_id}')"

class Image(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return f"Image('{self.filename}')"