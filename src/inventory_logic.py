"""
inventory_logic.py
==================
Smart Inventory Replenishment Dashboard — Inventory Replenishment Logic
Converts demand forecasts into actionable reorder recommendations.

Input  : data/processed/cleaned_inventory_sales.csv
         data/processed/product_demand_forecast.csv
Output : data/processed/inventory_recommendations.csv

Key formulas used
─────────────────
  Safety Stock         = std_daily_demand × √lead_time_days
  Reorder Point        = avg_daily_demand × lead_time_days + safety_stock
  Suggested Reorder Qty = forecast_30d − current_stock + safety_stock
                         (floored at 0 — never suggest a negative order)

Business rationale
──────────────────
  Safety Stock  →  buffer against demand spikes and late deliveries
  Reorder Point →  the stock level that triggers a new order
  Reorder Qty   →  how many units to order so we cover 30 days + safety buffer
"""

import os
import sys
import numpy as np
import pandas as pd

# ─────────────────────────────────────────────
# 0.  FILE PATHS
# ─────────────────────────────────────────────
CLEANED_FILE    = os.path.join("data", "processed", "cleaned_inventory_sales.csv")
FORECAST_FILE   = os.path.join("data", "processed", "product_demand_forecast.csv")
OUTPUT_FILE     = os.path.join("data", "processed", "inventory_recommendations.csv")


# ─────────────────────────────────────────────
# 1.  LOAD INPUT FILES  (with error handling)
# ─────────────────────────────────────────────
print("=" * 62)
print("  STEP 1 — Loading input files")
print("=" * 62)

# Check both files exist before attempting to load them
for path in [CLEANED_FILE, FORECAST_FILE]:
    if not os.path.exists(path):
        script = ("data_cleaning.py"   if "cleaned"  in path
                  else "forecasting.py")
        print(f"\n[✗] ERROR: File not found → '{path}'")
        print(f"    Please run {script} first.")
        sys.exit(1)

# Load the cleaned sales data — we only need a few columns from it
cleaned_df = pd.read_csv(CLEANED_FILE, parse_dates=["date"])

# Load the forecast file — this is our main working table
fc = pd.read_csv(FORECAST_FILE)

print(f"[✓] Cleaned sales data   : {len(cleaned_df):,} rows")
print(f"[✓] Forecast data        : {len(fc)} products | {len(fc.columns)} columns")


# ─────────────────────────────────────────────
# 2.  CALCULATE SAFETY STOCK
#
#     Safety Stock = std_daily_demand × √(lead_time_days)
#
#     Why?  During the lead time (days between ordering and receiving stock),
#     demand can be higher than average.  The standard deviation captures
#     how much demand varies day-to-day, and √lead_time scales that
#     variability over the entire lead-time window.
#     A larger safety stock = more protection against stockouts,
#     but also higher holding costs — so we balance both.
# ─────────────────────────────────────────────
print("\n" + "=" * 62)
print("  STEP 2 — Calculating Safety Stock")
print("=" * 62)

fc["safety_stock"] = (
    fc["std_daily_demand"] * np.sqrt(fc["lead_time_days"])
).round(2)

# Safety stock must be a whole number of units (can't hold 0.4 of a product)
fc["safety_stock_units"] = np.ceil(fc["safety_stock"]).astype(int)

print("[✓] Safety stock calculated.")
print(f"    Average safety stock across products : "
      f"{fc['safety_stock_units'].mean():.1f} units")
print(f"    Range : {fc['safety_stock_units'].min()} – "
      f"{fc['safety_stock_units'].max()} units")


# ─────────────────────────────────────────────
# 3.  CALCULATE REORDER POINT
#
#     Reorder Point = avg_daily_demand × lead_time_days + safety_stock
#
#     Why?  When stock falls to this level, we place an order.
#     By the time the order arrives (lead_time_days later), we will have
#     consumed exactly avg_daily_demand × lead_time_days units.
#     The safety_stock is the buffer so we don't hit zero while waiting.
# ─────────────────────────────────────────────
print("\n" + "=" * 62)
print("  STEP 3 — Calculating Reorder Point")
print("=" * 62)

