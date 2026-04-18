# 1_data_loading.py
import pandas as pd
import os

# Load dataset
df = pd.read_csv("ONLINE_FOOD_DELIVERY_ANALYSIS.csv")
print("Dataset loaded successfully!")
print("Rows & Columns:", df.shape)
print(df.head())

# Save intermediate df to pickle for next steps
df.to_pickle("df_step1.pkl")
print(os.path.exists("df_step1.pkl"))

