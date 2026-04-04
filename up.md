# Insurance Platform Architecture & Setup

## 1. Database & Architecture Setup (The Foundation)

To prevent hardcoding and ensure easy deployment, you need a managed database. Given your timeline, **Supabase (PostgreSQL)** or **MongoDB Atlas** are ideal for rapid setup.

### Core Schema Requirements

#### Users Table

* `id`
* `name`
* `email`
* `password_hash`
* `role` (Enum: `GIG_WORKER`, `FLEET_MANAGER`)
* `company` (e.g., Zomato, Swiggy)
* `base_location`
* `daily_earnings`
* `working_hours`

#### Quotes / Premiums Table

* `id`
* `user_id` (Foreign Key)
* `tier_name` (e.g., Basic, Comprehensive)
* `weekly_premium_amount`
* `coverage_payout`
* `active_status`

#### Policies Table

* Generated only when a user accepts a quote
* Must strictly track weekly cycles

#### Claims Table

* `policy_id`
* `trigger_event` (e.g., Flood, Heatwave)
* `payout_amount`
* `status`

---

## 2. Refactoring Authentication & Roles

### Role-Based Access Control (RBAC)

#### Remove Manager Registration

* Remove "Sign up as Manager" toggle from frontend
* `/api/auth/register` automatically assigns `GIG_WORKER`

#### Manager Onboarding

* Fleet Managers are inserted manually via:

  * SQL scripts
  * Database GUI
* Role must be explicitly set to `FLEET_MANAGER`

#### Login Flow

* Backend returns JWT with:

  * `userId`
  * `role`
* Frontend routing:

  * `GIG_WORKER` → Worker Dashboard
  * `FLEET_MANAGER` → Admin Analytics Panel

---

## 3. Dynamic Quoting Engine (No Hardcoding)

If a worker has no active policy, the frontend calls a quoting API.

### API Endpoint

```
POST /api/quotes/generate
```

### Inputs (from user profile)

* `location`
* `company`
* `daily_earnings`
* `working_hours`

### Risk Logic (Mock AI/ML)

* Assign risk weights based on:

  * Location (e.g., flood-prone areas)
  * Weather patterns
  * Work intensity

### Output (Weekly Only)

* **Option A (Standard):**

  * Covers 50% of daily earnings
  * Weekly premium: ₹X

* **Option B (Premium):**

  * Covers 80% of daily earnings
  * Weekly premium: ₹Y

**Constraint:** All pricing and payouts must be strictly weekly.

---

## 4. Enforcing Data Isolation

### Rule: Never Trust the Frontend

* Extract `userId` from JWT/session
* Do NOT accept userId from request params

### Example Query Constraint

```sql
SELECT * FROM policies
WHERE user_id = {authenticated_user_id};
```

This ensures users can only access their own data.

---

## 5. API-Driven Automated Triggers (Phase 2 Core)

### Cron Job / Webhook

* Runs every few hours
* Fetches data from weather APIs (e.g., OpenWeatherMap)

### Trigger Conditions

* Heavy Rainfall > 50mm
* Extreme Heat > 42°C

### Automation Flow

1. Fetch active policies by location
2. Check weather conditions
3. If threshold exceeded:

   * Create entry in `Claims` table

### Claim Requirements

* Must be tagged as:

  * `"Loss of Income"`
* Must NOT include:

  * Vehicle damage
  * Health claims

---

## 6. Deployment Strategy

### Frontend

* Tech: React / Next.js
* Deployment: Vercel / Netlify
* Benefits:

  * Fast deployment
  * Auto HTTPS
  * CDN support

### Backend

* Tech: Node.js (Express) or Python (FastAPI)
* Deployment: Render / Railway
* Features:

  * GitHub auto-deploy
  * Environment variable support

### Database

* Use managed services:

  * Supabase
  * MongoDB Atlas

### Setup Steps

1. Get connection string from database provider
2. Add to backend environment variables
3. Deploy backend
4. Deploy frontend
5. Connect frontend to backend API

---

## Summary

This architecture ensures:

* No hardcoding
* Secure role-based access
* Fully dynamic pricing system
* Automated parametric insurance claims
* Scalable and deployable stack within hours


---

## 7. Mathematical Risk Model & Backend Refactor

### Mathematical Risk Model (Dynamic Pricing)

Instead of hardcoding prices, premiums are calculated dynamically:

\[
P_{base} = \beta_{0} + (\alpha \times R_{prob}) + (\gamma \times T_{idx}) + \delta(H_{work} - 8)
\]

Where:
- \(\beta_{0}\): Base weekly rate (e.g., ₹15)
- \(R_{prob}\): Rain probability (real-time API)
- \(T_{idx}\): Traffic congestion index
- \(H_{work}\): Daily working hours

Additional multipliers apply based on coverage tiers.

---

### Backend Changes (Flask - app.py)

#### Remove Dummy ML Models
Delete the mock model block entirely.

#### Replace Quote Generation API

```python
@app.route('/api/quotes/generate', methods=['POST'])
@jwt_required()
def get_quote():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        zone = user.base_location or 'Koramangala, BLR'
        lat, lon = ZONES.get(zone, ZONES['Koramangala, BLR'])
        
        current_temp, rain_mm, rain_prob, is_high_risk = fetch_live_weather(lat, lon)
        traffic_index = float(np.random.uniform(4, 9))
        
        earnings = float(user.daily_earnings or 1000.0)
        hours = int(user.working_hours or 8)
        company = user.company or 'Food'
        
        base_rate = 15.0
        weather_penalty = float(rain_prob) * 0.3
        traffic_penalty = traffic_index * 1.5
        exposure_penalty = max(0, hours - 8) * 2.0
        
        company_multiplier = 1.3 if company == 'Grocery' else 1.1 if company == 'Food' else 1.0

        calculated_base_premium = (
            base_rate + weather_penalty + traffic_penalty + exposure_penalty
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
                'high_risk': is_high_risk
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

Frontend Changes (React - App.jsx)

const WorkerDashboard = ({ userMeta, activePolicy, lifetimePayout, quote, fetchQuote, liveWeather, onAcceptQuote }) => {
  useEffect(() => {
    if (!activePolicy && !quote) fetchQuote()
  }, [activePolicy, quote])

  if (!activePolicy) {
    if (!quote || !quote.options) return (
      <div className="flex flex-col items-center justify-center py-32 text-slate-400">
         <p className="font-bold">Analyzing real-time AI risk factors...</p>
      </div>
    )

    const tiers = Object.values(quote.options)

    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {tiers.map((opts) => (
          <div key={opts.tier}>
            <h3>{opts.tier}</h3>
            <p>₹{opts.premium}/wk</p>
            <p>Payout: ₹{opts.payout}</p>
            <button onClick={() => onAcceptQuote(opts.id)}>
              Activate
            </button>
          </div>
        ))}
      </div>
    )
  }
}