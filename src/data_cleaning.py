"""
data_cleaning.py
================
Smart Inventory Replenishment Dashboard — Data Cleaning & Feature Engineering
Loads the raw synthetic retail dataset, validates it, engineers new columns,
and saves a clean version ready for analysis and forecasting.

Input  : data/raw/retail_inventory_sales.csv
Output : data/processed/cleaned_inventory_sales.csv
"""

import os
import sys
import pandas as pd

# ─────────────────────────────────────────────
# 0.  FILE PATHS
# ─────────────────────────────────────────────
INPUT_FILE  = os.path.join("data", "raw",       "retail_inventory_sales.csv")
OUTPUT_DIR  = os.path.join("data", "processed")
OUTPUT_FILE = os.path.join(OUTPUT_DIR,           "cleaned_inventory_sales.csv")

# Create the output folder if it doesn't exist yet
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# 1.  LOAD RAW DATA  (with error handling)
# ─────────────────────────────────────────────
print("=" * 60)
print("  STEP 1 — Loading raw data")
print("=" * 60)

# Check that the source file actually exists before trying to open it
if not os.path.exists(INPUT_FILE):
    print(f"\n[✗] ERROR: Raw data file not found at '{INPUT_FILE}'")
    print("    Please run data_generator.py first to create the dataset.")
    sys.exit(1)   # Stop the script with a non-zero exit code (signals failure)

# Load the CSV into a pandas DataFrame
df = pd.read_csv(INPUT_FILE)

print(f"[✓] File loaded successfully: {INPUT_FILE}")
print(f"    Rows    : {len(df):,}")
print(f"    Columns : {len(df.columns)}")
print(f"    Columns : {list(df.columns)}")


# ─────────────────────────────────────────────
# 2.  CHECK FOR MISSING VALUES
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 2 — Checking for missing values")
print("=" * 60)

# Count missing (NaN) values in every column
missing_counts = df.isnull().sum()

# Filter to only columns that actually have missing values
missing_found = missing_counts[missing_counts > 0]

if missing_found.empty:
    print("[✓] No missing values found — dataset is complete.")
    total_missing = 0
else:
    print(f"[!] Missing values detected in {len(missing_found)} column(s):")
    for col, count in missing_found.items():
        pct = (count / len(df)) * 100
        print(f"    {col:<30} {count:>6,} missing  ({pct:.2f}%)")

    # Strategy: drop rows where critical columns are missing
    critical_cols = ["date", "product_id", "units_sold",
                     "unit_price", "unit_cost", "sales_revenue"]
    before = len(df)
    df.dropna(subset=critical_cols, inplace=True)
    dropped = before - len(df)

    if dropped > 0:
        print(f"    → Dropped {dropped:,} rows with missing critical values.")

    # For non-critical numeric columns, fill missing with column median
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            print(f"    → Filled missing '{col}' with median ({median_val}).")

    total_missing = missing_found.sum()
    print(f"[✓] Missing value handling complete.")


# ─────────────────────────────────────────────
# 3.  CHECK FOR DUPLICATE ROWS
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 3 — Checking for duplicate rows")
print("=" * 60)

# A "true" duplicate means the same date + product + store combination
# appears more than once (which shouldn't happen in our generated data)
duplicate_mask  = df.duplicated()           # True for every duplicate row
total_duplicates = duplicate_mask.sum()

if total_duplicates == 0:
    print("[✓] No duplicate rows found.")
else:
    print(f"[!] Found {total_duplicates:,} duplicate row(s) — removing them.")
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(f"[✓] Duplicates removed. Rows remaining: {len(df):,}")


# ─────────────────────────────────────────────
# 4.  CONVERT DATE COLUMN TO DATETIME
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 4 — Converting 'date' column to datetime")
print("=" * 60)

# pd.to_datetime() turns the string "2023-01-01" into a proper date object
# errors='coerce' turns any unparseable values into NaT (Not a Time) instead
# of crashing — we then drop those rows
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Drop any rows where the date couldn't be parsed
bad_dates = df["date"].isnull().sum()
if bad_dates > 0:
    print(f"[!] {bad_dates:,} rows had unparseable dates — dropping them.")
    df.dropna(subset=["date"], inplace=True)

