import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
import joblib

class AIPredictor:
    def __init__(self, model_type='mlp'):
        self.model_type = model_type
        self.model = None
        self.scaler = MinMaxScaler()
        self.last_trained_features = None
        
    def prepare_data(self, data, lookback=5):
        """Prepare data for model training"""
        # Ensure we have all required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            raise ValueError(f"Data must contain columns: {', '.join(required_columns)}")
        
        if len(data) < 20 + lookback:  # Need at least 20 days for MA20
            raise ValueError(f"Not enough data points. Need at least {20 + lookback} data points.")
            
        # Create features
        df = data.copy()
        
        # Add technical indicators
        df['returns'] = df['close'].pct_change()
        df['high_low_ratio'] = df['high'] / df['low']
        df['volume_ma5'] = df['volume'].rolling(window=5, min_periods=1).mean()
        df['price_ma5'] = df['close'].rolling(window=5, min_periods=1).mean()
        df['price_ma20'] = df['close'].rolling(window=20, min_periods=1).mean()
        
        # Forward fill any remaining NaN values
        df = df.fillna(method='ffill')
        # Backward fill any remaining NaN values at the beginning
        df = df.fillna(method='bfill')
        
        # Store the feature names for later use
        self.feature_names = ['open', 'high', 'low', 'close', 'volume', 
                            'returns', 'high_low_ratio', 'volume_ma5', 
                            'price_ma5', 'price_ma20']
        
        # Prepare features
        features = df[self.feature_names].values
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        X, y = [], []
        for i in range(lookback, len(scaled_features)):
            X.append(scaled_features[i-lookback:i].flatten())
            y.append(scaled_features[i, 3])  # Predict close price
            
        # Store last lookback days of features for prediction
        self.last_trained_features = scaled_features[-lookback:]
            
        return np.array(X), np.array(y)
    
    def create_mlp_model(self):
        """Create Neural Network model using sklearn MLPRegressor"""
        return MLPRegressor(
            hidden_layer_sizes=(100, 50),
            activation='relu',
            solver='adam',
            max_iter=1000,
            random_state=42
        )
    
    def create_rf_model(self):
        """Create Random Forest model"""
        return RandomForestRegressor(
            n_estimators=100,
            max_depth=20,
            random_state=42
        )
    
    def train(self, data, lookback=5):
        """Train the selected model"""
        print("Preparing data...")
        X, y = self.prepare_data(data, lookback)
        
        print(f"Training with {len(X)} samples...")
        
        if len(X) == 0 or len(y) == 0:
            raise ValueError("Not enough data for training after preparation")
        
        if self.model_type == 'mlp':
            self.model = self.create_mlp_model()
        else:
            self.model = self.create_rf_model()
            
        self.model.fit(X, y)
        return len(X)  # Return number of training samples
    
    def predict(self, data, lookback=5):
        """Make predictions using the trained model"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
            
        # Prepare the last lookback days of data
        X, _ = self.prepare_data(data[-lookback-20:], lookback)  # Include extra data for MA calculation
        
        if len(X) == 0:
            raise ValueError("Not enough data for prediction")
            
        # Make prediction using the last sample
        prediction = self.model.predict(X[-1:])
        
        # Create dummy array for inverse transform
        dummy_array = np.zeros((1, len(self.feature_names)))
        dummy_array[0, 3] = prediction[0]  # Put prediction in close price position
        
        # Inverse transform to get the actual price
        predicted_values = self.scaler.inverse_transform(dummy_array)
        return predicted_values[0, 3]  # Return the close price
    
    def get_prediction_metrics(self, data):
        """Calculate prediction metrics and confidence"""
        prediction = self.predict(data)
        last_price = data['close'].iloc[-1]
        
        # Calculate recent volatility
        returns = data['close'].pct_change().dropna()
        volatility = returns.std()
        
        # Adjust confidence based on volatility
        confidence = max(0, min(100, (1 - volatility * 10) * 100))
        
        metrics = {
            'predicted_price': prediction,
            'current_price': last_price,
            'predicted_movement': 'Up' if prediction > last_price else 'Down',
            'predicted_change_percent': ((prediction - last_price) / last_price) * 100,
            'confidence': confidence
        }
        
        if self.model_type == 'rf':
            feature_importance = self.model.feature_importances_
            metrics['feature_importance'] = feature_importance.tolist()
        
        return metrics
    
    def save_model(self, path):
        """Save the trained model and scaler"""
        if self.model is None:
            raise ValueError("No trained model to save")
        joblib.dump(self.model, f"{path}_{self.model_type}.joblib")
        joblib.dump(self.scaler, f"{path}_scaler.joblib")
        
        # Save feature names and last trained features
        np.save(f"{path}_features.npy", {
            'feature_names': self.feature_names,
            'last_trained_features': self.last_trained_features
        })
    
    def load_model(self, path):
        """Load the trained model and scaler"""
        self.model = joblib.load(f"{path}_{self.model_type}.joblib")
        self.scaler = joblib.load(f"{path}_scaler.joblib")
        
        # Load feature names and last trained features
        saved_features = np.load(f"{path}_features.npy", allow_pickle=True).item()
        self.feature_names = saved_features['feature_names']
        self.last_trained_features = saved_features['last_trained_features']