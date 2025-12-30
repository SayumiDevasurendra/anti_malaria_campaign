"""
Pydantic models for request and response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class HistoryRecord(BaseModel):
    """Single historical climate data record"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    District: str = Field(..., description="District name")
    rainfall: float = Field(..., description="Rainfall in mm")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage")


class ClimateRequest(BaseModel):
    """Request schema for climate forecasting"""
    district: str = Field(..., description="District name for forecasting")
    year: int = Field(..., ge=2000, le=2100, description="Target year")
    month: int = Field(..., ge=1, le=12, description="Target month (1-12)")
    history: Optional[List[HistoryRecord]] = Field(None, description="Historical climate data (optional if data is loaded on server)")

    class Config:
        json_schema_extra = {
            "example": {
                "district": "Colombo",
                "year": 2024,
                "month": 6,
                "history": [
                    {
                        "date": "2023-01-01",
                        "District": "Colombo",
                        "rainfall": 150.5,
                        "temperature": 28.3,
                        "humidity": 75.2
                    },
                    {
                        "date": "2023-02-01",
                        "District": "Colombo",
                        "rainfall": 120.3,
                        "temperature": 29.1,
                        "humidity": 72.8
                    }
                ]
            }
        }


class ClimateResponse(BaseModel):
    """Response schema for climate forecasting"""
    district: str
    year: int
    month: int
    forecasted_rainfall: float = Field(..., description="Forecasted rainfall in mm")
    forecasted_temperature: float = Field(..., description="Forecasted temperature in Celsius")
    forecasted_humidity: float = Field(..., description="Forecasted humidity percentage")
    forecasted_climatic_receptivity: float = Field(..., description="Climate risk score (0-1.5)")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    models_loaded: bool
