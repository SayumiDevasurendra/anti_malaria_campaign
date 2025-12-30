"""
FastAPI application for Climate Risk Forecasting
"""
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import (
    RAINFALL_MODEL_PATH,
    TEMPERATURE_MODEL_PATH,
    HUMIDITY_MODEL_PATH,
    CLIMATE_DATA_PATH,
    IMPORTATION_MODEL_PATH,
    POPULATION_DATA_PATH,
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION
)
from .schemas import (
    ClimateRequest,
    ClimateResponse,
    HistoryRecord,
    HealthResponse,
    ImportationRequest,
    ImportationResponse
)
from .services import ClimateForecastService
from .services_importation import ImportationRiskService


# Global variables for models, data, and service
models = {}
climate_data = None
population_data = None
forecast_service = None
importation_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager to load models on startup and cleanup on shutdown
    """
    global models, climate_data, population_data, forecast_service, importation_service
    
    try:
        # Load models on startup
        print("Loading models...")
        models["rainfall"] = joblib.load(RAINFALL_MODEL_PATH)
        models["temperature"] = joblib.load(TEMPERATURE_MODEL_PATH)
        models["humidity"] = joblib.load(HUMIDITY_MODEL_PATH)
        models["importation"] = joblib.load(IMPORTATION_MODEL_PATH)
        
        # Load climate data
        print(f"Loading climate data from {CLIMATE_DATA_PATH}...")
        if CLIMATE_DATA_PATH.exists():
            climate_data = pd.read_csv(CLIMATE_DATA_PATH)
            climate_data["date"] = pd.to_datetime(climate_data["date"])
            print(f"✓ Loaded {len(climate_data)} historical records")
        else:
            print(f"⚠ Warning: Climate data file not found at {CLIMATE_DATA_PATH}")
            climate_data = None
            
        # Load population data
        print(f"Loading population data from {POPULATION_DATA_PATH}...")
        if POPULATION_DATA_PATH.exists():
            population_data = pd.read_csv(POPULATION_DATA_PATH)
            print(f"✓ Loaded population data for {len(population_data)} districts")
        else:
            print(f"⚠ Warning: Population data file not found at {POPULATION_DATA_PATH}")
            population_data = None
        
        # Initialize forecast service with model dictionaries and global history
        forecast_service = ClimateForecastService(
            rain_models=models["rainfall"],
            temp_models=models["temperature"],
            hum_models=models["humidity"],
            global_history=climate_data
        )
        
        # Initialize importation service
        importation_service = ImportationRiskService(
            model=models["importation"],
            population_df=population_data
        )
        
        print("✓ Models loaded successfully!")
        yield
        
    except Exception as e:
        print(f"✗ Error loading models: {e}")
        raise
    finally:
        # Cleanup on shutdown
        models.clear()
        climate_data = None
        population_data = None
        forecast_service = None
        importation_service = None
        print("Models and data unloaded")


# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Climate Risk Forecasting API",
        "version": API_VERSION,
        "endpoints": {
            "health": "/health",
            "forecast": "/forecast/climate-risk"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API and model status
    """
    models_loaded = all(key in models for key in ["rainfall", "temperature", "humidity", "importation"])
    
    return {
        "status": "healthy" if models_loaded else "unhealthy",
        "message": "Models loaded successfully" if models_loaded else "Models not loaded",
        "models_loaded": models_loaded,
        "data_loaded": climate_data is not None and population_data is not None
    }


@app.get("/districts", tags=["Information"])
async def get_available_districts():
    """
    Get list of available districts for forecasting
    """
    if forecast_service is None:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please check server status."
        )
    
    return {
        "districts": forecast_service.get_available_districts(),
        "count": len(forecast_service.get_available_districts())
    }


@app.post("/forecast/climate-risk", response_model=ClimateResponse, tags=["Forecasting"])
async def forecast_climate_and_risk(request: ClimateRequest):
    """
    Forecast climate variables and calculate malaria climate receptivity risk
    
    Args:
        request: ClimateRequest with district, year, month, and historical data
        
    Returns:
        ClimateResponse with forecasted values and risk score
        
    Raises:
        HTTPException: If models are not loaded or forecasting fails
    """
    if forecast_service is None:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please check server status."
        )
    
    try:
        # Convert history to DataFrame if provided
        history_df = None
        if request.history:
            history_df = pd.DataFrame([record.dict() for record in request.history])
            history_df["date"] = pd.to_datetime(history_df["date"])
        
        # Perform forecasting
        result = forecast_service.forecast_climate_and_risk(
            district=request.district,
            year=request.year,
            month=request.month,
            history_df=history_df
        )
        
        return ClimateResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Forecasting error: {str(e)}"
        )


@app.post("/forecast/importation", response_model=ImportationResponse, tags=["Forecasting"])
async def forecast_importation_pressure(request: ImportationRequest):
    """
    Forecast district-wise national importation risk
    """
    if importation_service is None:
        raise HTTPException(
            status_code=503,
            detail="Service not initialized. Please check server status."
        )
        
    try:
        result = importation_service.forecast_risk(
            district=request.district,
            year=request.year
        )
        
        return ImportationResponse(
            district=request.district,
            year=request.year,
            **result
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Importation forecast error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