fc["reorder_point"] = (
    fc["avg_daily_demand"] * fc["lead_time_days"] + fc["safety_stock"]
).round(2)

fc["reorder_point_units"] = np.ceil(fc["reorder_point"]).astype(int)

print("[✓] Reorder points calculated.")
print(f"    Average reorder point : {fc['reorder_point_units'].mean():.1f} units")
print(f"    Range : {fc['reorder_point_units'].min()} – "
      f"{fc['reorder_point_units'].max()} units")


# ─────────────────────────────────────────────
# 4.  CALCULATE SUGGESTED REORDER QUANTITY
#
#     Suggested Qty = forecast_next_30d − current_stock + safety_stock_units
#
#     Why?  We want enough stock to cover 30 days of forecasted demand
#     plus maintain a safety buffer.  We subtract current stock because
#     we already have some on hand — no need to reorder what we have.
#     If the result is negative (we already have more than enough),
#     we set it to 0 — never suggest ordering when overstocked.
# ─────────────────────────────────────────────
print("\n" + "=" * 62)
print("  STEP 4 — Calculating Suggested Reorder Quantity")
print("=" * 62)

raw_qty = (
    fc["forecast_next_30d"]
    - fc["current_stock"]
    + fc["safety_stock_units"]
)

# Floor at 0 — a negative suggestion means we have surplus stock
fc["suggested_reorder_qty"] = raw_qty.clip(lower=0).round(0).astype(int)

# How many products need an actual order right now?
need_order = (fc["suggested_reorder_qty"] > 0).sum()
print(f"[✓] Reorder quantities calculated.")
print(f"    Products needing an order now : {need_order} / {len(fc)}")
print(f"    Largest single order          : "
      f"{fc['suggested_reorder_qty'].max():,} units  "
      f"({fc.loc[fc['suggested_reorder_qty'].idxmax(), 'product_name']})")


# ─────────────────────────────────────────────
# 5.  ASSIGN INVENTORY STATUS
#
#     Five mutually exclusive status labels — applied in priority order.
#     "Slow Moving" is checked first so that very low-demand products
#     don't get incorrectly flagged as Critical just because their
#     absolute stock numbers look low.
# ─────────────────────────────────────────────
print("\n" + "=" * 62)
print("  STEP 5 — Assigning Inventory Status")
print("=" * 62)

# Identify the slow-moving threshold:
# products whose average daily demand sits in the bottom 20%
slow_moving_threshold = fc["avg_daily_demand"].quantile(0.20)
print(f"    Slow-moving threshold (bottom 20%) : "
      f"≤ {slow_moving_threshold:.2f} units/day")

def assign_status(row: pd.Series) -> str:
    """
    Return an inventory status string for a single product row.

    Priority order (evaluated top-to-bottom — first match wins):
      1. Slow Moving   — demand is very low regardless of stock level
      2. Critical      — stock is at or below safety buffer
      3. Reorder Soon  — stock is above safety but below reorder point
      4. Overstocked   — stock is more than 1.5× the 30-day forecast
      5. Healthy       — everything else
    """
    avg_demand    = row["avg_daily_demand"]
    stock         = row["current_stock"]
    safety        = row["safety_stock_units"]
    rop           = row["reorder_point_units"]
    forecast_30d  = row["forecast_next_30d"]

    # Rule 1 — Slow Moving
    # Business meaning: this product barely sells; tie up less capital in it
    if avg_demand <= slow_moving_threshold:
        return "Slow Moving"

    # Rule 2 — Critical Stock
    # Business meaning: stock is dangerously low — we may stockout before
    # a reorder can arrive; act immediately
    if stock <= safety:
        return "Critical Stock"

    # Rule 3 — Reorder Soon
    # Business meaning: stock is above the safety buffer but an order
    # should be placed now so it arrives before we hit critical levels
    if stock <= rop:
        return "Reorder Soon"

    # Rule 4 — Overstocked
    # Business meaning: we have more than 1.5× the next 30-day demand on
    # hand — holding costs are accumulating unnecessarily
    if forecast_30d > 0 and stock > forecast_30d * 1.5:
        return "Overstocked"

    # Rule 5 — Healthy Stock (default)
    return "Healthy Stock"

