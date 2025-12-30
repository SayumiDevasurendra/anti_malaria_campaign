import pandas as pd
import numpy as np
from pathlib import Path

# List of all districts in the models
DISTRICTS = [
    'Anuradhapura', 'Badulla', 'Bandarawela', 'Batticaloa', 'Colombo', 
    'Galle', 'Hambantota', 'Jaffna', 'Katugastota', 'Katunayake', 
    'Kurunegala', 'Mahaillukpallama', 'Mannar', 'Mattala', 'Monaragala', 
    'Nuwara Eliya', 'Polonnaruwa', 'Potuvil', 'Puttalam', 'Ratmalana', 
    'Ratnapura', 'Trincomalee', 'Vavuniya'
]

# Sample data (Colombo based)
checkpoints = [
    {"date": "2023-01-01", "rainfall": 150.5, "temperature": 28.3, "humidity": 75.2},
    {"date": "2023-02-01", "rainfall": 120.3, "temperature": 29.1, "humidity": 72.8},
    {"date": "2023-03-01", "rainfall": 180.7, "temperature": 27.9, "humidity": 78.5},
    {"date": "2023-04-01", "rainfall": 200.2, "temperature": 28.5, "humidity": 76.3},
    {"date": "2023-05-01", "rainfall": 250.8, "temperature": 27.2, "humidity": 80.1},
    {"date": "2023-06-01", "rainfall": 190.4, "temperature": 26.8, "humidity": 79.6},
    {"date": "2023-07-01", "rainfall": 160.9, "temperature": 27.5, "humidity": 77.2},
    {"date": "2023-08-01", "rainfall": 140.6, "temperature": 28.1, "humidity": 75.8},
    {"date": "2023-09-01", "rainfall": 170.3, "temperature": 27.8, "humidity": 76.9},
    {"date": "2023-10-01", "rainfall": 220.5, "temperature": 27.3, "humidity": 78.4},
    {"date": "2023-11-01", "rainfall": 280.7, "temperature": 26.9, "humidity": 81.2},
    {"date": "2023-12-01", "rainfall": 195.8, "temperature": 27.6, "humidity": 77.5}
]

def generate_synthetic_data():
    all_data = []
    
    print(f"Generating synthetic data for {len(DISTRICTS)} districts...")
    
    for district in DISTRICTS:
        # Add a district-specific seed/offset to make data slightly different
        # Use hash of district name to get consistent random seed
        seed = sum(ord(c) for c in district)
        np.random.seed(seed)
        
        for record in checkpoints:
            # Add small random variation (-10% to +10%)
            variation = 1 + (np.random.rand() * 0.2 - 0.1)
            
            # Specific variations for hill country (cooler) or dry zone (hotter/drier)
            temp_mod = 0
            if district in ['Nuwara Eliya', 'Bandarawela', 'Badulla']:
                temp_mod = -5  # Cooler
            elif district in ['Mannar', 'Vavuniya', 'Jaffna', 'Trincomalee']:
                temp_mod = 2   # Hotter
            
            row = {
                "date": record["date"],
                "District": district,
                "rainfall": round(record["rainfall"] * variation, 1),
                "temperature": round(record["temperature"] * variation + temp_mod, 1),
                "humidity": round(record["humidity"] * variation, 1)
            }
            all_data.append(row)
            
    df = pd.DataFrame(all_data)
    
    # Save to CSV
    output_path = Path("data/data_10/climate_data.csv")
    df.to_csv(output_path, index=False)
    print(f"✓ Successfully defined {len(df)} records saved to {output_path}")

if __name__ == "__main__":
    generate_synthetic_data()
