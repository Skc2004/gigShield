# GigShield: Parametric Weather Protection for the Gig Economy

## 🛠️ Built With

GigShield leverages a modern, data-centric stack to ensure reliability and speed:

*   **Frontend**: [React.js](https://reactjs.org/) & [Tailwind CSS](https://tailwindcss.com/)
*   **Backend**: [Python (Flask)](https://flask.palletsprojects.com/)
*   **Database**: [SQLAlchemy (SQLite)](https://www.sqlalchemy.org/)
*   **AI/ML Engine**: [Scikit-Learn](https://scikit-learn.org/) (Random Forest Regressor)
*   **Weather Telemetry**: [Open-Meteo API](https://open-meteo.com/)
*   **Scheduling**: [APScheduler](https://apscheduler.readthedocs.io/) (for background parametric monitoring)
*   **Security**: [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/) (for role-based access control)

---

## 🛡️ About the Project

### The Inspiration
The gig economy is the backbone of modern urban life, yet its workers—delivery partners, bike-taxi riders, and couriers—are among the most vulnerable to climate volatility. In cities like Bangalore or Mumbai, a single hour of heavy rain or a $40^\circ\text{C}$ heatwave doesn't just mean a difficult commute; it means a total loss of daily earnings. Traditional insurance is built for large, infrequent catastrophes and requires manual claims, adjusters, and weeks of waiting. 

I was inspired to build **GigShield** to bridge this gap by treating a rainy Tuesday like the financial micro-disaster it is for a gig worker. By using **Parametric Insurance**, we remove the need for proof of loss; the weather itself is the proof.

### What I Learned
Building GigShield was a masterclass in **Parametric Design** and **Index-Based logic**. I learned how to move away from "indemnity-based" insurance (where you prove a loss) to "objective-based" insurance (where payment is triggered by verifiable data). This required deep integration with real-time meteorological telemetry and understanding how to map "Hyper-Local Risk." I also delved into the ethics of AI pricing—ensuring that our model balances high-risk coverage without becoming prohibitively expensive.

### How I Built It
The platform is an end-to-end full-stack solution:
- **The Parametric Engine**: I integrated the **Open-Meteo API** to fetch live precipitation and temperature data across specific urban zones.
- **AI Core**: Using **Scikit-Learn**, I implemented a `RiskNudgeModel` (Random Forest) that calculates a "Risk Nudge" based on historical flood frequency and real-time conditions.
- **Backend Architecture**: Built with **Flask** and **SQLAlchemy**, featuring a manual "Simulation Mode" to demonstrate parametric triggers on-demand.
- **Frontend Experience**: Developed a **React** PWA (Progressive Web App) with a premium "Glassmorphic" UI, optimized for workers using low-storage mobile devices.

### Challenges Faced
One of the primary challenges was **Telemetry Synchronization**. Syncing the exact millisecond an order was completed with the historical weather data at that specific GPS coordinate required high-precision data handling. Additionally, creating a fair pricing model involved complex math to ensure premiums remained affordable:

#### The Mathematics of Risk
The total weekly premium $P$ for a partner is dynamically calculated as:
$$P = (B + P_{\text{weather}} + P_{\text{traffic}} + P_{\text{exposure}} + P_{\text{nudge}}) \times M_{\text{company}}$$

Where:
- $B$ is the platform base rate.
- $P_{\text{weather}} = \text{PrecipitationProbability} \times 0.3$.
- $P_{\text{nudge}}$ is the AI-calculated hyper-local risk adjustment:
  $$P_{\text{nudge}} = \max(0, (R \cdot 0.5) + ((T - 35) \cdot 0.2))$$
  *(Where $R$ is rainfall in mm and $T$ is temperature in $^\circ\text{C}$)*.

The "Zero-Touch" automated claim is triggered if weather telemetry exceeds the **Catastrophic Threshold**:
$$\text{Rainfall} > 45\text{mm} \quad \text{or} \quad \text{Temperature} > 43^\circ\text{C}$$
