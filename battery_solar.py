import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pypsa

#Network parameters and load
low_power_mode = pd.read_csv('Datasets/aibel_yearly.csv', header=None, index_col=0, parse_dates=True, sep=';')
shuffled = pd.read_csv('Datasets/shuffled_power_timeseries_by_day.csv', index_col=0, parse_dates=True, sep=',')
low_power_mode[1] = shuffled['Power_Consumption'].iloc[:len(low_power_mode)].values
network = pypsa.Network()

Spot_prices2 = pd.read_csv('Datasets/Spot_price.csv', index_col=0)
solar_profile = pd.read_csv('Datasets/PV_system_production.csv', index_col=0)
solar_profile["0"] = solar_profile["0"].clip(lower=0.0).fillna(0.0)
low_power_mode.index = shuffled.index
low_power_mode['Spot Price'] = Spot_prices2['Spot Price (NO2) EUR/MWh'].iloc[:len(low_power_mode)].values / 1000
network.set_snapshots(low_power_mode.index)
solar_profile.index = network.snapshots
print(solar_profile.head())

#Add components, Bus - Load - Generator(Grid) - Battery
network.add("Bus", name="bus0")

network.add("Load",
            name="Shipyard_Load",
            bus="bus0",
            p_set=low_power_mode[1].squeeze())

network.add("Generator",
            name="Grid",
            bus="bus0",
            p_nom=5000,
            marginal_cost=low_power_mode["Spot Price"].squeeze())

network.add("Generator",
            name="solar_pv",
            bus="bus0",
            carrier="solar",
            p_nom=1,
            p_max_pu=solar_profile["0"],
            efficiency=1.0,
            capital_cost=0,
            marginal_cost=0.0,
            p_min_pu=0.0)

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
solar_profile = network.generators_t.p["solar_pv"]
battery_soc = network.stores_t.e["Battery"]
battery_soc2 = network.stores_t.e["Battery2"]
battery_soc3 = network.stores_t.e["Battery3"]
battery_soc4 = network.stores_t.e["Battery4"]
battery_soc5 = network.stores_t.e["Battery5"]
battery_soc6 = network.stores_t.e["Battery6"]
load_profile = network.loads_t.p_set["Shipyard_Load"]

total_system_cost = network.objective  # Total cost from optimization
print(f"Total System Cost: {total_system_cost:.2f} Euro")

grid_cost = (network.generators_t.p["Grid"] * low_power_mode['Spot Price'].squeeze()).sum()
print(f"Total Grid Supply Cost: {grid_cost:.2f} Euro")

print(f"Total Grid supply (kWh): {grid_supply.sum():.2f} kWh")

battery_charge_cost = ((network.stores_t.e["Battery"]) * low_power_mode['Spot Price'].squeeze()).sum()
print(f"Total Battery Charge Cost: {battery_charge_cost:.2f} Euro")

cost_breakdown = network.buses_t.marginal_price.sum()
print(f"Cost Breakdown: {cost_breakdown}")

marginal_prices = network.buses_t.marginal_price
print(marginal_prices.head())

energy_system = pd.DataFrame({
    "Load (kWh)": load_profile,
    "Grid supply (kWh)": grid_supply,
    "Spot Price (Euro/kWh)": low_power_mode["Spot Price"].squeeze(),
    "Solar (kWh)": solar_profile,
    "Battery (kWh)": battery_soc,
    "Battery2 (kWh)": battery_soc2,
    "Battery3 (kWh)": battery_soc3,
    "Battery4 (kWh)": battery_soc4,
    "Battery5 (kWh)": battery_soc5,
    "Battery6 (kWh)": battery_soc6
})

energy_system.to_csv("Results/BatterySolar_Case/energy_system_bs.csv")

economic_results = pd.DataFrame({
    "Grid supply (kWh)": [grid_supply.sum()],
    "Total System Cost(Euro)": [total_system_cost],
    "Grid Cost(Euro)": [grid_cost],
    "Battery Charge Cost(Euro)": [battery_charge_cost],
    "Marginal Prices (Avg Euro/kWh)": [marginal_prices.mean().mean()] ,
    "PV Generation (kWh)": [solar_profile.sum()]
})

economic_results.to_csv("Results/BatterySolar_Case/economic_results_bs.csv")