fc["inventory_status"] = fc.apply(assign_status, axis=1)

# Print status distribution
status_counts = fc["inventory_status"].value_counts()
print("\n[✓] Inventory status assigned:")
for status in ["Critical Stock", "Reorder Soon", "Healthy Stock",
               "Overstocked", "Slow Moving"]:
    count = status_counts.get(status, 0)
    bar   = "█" * count
    print(f"    {status:<18} {count:>3}  {bar}")


# ─────────────────────────────────────────────
# 6.  ASSIGN REORDER PRIORITY
#
#     High   → Critical Stock OR very large reorder quantity needed
#     Medium → Reorder Soon
#     Low    → Healthy, Overstocked, or Slow Moving
#
#     "Large reorder quantity" is defined as above the 75th percentile
#     of all non-zero reorder quantities — those products need significant
#     procurement action even if they aren't technically critical yet.
# ─────────────────────────────────────────────
print("\n" + "=" * 62)
print("  STEP 6 — Assigning Reorder Priority")
print("=" * 62)

# Compute the "large order" threshold on products that actually need ordering
nonzero_orders = fc.loc[fc["suggested_reorder_qty"] > 0, "suggested_reorder_qty"]
large_order_threshold = (
    nonzero_orders.quantile(0.75) if len(nonzero_orders) > 0 else float("inf")
)
print(f"    Large-order threshold (75th pct) : "
      f"≥ {large_order_threshold:.0f} units")

def assign_priority(row: pd.Series) -> str:
    """
    Return 'High', 'Medium', or 'Low' reorder priority.
    """
    status = row["inventory_status"]
    qty    = row["suggested_reorder_qty"]

    # High priority: critical situations or large orders needed now
    if status == "Critical Stock" or qty >= large_order_threshold:
        return "High"

    # Medium priority: not critical yet, but order should go out soon
    if status == "Reorder Soon":
        return "Medium"

    # Low priority: stock situation is under control
    return "Low"

fc["reorder_priority"] = fc.apply(assign_priority, axis=1)

priority_counts = fc["reorder_priority"].value_counts()
print("[✓] Reorder priority assigned:")
for level in ["High", "Medium", "Low"]:
    count = priority_counts.get(level, 0)
    bar   = "█" * count
    print(f"    {level:<8} {count:>3}  {bar}")


# ─────────────────────────────────────────────
# 7.  CALCULATE ESTIMATED REORDER COST
#     Provides a financial summary for each recommendation.
#     estimated_order_value = suggested_reorder_qty × unit_cost
# ─────────────────────────────────────────────
fc["estimated_order_value"] = (
    fc["suggested_reorder_qty"] * fc["unit_cost"]
).round(2)

total_order_value = fc["estimated_order_value"].sum()


# ─────────────────────────────────────────────
# 8.  SELECT & ORDER FINAL COLUMNS
# ─────────────────────────────────────────────
output_cols = [
    # Identity
    "product_id", "product_name", "category", "supplier"
    if "supplier" in fc.columns else None,
    # Pricing
    "unit_price", "unit_cost",
    # Inventory parameters
    "lead_time_days", "reorder_cost", "holding_cost_per_unit",
    # Current position
    "current_stock",
    # Demand stats
    "avg_daily_demand", "std_daily_demand",
    # Forecast outputs
    "forecast_daily_demand", "forecast_next_7d",
    "forecast_next_14d", "forecast_next_30d",
    # Calculated thresholds
    "safety_stock_units", "reorder_point_units",
    # Recommendation
    "suggested_reorder_qty", "estimated_order_value",
    # Classification
    "inventory_status", "reorder_priority",
    # Extra context
    "days_of_stock_remaining", "demand_variability",
    "stockout_risk", "reference_date",
]

# Keep only columns that actually exist in the dataframe
output_cols = [c for c in output_cols if c and c in fc.columns]
output_df = fc[output_cols].copy()

