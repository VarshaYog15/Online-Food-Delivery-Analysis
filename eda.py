import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ============================
# CONFIG
# ============================
CSV_PATH = "C:/Users/2SIN/Documents/Python/venv/online_food_delivery/featured_online_food_delivery.csv"
OUTPUT_DIR = "eda_outputs"

sns.set(style="whitegrid")
plt.switch_backend("Agg")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🔹 EDA Started")

# ============================
# LOAD DATA
# ============================
df = pd.read_csv(CSV_PATH)
print("✅ Data Loaded:", df.shape)

# ============================
# DATE HANDLING
# ============================
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce", format="mixed")
# Extract month in YYYY-MM format
df['month'] = df['order_date'].dt.to_period('M').astype(str)



# =====================================================
# CUSTOMER & ORDER ANALYSIS
# =====================================================

# ============================
# 1. Top Spending Customers (IMPROVED)
# ============================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Aggregate
customer_analysis = (
    df.groupby("customer_id")
    .agg(
        total_spent=("order_value", "sum"),
        total_orders=("order_id", "count"),
        avg_order_value=("order_value", "mean")
    )
    .reset_index()
)

# Step 2: Filter (important - remove one-time customers)
customer_analysis = customer_analysis[customer_analysis["total_orders"] >= 3]

# Step 3: Get top customers
top_customers = (
    customer_analysis
    .sort_values("total_spent", ascending=False)
    .head(10)
)

# Reverse for horizontal plot
top_customers = top_customers[::-1]

# ============================
# Plot
# ============================

plt.figure(figsize=(12, 7))

sns.barplot(
    data=top_customers,
    x="total_spent",
    y="customer_id",
    hue="customer_id",
    palette="viridis",
    legend=False
)

# Add total spend labels
for i, row in enumerate(top_customers["total_spent"]):
    plt.text(
        row,
        i,
        f"{row:.0f}",
        va='center'
    )

# Add order count insight
for i, row in enumerate(top_customers["total_orders"]):
    plt.text(
        5,  # left side
        i,
        f"Orders: {row}",
        va='center',
        fontsize=9
    )

plt.title("Top 10 Customers by Total Spending (Min 3 Orders)")
plt.xlabel("Total Spend")
plt.ylabel("Customer ID")

