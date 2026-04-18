import pandas as pd

# Load raw data
df = pd.read_csv("online_food_delivery.csv")

print("📥 Raw data loaded")

# Normalize column names
df.columns = df.columns.str.strip().str.lower()

# ---------- DERIVED & CLEANED COLUMNS ----------

# 1. discount (derived from discount_applied using median)
df['discount'] = df['discount_applied'].fillna(
    df['discount_applied'].median()
)

# 2. order_value (clean existing column using median)
df['order_value'] = df['order_value'].fillna(
    df['order_value'].median()
)

# 3. delivery_fee (derived using mean = 10% of order value)
df['delivery_fee'] = df['order_value'] * 0.10


# 4. orders (each row represents one order)
df['orders'] = 1

# 5. revenue (final amount paid by customer)
df['revenue'] = df['final_amount']

# ---------- SAVE CLEANED DATA ----------

output_file = "cleaned_online_food_delivery.csv"
df.to_csv(output_file, index=False)

print(f"✅ Cleaned data saved successfully as '{output_file}'")
print("📊 Total rows saved:", len(df))