print(f"[✓] Date column converted to datetime.")
print(f"    dtype : {df['date'].dtype}")
print(f"    Range : {df['date'].min().date()} → {df['date'].max().date()}")


# ─────────────────────────────────────────────
# 5.  CREATE DATE-RELATED FEATURE COLUMNS
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 5 — Engineering date-related columns")
print("=" * 60)

# year  — useful for year-over-year comparisons
df["year"] = df["date"].dt.year

# month — numeric month (1–12), good for sorting and grouping
df["month"] = df["date"].dt.month

# month_name — human-readable name like "January", "February", etc.
df["month_name"] = df["date"].dt.strftime("%B")

# week  — ISO week number (1–53), helpful for weekly aggregation
df["week"] = df["date"].dt.isocalendar().week.astype(int)

# day_of_week — name of the weekday (Monday, Tuesday, …)
df["day_of_week"] = df["date"].dt.strftime("%A")

print("[✓] New date columns created:")
print("    year, month, month_name, week, day_of_week")
print(f"    Sample row:\n{df[['date','year','month','month_name','week','day_of_week']].iloc[0].to_string()}")


# ─────────────────────────────────────────────
# 6.  CREATE PROFIT COLUMN
#     profit = sales_revenue - (units_sold × unit_cost)
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 6 — Calculating profit")
print("=" * 60)

# Total cost of goods sold for the day
df["cogs"] = df["units_sold"] * df["unit_cost"]   # Cost Of Goods Sold

# Profit = what we earned minus what we paid for the goods
df["profit"] = df["sales_revenue"] - df["cogs"]

# Round to 2 decimal places to avoid floating-point noise (e.g. 0.999999...)
df["profit"] = df["profit"].round(2)

print(f"[✓] 'profit' column created.")
print(f"    Total profit across dataset : £{df['profit'].sum():,.2f}")
print(f"    Min profit on a single row  : £{df['profit'].min():,.2f}")
print(f"    Max profit on a single row  : £{df['profit'].max():,.2f}")


# ─────────────────────────────────────────────
# 7.  CREATE PROFIT MARGIN COLUMN
#     profit_margin = profit / sales_revenue  (as a percentage)
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 7 — Calculating profit margin")
print("=" * 60)

# Avoid division by zero: where sales_revenue is 0, margin is also 0
df["profit_margin"] = df.apply(
    lambda row: round((row["profit"] / row["sales_revenue"]) * 100, 2)
    if row["sales_revenue"] > 0 else 0.0,
    axis=1   # apply row by row
)

avg_margin = df["profit_margin"].mean()
print(f"[✓] 'profit_margin' column created (percentage, e.g. 45.00 = 45%).")
print(f"    Average profit margin : {avg_margin:.2f}%")


# ─────────────────────────────────────────────
# 8.  CREATE REVENUE PER UNIT COLUMN
#     revenue_per_unit = sales_revenue / units_sold
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 8 — Calculating revenue per unit")
print("=" * 60)

# This should equal unit_price for most rows; slight differences can flag
# pricing anomalies or data entry errors in a real dataset
df["revenue_per_unit"] = df.apply(
    lambda row: round(row["sales_revenue"] / row["units_sold"], 4)
    if row["units_sold"] > 0 else 0.0,
    axis=1
)

print(f"[✓] 'revenue_per_unit' column created.")
print(f"    Mean revenue per unit : £{df['revenue_per_unit'].mean():.4f}")

# Quick sanity check: flag rows where revenue_per_unit deviates from unit_price
tolerance = 0.01   # allow 1 penny rounding difference
mismatch = df[abs(df["revenue_per_unit"] - df["unit_price"]) > tolerance]
if mismatch.empty:
    print("    Sanity check passed: revenue_per_unit matches unit_price ✓")
else:
    print(f"    [!] {len(mismatch):,} rows have revenue_per_unit ≠ unit_price "
          f"(possible zero-sales days — expected behaviour).")


# ─────────────────────────────────────────────
# 9.  ENFORCE CORRECT DATA TYPES ON NUMERIC COLUMNS
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 9 — Enforcing correct data types")
print("=" * 60)

