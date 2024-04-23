from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import event
from datetime import datetime, timedelta

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phonenumber = db.Column(db.String(80), nullable=False, unique=True)
    is_active = db.Column(db.Boolean(), default=True)  # Add a boolean column for is_active
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    websites = db.relationship('Website', backref='users', lazy=True)

class Website(db.Model):
    __tablename__ = 'websites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    website_name = db.Column(db.String(100), nullable=False)
    website_password = db.Column(db.String(100), nullable=False)

