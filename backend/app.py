import pandas as pd
import numpy as np
import requests
import uuid
import os
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from models import db, Worker, Policy, Claim

app = Flask(__name__)
CORS(app)

# Configure SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'gigshield_production.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

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
    phone = request.json.get('phone')
    worker = Worker.query.filter_by(phone=phone).first()
    if worker:
        return jsonify({
            "exists": True, 
            "user": {
                "phone": worker.phone,
                "name": worker.name,
                "zone": worker.zone,
                "platform": worker.platform
            }
        })
    return jsonify({"exists": False})

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.json
    phone = data.get('phone')
    worker = Worker.query.filter_by(phone=phone).first()
    if not worker:
        worker = Worker(
            phone=phone,
            name=data.get('name', 'Partner'),
            zone=data.get('zone', 'Koramangala, BLR'),
            platform=data.get('platform', 'Food')
        )
        db.session.add(worker)
        db.session.commit()
    return jsonify({
        "success": True, 
        "user": {
            "phone": worker.phone,
            "name": worker.name,
            "zone": worker.zone,
            "platform": worker.platform
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
    weekly_premium = round(prediction, 2)
    
    # Create policy if worker exists but lacks one
    worker = Worker.query.filter_by(phone=phone).first()
    if worker:
        policy = Policy.query.filter_by(phone=phone).first()
        if not policy:
            new_policy = Policy(
                worker_id=worker.id,
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
        'currency': 'INR',
        'risk_factors': {'temp': current_temp, 'rain_mm': rain_mm, 'traffic': round(traffic_index, 1), 'high_risk': is_high_risk}
    })

@app.route('/api/worker/data', methods=['GET'])
def get_worker_data():
    phone = request.args.get('phone')
    policy = Policy.query.filter_by(phone=phone).order_by(Policy.created_at.desc()).first()
    claims = Claim.query.filter_by(phone=phone).order_by(Claim.timestamp.desc()).all()
    
    pol_dict = None
    if policy:
        pol_dict = {
            'id': policy.id,
            'platform': policy.platform,
            'premium': policy.premium,
            'created_at': policy.created_at
        }
        
    claims_list = [{
        'id': c.id,
        'status': c.status,
        'reason': c.reason,
        'amount': c.amount,
        'txn_id': c.txn_id,
        'timestamp': c.timestamp
    } for c in claims]

    return jsonify({
        'policy': pol_dict,
        'claims': claims_list
    })

@app.route('/api/simulate-disruption', methods=['POST'])
def simulate_disruption():
    data = request.json
    disruption_type = data.get('type', 'rainstorm')
    phone = data.get('phone')
    
    worker = Worker.query.filter_by(phone=phone).first()
    worker_id = worker.id if worker else None

    payout_amount = 500 if disruption_type == 'rainstorm' else 750
    txn_id = f"pi_prod_{uuid.uuid4().hex[:12]}"
    
    new_claim = Claim(
        worker_id=worker_id,
        phone=phone,
        status='approved',
        reason=f'{disruption_type.capitalize()} Detected',
        amount=payout_amount,
        txn_id=txn_id
    )
    db.session.add(new_claim)
    db.session.commit()
    
    return jsonify({'status': 'triggered', 'claim_id': new_claim.id, 'payout': payout_amount})

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    active_policies = db.session.query(db.func.count(Policy.id)).scalar() or 0
    total_premiums = db.session.query(db.func.sum(Policy.premium)).scalar() or 0
    total_claims = db.session.query(db.func.sum(Claim.amount)).filter(Claim.status == 'approved').scalar() or 0
    
    return jsonify({
        'metrics': {
            'active_policies': active_policies,
            'total_premiums_collected': round(total_premiums, 2),
            'total_claims_paid': total_claims,
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
