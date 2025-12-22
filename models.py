from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

#crea de la table d'association des amis
friendship = db.Table('friendship',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

#crea de la table des utilisateurs
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    #relation entre la table d'association friend et la table user
    friends = db.relationship('User', 
                              secondary=friendship,
                              primaryjoin=(friendship.c.user_id == id),
                              secondaryjoin=(friendship.c.friend_id == id),
                              backref=db.backref('friend_of', lazy='dynamic'),
                              lazy='dynamic')
    messages_sent = db.relationship('Message', backref='author', lazy=True, foreign_keys='Message.sender_id')
    messages_received = db.relationship('Message', backref='recipient', lazy=True, foreign_keys='Message.recipient_id')

#crea de la table des messages
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)