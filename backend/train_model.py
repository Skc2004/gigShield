import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

def generate_synthetic_data(n_samples=5000):
    print(f"Generating {n_samples} synthetic records...")
    
    np.random.seed(42)
    # Features
    temp = np.random.uniform(25, 45, n_samples)
    rain = np.random.uniform(0, 100, n_samples)
    traffic = np.random.uniform(0, 10, n_samples)
    
    # Target value function (Base premium computation logic)
    # Premium starts at base 150. Increases with heat, heavy rain, and slow traffic.
    premium = 150 + (temp - 25)*2.5 + (rain * 1.2) + (traffic * 5.0) 
    
    # Add some stochastic noise
    noise = np.random.normal(0, 10, n_samples)
    premium = premium + noise
    
    df = pd.DataFrame({
        'temp': temp,
        'rain': rain,
        'traffic': traffic,
        'premium': premium
    })
    return df

def train_and_export():
    df = generate_synthetic_data()
    X = df[['temp', 'rain', 'traffic']]
    y = df['premium']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training RandomForestRegressor model...")
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Training Complete.")
    print(f"Metrics - MSE: {mse:.2f}, R2 Score: {r2:.4f}")
    
    print("Exporting model.pkl...")
    joblib.dump(model, 'model.pkl')
    print("Successfully exported Gigabit Shield pricing model.")

if __name__ == "__main__":
    train_and_export()
