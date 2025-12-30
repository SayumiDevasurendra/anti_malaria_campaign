# anti_malaria_campaign
Git repo for AMC research project

# Climate Risk Forecasting API - Backend

FastAPI backend for forecasting climate variables (rainfall, temperature, humidity) and calculating malaria climate receptivity risk.

## 📋 Features

- **Climate Forecasting**: Multi-step time series forecasting for rainfall, temperature, and humidity
- **Risk Assessment**: Calculate malaria climate receptivity based on forecasted climate conditions
- **Importation Risk**: Forecast district-wise national importation risk using SARIMA and population data
- **Automated Data Loading**: Automatically loads historical climate and population data on startup
- **RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation
- **Model Management**: Automatic model loading on startup with health checks

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Trained models in `models/models_10/` directory

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure models and data are in the correct location:
```
models/
  └── models_10/
      ├── rainfall_rf_models.pkl
      ├── temperature_sarima_models.pkl
      ├── humidity_sarima_models.pkl
      └── national_importation_sarima_model.pkl

data/
  └── data_10/
      ├── climate_data.csv
      └── population.csv
```

### Running the Server

#### Development Mode
```bash
# From the project root directory
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Root Endpoint
```http
GET /
```
Returns API information and available endpoints.

### Health Check
```http
GET /health
```
Check API and model loading status.

**Response:**
```json
{
  "status": "healthy",
  "message": "All models loaded successfully",
  "models_loaded": true
}
```

### Available Districts
```http
GET /districts
```
Returns a list of all 23 districts available for forecasting.

### Climate Risk Forecast
```http
POST /forecast/climate-risk
```

Forecast climate variables and calculate malaria risk. **Historical data is loaded automatically from the server.**

**Request Body (Simplified):**
```json
{
  "district": "Colombo",
  "year": 2028,
  "month": 1
}
```

**Response:**
```json
{
  "district": "Colombo",
  "year": 2028,
  "month": 1,
  "forecasted_rainfall": 145.23,
  "forecasted_temperature": 28.76,
  "forecasted_humidity": 74.15,
  "forecasted_climatic_receptivity": 1.5
}
```

### National Importation Risk
```http
POST /forecast/importation
```
Forecast district-wise monthly national importation risk.

**Request Body:**
```json
{
  "district": "Colombo",
  "year": 2028
}
```

**Response:**
```json
{
  "district": "Colombo",
  "year": 2028,
  "forecasted_national_imported_cases": 125.5,
  "district_monthly_importation_pressure": 1.25
}
```

## 📊 Risk Calculation

The climate receptivity risk score ranges from 0 to 1.5 based on:

| Condition | Risk Score | Threshold |
|-----------|------------|-----------|
| Temperature in optimal range (17-34°C) | +0.5 | Favorable for mosquito breeding |
| High humidity (>60%) | +0.5 | Favorable for mosquito survival |
| Low rainfall (≤300mm) | +0.5 | Stagnant water pools |

## 🏗️ Project Structure

```
backend/
├── __init__.py          # Package initialization
├── app.py              # FastAPI application and endpoints
├── config.py           # Configuration settings
├── schemas.py          # Pydantic models for validation
├── services.py         # Climate forecasting logic
└── services_importation.py # Importation risk logic
```

## 🧪 Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Forecast request
# Forecast request
curl -X POST http://localhost:8000/forecast/climate-risk \
  -H "Content-Type: application/json" \
  -d '{
    "district": "Colombo",
    "year": 2024,
    "month": 6
  }'
```

### Using Python

```python
import requests

url = "http://localhost:8000/forecast/climate-risk"
url = "http://localhost:8000/forecast/climate-risk"
data = {
    "district": "Colombo",
    "year": 2024,
    "month": 6
}

response = requests.post(url, json=data)
print(response.json())
```

## ⚙️ Configuration

Edit `backend/config.py` to customize:

- Model file paths
- Risk thresholds
- Lag periods
- API metadata

## 🔧 Troubleshooting

### Models not loading
- Verify model files exist in `models/models_10/`
- Check file permissions
- Ensure models are compatible with installed scikit-learn version

### CORS errors
- Update `allow_origins` in `app.py` for production
- Currently set to `["*"]` for development

### Import errors
- Run from project root directory
- Ensure `backend` is a proper Python package with `__init__.py`

## 📝 License

This project is part of the Anti-Malaria Campaign research initiative.
