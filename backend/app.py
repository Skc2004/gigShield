import pandas as pd
import numpy as np
import requests
import uuid
import random
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from models import db, User, Policy, Claim, Order
from fraud_detection import perform_ela_check, verify_exif_data, process_voice_claim

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'gigshield_production.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "GigShield Backend"})

# Dummy Model Training
def _t_p():
    d = pd.DataFrame({'temp': np.random.uniform(25, 45, 100), 'rain': np.random.uniform(0, 100, 100), 'traffic': np.random.uniform(0, 10, 100), 'premium': np.random.uniform(100, 500, 100)})
    return RandomForestRegressor(n_estimators=50, random_state=42).fit(d[['temp', 'rain', 'traffic']], d['premium'])
pm = _t_p()

ZONES = {
    'Koramangala, BLR': (12.9352, 77.6245),
    'Indiranagar, BLR': (12.9784, 77.6408),
    'Andheri West, MUM': (19.1363, 72.8277),
    'South Ex, DEL': (28.5684, 77.2183)
}

def fetch_live_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=precipitation_probability,rain"
        response = requests.get(url, timeout=3).json()
        current_temp = response.get('current_weather', {}).get('temperature', 35.0)
        hr_idx = min(len(response.get('hourly', {}).get('rain', [0])) - 1, datetime.now().hour)
        rain_mm = response.get('hourly', {}).get('rain', [0])[hr_idx]
        rain_prob = response.get('hourly', {}).get('precipitation_probability', [0])[hr_idx]
        is_high_risk = rain_prob > 50 or current_temp > 38
        return current_temp, float(rain_mm), float(rain_prob), is_high_risk
    except:
        return 35.0, 0.0, 15.0, False

@app.route('/api/auth/check', methods=['POST'])
def check_user():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    
    user = User.query.filter_by(phone=phone).first()
    if user:
        if password and check_password_hash(user.password_hash, password):
            return jsonify({
                "exists": True, 
                "user": {
                    "id": user.id,
                    "phone": user.phone,
                    "name": user.name,
                    "role": user.role,
                    "zone": user.zone,
                    "platform": user.platform
                }
            })
        elif not password:
            # Just checking if user exists for registration flow
            return jsonify({"exists": True, "needs_password": True})
        else:
            return jsonify({"exists": True, "error": "Invalid password"}), 401
            
    return jsonify({"exists": False})

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.json
    phone = data.get('phone')
    role = data.get('role', 'agent')
    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(
            phone=phone,
            name=data.get('name', 'Partner'),
            role=role,
            zone=data.get('zone', 'Koramangala, BLR') if role == 'agent' else None,
            platform=data.get('platform', 'Food') if role == 'agent' else None,
            password_hash=generate_password_hash(data.get('password', '1234'))
        )
        db.session.add(user)
        db.session.flush()

        if role == 'agent':
            # Create 3-5 dummy orders to seed the dashboard
            for _ in range(random.randint(3, 5)):
                order = Order(
                    user_id=user.id,
                    distance_km=round(random.uniform(1.5, 12.0), 1),
                    time_taken_mins=random.randint(15, 45)
                )
                db.session.add(order)
            
        db.session.commit()

    return jsonify({
        "success": True, 
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name,
            "role": user.role,
            "zone": user.zone,
            "platform": user.platform
        }
    })

@app.route('/api/weather', methods=['GET'])
def get_weather():
    zone = request.args.get('zone', 'Koramangala, BLR')
    lat, lon = ZONES.get(zone, ZONES['Koramangala, BLR'])
    curr_t, rain_mm, rain_prob, is_high_risk = fetch_live_weather(lat, lon)
    return jsonify({
        'zone': zone,
        'temperature': curr_t,
        'rain_mm': rain_mm,
        'rain_probability': rain_prob,
        'high_risk': is_high_risk
    })

