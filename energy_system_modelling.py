import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pypsa


def wind_speed_to_capacity_factor(wind_speed):
    cut_in = 3   # m/s
    rated = 12   # m/s
    cut_out = 25 # m/s

    return np.piecewise(
        wind_speed,
        [wind_speed < cut_in,
         (wind_speed >= cut_in) & (wind_speed < rated),
         (wind_speed >= rated) & (wind_speed <= cut_out),
         wind_speed > cut_out],
        [0,  # Below cut-in: no power
         lambda v: (v - cut_in) / (rated - cut_in),  # Ramp-up phase
         1,  # At or above rated speed: full power
         0]  # Above cut-out: no power
    )

#Network parameters and load
consumption = pd.read_csv('Datasets/Consumption.csv', sep=',', index_col=0, parse_dates=True)
#low_power_mode = consumption[['Time','Low Power Mode']]
#print(low_power_mode.head())

Spot_prices2 = pd.read_csv('Datasets/Spot_price.csv', index_col=0, parse_dates=True)
#Spot_prices2['Time'].replace('T', ' ', regex=True, inplace=True)
#Spot_prices2['Time'] = pd.to_datetime(Spot_prices2['Time'], format='ISO8601',utc=True)

Spot_prices2.index = pd.to_datetime(Spot_prices2.index).tz_convert(None)
consumption.index = pd.to_datetime(consumption.index)
#Spot_prices2.set_index('Time', inplace=True)

# Use "Low Power Mode" consumption
consumption_series = consumption['Low Power Mode']
spot_price_series = Spot_prices2['Spot Price (NO2) EUR/MWh']

# Align the time series
consumption_series = consumption_series.reindex(spot_price_series.index)
spot_price_series = spot_price_series.reindex(consumption_series.index)
print(spot_price_series.head())
print(consumption_series.head())

network = pypsa.Network()
network.set_snapshots(low_power_mode.index)

low_power_mode['Spot Price'] = Spot_prices2['Spot Price (NO2) EUR/MWh'].iloc[:len(low_power_mode)].values
print(low_power_mode.head())

#Add components, Bus - Load - Generator(Grid) - Battery
network.add("Bus", "bus0")
network.add("Load", "Shipyard_Load", bus="bus0", p_set=low_power_mode[1].squeeze()) # Load from csv
network.add("Generator", "Grid", bus="bus0",p_nom=3000, marginal_cost=low_power_mode['Spot Price'].squeeze()) # 3 MW nominal power
network.add("Generator"," wind",
                bus="bus0",
                p_max_pu = wind_pu["_ON"],
                p_nom_extendable = True,
                marginal_cost = 0.02, #Small cost to prefer curtailment to destroying energy in storage, solar curtails before wind
                capital_cost = 100000)
battery_names = ["Battery", "Battery2", "Battery3", "Battery4", "Battery5", "Battery6"]

for battery_name in battery_names:
    network.add("Store", battery_name,
                bus="bus0",
                e_nom=1000,  # Fixed battery capacity in kWh
                # e_nom_extendable=True,  # Battery capacity can be extended, model decides optimal size
                e_cyclic=False,  # No cyclic behavior (energy doesn't wrap around)
                e_initial=0,  # Initial state of charge (SOC) in kWh
                standing_loss=0.001,  # Small self-discharge loss per time step

                # Efficiency parameters
                efficiency_store=0.9,  # Charging efficiency (90%)
                efficiency_dispatch=0.9,  # Discharging efficiency (90%)

                # State of Charge (SOC) limits
                e_min_pu=0.2,  # Minimum SOC (20% of capacity)
                e_max_pu=0.8,  # Maximum SOC (80% of capacity)

                # Cost parameters
                capital_cost=100000,  # Investment cost per kWh installed capacity
                # lifetime=10,  # Battery lifetime in years
                # marginal_cost=0,  # Variable operation cost per kWh
                # interest_rate=0.05,  # Discount rate for investment
                # cyclic_state_of_charge=True,  # Allow cyclic SOC behavior (e.g., wrap around)
                )


#Cost minimization
network.optimize()

#Plots & Results

