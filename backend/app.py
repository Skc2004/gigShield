import pandas as pd
import numpy as np
import requests
import uuid
import random
import os
import traceback
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.ensemble import RandomForestRegressor
from models import db, User, Policy, Claim, Order, Quote
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.errorhandler(500)
def handle_500(e):
    return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    traceback.print_exc()
    return jsonify({"error": str(e)}), 500

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", 'sqlite:///' + os.path.join(basedir, 'gigshield_production.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", 'gigshield_dev_secret_key_123!')

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    # Only create if not exists
    db.create_all()
    
    # Aggressively ensure Manager exists with correct role
    User.query.filter_by(phone='9999999999').update({'role': 'FLEET_MANAGER'})
    manager = User.query.filter_by(phone='9999999999').first()
    if not manager:
        manager = User(
            phone='9999999999',
            name='Fleet Administrator',
            role='FLEET_MANAGER',
            password_hash=generate_password_hash('admin123'),
            base_location='Koramangala, BLR'
        )
        db.session.add(manager)
    else:
        manager.password_hash = generate_password_hash('admin123')
    db.session.commit()
    print(f"DEBUG: Shield System Initialized. Manager Role: {manager.role}")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "GigShield Backend - Phase 2 (Formula Engine)"})

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

@app.route('/api/auth/login', methods=['POST'])
def check_user():
    data = request.json
    phone = data.get('phone')
    password = data.get('password')
    
    user = User.query.filter_by(phone=phone).first()
    if user:
        if password and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.id, additional_claims={"role": user.role})
            return jsonify({
                "exists": True, 
                "access_token": access_token,
                "user": {
                    "id": user.id, "phone": user.phone, "name": user.name, "role": user.role,
                    "base_location": user.base_location, "company": user.company
                }
            })
        elif not password:
            return jsonify({"exists": True, "needs_password": True})
        else:
            return jsonify({"exists": True, "error": "Invalid password"}), 401
    return jsonify({"exists": False})

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.json
    phone = data.get('phone')
    user = User.query.filter_by(phone=phone).first()
    if not user:
        user = User(
            phone=phone,
            name=data.get('name', 'Partner'),
            role='GIG_WORKER',
            base_location=data.get('base_location', 'Koramangala, BLR'),
            company=data.get('company', 'Food'),
            daily_earnings=data.get('daily_earnings', 1000.0),
            working_hours=data.get('working_hours', 8),
            password_hash=generate_password_hash(data.get('password', '1234'))
        )
        db.session.add(user)
        db.session.flush()

        for _ in range(random.randint(3, 5)):
            order = Order(
                user_id=user.id,
                distance_km=round(random.uniform(1.5, 12.0), 1),
                time_taken_mins=random.randint(15, 45)
            )
            db.session.add(order)
            
        db.session.commit()

    access_token = create_access_token(identity=user.id, additional_claims={"role": user.role})
    return jsonify({
        "success": True, 
        "access_token": access_token,
        "user": {
            "id": user.id, "phone": user.phone, "name": user.name, "role": user.role,
            "base_location": user.base_location, "company": user.company
        }
    })

@app.route('/api/weather', methods=['GET'])
def get_weather():
    zone = request.args.get('zone', 'Koramangala, BLR')
    lat, lon = ZONES.get(zone, ZONES['Koramangala, BLR'])
    curr_t, rain_mm, rain_prob, is_high_risk = fetch_live_weather(lat, lon)
    return jsonify({
        'zone': zone, 'temperature': curr_t, 'rain_mm': rain_mm,
        'rain_probability': rain_prob, 'high_risk': is_high_risk
    })

