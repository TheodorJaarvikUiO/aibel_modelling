import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pypsa


#Network parameters and load
low_power_mode = pd.read_csv('Datasets/aibel_week_load.csv', header=None, index_col=0, parse_dates=True)
low_power_mode.head()
network = pypsa.Network()
network.set_snapshots(low_power_mode.index)


#Spot Prices
np.random.seed(55)
n_hours = len(low_power_mode.index)
cost_per_hour = np.random.uniform(10, 20, size=n_hours)
morning_peak = [8, 9, 10]   # 08:00 - 10:59
evening_peak = [16, 17, 18] # 16:00 - 18:59

# Apply peak multipliers every day
for i in range(n_hours):
    hour_of_day = i % 24  # Get the hour in a 24-hour cycle

    if hour_of_day in morning_peak:
        cost_per_hour[i] *= 1.5  # Increase by 50% during morning peak
    elif hour_of_day in evening_peak:
        cost_per_hour[i] *= 3 #Increase 200% during evening peak

cost_per_hour += np.random.normal(0, 3, size=n_hours)  # Add noise
spot_prices = pd.Series(cost_per_hour, index=low_power_mode.index)
print(spot_prices.mean())

#Add components, Bus - Load - Generator(Grid) - Battery
network.add("Bus", "bus0")
network.add("Load", "Shipyard_Load", bus="bus0", p_set=low_power_mode.squeeze()) # Load from csv
network.add("Generator", "Grid", bus="bus0",p_nom=3000, marginal_cost=spot_prices) # 3 MW nominal power

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

# Plot Power Flows
plt.figure(figsize=(10, 5))
plt.plot(time_index, load_profile, label="Load (kWh)", linestyle="dashed", color="black") # Load
plt.plot(time_index, grid_supply, label="Grid Supply (kWh)", color="blue") # Grid supply
plt.plot(time_index, battery_soc.diff() + battery_soc2.diff() + battery_soc3.diff() + battery_soc4.diff() + battery_soc5.diff() + battery_soc6.diff(), label="Battery Charge/Discharge (kWh) 1", color="green")
plt.plot(time_index, spot_prices * 100, label="Spot price", color="red", linestyle="dotted") # Plot the spot prices
plt.axhline(0, color="gray", linestyle="dotted")
plt.xlabel("Time")
plt.ylabel("Power (kWh)")
plt.legend()
plt.title("Load, Grid Supply, and Battery Usage Over Time")
plt.grid(True)
plt.savefig('Results/1week_usage.png')

# Plot Battery State of Charge (SOC)
plt.figure(figsize=(10, 5))
plt.plot(time_index, battery_soc + battery_soc2 + battery_soc3 + battery_soc4 + battery_soc5 + battery_soc6, label="Battery SOC (kWh)", color="purple")
plt.xlabel("Time")
plt.ylabel("Stored Energy (kWh)")
plt.title("Battery State of Charge Over Time")
plt.legend()
plt.grid(True)
plt.savefig('Results/battery_soc_1week.png')

# Plot just one single day
start_index = 0
end_index = 48
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

