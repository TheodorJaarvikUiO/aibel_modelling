from windpowerlib import ModelChain, WindTurbine
import pandas as pd

# Define wind turbine specifications
turbine_data = {
    "turbine_type": "SWT62/1300",  # Example turbine type
    "hub_height": 90,  # Hub height in meters
}

# Create a WindTurbine object
wind_turbine = WindTurbine(**turbine_data)

# Load weather data from CSV file
# Ensure the CSV file has columns: 'wind_speed', 'temperature', 'pressure', and a datetime index
weather_data = pd.read_csv(
    "Datasets/1year_wind_haugesund.csv", 
    index_col=0, 
    parse_dates=True
)

# Create a ModelChain object
model_chain = ModelChain(wind_turbine)

# Run the model chain with the weather data
power_output = model_chain.run_model(weather_data).power_output

# Calculate annual energy production (AEP) in MWh
annual_energy_production = power_output.sum() / 1000  # Convert Wh to MWh

print(f"Estimated Annual Energy Production: {annual_energy_production:.2f} MWh")