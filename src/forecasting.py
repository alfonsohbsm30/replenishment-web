"""
forecasting.py
==============
Smart Inventory Replenishment Dashboard — Product-Level Demand Forecasting
Uses moving averages to estimate future demand per product.
Simple, transparent, and explainable — no black-box machine learning.

Input  : data/processed/cleaned_inventory_sales.csv
Output : data/processed/product_demand_forecast.csv

Forecasting logic summary
─────────────────────────
We use a weighted blend of three moving averages (7-day, 14-day, 30-day).
Recent windows get more weight because recent demand is a better predictor
of near-future demand than older history.

  forecast = (0.50 × 7-day avg) + (0.30 × 14-day avg) + (0.20 × 30-day avg)

When history is shorter than a window, we fall back to the overall product
average so every product always gets a usable forecast.
"""

import os
import sys
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# 0.  FILE PATHS
# ─────────────────────────────────────────────
INPUT_FILE  = os.path.join("data", "processed", "cleaned_inventory_sales.csv")
OUTPUT_FILE = os.path.join("data", "processed", "product_demand_forecast.csv")


# ─────────────────────────────────────────────
# 1.  LOAD CLEANED DATA
# ─────────────────────────────────────────────
print("=" * 60)
print("  STEP 1 — Loading cleaned dataset")
print("=" * 60)

if not os.path.exists(INPUT_FILE):
    print(f"\n[✗] ERROR: Cleaned data file not found at '{INPUT_FILE}'")
    print("    Please run data_cleaning.py first.")
    sys.exit(1)

df = pd.read_csv(INPUT_FILE, parse_dates=["date"])

print(f"[✓] Loaded: {len(df):,} rows | {df['product_id'].nunique()} products")
print(f"    Date range: {df['date'].min().date()} → {df['date'].max().date()}")


# ─────────────────────────────────────────────
# 2.  AGGREGATE DAILY SALES PER PRODUCT
#     Sum units_sold across all stores for each product on each date.
#     This gives us total daily demand per product nationally.
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 2 — Aggregating daily sales per product")
print("=" * 60)

# Group by date + product, summing sales across all stores/regions
daily = (
    df.groupby(["date", "product_id", "product_name", "category"])
      .agg(
          units_sold    = ("units_sold",    "sum"),   # total units across stores
          current_stock = ("current_stock", "mean"),  # average stock level
          lead_time_days= ("lead_time_days","first"),  # same for all stores
          unit_price    = ("unit_price",    "first"),
          unit_cost     = ("unit_cost",     "first"),
          reorder_cost  = ("reorder_cost",  "first"),
          holding_cost_per_unit = ("holding_cost_per_unit", "first"),
      )
      .reset_index()
      .sort_values(["product_id", "date"])
)

print(f"[✓] Daily aggregation complete.")
print(f"    Unique product-date rows : {len(daily):,}")

# The reference date is the last day in the dataset
# — we forecast *forward* from this point
REFERENCE_DATE = daily["date"].max()
print(f"    Reference date (T)       : {REFERENCE_DATE.date()}  ← forecasting from here")


# ─────────────────────────────────────────────
# 3.  BUILD PRODUCT-LEVEL SUMMARY
#     One row per product with demand statistics and forecasts.
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 3 — Calculating demand statistics per product")
print("=" * 60)

records = []   # will hold one dict per product