@app.route('/api/quote', methods=['POST'])
def get_quote():
    data = request.json
    zone = data.get('zone', 'Koramangala, BLR')
    lat, lon = ZONES.get(zone, ZONES['Koramangala, BLR'])
    phone = data.get('phone', 'Unknown')
    
    current_temp, rain_mm, rain_prob, is_high_risk = fetch_live_weather(lat, lon)
    traffic_index = np.random.uniform(4, 9)
    input_features = pd.DataFrame([[current_temp, rain_mm, traffic_index]], columns=['temp', 'rain', 'traffic'])
    prediction = pm.predict(input_features)[0]
    base_premium = round(prediction, 2)
    
    # Dynamic Premium Adjustment based on claims history
    user = User.query.filter_by(phone=phone).first()
    historical_claims_count = 0
    multiplier = 1.0
    if user and user.role == 'agent':
        historical_claims = Claim.query.filter_by(user_id=user.id).all()
        historical_claims_count = len(historical_claims)
        # Increase premium by 5% per historical claim
        multiplier = 1.0 + (historical_claims_count * 0.05)
    
    weekly_premium = round(base_premium * multiplier, 2)
    
    if user and user.role == 'agent':
        policy = Policy.query.filter_by(phone=phone).first()
        if not policy:
            new_policy = Policy(
                user_id=user.id,
                phone=phone,
                zone=zone,
                platform=data.get('platform', 'Food'),
                premium=weekly_premium,
                status='active'
            )
            db.session.add(new_policy)
            db.session.commit()

    return jsonify({
        'zone': zone,
        'weekly_premium': weekly_premium,
        'base_premium': base_premium,
        'multiplier': multiplier,
        'currency': 'INR',
        'risk_factors': {'temp': current_temp, 'rain_mm': rain_mm, 'traffic': round(traffic_index, 1), 'high_risk': is_high_risk}
    })

@app.route('/api/worker/data', methods=['GET'])
def get_worker_data():
    phone = request.args.get('phone')
    user = User.query.filter_by(phone=phone).first()
    if not user: return jsonify({"error": "User not found"}), 404

    policy = Policy.query.filter_by(user_id=user.id).order_by(Policy.created_at.desc()).first()
    claims = Claim.query.filter_by(user_id=user.id).order_by(Claim.timestamp.desc()).all()
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    
    return jsonify({
        'policy': {
            'id': policy.id,
            'platform': policy.platform,
            'premium': policy.premium,
            'created_at': policy.created_at
        } if policy else None,
        'claims': [{
            'id': c.id,
            'status': c.status,
            'reason': c.reason,
            'amount': c.amount,
            'txn_id': c.txn_id,
            'order_id': c.order_id,
            'timestamp': c.timestamp
        } for c in claims],
        'orders': [{
            'id': o.id,
            'distance_km': o.distance_km,
            'time_taken_mins': o.time_taken_mins,
            'created_at': o.created_at
        } for o in orders]
    })

@app.route('/api/claims/initiate', methods=['POST'])
def initiate_claim():
    data = request.json
    phone = data.get('phone')
    order_id = data.get('order_id')
    # Extract fields for WoW features
    weather_override = data.get('simulated_weather', None) 
    exif_data = data.get('exif_data', None)
    audio_text = data.get('audio_text', None)
    
    user = User.query.filter_by(phone=phone).first()
    if not user: return jsonify({"error": "User not found"}), 404
    
    order = Order.query.get(order_id)
    if not order or order.user_id != user.id:
        return jsonify({"error": "Invalid order ID"}), 400

    # Avoid duplicate claims
    existing = Claim.query.filter_by(order_id=order.id).first()
    if existing: return jsonify({"error": "Claim already filed"}), 400

    lat, lon = ZONES.get(user.zone, ZONES['Koramangala, BLR'])
    curr_t, rain_mm, _, _ = fetch_live_weather(lat, lon)
    
    # NLP Context-Aware Extraction
    extracted_intent = process_voice_claim(audio_text) if audio_text else ""
    
    if weather_override == 'rain' or rain_mm > 0 or extracted_intent == 'rain':
        weather_cond = 'rain'
        base_payout = 100
    elif weather_override == 'heat' or curr_t > 38 or extracted_intent == 'heat':
        weather_cond = 'heat'
        base_payout = 150
    else:
        weather_cond = 'rain'
        base_payout = 100

    distance_bonus = order.distance_km * 10
    payout_amount = round(base_payout + distance_bonus, 2)
    
    # Track 1: AI Engine Fraud Checks
    fraud_flagged = False
    fraud_reasons = []
    
    # 1. ELA Check (10% random logic handled in func)
    is_ela_tampered, ela_score = perform_ela_check(None)
    if is_ela_tampered:
        fraud_flagged = True
        fraud_reasons.append(f"Image Tampered (ELA Score: {ela_score})")
        
    # 2. EXIF Spoofing check
    is_spoofed, spoof_reason = verify_exif_data(exif_data, lat, lon)
    if is_spoofed:
        fraud_flagged = True
        fraud_reasons.append(spoof_reason)
        
    final_fraud_reason = " | ".join(fraud_reasons) if fraud_reasons else None
    
    # Automated Approval Logic (Track 2 Gateway Integration)
    status = 'approved' if not fraud_flagged else 'pending'
    txn_id = f"pi_test_{uuid.uuid4().hex[:12]}" if status == 'approved' else None

    new_claim = Claim(
        user_id=user.id,
        order_id=order.id,
        phone=phone,
        status=status,
        reason=f'{weather_cond.capitalize()} conditions detected. Intent: {extracted_intent}. Route: {order.distance_km}km',
        weather_condition=weather_cond,
        amount=payout_amount,
        txn_id=txn_id,
        fraud_flag=fraud_flagged,
        fraud_reason=final_fraud_reason,
        audio_transcript=audio_text,
        exif_lat=exif_data.get('lat') if exif_data else None,
        exif_lon=exif_data.get('lon') if exif_data else None,
        exif_timestamp=exif_data.get('timestamp') if exif_data else None
    )
    db.session.add(new_claim)
    db.session.commit()
    
    # If approved instantly, simulate Stripe/Razorpay automated webhook triggering
    # In a real system, the webhook would hit an endpoint. We just return the sync success here.
    return jsonify({
        'status': status, 
        'claim_id': new_claim.id, 
        'payout': payout_amount,
        'fraud_flagged': fraud_flagged,
        'txn_id': txn_id,
        'message': 'Payout Instant Approval!' if status == 'approved' else 'Claim sent for manual review due to fraud checks.'
    })