plt.grid(axis='x', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/01_top_spending_customers_improved.png")
plt.close()

# ============================
# 2. Age Group vs Order Value (IMPROVED)
# ============================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Clean data
df = df.dropna(subset=["customer_age", "order_value"])

# Step 2: Create age groups
bins = [0, 18, 25, 35, 45, 60, 100]
labels = ["<18", "18-25", "26-35", "36-45", "46-60", "60+"]

df["age_group"] = pd.cut(df["customer_age"], bins=bins, labels=labels)

# Step 3: Aggregate
age_analysis = (
    df.groupby("age_group", observed=True)
    .agg(
        avg_order_value=("order_value", "mean"),
        median_order_value=("order_value", "median"),
        total_orders=("order_id", "count")
    )
    .reset_index()
)

# Step 4: Filter small groups
age_analysis = age_analysis[age_analysis["total_orders"] >= 30]

# ============================
# Plot
# ============================

plt.figure(figsize=(12, 6))

sns.barplot(
    data=age_analysis,
    x="age_group",
    y="avg_order_value",
    hue="age_group",
    palette="Blues",
    legend=False
)

# Add mean labels
for i, row in age_analysis.iterrows():
    plt.text(
        i,
        row["avg_order_value"],
        f"{row['avg_order_value']:.1f}",
        ha='center'
    )

# Add order count
for i, row in age_analysis.iterrows():
    plt.text(
        i,
        row["avg_order_value"] * 0.85,
        f"n={row['total_orders']}",
        ha='center',
        fontsize=8,
        color='black'
    )

plt.title("Age Group vs Average Order Value")
plt.xlabel("Age Group")
plt.ylabel("Average Order Value")

plt.grid(axis='y', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/02_age_group_order_value_improved.png")
plt.close()

# ============================
# 3. Weekend vs Weekday Order Patterns (FINAL WORKING)
# ============================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================
# Step 1: Ensure valid datetime
# ============================

# Convert to datetime (adjust column name if needed)
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

# Drop invalid rows
df = df.dropna(subset=["order_date"])

# ============================
# Step 2: Extract day name
# ============================

df["order_day"] = df["order_date"].dt.day_name()

# ============================
# Step 3: Create weekend/weekday
# ============================

weekend_days = ["Saturday", "Sunday"]

df["day_type"] = df["order_day"].apply(
    lambda x: "Weekend" if x in weekend_days else "Weekday"
)

# ============================
# Step 4: Validate data (IMPORTANT)
# ============================

print("Sample Days:", df["order_day"].unique())
print("\nDay Counts:\n", df["order_day"].value_counts())
print("\nDay Type Counts:\n", df["day_type"].value_counts())

# ============================
# Step 5: Daily distribution
# ============================

day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

day_counts = (
    df["order_day"]
    .value_counts()
    .reindex(day_order)
    .reset_index()
)

day_counts.columns = ["day", "orders"]

# ============================
# Plot 1: Orders across days
# ============================

plt.figure(figsize=(12, 6))

sns.barplot(
    data=day_counts,
    x="day",
    y="orders"
)

# Add labels
for i, row in day_counts.iterrows():
    if pd.notnull(row["orders"]):
        plt.text(i, row["orders"], int(row["orders"]), ha='center')

plt.title("Orders Distribution Across Days")
plt.xlabel("Day of Week")
plt.ylabel("Number of Orders")

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/03_orders_by_day.png")
plt.close()

# ============================
# Step 6: Weekend vs Weekday summary
# ============================

summary = (
    df["day_type"]
    .value_counts()
    .reset_index()
)

summary.columns = ["day_type", "orders"]

summary["percentage"] = (
    summary["orders"] / summary["orders"].sum() * 100
)


# =====================================================
# REVENUE & PROFIT ANALYSIS
# =====================================================

# ============================
# 4. Monthly Revenue Trend (Improved)
# ============================

# Ensure proper datetime
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce", format="mixed")

# Extract month properly
df["month"] = df["order_date"].dt.to_period("M").astype(str)

monthly_revenue = (
    df.groupby("month")["order_value"]
    .sum()
    .reset_index()
)

# Sort properly
monthly_revenue = monthly_revenue.sort_values("month")

# ============================
# Plot
# ============================
plt.figure(figsize=(12,6))

sns.lineplot(
    data=monthly_revenue,
    x="month",
    y="order_value",
    marker="o"
)

# Highlight max & min points
max_idx = monthly_revenue["order_value"].idxmax()
min_idx = monthly_revenue["order_value"].idxmin()

plt.scatter(
    monthly_revenue.loc[max_idx, "month"],
    monthly_revenue.loc[max_idx, "order_value"],
    s=100
)

plt.scatter(
    monthly_revenue.loc[min_idx, "month"],
    monthly_revenue.loc[min_idx, "order_value"],
    s=100
)

# Labels
plt.title("Monthly Revenue Trend", fontsize=14)
plt.xlabel("Month")
plt.ylabel("Total Revenue")

plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

plt.savefig(f"{OUTPUT_DIR}/04_monthly_revenue.png")
plt.clf()

# ============================
# 5. Impact of Discount on Profit (FINAL BEST)
# ============================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Clean data
df = df.dropna(subset=["discount", "profit"])

# Step 2: Create discount bins
df["discount_bin"] = pd.cut(
    df["discount"],
    bins=[0, 10, 20, 30, 40, 50, 100],
    labels=["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50%+"]
)

# Step 3: Aggregate
discount_analysis = (
    df.groupby("discount_bin", observed=True)
    .agg(
        avg_profit=("profit", "mean"),
        median_profit=("profit", "median"),
        total_orders=("order_id", "count")
    )
    .reset_index()
)

# Step 4: Remove weak bins
discount_analysis = discount_analysis[discount_analysis["total_orders"] >= 30]

# Step 5: Find optimal discount
optimal = discount_analysis.loc[discount_analysis["avg_profit"].idxmax()]

print("\nOptimal Discount Range:", optimal["discount_bin"])
print("Max Avg Profit:", round(optimal["avg_profit"], 2))

# ============================
# Plot
# ============================

plt.figure(figsize=(12, 6))

sns.lineplot(
    data=discount_analysis,
    x="discount_bin",
    y="avg_profit",
    marker="o"
)

# Add labels
for i, row in discount_analysis.iterrows():
    plt.text(i, row["avg_profit"] + 1, f"{row['avg_profit']:.1f}", ha='center')

# Add order count
for i, row in discount_analysis.iterrows():
    plt.text(i, row["avg_profit"] - 3, f"n={row['total_orders']}", ha='center', fontsize=8)

# Highlight optimal point
opt_index = discount_analysis.index.get_loc(optimal.name)

plt.scatter(opt_index, optimal["avg_profit"], s=100)
plt.text(
    opt_index,
    optimal["avg_profit"] + 3,
    "Optimal",
    ha='center',
    fontweight='bold'
)

plt.title("Impact of Discount on Profit (Optimal Range Analysis)")
plt.xlabel("Discount Range")
plt.ylabel("Average Profit")

plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/05_discount_profit_best.png")
plt.close()

# ============================
# 6. High Revenue Cities with Cuisines (Improved)
# ============================

# Step 1: Get top 5 cities by revenue
top_cities = (
    df.groupby("city")["order_value"]
    .sum()
    .nlargest(5)
    .index
)

# Filter only those cities
df_top = df[df["city"].isin(top_cities)]

# Step 2: Aggregate by city + cuisine
city_cuisine_revenue = (
    df_top.groupby(["city", "cuisine_type"])["order_value"]
    .sum()
    .reset_index()
)

# Step 3: Plot
plt.figure(figsize=(12,6))

sns.barplot(
    data=city_cuisine_revenue,
    x="city",
    y="order_value",
    hue="cuisine_type"
)

plt.title("Revenue by Cuisine in Top Cities")
plt.xlabel("City")
plt.ylabel("Total Revenue")

plt.xticks(rotation=30)
plt.legend(title="Cuisine", bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/06_city_cuisine_revenue.png")
plt.clf()

# =====================================================
# DELIVERY PERFORMANCE
# =====================================================

# ============================
# 7. Avg Delivery Time by City (HIGH QUALITY)
# ============================

# Step 1: Aggregate
city_delivery = (
    df.groupby("city")["delivery_time_min"]
    .mean()
    .reset_index()
)

# Step 2: Take top 10 fastest cities (or use nlargest for slowest)
top_cities = city_delivery.nsmallest(10, "delivery_time_min")

# Step 3: Sort for clean visualization
top_cities = top_cities.sort_values("delivery_time_min")

# ============================
# Plot
# ============================
plt.figure(figsize=(12,6))

sns.barplot(
    data=top_cities,
    x="delivery_time_min",
    y="city",
    hue="city",          # assign hue
    palette="viridis",
    legend=False         # remove extra legend
)


# Add value labels
for i, row in top_cities.iterrows():
    plt.text(
        row["delivery_time_min"] + 0.3,
        i,
        f"{row['delivery_time_min']:.1f}",
        va='center'
    )

plt.title("Top 10 Fastest Delivery Cities")
plt.xlabel("Average Delivery Time (minutes)")
plt.ylabel("City")

plt.grid(axis='x', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/07_delivery_city.png")
plt.clf()


# ============================
# 8. Distance vs Delivery Time (FINAL)
# ============================

# Step 1: Create distance bins (if not already present)
bins = [0, 2, 5, 10, 15, 20, 50]
labels = ["0-2 km", "2-5 km", "5-10 km", "10-15 km", "15-20 km", "20+ km"]

df["distance_range"] = pd.cut(df["distance_km"], bins=bins, labels=labels)

# Step 2: Aggregate
distance_time = (
    df.groupby("distance_range", observed=False)["delivery_time_min"]
    .mean()
    .reset_index()
)

# Step 3: Plot
plt.figure(figsize=(10,6))

sns.barplot(
    data=distance_time,
    x="distance_range",
    y="delivery_time_min",
    hue="distance_range",
    palette="coolwarm",
    legend=False
)

# Add value labels
for i, row in distance_time.iterrows():
    plt.text(
        i,
        row["delivery_time_min"] + 0.5,
        f"{row['delivery_time_min']:.1f}",
        ha='center'
    )

plt.title("Average Delivery Time by Distance Range")
plt.xlabel("Distance Range")
plt.ylabel("Avg Delivery Time (minutes)")

plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/08_distance_delay.png")
plt.clf()

# ============================
# 9. Delivery Rating vs Delivery Time (SINGLE CLEAN PLOT)
# ============================

import matplotlib.pyplot as plt
import seaborn as sns

# Clean data
df = df.dropna(subset=["delivery_rating", "delivery_time_min"])

plt.figure(figsize=(10, 6))

# Boxplot (main insight)
sns.boxplot(
    data=df,
    x="delivery_rating",
    y="delivery_time_min"
)

# Overlay trend line
sns.regplot(
    data=df.sample(min(3000, len(df))),
    x="delivery_rating",
    y="delivery_time_min",
    scatter=False,   # no points, just line
    color="red"
)

plt.title("Delivery Time vs Rating (Distribution + Trend)")
plt.xlabel("Delivery Rating")
plt.ylabel("Delivery Time (minutes)")

plt.ylim(120, 140)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/09_rating_delivery_time_final.png")
plt.close()
# =====================================================
# RESTAURANT PERFORMANCE
# =====================================================

# ============================
# 10. Top Rated Restaurants (FINAL CORRECT)
# ============================

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# ============================
# Step 1: Clean data (IMPORTANT FIX)
# ============================

df = df.dropna(subset=["delivery_rating", "restaurant_name"])

# ============================
# Step 2: Aggregate
# ============================

restaurant_rating = (
    df.groupby("restaurant_name")
    .agg(
        avg_rating=("delivery_rating", "mean"),
        total_orders=("order_id", "count")
    )
    .reset_index()
)

# ============================
# Step 3: Filter (SAFE VERSION)
# ============================

# Instead of fixed 50 → adaptive threshold
threshold = max(10, int(df["restaurant_name"].value_counts().quantile(0.25)))

restaurant_rating = restaurant_rating[
    restaurant_rating["total_orders"] >= threshold
]

# ============================
# Step 4: Handle empty data (CRITICAL FIX)
# ============================

if restaurant_rating.empty:
    print("⚠️ No restaurants available after filtering")

else:
    # ============================
    # Step 5: Get Top 10
    # ============================

    top_restaurants = (
        restaurant_rating
        .sort_values("avg_rating", ascending=False)
        .head(10)
    )

    # Reverse for horizontal plot
    top_restaurants = top_restaurants[::-1]

    # ============================
    # Step 6: Plot
    # ============================

    plt.figure(figsize=(12, 7))

    sns.barplot(
        data=top_restaurants,
        x="avg_rating",
        y="restaurant_name"
    )

    # 🔥 SAFE XLIM (MAIN FIX FOR YOUR ERROR)
    min_rating = top_restaurants["avg_rating"].min()

    if pd.notnull(min_rating):
        plt.xlim(min_rating - 0.05, 5)

    # Add labels
    for i, v in enumerate(top_restaurants["avg_rating"]):
        plt.text(v, i, f"{v:.2f}", va='center')

    plt.title("Top Rated Restaurants")
    plt.xlabel("Average Rating")
    plt.ylabel("Restaurant")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/10_top_restaurants.png")
    plt.close()

# ============================
# 11. Cancellation Rate by Restaurant (FINAL FIXED)
# ============================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================
# Step 1: Clean data (IMPORTANT)
# ============================

df = df.dropna(subset=["restaurant_name", "order_status"])

# Step 2: Cancellation flag
df["is_cancelled"] = (df["order_status"] == "Cancelled").astype(int)

# ============================
# Step 3: Aggregate
# ============================

restaurant_perf = (
    df.groupby("restaurant_name")
    .agg(
        total_orders=("order_id", "count"),
        cancelled_orders=("is_cancelled", "sum")
    )
    .reset_index()
)

# Step 4: Calculate rate
restaurant_perf["cancel_rate"] = (
    restaurant_perf["cancelled_orders"] / restaurant_perf["total_orders"]
) * 100

# ============================
# Step 5: Remove invalid values
# ============================

restaurant_perf = restaurant_perf.dropna(subset=["cancel_rate"])

# ============================
# Step 6: Adaptive filter (IMPORTANT FIX)
# ============================

threshold = max(10, int(df["restaurant_name"].value_counts().quantile(0.25)))

restaurant_perf = restaurant_perf[
    restaurant_perf["total_orders"] >= threshold
]

# ============================
# Step 7: Handle empty case (CRITICAL)
# ============================

if restaurant_perf.empty:
    print("⚠️ No restaurant data available after filtering")

else:
    # Step 8: Get worst restaurants
    worst_restaurants = (
        restaurant_perf
        .sort_values("cancel_rate", ascending=False)
        .head(10)
    )

    worst_restaurants = worst_restaurants[::-1]

    # ============================
    # Step 9: Plot
    # ============================

    plt.figure(figsize=(12, 7))

    sns.barplot(
        data=worst_restaurants,
        x="cancel_rate",
        y="restaurant_name"
    )

    # 🔥 SAFE XLIM (FIXES YOUR ERROR)
    max_rate = worst_restaurants["cancel_rate"].max()

    if pd.notnull(max_rate):
        plt.xlim(0, max_rate + 2)

    # Labels
    for i, v in enumerate(worst_restaurants["cancel_rate"]):
        plt.text(v, i, f"{v:.1f}%", va='center')

    plt.title("Top Restaurants by Cancellation Rate")
    plt.xlabel("Cancellation Rate (%)")
    plt.ylabel("Restaurant")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/11_cancellation_restaurants.png")
    plt.close()

# ============================
# 12. Cuisine-wise Performance (FINAL)
# ============================

# Step 1: Aggregate multiple metrics
cuisine_perf = (
    df.groupby("cuisine_type")
    .agg(
        total_orders=("order_id", "count"),
        total_revenue=("order_value", "sum"),
        avg_order_value=("order_value", "mean"),
        avg_delivery_time=("delivery_time_min", "mean"),
        avg_rating=("delivery_rating", "mean")
    )
    .reset_index()
)

# Step 2: Sort by revenue (important)
cuisine_perf = cuisine_perf.sort_values("total_revenue", ascending=False)

# Step 3: Take top 10 cuisines
top_cuisine = cuisine_perf.head(10)

# ============================
# Plot (Revenue Focus)
# ============================
plt.figure(figsize=(12,6))

sns.barplot(
    data=top_cuisine,
    x="total_revenue",
    y="cuisine_type",
    hue="cuisine_type",
    palette="viridis",
    legend=False
)

# Add value labels
for i, row in top_cuisine.iterrows():
    plt.text(
        row["total_revenue"],
        i,
        f"{int(row['total_revenue'])}",
        va='center'
    )

plt.title("Top Performing Cuisines by Revenue")
plt.xlabel("Total Revenue")
plt.ylabel("Cuisine")

plt.grid(axis='x', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/12_cuisine_performance.png")
plt.clf()


# ============================
# 13. Peak Hour Demand (FINAL BEST)
# ============================

# Step 1: Ensure proper datetime parsing
df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="coerce",
    format="mixed"
)

# Step 2: Extract hour
df["order_hour"] = df["order_date"].dt.hour

# Step 3: Drop invalid rows
df = df.dropna(subset=["order_hour"])

# Step 4: Aggregate demand
hourly_demand = (
    df.groupby("order_hour")
    .size()
    .reset_index(name="order_count")
    .sort_values("order_hour")
)

# Step 5: Plot
plt.figure(figsize=(12,6))

sns.lineplot(
    data=hourly_demand,
    x="order_hour",
    y="order_count",
    marker="o"
)

# Highlight peak hour
peak_idx = hourly_demand["order_count"].idxmax()

plt.scatter(
    hourly_demand.loc[peak_idx, "order_hour"],
    hourly_demand.loc[peak_idx, "order_count"],
    s=120
)

# Add label for peak
plt.text(
    hourly_demand.loc[peak_idx, "order_hour"],
    hourly_demand.loc[peak_idx, "order_count"],
    f" Peak: {int(hourly_demand.loc[peak_idx, 'order_hour'])}:00",
    fontsize=10,
    fontweight="bold"
)

# Styling
plt.title("Hourly Order Demand Pattern")
plt.xlabel("Hour of Day (0–23)")
plt.ylabel("Number of Orders")

plt.xticks(range(0,24))
plt.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/13_peak_hour_demand.png")
plt.clf()


# ============================
# 14. Payment Mode Preferences (FINAL)
# ============================

# Step 1: Count + percentage
payment_data = df["payment_mode"].value_counts().reset_index()
payment_data.columns = ["payment_mode", "order_count"]

payment_data["percentage"] = (
    payment_data["order_count"] / payment_data["order_count"].sum()
) * 100

# Step 2: Plot
plt.figure(figsize=(10,6))

sns.barplot(
    data=payment_data,
    x="payment_mode",
    y="order_count",
    hue="payment_mode",
    palette="Set2",
    legend=False
)

# Add percentage labels
for i, row in payment_data.iterrows():
    plt.text(
        i,
        row["order_count"],
        f"{row['percentage']:.1f}%",
        ha='center',
        va='bottom',
        fontweight="bold"
    )

plt.title("Payment Mode Preferences")
plt.xlabel("Payment Mode")
plt.ylabel("Number of Orders")

plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/14_payment_mode.png")
plt.clf()

# ============================
# 15. Cancellation Reason Analysis (FINAL)
# ============================

# Step 1: Filter cancelled orders only (IMPORTANT)
cancel_df = df[df["order_status"] == "Cancelled"]

# Step 2: Count + percentage
cancel_data = cancel_df["cancellation_reason"].value_counts().reset_index()
cancel_data.columns = ["reason", "count"]

cancel_data["percentage"] = (
    cancel_data["count"] / cancel_data["count"].sum()
) * 100

# Step 3: Sort (most important reason first)
cancel_data = cancel_data.sort_values("count", ascending=False)

# Step 4: Plot
plt.figure(figsize=(12,6))

sns.barplot(
    data=cancel_data,
    x="count",
    y="reason",
    hue="reason",
    palette="Set1",
    legend=False
)

# Add percentage labels
for i, row in cancel_data.iterrows():
    plt.text(
        row["count"],
        i,
        f"{row['percentage']:.1f}%",
        va='center',
        fontweight="bold"
    )

plt.title("Cancellation Reasons Distribution")
plt.xlabel("Number of Cancelled Orders")
plt.ylabel("Reason")

plt.grid(axis='x', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/15_cancellation_reasons.png")
plt.clf()

print("✅ ALL 15 EDA INSIGHTS GENERATED SUCCESSFULLY")
