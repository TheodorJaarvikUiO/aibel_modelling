import pandas as pd
from windpowerlib import WindTurbine, ModelChain, create_power_curve
from windpowerlib import get_turbine_types
from windpowerlib import WindTurbine
from datetime import datetime

# Load raw data without headers
df = pd.read_csv("Datasets/weather_data.csv",sep=",",index_col=0,header=[0, 1])

# Parse time and convert wind speed to float
df.index = pd.to_datetime(df.index, format="%d.%m.%Y %H:%M", errors="coerce")
df.dropna(subset=[('wind_speed', '92')],inplace=True)
df["wind_speed"] = df["wind_speed"].astype(float)


df["pressure"] = 1013.25  # in hPa

# Choose a turbine type (e.g., 'ENERCON E 53 800')
turbine = WindTurbine(turbine_type='E-115/3200',hub_height=92)

# 4. Use ModelChain to compute power output
mc = ModelChain(turbine).run_model(df)

# 5. Output
df['power_output_kW'] = mc.power_output.values/1000  # Convert to kW
df.to_csv("Datasets/wind_turbine_output_wind_park.csv", index=True)
