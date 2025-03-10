import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pypsa


#Network parameters and load
low_power_mode = pd.read_csv('aibel_monthly_load.csv', header=None, index_col=0, parse_dates=True)
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

#Add components, Bus - Load - Generator(Grid) - Battery
network.add("Bus", "bus0")
network.add("Load", "Shipyard_Load", bus="bus0", p_set=low_power_mode.squeeze()) # Load from csv
network.add("Generator", "Grid", bus="bus0",p_nom=3000, marginal_cost=spot_prices) # 3 MWh peak

network.add("Store", "Battery",
            bus="bus0",
            e_nom=3000,  # Battery capacity in kWh
            e_cyclic=False,  # No cyclic behavior
            e_initial=1500,# initial charge
            standing_loss=0.001,  # Small loss over time
            efficiency_store=0.9,  # Charge efficiency
            efficiency_dispatch=0.9,# Discharge efficiency
            e_min_pu = 0.2, # Minimum SOC
            e_max_pu = 0.8) # Maximum SOC

#Cost minimization
network.optimize()

#Plots & Results

# Extract results
time_index = network.snapshots
grid_supply = network.generators_t.p["Grid"]
battery_soc = network.stores_t.e["Battery"]
load_profile = network.loads_t.p_set["Shipyard_Load"]

total_system_cost = network.objective  # Total cost from optimization
print(f"Total System Cost: {total_system_cost:.2f} currency units")

grid_cost = (network.generators_t.p["Grid"] * spot_prices).sum()
print(f"Total Grid Supply Cost: {grid_cost:.2f} currency units")

battery_charge_cost = (network.stores_t.e["Battery"] * 0.001).sum()  # Example cost factor
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
plt.plot(time_index, battery_soc.diff(), label="Battery Charge/Discharge (kWh)", color="green") # Battery charge/discharge
#plt.plot(time_index, spot_prices * 100, label="Spot price", color="red", linestyle="dotted") # Plot the spot prices
plt.axhline(0, color="gray", linestyle="dotted")
plt.xlabel("Time")
plt.ylabel("Power (kWh)")
plt.legend()
plt.title("Load, Grid Supply, and Battery Usage Over Time")
plt.grid(True)
plt.show()

# Plot Battery State of Charge (SOC)
plt.figure(figsize=(10, 5))
plt.plot(time_index, battery_soc, label="Battery SOC (kWh)", color="purple")
plt.xlabel("Time")
plt.ylabel("Stored Energy (kWh)")
plt.title("Battery State of Charge Over Time")
plt.legend()
plt.grid(True)
plt.show()