# Extract results
time_index = network.snapshots
grid_supply = network.generators_t.p["Grid"]
battery_soc = network.stores_t.e["Battery"]
battery_soc2 = network.stores_t.e["Battery2"]
battery_soc3 = network.stores_t.e["Battery3"]
battery_soc4 = network.stores_t.e["Battery4"]
battery_soc5 = network.stores_t.e["Battery5"]
battery_soc6 = network.stores_t.e["Battery6"]

load_profile = network.loads_t.p_set["Shipyard_Load"]

total_system_cost = network.objective  # Total cost from optimization
print(f"Total System Cost: {total_system_cost:.2f} currency units")

grid_cost = (network.generators_t.p["Grid"] * Spot_prices2).sum()
print(f"Total Grid Supply Cost: {grid_cost:.2f} currency units")

battery_charge_cost = ((network.stores_t.e["Battery"]) * Spot_prices2).sum()  # Example cost factor
print(f"Total Battery Charge Cost: {battery_charge_cost:.2f} currency units")

cost_breakdown = network.buses_t.marginal_price.sum()
print(f"Cost Breakdown: {cost_breakdown}")

marginal_prices = network.buses_t.marginal_price
print(marginal_prices.head())

economic_results = pd.DataFrame({
    "Total System Cost": [total_system_cost],
    "Grid Cost": [grid_cost],
    "Battery Charge Cost": [battery_charge_cost],
    "Marginal Prices (Avg)": [marginal_prices.mean().mean()],
})

print(economic_results)

# Plot just one single day
start_index = 0
end_index = 100
plt.figure(figsize=(10, 5))
plt.plot(time_index[start_index:end_index], load_profile[start_index:end_index], label="Load (kWh)", linestyle="dashed", color="black") # Load
plt.plot(time_index[start_index:end_index], grid_supply[start_index:end_index], label="Grid Supply (kWh)", color="blue") # Grid supply
plt.plot(time_index[start_index:end_index], battery_soc.diff()[start_index:end_index] + battery_soc2.diff()[start_index:end_index] + battery_soc3.diff()[start_index:end_index] + battery_soc4.diff()[start_index:end_index] + battery_soc5.diff()[start_index:end_index] + battery_soc6.diff()[start_index:end_index], label="Battery Charge/Discharge (kWh)", color="green") # Battery charge/discharge
plt.plot(time_index[start_index:end_index], Spot_prices2[start_index:end_index] * 100, label="Spot price", color="red", linestyle="dotted") # Plot the spot prices
plt.axhline(0, color="gray", linestyle="dotted")
plt.xlabel("Time")
plt.ylabel("Power (kWh)")
plt.legend()
plt.title("Load, Grid Supply, and Battery Usage Over Time")
plt.grid(True)
plt.savefig('Results/one_day_usage.png')

# battery soc
plt.figure(figsize=(10, 5))
plt.plot(time_index[start_index:end_index], battery_soc[start_index:end_index] + battery_soc2[start_index:end_index] + battery_soc3[start_index:end_index] + battery_soc4[start_index:end_index] + battery_soc5[start_index:end_index] + battery_soc6[start_index:end_index], label="Battery SOC (kWh)", color="purple")
plt.xlabel("Time")
plt.ylabel("Stored Energy (kWh)")
plt.title("Battery State of Charge Over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('Results/battery_soc_usage.png')

# Calculate installed capacity
installed_capacity = network.statistics.installed_capacity()
# Plot installed capacity by component type
installed_capacity.plot(kind='bar', figsize=(10, 6))
plt.title('Installed Capacity by Component Type')
plt.xlabel('Component Type')
plt.ylabel('Installed Capacity (MW)')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.savefig('Results/statistics_advanced_usage.png')

#plt.figure(figsize=(10, 5))
#plt.plot(time_index, wind_capacity_factor, label="Wind Capacity Factor", color="cyan")
#plt.xlabel("Time")
#plt.ylabel("Capacity Factor (0-1)")
#plt.title("Wind Turbine Capacity Factor Over Time")
#plt.legend()
#plt.grid(True)
#plt.savefig('Results/wind_capacity_factor.png')