# Sort: High priority first, then by reorder quantity descending
priority_order = {"High": 0, "Medium": 1, "Low": 2}
output_df["_priority_sort"] = output_df["reorder_priority"].map(priority_order)
output_df.sort_values(
    ["_priority_sort", "suggested_reorder_qty"],
    ascending=[True, False],
    inplace=True
)
output_df.drop(columns=["_priority_sort"], inplace=True)
output_df.reset_index(drop=True, inplace=True)


# ─────────────────────────────────────────────
# 9.  SAVE OUTPUT
# ─────────────────────────────────────────────
print("\n" + "=" * 62)
print("  STEP 7 — Saving recommendations")
print("=" * 62)

output_df.to_csv(OUTPUT_FILE, index=False)
print(f"[✓] Recommendations saved → {OUTPUT_FILE}")
print(f"    Rows    : {len(output_df)}")
print(f"    Columns : {len(output_df.columns)}")


# ─────────────────────────────────────────────
# 10.  SUMMARY REPORT
# ─────────────────────────────────────────────
print("\n" + "=" * 62)
print("  INVENTORY STATUS SUMMARY")
print("=" * 62)
for status in ["Critical Stock", "Reorder Soon", "Healthy Stock",
               "Overstocked", "Slow Moving"]:
    count = status_counts.get(status, 0)
    pct   = (count / len(output_df)) * 100
    print(f"  {status:<20} : {count:>3} products  ({pct:.0f}%)")

print(f"\n  Total estimated order value : £{total_order_value:,.2f}")
print(f"  Products needing an order   : {need_order} / {len(output_df)}")

# ── Top 10 reorder recommendations ─────────────────────────────────────
print("\n" + "=" * 62)
print("  TOP 10 REORDER RECOMMENDATIONS")
print("=" * 62)

top10 = output_df[output_df["suggested_reorder_qty"] > 0].head(10)

print(f"\n  {'#':<3} {'Product':<28} {'Status':<16} {'Pri':<7} "
      f"{'Stock':>6} {'ROP':>6} {'Ord Qty':>8} {'Est £':>10}")
print(f"  {'-'*3} {'-'*28} {'-'*16} {'-'*7} "
      f"{'-'*6} {'-'*6} {'-'*8} {'-'*10}")

for rank, (_, row) in enumerate(top10.iterrows(), start=1):
    print(
        f"  {rank:<3} "
        f"{row['product_name']:<28} "
        f"{row['inventory_status']:<16} "
        f"{row['reorder_priority']:<7} "
        f"{row['current_stock']:>6,} "
        f"{row['reorder_point_units']:>6,} "
        f"{row['suggested_reorder_qty']:>8,} "
        f"£{row['estimated_order_value']:>9,.2f}"
    )

# ── Products that are overstocked ──────────────────────────────────────
overstocked = output_df[output_df["inventory_status"] == "Overstocked"]
if not overstocked.empty:
    print("\n" + "=" * 62)
    print("  OVERSTOCKED PRODUCTS — Consider reducing future orders")
    print("=" * 62)
    for _, row in overstocked.iterrows():
        excess = int(row["current_stock"] - row["forecast_next_30d"])
        print(f"  • {row['product_name']:<30}  "
              f"Stock: {row['current_stock']:>5,}  "
              f"30d forecast: {int(row['forecast_next_30d']):>5,}  "
              f"Excess: {excess:>5,} units")

# ── Slow moving products ───────────────────────────────────────────────
slow = output_df[output_df["inventory_status"] == "Slow Moving"]
if not slow.empty:
    print("\n" + "=" * 62)
    print("  SLOW MOVING PRODUCTS — Review stocking policy")
    print("=" * 62)
    for _, row in slow.iterrows():
        print(f"  • {row['product_name']:<30}  "
              f"Avg/day: {row['avg_daily_demand']:>6.1f}  "
              f"Stock: {row['current_stock']:>5,}  "
              f"Days cover: {row['days_of_stock_remaining']:>6.1f}")

print("\n[✓] inventory_logic.py completed successfully.")