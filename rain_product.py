#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 14:47:02 2025

@author: rafaelagramata
"""

import pandas as pd 
from pathlib import Path  


# Reading the CSV file
df = pd.read_csv("Datasets/rain_data_storasund_1year.csv", sep= ";", decimal= ",") 

factor = 1E-3

energy_perdrop = 0.022 #J/drop

avg_voldrop = 50E-6 #m^3

roof_area = 0.7 * 18100 #m^2



df["rain_production"] = ((df["Nedbør (1 t)"] * factor) / avg_voldrop ) * energy_perdrop * roof_area

filepath = Path('Datasets/rain_production.csv')  
filepath.parent.mkdir(parents=True, exist_ok=True)  
 

df.to_csv(filepath, index= False)



