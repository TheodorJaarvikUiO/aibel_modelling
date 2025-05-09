import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

#------------------------------------------------Dataset processing-----------------------------------------------------

# Load the data
df = pd.read_csv("Datasets/Consumption.csv")
time = pd.to_datetime(df["Time"], format="%m/%d/%y %H:%M")
df["Time"] = time
df.set_index("Time", inplace=True)

# Split into daily blocks (each with 24 rows)
daily_blocks = [df.iloc[i:i+24] for i in range(0, len(df), 24)]

# Separate each mode into lists of daily blocks
normal_days = [day["Normal Mode"] for day in daily_blocks]
low_days = [day["Low Power Mode"] for day in daily_blocks]
peak_days = [day["Peak Power Mode"] for day in daily_blocks]

# Set number of days to use from each mode (adjust these ratios as needed)
n_days = len(daily_blocks)
n_normal = int(n_days * 0.5)
n_low = int(n_days * 0.35)
n_peak = n_days - n_normal - n_low

# Sample full days from each mode
random.seed(42)
normal_sample = random.sample(normal_days, n_normal)

random.seed(43)
low_sample = random.sample(low_days, n_low)

random.seed(44)
peak_sample = random.sample(peak_days, n_peak)


# Combine and shuffle daily blocks
all_days = list(normal_sample) + list(low_sample) + list(peak_sample)
np.random.default_rng(seed=123).shuffle(all_days)

# Flatten back into a single series
shuffled_series = pd.concat(all_days).reset_index(drop=True)

# Generate a new datetime index
start_time = pd.to_datetime("2024-01-01 00:00")
date_range = pd.date_range(start=start_time, periods=len(shuffled_series), freq="h")
shuffled_series.index = date_range
shuffled_series.name = "Power_Consumption"
shuffled_series.to_csv("Datasets/shuffled_power_timeseries_by_day.csv", index_label="Timestamp")

#------------------------------------------------Plots------------------------------------------------------------------

# Datasets

base_case = pd.read_csv("Datasets/shuffled_power_timeseries_by_day.csv", index_col=0, parse_dates=True)
battery_case = pd.read_csv("Results/Battery_Case/energy_system.csv", index_col=0, parse_dates=True)
solar_case = pd.read_csv("Results/BatterySolar_Case/energy_system_bs.csv", index_col=0, parse_dates=True)
rain_case = pd.read_csv("Results/BatteryRain_Case/energy_system_br.csv", index_col=0, parse_dates=True)
wind_case = pd.read_csv("Results/BatteryWind_Case/energy_system_bw.csv", index_col=0, parse_dates=True)
solar_wind_case = pd.read_csv("Results/BatteryWindSolar_Case/energy_system_bws.csv", index_col=0, parse_dates=True)
wind_park_case = pd.read_csv("Results/BatteryWindPark_Case/energy_system_bwp.csv", index_col=0, parse_dates=True)

base_case_grid = base_case['Power_Consumption'].resample('ME').sum()
battery_case_grid = battery_case['Grid supply (kWh)'].resample('ME').sum()
solar_case_grid = solar_case['Grid supply (kWh)'].resample('ME').sum()
wind_case_grid = wind_case['Grid supply (kWh)'].resample('ME').sum()
rain_case_grid = rain_case['Grid supply (kWh)'].resample('ME').sum()
solar_wind_case_grid = solar_wind_case['Grid supply (kWh)'].resample('ME').sum()
months = base_case_grid.index.strftime('%b')
x = range(len(months))

# Monthly grid consumption
plt.figure(figsize=(16, 5))
bar_width = 0.19
x = range(len(months))
plt.bar(x, base_case_grid.values, width=bar_width, label="Base Case", color="red")
plt.bar([i + bar_width*1 for i in x], solar_case_grid.values, width=bar_width, label="Battery & Solar", color="orange")
plt.bar([i + bar_width*2 for i in x], wind_case_grid.values, width=bar_width, label="Battery & Wind", color="green")
plt.bar([i + bar_width*3 for i in x], solar_wind_case_grid.values, width=bar_width, label="Battery & Solar & Wind", color="blue")
plt.xlabel("Month")
plt.ylabel("kW")
plt.title("Monthly Grid Consumption")
plt.xticks([i + bar_width/2 for i in x], months)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig('Results/Analysis/monthly_grid_consumption.png')
plt.close()

