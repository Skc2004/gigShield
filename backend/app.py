import sqlite3
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

app = Flask(__name__)
CORS(app)

DATABASE = 'gigshield_production.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS policies (
                            id TEXT PRIMARY KEY,
                            phone TEXT,
                            zone TEXT,
                            platform TEXT,
                            premium REAL,
                            status TEXT,
                            created_at TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS claims (
                            id TEXT PRIMARY KEY,
                            phone TEXT,
                            status TEXT,
                            reason TEXT,
                            amount REAL,
                            txn_id TEXT,
                            timestamp TEXT)''')
        db.commit()

init_db()

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
    
    # Auto-enroll internally
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM policies WHERE phone=?", (phone,))
    if not cursor.fetchone():
        policy_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO policies (id, phone, zone, platform, premium, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (policy_id, phone, zone, data.get('platform', 'Food'), weekly_premium, 'active', datetime.now().isoformat()))
        db.commit()

    return jsonify({
        'zone': zone,
        'weekly_premium': weekly_premium,
        'currency': 'INR',
        'risk_factors': {'temp': current_temp, 'rain_mm': rain_mm, 'traffic': round(traffic_index, 1), 'high_risk': is_high_risk}
    })

@app.route('/api/worker/data', methods=['GET'])
def get_worker_data():
    phone = request.args.get('phone')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, platform, premium, created_at FROM policies WHERE phone=? ORDER BY created_at DESC LIMIT 1", (phone,))
    pol = cursor.fetchone()
    cursor.execute("SELECT id, status, reason, amount, txn_id, timestamp FROM claims WHERE phone=? ORDER BY timestamp DESC", (phone,))
    claims = [dict(c) for c in cursor.fetchall()]
    return jsonify({
        'policy': dict(pol) if pol else None,
        'claims': claims
    })

@app.route('/api/simulate-disruption', methods=['POST'])
def simulate_disruption():
    data = request.json
    disruption_type = data.get('type', 'rainstorm')
    phone = data.get('phone')
    
    db = get_db()
    cursor = db.cursor()
    claim_id = str(uuid.uuid4())
    payout_amount = 500 if disruption_type == 'rainstorm' else 750
    txn_id = f"pi_prod_{uuid.uuid4().hex[:12]}"
    
    cursor.execute("INSERT INTO claims (id, phone, status, reason, amount, txn_id, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (claim_id, phone, 'approved', f'{disruption_type.capitalize()} Detected', payout_amount, txn_id, datetime.now().isoformat()))
    db.commit()
    
    return jsonify({'status': 'triggered', 'claim_id': claim_id, 'payout': payout_amount})

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*), SUM(premium) FROM policies")
    pol_row = cursor.fetchone()
    cursor.execute("SELECT SUM(amount) FROM claims WHERE status='approved'")
    payout_row = cursor.fetchone()
    
    return jsonify({
        'metrics': {
            'active_policies': pol_row[0] or 0,
            'total_premiums_collected': round(pol_row[1] or 0, 2),
            'total_claims_paid': payout_row[0] or 0,
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
