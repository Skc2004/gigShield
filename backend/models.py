from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), default='agent') # 'agent' or 'manager'
    zone = db.Column(db.String(100), nullable=True)
    platform = db.Column(db.String(50), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True) # password for security
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    policies = db.relationship('Policy', backref='user', lazy=True)
    claims = db.relationship('Claim', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    distance_km = db.Column(db.Float, nullable=False)
    time_taken_mins = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    claims = db.relationship('Claim', backref='order', lazy=True)

class Policy(db.Model):
    __tablename__ = 'policies'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    zone = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    premium = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

class Claim(db.Model):
    __tablename__ = 'claims'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, approved, declined
    reason = db.Column(db.String(255), nullable=False) 
    weather_condition = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    txn_id = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