base_case_grid = base_case['Power_Consumption'].sum()
battery_case_grid = battery_case['Grid supply (kWh)'].sum()
solar_case_grid = solar_case['Grid supply (kWh)'].sum()
wind_case_grid = wind_case['Grid supply (kWh)'].sum()
rain_case_grid = rain_case['Grid supply (kWh)'].sum()
solar_wind_case_grid = solar_wind_case['Grid supply (kWh)'].sum()
wind_park_case_grid = wind_park_case['Grid supply (kWh)'].sum()


cases = ["Battery & Rain", "Battery & Solar", "Battery & Wind", "Battery & Solar & Wind", "Battery & Windpark"]
case_values = [rain_case_grid, solar_case_grid, wind_case_grid, solar_wind_case_grid, wind_park_case_grid]

x = range(len(cases))
width = 0.35

plt.figure(figsize=(12, 6))
plt.bar([i - width/2 for i in x], [base_case_grid]*len(cases), width=width, label='Base Case', color='red')
bars = plt.bar([i + width/2 for i in x], case_values, width=width, label='Scenario Case', color='orange')

for i, val in enumerate(case_values):
    percent = val / base_case_grid * 100
    plt.text(i + width/2, val + 10, f"{percent:.1f}%", ha='center', va='bottom')

plt.xlabel("Case")
plt.ylabel("Grid Consumption (kWh)")
plt.title("Grid Consumption Comparison by Case")
plt.xticks(x, cases)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig('Results/Analysis/grid_consumption_comparison.png')
plt.close()

spot_prices = pd.read_csv("Datasets/Spot_price.csv", index_col=0, parse_dates=True)
base_case['Spot Price'] = spot_prices['Spot Price (NO2) EUR/MWh'].iloc[:len(base_case)].values / 1000
base_case_grid_cost =  (base_case['Power_Consumption'] * base_case["Spot Price"]).sum()
battery_case_grid_cost = (battery_case['Grid supply (kWh)'] * base_case["Spot Price"]).sum()
rain_case_grid_cost = (rain_case['Grid supply (kWh)'] * base_case["Spot Price"]).sum()
solar_case_grid_cost = (solar_case['Grid supply (kWh)'] * base_case["Spot Price"]).sum()
wind_case_grid_cost = (wind_case['Grid supply (kWh)'] * base_case["Spot Price"]).sum()
solar_wind_case_grid_cost = (solar_wind_case['Grid supply (kWh)'] * base_case["Spot Price"]).sum()
wind_park_case_grid_cost = (wind_park_case['Grid supply (kWh)'] * base_case["Spot Price"]).sum()

cases = ["Battery" ,"Battery & Rain", "Battery & Solar", "Battery & Wind", "Battery & Solar & Wind", "Battery & Windpark"]
case_values = [battery_case_grid_cost, rain_case_grid_cost, solar_case_grid_cost, wind_case_grid_cost, solar_wind_case_grid_cost, wind_park_case_grid_cost]

x = range(len(cases))
width = 0.35

plt.figure(figsize=(12, 6))
plt.bar([i - width/2 for i in x], [base_case_grid_cost]*len(cases), width=width, label='Base Case', color='red')
bars = plt.bar([i + width/2 for i in x], case_values, width=width, label='Scenario Case', color='orange')

for i, val in enumerate(case_values):
    percent = val / base_case_grid_cost * 100
    plt.text(i + width/2, val + 10, f"{percent:.1f}%", ha='center', va='bottom')

plt.xlabel("Case")
plt.ylabel("Grid Consumption Cost (EUR)")
plt.title("Grid Consumption Cost Comparison by Case")
plt.xticks(x, cases)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig('Results/Analysis/grid_consumption_cost_comparison.png')
plt.close()


