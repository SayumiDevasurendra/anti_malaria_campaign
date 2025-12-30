"""
Configuration settings for the Climate Risk Forecasting API
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Model paths
MODELS_DIR = BASE_DIR / "models" / "models_10"
RAINFALL_MODEL_PATH = MODELS_DIR / "rainfall_rf_models.pkl"
TEMPERATURE_MODEL_PATH = MODELS_DIR / "temperature_sarima_models.pkl"
HUMIDITY_MODEL_PATH = MODELS_DIR / "humidity_sarima_models.pkl"

# Data paths
CLIMATE_DATA_PATH = BASE_DIR / "data" / "data_10" / "climate_data.csv"

# Forecasting parameters
LAGS = list(range(5))  # Use last 5 months for lag features (Model expects 7 features: 2 cyclical + 5 lags)

# Risk thresholds for malaria climate receptivity
RISK_THRESHOLDS = {
    "temperature_min": 17,
    "temperature_max": 34,
    "humidity_threshold": 60,
    "rainfall_threshold": 300
}

# API settings
API_TITLE = "Climate Risk Forecasting API"
API_DESCRIPTION = "API for forecasting climate variables and malaria risk assessment"
API_VERSION = "1.0.0"