# Define which columns should be which dtype
dtype_map = {
    # Integer columns
    "units_sold"            : "int64",
    "current_stock"         : "int64",
    "lead_time_days"        : "int64",
    "year"                  : "int64",
    "month"                 : "int64",
    "week"                  : "int64",
    # Float columns
    "unit_price"            : "float64",
    "unit_cost"             : "float64",
    "sales_revenue"         : "float64",
    "reorder_cost"          : "float64",
    "holding_cost_per_unit" : "float64",
    "cogs"                  : "float64",
    "profit"                : "float64",
    "profit_margin"         : "float64",
    "revenue_per_unit"      : "float64",
}

for col, target_dtype in dtype_map.items():
    if col in df.columns:
        try:
            df[col] = df[col].astype(target_dtype)
        except ValueError as e:
            print(f"    [!] Could not convert '{col}' to {target_dtype}: {e}")

# String / categorical columns — strip whitespace to avoid silent mismatches
string_cols = ["product_id", "product_name", "category",
               "supplier", "region", "store_id",
               "month_name", "day_of_week"]

for col in string_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

print("[✓] Data types enforced.")
print("\n  Column dtypes after cleaning:")
for col in df.columns:
    print(f"    {col:<30} {str(df[col].dtype)}")


# ─────────────────────────────────────────────
# 10.  DROP THE INTERMEDIATE 'cogs' HELPER COLUMN
#      (it was only needed to compute profit; not required downstream)
# ─────────────────────────────────────────────
df.drop(columns=["cogs"], inplace=True)


# ─────────────────────────────────────────────
# 11.  FINAL COLUMN ORDER  — keep things tidy
# ─────────────────────────────────────────────
desired_order = [
    # Time
    "date", "year", "month", "month_name", "week", "day_of_week",
    # Product identity
    "product_id", "product_name", "category", "supplier",
    # Location
    "store_id", "region",
    # Demand
    "units_sold", "current_stock", "lead_time_days",
    # Pricing
    "unit_price", "unit_cost",
    # Financials
    "sales_revenue", "revenue_per_unit",
    "profit", "profit_margin",
    # Cost parameters
    "reorder_cost", "holding_cost_per_unit",
]

# Only include columns that actually exist (defensive programming)
final_cols = [c for c in desired_order if c in df.columns]
df = df[final_cols]


# ─────────────────────────────────────────────
# 12.  SAVE CLEANED FILE
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  STEP 10 — Saving cleaned dataset")
print("=" * 60)

df.to_csv(OUTPUT_FILE, index=False)
print(f"[✓] Cleaned dataset saved → {OUTPUT_FILE}")


# ─────────────────────────────────────────────
# 13.  CLEANING SUMMARY REPORT
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  CLEANING SUMMARY")
print("=" * 60)
print(f"  Rows in cleaned dataset     : {len(df):,}")
print(f"  Columns in cleaned dataset  : {len(df.columns)}")
print(f"  Unique products             : {df['product_id'].nunique()}")
print(f"  Unique stores               : {df['store_id'].nunique()}")
print(f"  Unique regions              : {df['region'].nunique()}")
print(f"  Date range                  : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"  Missing values found        : {total_missing:,}")
print(f"  Duplicate rows found        : {total_duplicates:,}")
print(f"  Total revenue               : £{df['sales_revenue'].sum():,.2f}")
print(f"  Total profit                : £{df['profit'].sum():,.2f}")
print(f"  Overall profit margin       : {df['profit_margin'].mean():.2f}%")
print("=" * 60)

print("\n  Revenue & profit by category:")
cat_summary = (
    df.groupby("category")
      .agg(
          total_revenue = ("sales_revenue", "sum"),
          total_profit  = ("profit",        "sum"),
          avg_margin    = ("profit_margin", "mean"),
      )
      .sort_values("total_revenue", ascending=False)
)
print(f"  {'Category':<20} {'Revenue':>14} {'Profit':>14} {'Avg Margin':>12}")
print(f"  {'-'*20} {'-'*14} {'-'*14} {'-'*12}")
for cat, row in cat_summary.iterrows():
    print(f"  {cat:<20} £{row['total_revenue']:>12,.2f} "
          f"£{row['total_profit']:>12,.2f} "
          f"{row['avg_margin']:>10.2f}%")

print("\n[✓] data_cleaning.py completed successfully.")