# Plot just one single day
start_index = 6000
end_index = 6100
plt.figure(figsize=(16, 5))
plt.plot(time_index[start_index:end_index], load_profile[start_index:end_index], label="Load (kWh)", linestyle="dashed", color="black") # Load
plt.plot(time_index[start_index:end_index], grid_supply[start_index:end_index], label="Grid Supply (kWh)", color="blue") # Grid supply
plt.plot(time_index[start_index:end_index], battery_soc.diff()[start_index:end_index] + battery_soc2.diff()[start_index:end_index] + battery_soc3.diff()[start_index:end_index] + battery_soc4.diff()[start_index:end_index] + battery_soc5.diff()[start_index:end_index] + battery_soc6.diff()[start_index:end_index], label="Battery Charge/Discharge (kWh)", color="green") # Battery charge/discharge
plt.plot(time_index[start_index:end_index], low_power_mode['Spot Price'].squeeze()[start_index:end_index] * 10000, label="Spot price", color="red", linestyle="dotted") # Plot the spot prices
plt.plot(time_index[start_index:end_index], solar_profile[start_index:end_index], label="Solar (kWh)", color="orange")
plt.axhline(0, color="gray", linestyle="dotted")
plt.xlabel("Time")
plt.ylabel("Power (kWh)")
plt.legend()
plt.title("Load, Grid Supply, and Battery Usage Over Time")
plt.grid(True)
plt.savefig('Results/BatterySolar_Case/1_week_battery_solar.png')
plt.close()


# Battery soc
plt.figure(figsize=(16, 5))
plt.plot(time_index[start_index:end_index], battery_soc[start_index:end_index] + battery_soc2[start_index:end_index] + battery_soc3[start_index:end_index] + battery_soc4[start_index:end_index] + battery_soc5[start_index:end_index] + battery_soc6[start_index:end_index] , label="Battery SOC (kWh)", color="purple")
plt.xlabel("Time")
plt.ylabel("Stored Energy (kWh)")
plt.title("Battery State of Charge Over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('Results/BatterySolar_Case/1_week_battery_solar_soc.png')
plt.close()

# Battery soc and solar productrion
plt.figure(figsize=(16, 5))
plt.plot(time_index[start_index:end_index], battery_soc[start_index:end_index] + battery_soc2[start_index:end_index] + battery_soc3[start_index:end_index] + battery_soc4[start_index:end_index] + battery_soc5[start_index:end_index] + battery_soc6[start_index:end_index] , label="Battery SOC (kWh)", color="purple")
plt.plot(time_index[start_index:end_index], solar_profile[start_index:end_index], label="Solar (kWh)", color="orange")
plt.xlabel("Time")
plt.ylabel("kW per hour")
plt.title("Battery SOC and solar")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('Results/BatterySolar_Case/1_week_battery_solar_prod.png')
plt.close()

# 1 Year Solar
plt.figure(figsize=(16, 5))
plt.plot(time_index, solar_profile, label="Solar (kWh)", color="orange")
plt.xlabel("Time")
plt.ylabel("kW per hour")
plt.title("Solar Profile")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('Results/BatterySolar_Case/1_year_solar.png')
plt.close()

solar_profile.index = pd.to_datetime(solar_profile.index)
monthly = solar_profile.resample("ME").sum()
monthly.index = monthly.index.strftime("%b")
plt.figure(figsize=(16, 5))
monthly.plot(kind='bar', title="Monthly PV Production")
plt.ylabel("kW per hour")
plt.xlabel("Month")
plt.tight_layout()
plt.savefig('Results/BatterySolar_Case/monthly_pv.png')
plt.close()

grid_supply_no_battery = low_power_mode[1]
grid_cost_no_battery = (grid_supply_no_battery * low_power_mode["Spot Price"]).resample('ME').sum()
grid_cost_with_battery = (grid_supply * low_power_mode["Spot Price"]).resample('ME').sum()
months = grid_cost_with_battery.index.strftime('%b')

# Monthly grid cost
plt.figure(figsize=(16, 5))
bar_width = 0.20
x = range(len(months))
plt.bar(x, grid_cost_no_battery.values, width=bar_width, label="Without Battery", color="red")
plt.bar([i + bar_width for i in x], grid_cost_with_battery.values, width=bar_width, label="With Battery", color="green")
plt.xlabel("Month")
plt.ylabel("Grid Cost (€)")
plt.title("Monthly Grid Cost: With vs Without Battery")
plt.xticks([i + bar_width/2 for i in x], months)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig('Results/BatterySolar_Case/monthly_grid_cost_comparison_bs.png')
plt.close()

grid_supply_og = low_power_mode[1].resample('ME').sum()
grid_supply_with_battery = grid_supply.resample('ME').sum()

# Monthly consumption
plt.figure(figsize=(16, 5))
bar_width = 0.20
x = range(len(months))
plt.bar(x, grid_supply_og.values, width=bar_width, label="Original", color="red")
plt.bar([i + bar_width for i in x], grid_supply_with_battery.values, width=bar_width, label="With Battery & PV", color="green")
plt.xlabel("Month")
plt.ylabel("kW")
plt.title("Monthly Grid supply: With vs Without PV & Battery")
plt.xticks([i + bar_width/2 for i in x], months)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig('Results/BatterySolar_Case/monthly_grid_supply_comparison_bs.png')
plt.close()
