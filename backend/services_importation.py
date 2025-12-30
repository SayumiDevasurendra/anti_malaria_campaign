import pandas as pd
import numpy as np

class ImportationRiskService:
    """Service for forecasting national importation risk"""
    
    def __init__(self, model, population_df):
        """
        Initialize the service
        
        Args:
            model: Trained SARIMA model for national importation
            population_df: DataFrame containing district population shares
        """
        self.model = model
        self.population_df = population_df
        
    def forecast_national_importation(self, year):
        """
        Forecast national importation cases for a specific year
        """
        try:
            # Try predicting using the user-provided syntax
            # This assumes the model uses integer-based years or interprets the int correctly
            pred = self.model.predict(start=year, end=year)
            
            # Handle different return types
            if isinstance(pred, (pd.Series, pd.DataFrame)):
                 return float(pred.iloc[0])
            return float(pred[0])
            
        except Exception as e:
            # Fallback for different statsmodels versions or index types
            try:
                # If start/end fails, maybe try get_prediction or forecast
                # But since this is a specific user snippet, we log and re-raise or try simple string casting
                pred = self.model.predict(start=str(year), end=str(year))
                if isinstance(pred, (pd.Series, pd.DataFrame)):
                     return float(pred.iloc[0])
                return float(pred[0])
            except Exception as e2:
                 raise ValueError(f"Failed to forecast for year {year}. Error: {e}")

    def allocate_importation_pressure(self, district, annual_cases):
        """
        Allocate national cases to district based on population share
        """
        # Case-insensitive matching setup if needed, but assuming exact match from CSV
        subset = self.population_df[self.population_df["District"] == district]
        
        if len(subset) == 0:
            available = ", ".join(self.population_df["District"].tolist())
            raise ValueError(f"District '{district}' not found in population data. Available: {available}")
            
        share = subset["Population_share"].values[0]
        
        # Calculate monthly pressure: (Annual * Share) / 12
        return (annual_cases * share) / 12

    def forecast_risk(self, district, year):
        """
        Orchestrate the forecast and allocation
        """
        # 1. Forecast National Annual Cases
        annual_cases = self.forecast_national_importation(year)
        
        # 2. Allocate to District (Monthly Force of Infection)
        monthly_pressure = self.allocate_importation_pressure(district, annual_cases)
        
        return {
            "forecasted_national_imported_cases": annual_cases,
            "district_monthly_importation_pressure": monthly_pressure
        }
