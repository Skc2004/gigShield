# GigShield: Parametric Weather Protection for the Gig Economy

**GigShield** is a next-generation parametric insurance platform designed specifically for delivery partners and gig workers. It provides instant, data-driven financial protection against extreme weather conditions (heavy rain and intense heat) that directly impact a worker's ability to earn.

## 1. Core Strategy & Requirement Details

### Persona-Based Scenarios

#### Scenario A: The Delivery Partner (Agent)
- **Persona Name**: Arjun, Food Delivery Partner in Bangalore.
- **Problem**: During heavy monsoon rains, Arjun's bike is unsafe to ride, or delivery times double due to waterlogging, leading to fewer orders and lost income.
- **GigShield Workflow**: Arjun logs into the GigShield app. The app verifies his location (Koramangala, BLR) and the live Open-Meteo weather data. If the rain exceeds the **parametric trigger** (e.g., >5mm/hr), Arjun can initiate a claim for any order he completed during those high-risk hours. The system automatically calculates his payout based on the severity of the weather and his delivery distance.

#### Scenario B: The Fleet Manager (Admin)
- **Persona Name**: Sarah, Regional Manager for a Logisitics Fleet.
- **Problem**: Sarah needs to ensure her 500+ delivery partners are fairly compensated and incentivized to work (or stay safe) during extreme weather without manual claim processing overhead.
- **GigShield Workflow**: Sarah uses the **System Console** (Admin Dashboard) to monitor fleet-wide metrics. She receives real-time notifications when new claims are initiated by her agents. She reviews the 'Detection Proof' (automated weather data audit) and clicks 'Approve' to process payouts instantly, maintaining fleet morale and operational efficiency.

---

## 2. Parametric Premium Model

### How it Works
- **Weekly Subscription**: Workers pay a small weekly premium (starting at ₹20) to stay "Covered."
- **Risk-Based Calculation**: Premiums are not flat. Our **AI/ML model (Random Forest)** calculates the premium dynamically based on:
    - **Zone Risk**: Historical weather data for the specific work location (e.g., South Ex, Delhi is higher risk for heat than Bangalore).
    - **Platform Type**: E-commerce, Food, or Grocery delivery patterns.
    - **Real-Time Traffic**: Simulated traffic congestion indexes impacting delivery duration.

### Parametric Triggers
Unlike traditional insurance that requires manual surveyors, GigShield uses **objective, verifiable data points**:
1. **Precipitation Trigger**: Rain probability > 50% or intensity > 5mm/hr.
2. **Thermal Trigger**: Ambient temperature > 38°C (Extreme Heat).
3. **Distance Weighting**: Payout amounts are scaled by the `distance_km` of the specific order to reflect the increased effort/risk of driving long distances in poor conditions.

### Platform Choice: Web vs. Mobile
We have built a **Responsive Web Application (PWA-ready)**.
- **Justification**: Gig workers often use low-storage smartphones. A web-based platform allows them to access GigShield without downloading a heavy app, ensuring quick onboarding and immediate accessibility across Android, iOS, and Desktop.

---

## 3. AI/ML Integration Plans

### Phase 1: Dynamic Premium Calculation (Implemented)
We use a **Random Forest Regressor** to predict the fair premium for a user based on their specific work zone risk and current platform traffic patterns. This ensures that a worker in a safe, cool zone doesn't overpay.

### Phase 2: Fraud & Anomaly Detection (Planned)
- **Claim Integrity**: AI models will cross-reference the `order_id` completion time with the precise GPS/Weather historical data to detect "weather-mining" (claims for orders not actually impacted).
- **Behavioral Scoring**: Tracking "Safe Driving" scores to offer premium discounts to partners who maintain high safety standards during insured hours.

---

## 4. Tech Stack & Development Plan

### Stack
- **Backend**: Python (Flask), SQLAlchemy (SQLite), Scikit-Learn (ML), NumPy/Pandas (Data processing).
- **Frontend**: React.js, Tailwind CSS (Vanilla CSS for custom components), Lucide Icons (UI).
- **Data Source**: Open-Meteo REST API (Live Parametric Weather).

### Development Roadmap
1. **MVP (Phase 1 - Current)**: Core auth, order-based claims, live weather integration, manager approval queue, and basic analytics.
2. **Beta (Phase 2)**: Integration with real delivery platform APIs (Swiggy/Zomato/Amazon) and multi-payment gateway support (UPI/Stripe).
3. **Scale (Phase 3)**: Deployment on AWS/GCP and expansion to 10+ Tier-1 cities with localized risk models.

---

## 5. Relevant Links & Project Assets

- **GitHub Repository**: [https://github.com/Skc2004/gigShield]
- **Project Walkthrough**: [Link to 2-minute video presentation]

---
*Developed for the Gig Economy by GigShield Team.*