for product_id, group in daily.groupby("product_id"):

    # Sort by date — essential for rolling/recent window calculations
    g = group.sort_values("date").reset_index(drop=True)

    # ── Static product attributes ──────────────────────────────────────
    product_name   = g["product_name"].iloc[0]
    category       = g["category"].iloc[0]
    unit_price     = g["unit_price"].iloc[0]
    unit_cost      = g["unit_cost"].iloc[0]
    lead_time_days = int(g["lead_time_days"].iloc[0])
    reorder_cost   = g["reorder_cost"].iloc[0]
    holding_cost   = g["holding_cost_per_unit"].iloc[0]

    # ── Current stock: use the most recent day's average stock ─────────
    current_stock  = round(g["current_stock"].iloc[-1])

    # ── How many days of history do we have? ───────────────────────────
    n_days = len(g)

    # ── Overall average daily demand ───────────────────────────────────
    # Business meaning: if nothing else were known, sell this many units/day
    avg_daily_demand = g["units_sold"].mean()
    std_daily_demand = g["units_sold"].std()   # variability / demand uncertainty

    # ── Helper: safe moving average with fallback ───────────────────────
    # If the product has fewer days than the window, we fall back to the
    # overall average so the forecast is still meaningful.
    def recent_avg(window: int) -> float:
        """Return mean units_sold over the last `window` days of history.
        Falls back to overall average when history < window."""
        if n_days >= window:
            return g["units_sold"].tail(window).mean()
        else:
            # Not enough history — use whatever we have
            return avg_daily_demand

    avg_7d  = recent_avg(7)    # last  7 days average
    avg_14d = recent_avg(14)   # last 14 days average
    avg_30d = recent_avg(30)   # last 30 days average

    # ── Weighted forecast (blended moving average) ─────────────────────
    # Business logic: recent demand (7-day) is weighted most heavily
    # because it captures the current trend. Older windows provide
    # stability against one-off spikes.
    #
    #   Weight breakdown:
    #     7-day  → 50%  (most recent, highest relevance)
    #    14-day  → 30%  (medium-term trend)
    #    30-day  → 20%  (longer-term baseline)
    #
    # This is called an "exponentially-inspired weighted moving average"
    # and is widely used in retail replenishment planning.
    forecast_daily = (0.50 * avg_7d) + (0.30 * avg_14d) + (0.20 * avg_30d)

    # Total expected demand over each planning horizon
    forecast_7d  = round(forecast_daily * 7,  1)
    forecast_14d = round(forecast_daily * 14, 1)
    forecast_30d = round(forecast_daily * 30, 1)

    # ── Demand variability classification ──────────────────────────────
    # Coefficient of Variation (CV) = std / mean
    # A high CV means demand is erratic → need more safety stock.
    # CV < 0.3 → stable demand
    # CV 0.3–0.6 → moderate variability
    # CV > 0.6 → highly variable / erratic
    if avg_daily_demand > 0:
        cv = std_daily_demand / avg_daily_demand
        if cv < 0.3:
            demand_variability = "Stable"
        elif cv < 0.6:
            demand_variability = "Moderate"
        else:
            demand_variability = "Erratic"
    else:
        cv = 0.0
        demand_variability = "No Demand"

    # ── Days of stock remaining ─────────────────────────────────────────
    # Business meaning: at the current forecast rate, how many days until
    # we run out of stock? Critical for spotting imminent stockouts.
    if forecast_daily > 0:
        days_of_stock = round(current_stock / forecast_daily, 1)
    else:
        days_of_stock = 999.0   # effectively infinite (no demand)

    # ── Stockout risk flag ──────────────────────────────────────────────
    # If days_of_stock is less than or equal to the lead time, we will
    # likely run out before a new order can arrive — that is a HIGH risk.
    if days_of_stock <= lead_time_days:
        stockout_risk = "HIGH"
    elif days_of_stock <= lead_time_days * 2:
        stockout_risk = "MEDIUM"
    else:
        stockout_risk = "LOW"

    # ── Assemble the record ─────────────────────────────────────────────
    records.append({
        "product_id"            : product_id,
        "product_name"          : product_name,
        "category"              : category,
        "unit_price"            : round(unit_price,  2),
        "unit_cost"             : round(unit_cost,   2),
        "lead_time_days"        : lead_time_days,
        "reorder_cost"          : round(reorder_cost, 2),
        "holding_cost_per_unit" : round(holding_cost, 4),
        "current_stock"         : int(current_stock),
        "history_days"          : n_days,
        # Demand statistics
        "avg_daily_demand"      : round(avg_daily_demand, 2),
        "std_daily_demand"      : round(std_daily_demand,  2),
        "cv"                    : round(cv, 4),
        "demand_variability"    : demand_variability,
        # Recent moving averages (daily)
        "avg_demand_last_7d"    : round(avg_7d,  2),
        "avg_demand_last_14d"   : round(avg_14d, 2),
        "avg_demand_last_30d"   : round(avg_30d, 2),
        # Forecasted daily rate
        "forecast_daily_demand" : round(forecast_daily, 2),
        # Forecasted totals per horizon
        "forecast_next_7d"      : forecast_7d,
        "forecast_next_14d"     : forecast_14d,
        "forecast_next_30d"     : forecast_30d,
        # Inventory health
        "days_of_stock_remaining": days_of_stock,
        "stockout_risk"          : stockout_risk,
        # Metadata
        "reference_date"         : REFERENCE_DATE.date(),
    })

