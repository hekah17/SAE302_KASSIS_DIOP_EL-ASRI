from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy() #initialisation de la bdd

#crea de la table des utilisateur
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) #id uniques
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    messages = db.relationship('Message', backref='author', lazy=True) #lien avec la table message

#crea de la table des message
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #ien avec l'utilisateur du message