@app.route('/api/manager/dashboard', methods=['GET'])
def manager_dashboard():
    agents = User.query.filter_by(role='agent').all()
    claims = Claim.query.order_by(Claim.timestamp.desc()).all()
    
    active_policies = db.session.query(db.func.count(Policy.id)).scalar() or 0
    total_premiums = db.session.query(db.func.sum(Policy.premium)).scalar() or 0
    total_claims_paid = db.session.query(db.func.sum(Claim.amount)).filter(Claim.status == 'approved').scalar() or 0
    
    return jsonify({
        'agents': [{
            "id": u.id, "name": u.name, "phone": u.phone, 
            "zone": u.zone, "platform": u.platform, "created_at": u.created_at
        } for u in agents],
        'claims': [{
            "id": c.id, "agent_name": c.user.name if c.user else "Unknown",
            "phone": c.phone, "amount": c.amount, "status": c.status,
            "reason": c.reason, "order_id": c.order_id, "timestamp": c.timestamp,
            "fraud_flag": c.fraud_flag, "fraud_reason": c.fraud_reason
        } for c in claims],
        'metrics': {
            'active_policies': active_policies,
            'total_premiums_collected': round(total_premiums, 2),
            'total_claims_paid': total_claims_paid,
            'pending_claims': len([c for c in claims if c.status == 'pending'])
        }
    })

@app.route('/api/manager/claims/update', methods=['POST'])
def update_claim():
    data = request.json
    claim_id = data.get('claim_id')
    status = data.get('status')
    
    if status not in ['approved', 'declined']: 
        return jsonify({"error": "Invalid status"}), 400
        
    claim = Claim.query.get(claim_id)
    if claim:
        claim.status = status
        if status == 'approved':
            claim.txn_id = f"pi_prod_{uuid.uuid4().hex[:12]}"
        db.session.commit()
        return jsonify({"success": True, "claim_id": claim.id, "status": claim.status, "txn_id": claim.txn_id})
    return jsonify({"error": "Claim not found"}), 404

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    role = request.args.get('role')
    user_id = request.args.get('user_id')
    
    if role == 'agent' and user_id:
        # Payouts over last 30 days and 12 months
        claims = Claim.query.filter_by(user_id=user_id, status='approved').all()
    else:
        # Manager: Total payouts across all agents
        claims = Claim.query.filter_by(status='approved').all()
    
    # Process into buckets (simplified for dummy purposes)
    # In a real app we'd use SQL aggregation
    daily = {}
    monthly = {}
    
    for c in claims:
        # Parse ISO date (YYYY-MM-DD...)
        d_str = c.timestamp[:10]
        m_str = c.timestamp[:7]
        daily[d_str] = daily.get(d_str, 0) + c.amount
        monthly[m_str] = monthly.get(m_str, 0) + c.amount
        
    return jsonify({
        "daily": sorted([{"date": k, "amount": v} for k, v in daily.items()], key=lambda x: x['date']),
        "monthly": sorted([{"month": k, "amount": v} for k, v in monthly.items()], key=lambda x: x['month'])
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
