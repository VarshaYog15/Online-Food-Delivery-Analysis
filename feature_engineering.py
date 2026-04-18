import pandas as pd

df = pd.read_csv("cleaned_online_food_delivery.csv")

# Profit calculation
df['cost'] = df['revenue'] * 0.6
df['profit'] = df['revenue'] - df['cost']

# Delivery speed category
df['delivery_speed'] = pd.cut(
    df['delivery_time_min'],
    bins=[0, 30, 45, 60, 120],
    labels=['Fast', 'Medium', 'Slow', 'Very Slow']
)

df.to_csv("featured_online_food_delivery.csv", index=False)

print("✅ Feature engineering completed")
