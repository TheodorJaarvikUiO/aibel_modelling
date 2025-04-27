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

base_case_grid = base_case['Power_Consumption'].resample('ME').sum()
battery_case_grid = battery_case['Grid supply (kWh)'].resample('ME').sum()
solar_case_grid = solar_case['Grid supply (kWh)'].resample('ME').sum()
rain_case_grid = rain_case['Grid supply (kWh)'].resample('ME').sum()
months = base_case_grid.index.strftime('%b')
x = range(len(months))

# Monthly grid consumption
plt.figure(figsize=(16, 5))
bar_width = 0.20
x = range(len(months))
plt.bar(x, base_case_grid.values, width=bar_width, label="Base Case", color="red")
plt.bar([i + bar_width for i in x], battery_case_grid.values, width=bar_width, label="Battery", color="green")
plt.bar([i + bar_width*2 for i in x], rain_case_grid.values, width=bar_width, label="Battery & Rain", color="blue")
plt.bar([i + bar_width*3 for i in x], solar_case_grid.values, width=bar_width, label="Battery & Solar", color="orange")
plt.xlabel("Month")
plt.ylabel("kW")
plt.title("Monthly Grid Consumption")
plt.xticks([i + bar_width/2 for i in x], months)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig('Results/Analysis/monthly_grid_consumption.png')
plt.close()

