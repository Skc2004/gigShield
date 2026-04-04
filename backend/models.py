from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), default='GIG_WORKER') # 'GIG_WORKER' or 'FLEET_MANAGER'
    company = db.Column(db.String(50), nullable=True)
    base_location = db.Column(db.String(100), nullable=True)
    daily_earnings = db.Column(db.Float, nullable=True)
    working_hours = db.Column(db.Integer, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True) # password for security
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    quotes = db.relationship('Quote', backref='user', lazy=True)
    policies = db.relationship('Policy', backref='user', lazy=True)
    claims = db.relationship('Claim', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

class Quote(db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    tier_name = db.Column(db.String(50), nullable=False)
    billing_cycle = db.Column(db.String(20), nullable=False, default='Weekly')
    premium_amount = db.Column(db.Float, nullable=False)
    coverage_payout = db.Column(db.Float, nullable=False)
    active_status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

    policies = db.relationship('Policy', backref='quote', lazy=True)

class Policy(db.Model):
    __tablename__ = 'policies'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    quote_id = db.Column(db.String(36), db.ForeignKey('quotes.id'), nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    claims = db.relationship('Claim', backref='policy', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    distance_km = db.Column(db.Float, nullable=False)
    time_taken_mins = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    claims = db.relationship('Claim', backref='order', lazy=True)

class Claim(db.Model):
    __tablename__ = 'claims'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    policy_id = db.Column(db.String(36), db.ForeignKey('policies.id'), nullable=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=True)
    trigger_event = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, approved, declined
    reason = db.Column(db.String(255), default='Loss of Income') 
    payout_amount = db.Column(db.Float, nullable=False)
    txn_id = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
