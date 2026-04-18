import streamlit as st
import pandas as pd

st.set_page_config(page_title="Food Dashboard", layout="wide")


st.markdown("""
<style>
.metric-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: white;
}
.metric-title {
    font-size: 16px;
    color: #9CA3AF;
}
.metric-value {
    font-size: 28px;
    font-weight: bold;
}
.section {
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

st.title("Food Delivery Dashboard")


@st.cache_data
def load_data():
    return pd.read_csv("featured_online_food_delivery.csv")  # change this

df = load_data()


df = df.dropna(subset=[
    "restaurant_name",
    "order_value",
    "delivery_rating",
    "delivery_time_min",
    "order_status",
    "profit"
])

df = df[df["order_value"] > 0]

df["is_cancelled"] = (df["order_status"] == "Cancelled").astype(int)


total_orders = len(df)
total_revenue = df["order_value"].sum()
total_profit = df["profit"].sum()

profit_margin = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0
cancellation_rate = (df["is_cancelled"].sum() / total_orders) * 100 if total_orders > 0 else 0
avg_rating = df["delivery_rating"].mean()
avg_delivery_time = df["delivery_time_min"].mean()


st.subheader("Business Overview")

col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"""
<div class="metric-card">
<div class="metric-title">Total Orders</div>
<div class="metric-value">{total_orders:,}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="metric-card">
<div class="metric-title">Revenue</div>
<div class="metric-value">₹ {total_revenue:,.0f}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="metric-card">
<div class="metric-title">Profit Margin</div>
<div class="metric-value">{profit_margin:.2f}%</div>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="metric-card">
<div class="metric-title">Cancellation Rate</div>
<div class="metric-value">{cancellation_rate:.2f}%</div>
</div>
""", unsafe_allow_html=True)

col5, col6 = st.columns(2)

col5.markdown(f"""
<div class="metric-card">
<div class="metric-title">Avg Rating</div>
<div class="metric-value">{avg_rating:.2f}</div>
</div>
""", unsafe_allow_html=True)

col6.markdown(f"""
<div class="metric-card">
<div class="metric-title">Avg Delivery Time</div>
<div class="metric-value">{avg_delivery_time:.1f} mins</div>
</div>
""", unsafe_allow_html=True)


st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("Top Restaurants")

restaurant_perf = (
    df.groupby("restaurant_name")
    .agg(avg_rating=("delivery_rating", "mean"),
         total_orders=("order_id", "count"))
    .reset_index()
)

restaurant_perf = restaurant_perf[restaurant_perf["total_orders"] >= 5]

top_restaurants = restaurant_perf.sort_values(
    ["avg_rating", "total_orders"], ascending=[False, False]
).head(10)

st.dataframe(top_restaurants, width="stretch")


st.subheader("High Cancellation Restaurants")

cancel_perf = (
    df.groupby("restaurant_name")
    .agg(cancel_rate=("is_cancelled", "mean"),
         total_orders=("order_id", "count"))
    .reset_index()
)

cancel_perf["cancel_rate"] = cancel_perf["cancel_rate"] * 100
cancel_perf = cancel_perf[cancel_perf["total_orders"] >= 5]

worst_restaurants = cancel_perf.sort_values(
    ["cancel_rate", "total_orders"], ascending=[False, False]
).head(10)

st.dataframe(worst_restaurants, width="stretch")


if "discount" in df.columns:

    st.subheader(" Discount Performance")

    df["discount_bin"] = pd.cut(
        df["discount"],
        bins=[0,10,20,30,40,50,100],
        labels=["0-10%","10-20%","20-30%","30-40%","40-50%","50%+"]
    )

    discount_analysis = (
        df.groupby("discount_bin", observed=True)
        .agg(avg_profit=("profit","mean"),
             total_orders=("order_id","count"))
        .reset_index()
    )

    discount_analysis = discount_analysis[discount_analysis["total_orders"] >= 5]

    st.dataframe(discount_analysis, width="stretch")


st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("Insights")

best_restaurant = top_restaurants.iloc[0]["restaurant_name"] if not top_restaurants.empty else "N/A"
worst_restaurant = worst_restaurants.iloc[0]["restaurant_name"] if not worst_restaurants.empty else "N/A"

if "discount" in df.columns and not discount_analysis.empty:
    best_discount = discount_analysis.loc[
        discount_analysis["avg_profit"].idxmax()
    ]["discount_bin"]
else:
    best_discount = "N/A"

st.success(f"Top performing restaurant: {best_restaurant}")
st.error(f"Highest cancellation: {worst_restaurant}")
st.info(f"Best discount range: {best_discount}")