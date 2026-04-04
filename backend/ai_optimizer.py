import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle
import os

# Simulated Historical Records for Bangalore Zones
ZONES_HISTORY = {
    'Koramangala, BLR': {'flood_freq': 0.8, 'traffic_vol': 0.9, 'risk_score': 0.75},
    'Indiranagar, BLR': {'flood_freq': 0.4, 'traffic_vol': 0.8, 'risk_score': 0.60},
    'Andheri West, MUM': {'flood_freq': 0.9, 'traffic_vol': 0.95, 'risk_score': 0.85},
    'South Ex, DEL': {'flood_freq': 0.3, 'traffic_vol': 0.7, 'risk_score': 0.50}
}

class RiskNudgeModel:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self._is_trained = False

    def generate_synthetic_data(self):
        # Features: [flood_risk, traffic_density, current_rain, current_temp]
        # Target: premium_nudge (adjustment in INR)
        data = []
        for _ in range(100):
            zone = np.random.choice(list(ZONES_HISTORY.keys()))
            hist = ZONES_HISTORY[zone]
            
            rain = np.random.uniform(0, 100)
            temp = np.random.uniform(25, 45)
            
            # Label logic: Nudge higher if high flood freq + current rain
            nudge = (hist['flood_freq'] * (rain / 10)) + (hist['traffic_vol'] * 2) - 2
            
            data.append([hist['flood_freq'], hist['traffic_vol'], rain, temp, nudge])
            
        return pd.DataFrame(data, columns=['flood_f', 'traffic_v', 'rain', 'temp', 'nudge'])

    def train(self):
        df = self.generate_synthetic_data()
        X = df.drop('nudge', axis=1)
        y = df['nudge']
        self.model.fit(X, y)
        self._is_trained = True
        print("AI Risk Optimizer: Model Trained on Hyper-Local Features.")

    def get_nudge(self, zone_name, rain_mm, temp_c):
        if not self._is_trained:
            self.train()
            
        hist = ZONES_HISTORY.get(zone_name, {'flood_freq': 0.5, 'traffic_vol': 0.5})
        X_input = np.array([[hist['flood_freq'], hist['traffic_vol'], rain_mm, temp_c]])
        nudge = self.model.predict(X_input)[0]
        return round(float(nudge), 2)

# Singleton instance
optimizer = RiskNudgeModel()
