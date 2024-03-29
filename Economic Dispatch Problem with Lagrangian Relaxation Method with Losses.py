# -*- coding: utf-8 -*-
"""with_losses.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HhnuhHOVBIfODLoTpQlJMf5EjjymifX6
"""

# Economic Dispatch Problem with Lagrangian Relaxation Method with Losses
# H Kesava Sravan - CB.EN.U4ELC20023
# B Ram Narayan - CB.EN.U4ELC20055
# K Pranathi - CB.EN.U4EEE20054
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Sample data (assuming you have the loss coefficients in the 'Loss_Coefficients' column of your CSV file)
data = pd.read_csv('Economic_Dispatch_PROBLEM.csv')
data

a = data['a']
b = data['b']
c = data['c']
min_capacity = data['Min_Capacity']
max_capacity = data['Max_Capacity']

# Function to calculate the cost for a given power output
def calculate_cost(P, a, b, c):
    return a * np.square(P) + b * P + c

# Objective function for optimization (to minimize the cost)
def objective_function(P, a, b, c, lambda_val, power_demand):
    return sum(calculate_cost(P, a, b, c)) + lambda_val * (sum(P) - power_demand)

# Constraint function for the total power demand
def total_power_constraint(P, power_demand):
    return sum(P) - power_demand

def calculate_transmission_loss(P, loss_factor):
    total_power = sum(P)
    return total_power * loss_factor

def economic_load_dispatch_with_losses(a, b, c, min_capacity, max_capacity, power_demand, loss_factor):
    num_units = len(a)
    results = []

    for idx, demand in enumerate(power_demand, start=1):
        initial_guess = np.ones(num_units) * (demand / num_units)  # Initial guess for power output
        lambda_val = 0
        while True:
            optimization_result = minimize(
                lambda P: objective_function(P, a, b, c, lambda_val, demand),
                initial_guess,
                constraints={'type': 'eq', 'fun': total_power_constraint, 'args': (demand,)},
                bounds=[(min_capacity[i], max_capacity[i]) for i in range(num_units)]
            )
            optimized_power = optimization_result.x
            total_fuel_cost = sum(calculate_cost(optimized_power, a, b, c))
            lambda_val += sum(optimized_power) - demand

            # Transmission losses calculation
            total_losses = calculate_transmission_loss(optimized_power, loss_factor)
            total_with_losses = total_fuel_cost + total_losses

            if abs(sum(optimized_power) - demand) < 1e-5:
                break

        results.append({
            'SLNo.': idx,
            'Powerdemand': demand,
            'P1': optimized_power[0],
            'P2': optimized_power[1],
            'P3': optimized_power[2],
            'P4': optimized_power[3],
            'P5': optimized_power[4],
            'P6': optimized_power[5],
            'Lambda': lambda_val,
            'TotalFuelCost': total_fuel_cost,
            'Ploss': total_losses,
            'TotalCostWithLosses': total_with_losses
        })

    return pd.DataFrame(results)

# Use hypothetical loss coefficients generated above
num_units = len(a)
loss_coefficients = np.random.uniform(0.001, 0.01, num_units)
# Power demand values
power_demand = [700, 800, 900, 1000, 1100]
# Assuming the data reading and power_demand remain the same as before
loss_factor = 0.03  # Example transmission loss factor (3% in this case)
result_table_with_losses = economic_load_dispatch_with_losses(a, b, c, min_capacity, max_capacity, power_demand, loss_factor)
# Display the resulting table
print(result_table_with_losses)

# Extracting 'Power demand' and 'Ploss' columns from the DataFrame
power_demand_values = result_table_with_losses['Powerdemand']
power_loss_values = result_table_with_losses['Ploss']

# Plotting the bar graph
plt.figure(figsize=(8, 6))
plt.bar(power_demand_values, power_loss_values, color='skyblue')
plt.xlabel('Power Demand')
plt.ylabel('Power Loss')
plt.title('Variation of Power Loss with Load Demand')
plt.xticks(power_demand_values)  # Set x-axis ticks as power demand values
plt.grid(axis='y')  # Show gridlines on the y-axis
plt.show()
