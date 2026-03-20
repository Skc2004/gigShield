from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Worker(db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    zone = db.Column(db.String(100), nullable=True)
    platform = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    policies = db.relationship('Policy', backref='worker', lazy=True)
    claims = db.relationship('Claim', backref='worker', lazy=True)

class Policy(db.Model):
    __tablename__ = 'policies'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = db.Column(db.String(36), db.ForeignKey('workers.id'), nullable=True) # allow null for old data
    phone = db.Column(db.String(20), nullable=False)
    zone = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    premium = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

class Claim(db.Model):
    __tablename__ = 'claims'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = db.Column(db.String(36), db.ForeignKey('workers.id'), nullable=True) # allow null for old data
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    txn_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