print(f"[✓] Demand statistics calculated for {len(records)} products.")


# ─────────────────────────────────────────────
# 4.  BUILD FINAL DATAFRAME & SORT
# ─────────────────────────────────────────────
forecast_df = pd.DataFrame(records)

# Sort by forecasted 30-day demand descending — highest-demand products first
forecast_df.sort_values("forecast_next_30d", ascending=False, inplace=True)
forecast_df.reset_index(drop=True, inplace=True)


# ─────────────────────────────────────────────
# 5.  SAVE OUTPUT
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 4 — Saving forecast output")
print("=" * 60)

forecast_df.to_csv(OUTPUT_FILE, index=False)
print(f"[✓] Forecast saved → {OUTPUT_FILE}")
print(f"    Rows    : {len(forecast_df)}")
print(f"    Columns : {len(forecast_df.columns)}")


# ─────────────────────────────────────────────
# 6.  SUMMARY REPORT — TOP 10 BY 30-DAY FORECAST
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  FORECAST SUMMARY — Top 10 Products by 30-Day Demand")
print("=" * 60)

top10 = forecast_df.head(10)

# Header
print(f"\n  {'#':<3} {'Product':<30} {'Cat':<14} "
      f"{'Avg/Day':>8} {'7d Fcast':>9} {'14d Fcast':>10} "
      f"{'30d Fcast':>10} {'Stock':>7} {'Risk':<8}")
print(f"  {'-'*3} {'-'*30} {'-'*14} "
      f"{'-'*8} {'-'*9} {'-'*10} {'-'*10} {'-'*7} {'-'*8}")

for rank, (_, row) in enumerate(top10.iterrows(), start=1):
    print(
        f"  {rank:<3} "
        f"{row['product_name']:<30} "
        f"{row['category']:<14} "
        f"{row['forecast_daily_demand']:>8.1f} "
        f"{row['forecast_next_7d']:>9.0f} "
        f"{row['forecast_next_14d']:>10.0f} "
        f"{row['forecast_next_30d']:>10.0f} "
        f"{row['current_stock']:>7,} "
        f"{row['stockout_risk']:<8}"
    )

# ── Stockout risk breakdown ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STOCKOUT RISK BREAKDOWN (all products)")
print("=" * 60)
risk_counts = forecast_df["stockout_risk"].value_counts()
for level in ["HIGH", "MEDIUM", "LOW"]:
    count = risk_counts.get(level, 0)
    bar   = "█" * count
    print(f"  {level:<8} {count:>3} products  {bar}")

# ── Demand variability breakdown ────────────────────────────────────────
print("\n" + "=" * 60)
print("  DEMAND VARIABILITY BREAKDOWN (all products)")
print("=" * 60)
var_counts = forecast_df["demand_variability"].value_counts()
for label in ["Stable", "Moderate", "Erratic", "No Demand"]:
    count = var_counts.get(label, 0)
    bar   = "█" * count
    print(f"  {label:<12} {count:>3} products  {bar}")

# ── HIGH-risk products ──────────────────────────────────────────────────
high_risk = forecast_df[forecast_df["stockout_risk"] == "HIGH"]
if not high_risk.empty:
    print("\n" + "=" * 60)
    print("  ⚠  HIGH STOCKOUT RISK — Immediate attention needed")
    print("=" * 60)
    for _, row in high_risk.iterrows():
        print(f"  • {row['product_name']:<30}  "
              f"Stock: {row['current_stock']:>5}  "
              f"Days left: {row['days_of_stock_remaining']:>5.1f}  "
              f"Lead time: {row['lead_time_days']} days")

print("\n[✓] forecasting.py completed successfully.")