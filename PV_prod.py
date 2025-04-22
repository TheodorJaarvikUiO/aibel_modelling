import math
import pandas as pd
import plotly.graph_objects as go

import pvlib
from pvlib.modelchain import ModelChain
from pvlib.pvsystem import PVSystem
from pvlib.location import Location

weather_df = pd.read_csv('Datasets/479237_59.41_5.26_2019.csv')

#drop the first row and change the header
weather_df = weather_df.drop(0)
weather_df.columns = weather_df.iloc[0]
weather_df = weather_df.drop(1)

# create new datetime column using the columns year, month, day, hour, minute
weather_df['datetime'] = pd.to_datetime(weather_df[['Year', 'Month', 'Day', 'Hour', 'Minute']])
weather_df.set_index('datetime', inplace=True)
weather_df.index = pd.to_datetime(weather_df.index)

# resample to hourly
weather_df = weather_df.astype(float)
weather_df = weather_df.resample('h').mean()

# rename columns to use the pvlib nomenclature
weather_df = weather_df.rename(
            {
                "Temperature": "temp_air",
                "Wind Speed": "wind_speed",
                "Relative Humidity": "humidity",
                "Precipitable Water": "precipitable_water",
                "GHI": "ghi",
                "DNI": "dni",
                "DHI": "dhi",
            },
            axis=1,
        )


# select only relevant columns
weather_df = weather_df[['temp_air', 'wind_speed', 'humidity', 'precipitable_water', 'ghi', 'dni', 'dhi', ]]

# resample to hourly
weather_df = weather_df.resample('h').mean()

# retrieve the inverter and panel specifications from the pvlib library

cec_modules = pvlib.pvsystem.retrieve_sam("cecmod")
sapm_inverters = pvlib.pvsystem.retrieve_sam("cecinverter")
module = cec_modules["Znshine_PV_Tech_ZXP6_72_295_P"]
inverter = sapm_inverters["ABB__MICRO_0_3_I_OUTD_US_208__208V_"]
temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS[
    "sapm"
]["open_rack_glass_glass"]

# Create a Location and a PV System
location = Location(
    latitude=59.4135,
    longitude=5.267252,
    name="Haugesund",
    altitude=0,
    tz='Europe/Oslo',
)

system = PVSystem(
        surface_tilt=35,
        surface_azimuth=180,
        module_parameters=module,
        inverter_parameters=inverter,
        temperature_model_parameters=temperature_model_parameters,
    )

# Create and run PV Model
mc = ModelChain(system, location, aoi_model="physical")
mc.run_model(weather=weather_df)
module_energy = mc.results.ac.fillna(0)

# Plot the estimated energy produced by a single panel
fig = go.Figure()
fig.add_trace(go.Scatter(x=module_energy.index, y=module_energy, mode='lines'))
fig.update_layout(yaxis_title='Energy Produced (kWh)')
fig.show()

# Define panel dimensions and peak power for Znshine_PV_Tech_ZXP6_72_295_P
panel_height = 1.95
panel_width = 0.99
panel_peak_power = 295
tilt_angle = 35
orientation = 180

# Calculate the area occupied by the PV panel on a flat roof
panel_area_flat_roof = (
        panel_height
        * panel_width
        * math.cos(tilt_angle * math.pi / 180)
    )

# calculate amount of panels that fit in a certain roof area
roof_area = 3600
panel_count = math.floor(roof_area / panel_area_flat_roof)

# calculate the peak capacity of this system in kWp
system_peak_capacity = panel_count * panel_peak_power / 1000

print(f"Based on the specified system characteristics, {panel_count} panels can be installed on a {roof_area} m² flat roof. \nThis corresponds to a total system capacity of {system_peak_capacity} kWp.")

# Calculate the monthly production of the entire PV installation 
system_production = panel_count * module_energy / 1000
system_production.to_csv('Results/system_production.csv', index=True)
#monthly_production = system_production.resample('ME').sum()

# Plot monthly production
#fig = go.Figure()
#fig.add_trace(go.Bar(x=monthly_production.index, y=monthly_production))
#fig.update_layout(yaxis_title='Energy Produced (kWh)')
#fig.show()
