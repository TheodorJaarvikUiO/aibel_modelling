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
low_power_mode = pd.read_csv('Datasets/aibel_yearly.csv', header=None, index_col=0, parse_dates=True, sep=';')
wind_data = pd.read_csv('Datasets/1year_wind_haugesund.csv', header=None, index_col=0, parse_dates=True, dayfirst=True)
wind_speed = wind_data.iloc[:, 0].values  # Extract first column as NumPy array
network = pypsa.Network()
network.set_snapshots(low_power_mode.index)
wind_capacity_factor = wind_speed_to_capacity_factor(wind_speed)
wind_capacity_factor = pd.Series(wind_capacity_factor, index=wind_data.index)
wind_capacity_factor = wind_capacity_factor.reindex(network.snapshots, method="nearest")


#Spot Prices
spotPrice_csv = pd.read_csv("Datasets/Spot_price.csv")
spotPrice_csv['Time'] = pd.to_datetime(spotPrice_csv['Time'], format='%Y-%m-%dT%H:%M%z',utc=True)
full_time_range = pd.date_range(start="2024-01-01 01:00+1:00", end="2024-12-31 23:00+1:00", freq='h')  
full_time_range = full_time_range.tz_convert('UTC')  # Convert to UTC timezone
df_time = pd.DataFrame({'Time': full_time_range})
spot_prices = df_time.merge(spotPrice_csv, on='Time', how='outer')

#Add components, Bus - Load - Generator(Grid) - Battery
network.add("Bus", "bus0")
network.add("Load", "Shipyard_Load", bus="bus0", p_set=low_power_mode.squeeze()) # Load from csv
network.add("Generator", "Grid", bus="bus0",p_nom=3000, marginal_cost=spot_prices) # 3 MW nominal power
# # network.add("Generator", "Wind", bus="bus0", p_nom=1000, p_max_pu=pd.Series(wind_capacity_factor, index=wind_data.index)
#             )


network.add("Store", "Battery",
            bus="bus0",
            e_nom=1000,  # Fixed battery capacity in kWh
            #e_nom_extendable=True,  # Battery capacity can be extended, model decides optimal size
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

network.add("Store", "Battery2",
            bus="bus0",
            e_nom=1000,  # Fixed battery capacity in kWh
            #e_nom_extendable=True,  # Battery capacity can be extended, model decides optimal size
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

network.add("Store", "Battery3",
            bus="bus0",
            e_nom=1000,  # Fixed battery capacity in kWh
            #e_nom_extendable=True,  # Battery capacity can be extended, model decides optimal size
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

network.add("Store", "Battery4",
            bus="bus0",
            e_nom=1000,  # Fixed battery capacity in kWh
            #e_nom_extendable=True,  # Battery capacity can be extended, model decides optimal size
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

network.add("Store", "Battery5",
            bus="bus0",
            e_nom=1000,  # Fixed battery capacity in kWh
            #e_nom_extendable=True,  # Battery capacity can be extended, model decides optimal size
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

network.add("Store", "Battery6",
            bus="bus0",
            e_nom=1000,  # Fixed battery capacity in kWh
            #e_nom_extendable=True,  # Battery capacity can be extended, model decides optimal size
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

grid_cost = (network.generators_t.p["Grid"] * spot_prices).sum()
print(f"Total Grid Supply Cost: {grid_cost:.2f} currency units")

battery_charge_cost = ((network.stores_t.e["Battery"]) * spot_prices).sum()  # Example cost factor
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
plt.plot(time_index[start_index:end_index], spot_prices[start_index:end_index] * 100, label="Spot price", color="red", linestyle="dotted") # Plot the spot prices
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

plt.figure(figsize=(10, 5))
plt.plot(time_index, wind_capacity_factor, label="Wind Capacity Factor", color="cyan")
plt.xlabel("Time")
plt.ylabel("Capacity Factor (0-1)")
plt.title("Wind Turbine Capacity Factor Over Time")
plt.legend()
plt.grid(True)
plt.savefig('Results/wind_capacity_factor.png')
