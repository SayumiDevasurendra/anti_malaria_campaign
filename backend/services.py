"""
Climate forecasting service with business logic
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from .config import LAGS, RISK_THRESHOLDS


class ClimateForecastService:
    """Service for climate forecasting and risk assessment"""
    
    def __init__(self, rain_models, temp_models, hum_models, global_history=None):
        """
        Initialize the forecasting service with loaded models
        
        Args:
            rain_models: Dictionary of rainfall forecasting models by district
            temp_models: Dictionary of temperature forecasting models by district
            hum_models: Dictionary of humidity forecasting models by district
            global_history: Optional DataFrame containing historical data for all districts
        """
        self.rain_models = rain_models
        self.temp_models = temp_models
        self.hum_models = hum_models
        self.global_history = global_history
    
    def get_available_districts(self):
        """Get list of available districts"""
        return list(self.rain_models.keys())
    
    @staticmethod
    def create_cyclical_features(month: int) -> Tuple[float, float]:
        """
        Create cyclical encoding for month to capture seasonality
        
        Args:
            month: Month number (1-12)
            
        Returns:
            Tuple of (sin_month, cos_month)
        """
        sin_month = np.sin(2 * np.pi * month / 12)
        cos_month = np.cos(2 * np.pi * month / 12)
        return sin_month, cos_month
    
    def prepare_features(self, month: int, history: List[float]) -> List[float]:
        """
        Prepare feature vector for model prediction
        
        Args:
            month: Month number for cyclical encoding
            history: Historical values (most recent last)
            
        Returns:
            Feature vector [sin, cos, lag_1, lag_2, ..., lag_n]
        """
        sin_month, cos_month = self.create_cyclical_features(month)
        
        # Get last 12 values in reverse order (most recent first)
        lags = history[-12:][::-1][:len(LAGS)]
        
        # Pad with zeros if not enough history
        while len(lags) < len(LAGS):
            lags.append(0)
        
        return [sin_month, cos_month] + lags
    
    def model_predict(self, model, features):
        """
        Make prediction handling different model types (sklearn vs statsmodels)
        """
        try:
            # Check if it looks like a statsmodels SARIMAX result
            if hasattr(model, 'forecast') or hasattr(model, 'get_forecast'):
                # For SARIMAX, use forecast with exogenous variables
                # Reshape features if needed (1 sample, n_features)
                exog = np.array(features).reshape(1, -1)
                pred = model.forecast(steps=1, exog=exog)
                
                # Handle Series result
                if isinstance(pred, (pd.Series, pd.DataFrame)):
                    return float(pred.iloc[0])
                return float(pred[0])
            else:
                # Assume sklearn-like predict([features])
                return float(model.predict([features])[0])
        except Exception as e:
            # Fallback or re-raise with context
            raise ValueError(f"Prediction failed for model type {type(model)}: {str(e)}")

    def forecast_multi_step(
        self,
        district: str,
        target_year: int,
        target_month: int,
        history_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Perform multi-step forecasting for rainfall, temperature, and humidity
        
        Args:
            district: District name
            target_year: Target year for forecast
            target_month: Target month for forecast
            history_df: DataFrame with historical data
            
        Returns:
            Dictionary with forecasted values
        """
        # Validate district is available
        if district not in self.rain_models:
            available = ", ".join(self.get_available_districts())
            raise ValueError(
                f"District '{district}' not found in models. "
                f"Available districts: {available}"
            )
        
        # Get district-specific models
        rain_model = self.rain_models[district]
        temp_model = self.temp_models[district]
        hum_model = self.hum_models[district]
        
        if history_df is None or len(history_df) == 0:
            if self.global_history is None:
                raise ValueError("No history provided in request and no global history loaded on server")
            # Use global history
            hist = self.global_history[self.global_history["District"] == district].sort_values("date")
        else:
            # Use provided history
            hist = history_df[history_df["District"] == district].sort_values("date")
        
        if len(hist) == 0:
            # Check if district exists in global history but has no data?
            # Or if we used global history, it means no data for this district
            source = "global history" if (history_df is None or len(history_df) == 0) else "request history"
            raise ValueError(f"No historical data found for district: {district} in {source}")
        
        # Get the last date in history
        last_date = hist["date"].max()
        target_date = pd.to_datetime(f"{target_year}-{target_month:02d}-01")
        
        # Calculate number of steps to forecast
        steps = (target_date.year - last_date.year) * 12 + (target_date.month - last_date.month)
        
        if steps <= 0:
            raise ValueError(f"Target date must be in the future. Last date: {last_date}, Target: {target_date}")
        
        # Initialize history lists
        rainfall_hist = list(hist["rainfall"].values)
        temp_hist = list(hist["temperature"].values)
        hum_hist = list(hist["humidity"].values)
        
        # Iteratively forecast each step
        for step in range(steps):
            future_month = ((last_date.month + step) % 12) + 1
            if future_month == 0:
                future_month = 12
            
            # Prepare features for each variable
            rain_X = self.prepare_features(future_month, rainfall_hist)
            temp_X = self.prepare_features(future_month, temp_hist)
            hum_X = self.prepare_features(future_month, hum_hist)
            
            # Make predictions using helper to handle different model types
            rainfall_pred = self.model_predict(rain_model, rain_X)
            temp_pred = self.model_predict(temp_model, temp_X)
            hum_pred = self.model_predict(hum_model, hum_X)
            
            # Append predictions to history
            rainfall_hist.append(rainfall_pred)
            temp_hist.append(temp_pred)
            hum_hist.append(hum_pred)
        
        # Return the final forecasted values
        return {
            "rainfall": rainfall_hist[-1],
            "temperature": temp_hist[-1],
            "humidity": hum_hist[-1]
        }
    
    @staticmethod
    def calculate_climate_risk(rainfall: float, temperature: float, humidity: float) -> float:
        """
        Calculate climate receptivity risk for malaria based on forecasted values
        
        Args:
            rainfall: Forecasted rainfall (mm)
            temperature: Forecasted temperature (Celsius)
            humidity: Forecasted humidity (%)
            
        Returns:
            Risk score (0 to 1.5)
        """
        risk = 0.0
        
        # Temperature in optimal range for mosquito breeding
        if RISK_THRESHOLDS["temperature_min"] <= temperature <= RISK_THRESHOLDS["temperature_max"]:
            risk += 0.5
        
        # High humidity favorable for mosquitoes
        if humidity > RISK_THRESHOLDS["humidity_threshold"]:
            risk += 0.5
        
        # Low rainfall (stagnant water pools)
        if rainfall <= RISK_THRESHOLDS["rainfall_threshold"]:
            risk += 0.5
        
        return risk
    
    def forecast_climate_and_risk(
        self,
        district: str,
        year: int,
        month: int,
        history_df: pd.DataFrame
    ) -> Dict:
        """
        Main method to forecast climate variables and calculate risk
        
        Args:
            district: District name
            year: Target year
            month: Target month
            history_df: Historical climate data
            
        Returns:
            Dictionary with all forecasted values and risk score
        """
        # Perform multi-step forecasting
        forecast = self.forecast_multi_step(district, year, month, history_df)
        
        # Calculate climate risk
        risk = self.calculate_climate_risk(
            forecast["rainfall"],
            forecast["temperature"],
            forecast["humidity"]
        )
        
        return {
            "district": district,
            "year": year,
            "month": month,
            "forecasted_rainfall": round(forecast["rainfall"], 2),
            "forecasted_temperature": round(forecast["temperature"], 2),
            "forecasted_humidity": round(forecast["humidity"], 2),
            "forecasted_climatic_receptivity": risk
        }
