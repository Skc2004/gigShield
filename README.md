# GigShield: AI-Powered Parametric Insurance for Delivery Partners

## 1. Requirement, Persona, & Workflow
GigShield is an AI-enabled parametric insurance platform designed to safeguard platform-based delivery partners against income loss caused by external disruptions. The platform strictly excludes coverage for health, life, accidents, or vehicle repairs, focusing solely on protecting daily wages.

*   **Target Persona:** Food Delivery Partners (e.g., Zomato, Swiggy) operating in urban environments.
*   **Persona Scenario:** A delivery partner relies on daily active hours to meet their financial goals. During severe waterlogging or an extreme heatwave, working becomes impossible or highly restricted, leading to a direct loss of income.
*   **Application Workflow:**
    1.  **Onboarding:** Quick registration capturing the user's primary delivery zones and platform.
    2.  **Policy Issuance:** The user purchases a weekly policy based on a dynamically calculated premium.
    3.  **Active Monitoring:** The system continuously monitors external API triggers (weather, traffic, social alerts).
    4.  **Zero-Touch Claims:** When a disruption threshold is met in the user's active zone, a claim is automatically initiated.
    5.  **Instant Payout:** Validated claims instantly disburse the calculated lost income via mock payment gateways.

## 2. Core Mechanics: Premiums, Triggers, & Platform
*   **Weekly Premium Model:** Gig workers operate on week-to-week cash flows. Our financial model reflects this with a Weekly pricing structure. The premium adjusts dynamically each week based on hyper-local risk factors and forecasted disruptions.
*   **Parametric Triggers:**
    *   **Environmental:** Extreme heat (> 42°C) or heavy rain/waterlogging that halts deliveries.
    *   **Social:** Unplanned curfews or sudden zone closures.
*   **Platform Choice (Mobile-First Web App):** A responsive web application (accessible via mobile) is chosen over a native app. Delivery partners have limited phone storage and are constantly on their mobile devices. A mobile-optimized web app (or PWA) ensures high accessibility without the friction of app store downloads, making the onboarding process seamless.

## 3. AI/ML Integration Strategy
*   **Dynamic Premium Calculation (Random Forest):** We will implement predictive risk modeling specific to the delivery persona. Machine Learning will adjust the weekly premium based on hyper-local risk factors, such as historical weather data and upcoming forecasts for the worker's specific zone.
*   **Intelligent Fraud Detection (K-Means & Anomaly Detection):** To prevent duplicate claims and validate location activity, we will use ML models to detect anomalies in claim patterns. The system will cross-reference claimed disruption zones with the user's historical active locations to prevent "zone-spoofing."

## 4. Tech Stack
*   **Frontend:** React.js with Tailwind CSS (for a fast, mobile-responsive UI).
*   **Backend & APIs:** Python (Flask) to handle core logic, AI/ML model serving, and API integrations.
*   **Database & Auth:** Supabase (for seamless user management and real-time database updates).
*   **AI/ML:** Python data science libraries (Scikit-learn, Pandas) for building the Random Forest pricing model and K-Means anomaly detection.
*   **External Integrations:** OpenWeatherMap API (for parametric triggers) and Razorpay/Stripe Sandbox (for simulated instant payouts).

## 5. Development Plan
*   **Weeks 1-2 (Phase 1):** Ideation, defining the data schema, setting up the GitHub repository, and building the basic frontend UI shell.
*   **Weeks 3-4 (Phase 2):** Integrating the Python backend with weather APIs, implementing the dynamic weekly premium ML model, and demonstrating automated triggers.
*   **Weeks 5-6 (Phase 3):** Finalizing the advanced fraud detection models, integrating the simulated payment sandbox, and completing the analytics dashboard.

## 6. Repository Link
Link to Repository: https://github.com/Sudeep2412/GigShield-DEVTrails