@app.route('/api/quotes/generate', methods=['POST'])
@jwt_required()
def get_quote():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user: return jsonify({"error": "User not found"}), 404
        
        zone = user.base_location or 'Koramangala, BLR'
        lat, lon = ZONES.get(zone, ZONES['Koramangala, BLR'])
        
        current_temp, rain_mm, rain_prob, is_high_risk = fetch_live_weather(lat, lon)
        
        # Determine traffic index based on hour of the day (Mocked for Demo Persistence)
        hour = datetime.now().hour
        if (8 <= hour <= 11) or (17 <= hour <= 20): # Peak Hours
            traffic_index = 8.5 
        else:
            traffic_index = 4.2
        
        earnings = float(user.daily_earnings or 1000.0)
        hours = int(user.working_hours or 8)
        company = user.company or 'Food'
        
        base_rate = 15.0
        weather_penalty = float(rain_prob) * 0.3
        traffic_penalty = traffic_index * 1.5
        exposure_penalty = max(0, hours - 8) * 2.0
        
        company_multiplier = 1.3 if company == 'Grocery' else 1.1 if company == 'Food' else 1.0

        # Phase 2: AI Hyper-Local Risk Nudge
        ai_nudge = round(max(0, (rain_mm * 0.5) + ((current_temp - 35) * 0.2)), 2)
        
        calculated_base_premium = (
            base_rate + weather_penalty + traffic_penalty + exposure_penalty + ai_nudge
        ) * company_multiplier

        db.session.query(Quote).filter_by(user_id=user.id, active_status=True).update({'active_status': False})

        weekly_earnings = earnings * 7

        tiers = {
            'Standard': {'coverage': 0.50, 'prem_mult': 1.0},
            'Premium': {'coverage': 0.80, 'prem_mult': 1.6},
            'Platinum': {'coverage': 1.00, 'prem_mult': 2.2}
        }
        
        generated_options = {}
        for tier, math in tiers.items():
            premium = round(calculated_base_premium * math['prem_mult'], 2)
            payout = round(weekly_earnings * math['coverage'], 2)
            
            q = Quote(user_id=user.id, tier_name=tier, billing_cycle='Weekly', premium_amount=premium, coverage_payout=payout)
            db.session.add(q)
            db.session.flush()
            
            generated_options[tier.lower()] = {
                'id': q.id,
                'premium': premium,
                'payout': payout,
                'tier': tier
            }
            
        db.session.commit()

        return jsonify({
            'zone': zone,
            'options': generated_options,
            'risk_factors': {
                'temp': current_temp,
                'rain_mm': rain_mm,
                'traffic': round(traffic_index, 1),
                'high_risk': is_high_risk,
                'ai_nudge': ai_nudge
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/quotes/accept', methods=['POST'])
@jwt_required()
def accept_quote():
    user_id = get_jwt_identity()
    quote_id = request.json.get('quote_id')
    quote = Quote.query.get(quote_id)
    if not quote or quote.user_id != user_id: return jsonify({"error": "Invalid quote"}), 400
    
    Policy.query.filter_by(user_id=user_id, status='active').update({'status': 'expired'})
    
    new_policy = Policy(user_id=user_id, quote_id=quote.id, status='active')
    db.session.add(new_policy)
    db.session.commit()
    
    return jsonify({"success": True, "policy_id": new_policy.id})

@app.route('/api/worker/data', methods=['GET'])
@jwt_required()
def get_worker_data():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user: return jsonify({"error": "User not found"}), 404

    policy = Policy.query.filter_by(user_id=user.id).order_by(Policy.created_at.desc()).first()
    claims = Claim.query.filter_by(user_id=user.id).order_by(Claim.timestamp.desc()).all()
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    
    lifetime_payout = sum([c.payout_amount for c in claims if c.status == 'approved'])

    policy_data = None
    if policy and policy.quote:
        policy_data = {
            'id': policy.id,
            'status': policy.status,
            'tier_name': policy.quote.tier_name,
            'billing_cycle': policy.quote.billing_cycle,
            'premium': policy.quote.premium_amount,
            'payout': policy.quote.coverage_payout,
            'created_at': policy.created_at
        }
    
    return jsonify({
        'policy': policy_data,
        'lifetime_payout': lifetime_payout,
        'claims': [{
            'id': c.id, 'status': c.status, 'reason': c.reason,
            'payout_amount': c.payout_amount, 'txn_id': c.txn_id,
            'order_id': c.order_id, 'timestamp': c.timestamp, 'trigger_event': c.trigger_event
        } for c in claims],
        'orders': [{
            'id': o.id, 'distance_km': o.distance_km, 'time_taken_mins': o.time_taken_mins, 'created_at': o.created_at
        } for o in orders]
    })

@app.route('/api/claims/initiate', methods=['POST'])
@jwt_required()
def initiate_claim():
    user_id = get_jwt_identity()
    data = request.json
    order_id = data.get('order_id')
    simulate = data.get('simulate', False) # Check for the demo simulation flag
    
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order: return jsonify({"error": "Invalid order"}), 400
    
    policy = Policy.query.filter_by(user_id=user_id, status='active').first()
    if not policy: return jsonify({"error": "No active policy found"}), 400

    user = User.query.get(user_id)
    zone = user.base_location or 'Koramangala, BLR'
    lat, lon = ZONES.get(zone, ZONES['Koramangala, BLR'])
    curr_t, rain_mm, _, _ = fetch_live_weather(lat, lon)
    
    trigger_event = None
    
    # 1. Evaluate Parametric Triggers (Simulation overrides real weather)
    if simulate:
        trigger_event = "Simulated Disruption: Flash Flood Warning (85mm)"
    elif rain_mm > 0.1: # Real weather trigger
        trigger_event = f"Rain Detected ({rain_mm}mm)"
    elif curr_t > 38:   # Real weather trigger
        trigger_event = f"High Temperature ({curr_t}°C)"

    if not trigger_event:
        return jsonify({"success": False, "message": f"Claim rejected: Weather in {zone} is currently safe. Enable 'Simulate Disruption' to force a demo trigger."})

    existing = Claim.query.filter_by(order_id=order_id).first()
    if existing: return jsonify({"success": False, "message": "Claim already initiated for this order."})

    new_claim = Claim(
        user_id=user_id, 
        policy_id=policy.id,
        order_id=order_id,
        trigger_event=trigger_event,
        payout_amount=policy.quote.coverage_payout,
        status='pending',
        reason='Loss of Income - Parametric Trigger'
    )
    db.session.add(new_claim)
    db.session.commit()
    
    return jsonify({"success": True, "claim_id": new_claim.id})

@app.route('/api/manager/dashboard', methods=['GET'])
@jwt_required()
def manager_dashboard():
    user = User.query.get(get_jwt_identity())
    if not user or user.role != 'FLEET_MANAGER': return jsonify({"error": "Unauthorized"}), 403

    agents = User.query.filter_by(role='GIG_WORKER').all()
    claims = Claim.query.order_by(Claim.timestamp.desc()).all()
    
    active_policies = db.session.query(db.func.count(Policy.id)).filter(Policy.status=='active').scalar() or 0
    active_premium_sum = db.session.query(db.func.sum(Quote.premium_amount)).join(Policy).filter(Policy.status=='active').scalar() or 0
    total_claims_paid = db.session.query(db.func.sum(Claim.payout_amount)).filter(Claim.status == 'approved').scalar() or 0
    
    return jsonify({
        'agents': [{
            "id": u.id, "name": u.name, "phone": u.phone, 
            "base_location": u.base_location, "company": u.company, "created_at": u.created_at
        } for u in agents],
        'claims': [{
            "id": c.id, "agent_name": c.user.name if c.user else "Unknown",
            "phone": c.user.phone if c.user else "N/A",
            "payout_amount": c.payout_amount, "status": c.status,
            "reason": c.reason, "order_id": c.order_id, "timestamp": c.timestamp, "trigger_event": c.trigger_event
        } for c in claims],
        'metrics': {
            'active_policies': active_policies,
            'total_premiums_collected': round(active_premium_sum, 2),
            'total_claims_paid': round(total_claims_paid, 2),
            'pending_claims': len([c for c in claims if c.status == 'pending'])
        }
    })

@app.route('/api/manager/claims/update', methods=['POST'])
@jwt_required()
def update_claim():
    data = request.json
    claim_id = data.get('claim_id')
    status = data.get('status')
    
    claim = Claim.query.get(claim_id)
    if not claim: return jsonify({"error": "Claim not found"}), 404
    
    claim.status = status
    if status == 'approved':
        claim.txn_id = f"pi_prod_{uuid.uuid4().hex[:12]}"
    db.session.commit()
    return jsonify({"success": True, "claim_id": claim.id, "status": claim.status, "txn_id": claim.txn_id})

@app.route('/api/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    user = User.query.get(get_jwt_identity())
    
    if user.role == 'GIG_WORKER':
        claims = Claim.query.filter_by(user_id=user.id, status='approved').all()
    else:
        claims = Claim.query.filter_by(status='approved').all()
    
    daily = {}
    monthly = {}
    
    for c in claims:
        d_str = c.timestamp[:10]
        m_str = c.timestamp[:7]
        daily[d_str] = daily.get(d_str, 0) + c.payout_amount
        monthly[m_str] = monthly.get(m_str, 0) + c.payout_amount
        
    return jsonify({
        "daily": sorted([{"date": k, "amount": v} for k, v in daily.items()], key=lambda x: x['date']),
        "monthly": sorted([{"month": k, "amount": v} for k, v in monthly.items()], key=lambda x: x['month'])
    })

# --- AUTOMATION SERVICE: ZERO-TOUCH PARAMETRIC CLAIMS --- #

def trigger_weather_claims():
    """
    Parametric Engine: Automatically scans weather telemetry for all active policies
    and initiates claims if catastrophic thresholds are met (Zero-Touch).
    """
    with app.app_context():
        print(f"[{datetime.now().isoformat()}] Parametric Shield: Scanning telemetry for triggers...")
        active_policies = Policy.query.filter_by(status='active').all()
        
        for p in active_policies:
            if not p.user or not p.quote: continue
            
            zone = p.user.base_location or 'Koramangala, BLR'
            lat, lon = ZONES.get(zone, ZONES['Koramangala, BLR'])
            curr_t, rain_mm, _, _ = fetch_live_weather(lat, lon)
            
            # Catastrophic Parametric Thresholds
            trigger_event = None
            if rain_mm > 45: # Parametric Cloudburst Protocol
                trigger_event = f"Automated Shield: Extreme Rainfall Detected ({rain_mm}mm)"
            elif curr_t > 43: # Parametric Heatwave Protocol
                trigger_event = f"Automated Shield: Critical Temperature Detected ({curr_t}°C)"
                
            if trigger_event:
                # Deduplication: Ensure only one automated claim per 24h window per user
                today_str = datetime.now().isoformat()[:10]
                existing = Claim.query.filter(
                    Claim.user_id == p.user_id, 
                    Claim.timestamp.like(f"{today_str}%"),
                    Claim.reason == 'Loss of Income - Automated Detection'
                ).first()
                
                if not existing:
                    new_claim = Claim(
                        user_id=p.user_id,
                        policy_id=p.id,
                        trigger_event=trigger_event,
                        payout_amount=p.quote.coverage_payout,
                        status='pending',
                        reason='Loss of Income - Automated Detection'
                    )
                    db.session.add(new_claim)
                    print(f"!!! PARAMETRIC TRIGGER: Auto-initiated claim for {p.user.name} in {zone} !!!")
        
        db.session.commit()

@app.route('/api/parametric/trigger', methods=['POST'])
def trigger_parametric_check():
    """Manual trigger for CRON jobs on Vercel"""
    trigger_weather_claims()
    return jsonify({"success": True, "message": "Parametric check completed."})

# --- SCHEDULER: DISABLE ON VERCEL --- #

if os.environ.get('VERCEL'):
    print("DEBUG: Serverless mode detected. Background scheduler disabled. Use /api/parametric/trigger for cron tasks.")
else:
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=trigger_weather_claims, trigger="interval", seconds=60)
    scheduler.start()
    print("DEBUG: Local environment detected. Background scheduler started (60s).")

if __name__ == '__main__':
    # Use reloader=False to avoid scheduler double-firing
    app.run(debug=True, port=5000, use_reloader=False)
