import os
import random
import uuid
from datetime import datetime, timedelta
from app import app
from models import db, User, Policy, Claim, Order

ZONES = ['Koramangala, BLR', 'Indiranagar, BLR', 'Andheri West, MUM', 'South Ex, DEL']
PLATFORMS = ['Food', 'Grocery', 'E-commerce']

def seed_db():
    with app.app_context():
        # Clear existing data safely
        db.drop_all()
        db.create_all()
        
        print("Creating mock manager...")
        manager = User(
            phone="9999999999",
            name="Super Admin",
            role="manager"
        )
        db.session.add(manager)
        db.session.flush()

        print("Creating 50+ agents and claims...")
        for i in range(55):
            phone = f"98000{str(i).zfill(5)}"
            zone = random.choice(ZONES)
            platform = random.choice(PLATFORMS)
            
            user = User(
                phone=phone,
                name=f"Mock Agent {i}",
                role="agent",
                zone=zone,
                platform=platform
            )
            db.session.add(user)
            db.session.flush()
            
            # Policy
            policy = Policy(
                user_id=user.id,
                phone=phone,
                zone=zone,
                platform=platform,
                premium=round(random.uniform(50.0, 300.0), 2),
                status='active'
            )
            db.session.add(policy)
            
            # Orders
            orders_count = random.randint(3, 10)
            user_orders = []
            for j in range(orders_count):
                order = Order(
                    user_id=user.id,
                    distance_km=round(random.uniform(1.0, 15.0), 1),
                    time_taken_mins=random.randint(10, 60)
                )
                db.session.add(order)
                db.session.flush()
                user_orders.append(order)
                
            # Claims
            claims_count = random.randint(1, 3)
            for j in range(claims_count):
                sel_order = random.choice(user_orders)
                # Ensure no duplicate claim per order
                if Claim.query.filter_by(order_id=sel_order.id).first():
                    continue
                
                is_fraud = random.random() < 0.2
                status = 'approved' if not is_fraud else 'pending'
                amount = round(100.0 + (sel_order.distance_km * 10), 2)
                
                claim = Claim(
                    user_id=user.id,
                    order_id=sel_order.id,
                    phone=phone,
                    status=status,
                    reason=f"Rain conditions. Route: {sel_order.distance_km}km",
                    weather_condition="rain",
                    amount=amount,
                    txn_id=f"pi_test_{uuid.uuid4().hex[:12]}" if status == 'approved' else None,
                    fraud_flag=is_fraud,
                    fraud_reason="EXIF location far from live ping (diff: 0.08)" if is_fraud else None,
                    timestamp=(datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
                )
                db.session.add(claim)
                
        db.session.commit()
        print("Database seeded completely!")

if __name__ == "__main__":
    seed_db()
