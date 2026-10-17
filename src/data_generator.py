"""
data_generator.py
=================
Smart Inventory Replenishment Dashboard — Synthetic Dataset Generator
Generates 18 months of daily retail inventory/sales data for 40 products.

Author  : Portfolio Project
Purpose : Generate realistic synthetic retail data for demand forecasting
          and inventory replenishment analysis.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import date, timedelta

# ─────────────────────────────────────────────
# 0.  REPRODUCIBILITY & OUTPUT PATH
# ─────────────────────────────────────────────
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

OUTPUT_DIR  = os.path.join("data", "raw")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "retail_inventory_sales.csv")

# Create folder if it does not exist yet
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"[✓] Output directory ready: {OUTPUT_DIR}")


# ─────────────────────────────────────────────
# 1.  DATE RANGE  (18 months of daily data)
# ─────────────────────────────────────────────
START_DATE = date(2023, 1, 1)
END_DATE   = date(2024, 6, 30)   # ~18 months

all_dates = [START_DATE + timedelta(days=i)
             for i in range((END_DATE - START_DATE).days + 1)]

print(f"[✓] Date range: {START_DATE} → {END_DATE}  ({len(all_dates)} days)")


# ─────────────────────────────────────────────
# 2.  PRODUCT CATALOGUE  (40 products)
# ─────────────────────────────────────────────
# Each product is defined as a dictionary with its static attributes
# and a demand_profile that controls how units_sold is generated.

products = [

    # ── BEVERAGES (6 products) ───────────────────────────────────────────
    {"product_id": "P001", "product_name": "Sparkling Water 500ml",
     "category": "Beverages", "supplier": "AquaFresh Ltd",
     "unit_price": 1.50, "unit_cost": 0.60,
     "lead_time_days": 3, "reorder_cost": 50,  "holding_cost_per_unit": 0.05,
     "demand_profile": "fast", "base_demand": 80,  "seasonal": "summer"},

    {"product_id": "P002", "product_name": "Orange Juice 1L",
     "category": "Beverages", "supplier": "FruitVine Co",
     "unit_price": 2.20, "unit_cost": 1.10,
     "lead_time_days": 4, "reorder_cost": 60,  "holding_cost_per_unit": 0.08,
     "demand_profile": "fast", "base_demand": 70,  "seasonal": "none"},

    {"product_id": "P003", "product_name": "Energy Drink 250ml",
     "category": "Beverages", "supplier": "BoltDrinks Inc",
     "unit_price": 1.80, "unit_cost": 0.75,
     "lead_time_days": 5, "reorder_cost": 55,  "holding_cost_per_unit": 0.06,
     "demand_profile": "spike", "base_demand": 40,  "seasonal": "none"},

    {"product_id": "P004", "product_name": "Green Tea Bags 50pk",
     "category": "Beverages", "supplier": "TeaLeaf Traders",
     "unit_price": 3.50, "unit_cost": 1.80,
     "lead_time_days": 7, "reorder_cost": 70,  "holding_cost_per_unit": 0.10,
     "demand_profile": "slow",  "base_demand": 12,  "seasonal": "winter"},

    {"product_id": "P005", "product_name": "Coffee Capsules 10pk",
     "category": "Beverages", "supplier": "BeanBridge Ltd",
     "unit_price": 5.99, "unit_cost": 2.80,
     "lead_time_days": 6, "reorder_cost": 80,  "holding_cost_per_unit": 0.15,
     "demand_profile": "fast", "base_demand": 55,  "seasonal": "winter"},

    {"product_id": "P006", "product_name": "Coconut Water 330ml",
     "category": "Beverages", "supplier": "TropicSip Co",
     "unit_price": 2.00, "unit_cost": 0.90,
     "lead_time_days": 5, "reorder_cost": 55,  "holding_cost_per_unit": 0.07,
     "demand_profile": "slow",  "base_demand": 15,  "seasonal": "summer"},

    # ── SNACKS (7 products) ──────────────────────────────────────────────
    {"product_id": "P007", "product_name": "Potato Chips 150g",
     "category": "Snacks", "supplier": "CrunchCo Foods",
     "unit_price": 1.99, "unit_cost": 0.85,
     "lead_time_days": 4, "reorder_cost": 50,  "holding_cost_per_unit": 0.06,
     "demand_profile": "fast", "base_demand": 90,  "seasonal": "none"},

    {"product_id": "P008", "product_name": "Mixed Nuts 200g",
     "category": "Snacks", "supplier": "NutHouse Ltd",
     "unit_price": 4.50, "unit_cost": 2.20,
     "lead_time_days": 7, "reorder_cost": 75,  "holding_cost_per_unit": 0.12,
     "demand_profile": "slow",  "base_demand": 18,  "seasonal": "winter"},

    {"product_id": "P009", "product_name": "Chocolate Bar 50g",
     "category": "Snacks", "supplier": "ChocoWorld Inc",
     "unit_price": 1.20, "unit_cost": 0.55,
     "lead_time_days": 3, "reorder_cost": 45,  "holding_cost_per_unit": 0.04,
     "demand_profile": "fast", "base_demand": 100, "seasonal": "winter"},

    {"product_id": "P010", "product_name": "Rice Cakes 100g",
     "category": "Snacks", "supplier": "GrainCraft Foods",
     "unit_price": 1.60, "unit_cost": 0.70,
     "lead_time_days": 5, "reorder_cost": 50,  "holding_cost_per_unit": 0.05,
     "demand_profile": "slow",  "base_demand": 20,  "seasonal": "none"},

    {"product_id": "P011", "product_name": "Popcorn Microwave 3pk",
     "category": "Snacks", "supplier": "PopKing Ltd",
     "unit_price": 2.50, "unit_cost": 1.00,
     "lead_time_days": 4, "reorder_cost": 55,  "holding_cost_per_unit": 0.07,
     "demand_profile": "spike", "base_demand": 30,  "seasonal": "none"},

    {"product_id": "P012", "product_name": "Granola Bar 6pk",
     "category": "Snacks", "supplier": "FitSnack Co",
     "unit_price": 3.20, "unit_cost": 1.50,
     "lead_time_days": 5, "reorder_cost": 60,  "holding_cost_per_unit": 0.09,
     "demand_profile": "fast", "base_demand": 50,  "seasonal": "none"},

    {"product_id": "P013", "product_name": "Pretzels 200g",
     "category": "Snacks", "supplier": "CrunchCo Foods",
     "unit_price": 2.10, "unit_cost": 0.95,
     "lead_time_days": 4, "reorder_cost": 52,  "holding_cost_per_unit": 0.06,
     "demand_profile": "slow",  "base_demand": 22,  "seasonal": "none"},

    # ── PERSONAL CARE (6 products) ───────────────────────────────────────
    {"product_id": "P014", "product_name": "Shampoo 400ml",
     "category": "Personal Care", "supplier": "GlowCare Ltd",
     "unit_price": 4.99, "unit_cost": 2.10,
     "lead_time_days": 7, "reorder_cost": 80,  "holding_cost_per_unit": 0.14,
     "demand_profile": "slow",  "base_demand": 25,  "seasonal": "none"},

    {"product_id": "P015", "product_name": "Toothpaste 100ml",
     "category": "Personal Care", "supplier": "BrightSmile Inc",
     "unit_price": 2.50, "unit_cost": 1.10,
     "lead_time_days": 5, "reorder_cost": 60,  "holding_cost_per_unit": 0.08,
     "demand_profile": "fast", "base_demand": 60,  "seasonal": "none"},

    {"product_id": "P016", "product_name": "Hand Sanitizer 250ml",
     "category": "Personal Care", "supplier": "PureGuard Co",
     "unit_price": 3.00, "unit_cost": 1.20,
     "lead_time_days": 4, "reorder_cost": 55,  "holding_cost_per_unit": 0.09,
     "demand_profile": "spike", "base_demand": 35,  "seasonal": "winter"},

    {"product_id": "P017", "product_name": "Body Lotion 200ml",
     "category": "Personal Care", "supplier": "GlowCare Ltd",
     "unit_price": 5.50, "unit_cost": 2.40,
     "lead_time_days": 7, "reorder_cost": 85,  "holding_cost_per_unit": 0.15,
     "demand_profile": "slow",  "base_demand": 18,  "seasonal": "winter"},

    {"product_id": "P018", "product_name": "Razor 5pk",
     "category": "Personal Care", "supplier": "SmoothShave Ltd",
     "unit_price": 6.99, "unit_cost": 3.10,
     "lead_time_days": 6, "reorder_cost": 90,  "holding_cost_per_unit": 0.18,
     "demand_profile": "slow",  "base_demand": 15,  "seasonal": "none"},

    {"product_id": "P019", "product_name": "Deodorant Spray 150ml",
     "category": "Personal Care", "supplier": "FreshScent Co",
     "unit_price": 3.80, "unit_cost": 1.60,
     "lead_time_days": 5, "reorder_cost": 65,  "holding_cost_per_unit": 0.11,
     "demand_profile": "fast", "base_demand": 45,  "seasonal": "summer"},

    # ── HOUSEHOLD (5 products) ───────────────────────────────────────────
    {"product_id": "P020", "product_name": "Dish Soap 500ml",
     "category": "Household", "supplier": "CleanHome Ltd",
     "unit_price": 2.20, "unit_cost": 0.95,
     "lead_time_days": 5, "reorder_cost": 55,  "holding_cost_per_unit": 0.07,
     "demand_profile": "fast", "base_demand": 65,  "seasonal": "none"},

    {"product_id": "P021", "product_name": "Paper Towels 6pk",
     "category": "Household", "supplier": "PaperPlus Co",
     "unit_price": 5.50, "unit_cost": 2.50,
     "lead_time_days": 6, "reorder_cost": 80,  "holding_cost_per_unit": 0.16,
     "demand_profile": "fast", "base_demand": 55,  "seasonal": "none"},

    {"product_id": "P022", "product_name": "Laundry Detergent 1kg",
     "category": "Household", "supplier": "WashWell Inc",
     "unit_price": 7.99, "unit_cost": 3.50,
     "lead_time_days": 8, "reorder_cost": 100, "holding_cost_per_unit": 0.22,
     "demand_profile": "slow",  "base_demand": 20,  "seasonal": "none"},

    {"product_id": "P023", "product_name": "Trash Bags 20pk",
     "category": "Household", "supplier": "CleanHome Ltd",
     "unit_price": 4.50, "unit_cost": 2.00,
     "lead_time_days": 6, "reorder_cost": 70,  "holding_cost_per_unit": 0.13,
     "demand_profile": "slow",  "base_demand": 22,  "seasonal": "none"},

    {"product_id": "P024", "product_name": "All-Purpose Cleaner 750ml",
     "category": "Household", "supplier": "WashWell Inc",
     "unit_price": 3.20, "unit_cost": 1.40,
     "lead_time_days": 5, "reorder_cost": 60,  "holding_cost_per_unit": 0.09,
     "demand_profile": "spike", "base_demand": 30,  "seasonal": "none"},

    # ── DAIRY (6 products) ───────────────────────────────────────────────
    {"product_id": "P025", "product_name": "Whole Milk 2L",
     "category": "Dairy", "supplier": "FarmFresh Dairy",
     "unit_price": 2.10, "unit_cost": 1.10,
     "lead_time_days": 2, "reorder_cost": 40,  "holding_cost_per_unit": 0.06,
     "demand_profile": "fast", "base_demand": 120, "seasonal": "none"},

    {"product_id": "P026", "product_name": "Greek Yoghurt 500g",
     "category": "Dairy", "supplier": "FarmFresh Dairy",
     "unit_price": 2.80, "unit_cost": 1.30,
     "lead_time_days": 2, "reorder_cost": 40,  "holding_cost_per_unit": 0.07,
     "demand_profile": "fast", "base_demand": 80,  "seasonal": "summer"},

    {"product_id": "P027", "product_name": "Cheddar Cheese 400g",
     "category": "Dairy", "supplier": "CheeseCraft Ltd",
     "unit_price": 4.50, "unit_cost": 2.20,
     "lead_time_days": 3, "reorder_cost": 55,  "holding_cost_per_unit": 0.12,
     "demand_profile": "fast", "base_demand": 55,  "seasonal": "none"},

    {"product_id": "P028", "product_name": "Butter 250g",
     "category": "Dairy", "supplier": "CreamTop Co",
     "unit_price": 3.50, "unit_cost": 1.80,
     "lead_time_days": 3, "reorder_cost": 50,  "holding_cost_per_unit": 0.10,
     "demand_profile": "slow",  "base_demand": 28,  "seasonal": "winter"},

    {"product_id": "P029", "product_name": "Cream Cheese 200g",
     "category": "Dairy", "supplier": "CreamTop Co",
     "unit_price": 2.90, "unit_cost": 1.40,
     "lead_time_days": 3, "reorder_cost": 48,  "holding_cost_per_unit": 0.08,
     "demand_profile": "slow",  "base_demand": 20,  "seasonal": "none"},

    {"product_id": "P030", "product_name": "Skimmed Milk 1L",
     "category": "Dairy", "supplier": "FarmFresh Dairy",
     "unit_price": 1.60, "unit_cost": 0.80,
     "lead_time_days": 2, "reorder_cost": 38,  "holding_cost_per_unit": 0.05,
     "demand_profile": "fast", "base_demand": 70,  "seasonal": "none"},

    # ── BAKERY (5 products) ──────────────────────────────────────────────
    {"product_id": "P031", "product_name": "White Bread 800g",
     "category": "Bakery", "supplier": "BakeMaster Ltd",
     "unit_price": 1.80, "unit_cost": 0.75,
     "lead_time_days": 2, "reorder_cost": 35,  "holding_cost_per_unit": 0.05,
     "demand_profile": "fast", "base_demand": 130, "seasonal": "none"},

    {"product_id": "P032", "product_name": "Sourdough Loaf 600g",
     "category": "Bakery", "supplier": "ArtisanBake Co",
     "unit_price": 3.50, "unit_cost": 1.60,
     "lead_time_days": 2, "reorder_cost": 45,  "holding_cost_per_unit": 0.09,
     "demand_profile": "fast", "base_demand": 60,  "seasonal": "none"},

    {"product_id": "P033", "product_name": "Croissants 4pk",
     "category": "Bakery", "supplier": "BakeMaster Ltd",
     "unit_price": 2.60, "unit_cost": 1.10,
     "lead_time_days": 2, "reorder_cost": 40,  "holding_cost_per_unit": 0.07,
     "demand_profile": "spike", "base_demand": 35,  "seasonal": "none"},

    {"product_id": "P034", "product_name": "Muffins 6pk",
     "category": "Bakery", "supplier": "SweetBakes Inc",
     "unit_price": 3.20, "unit_cost": 1.40,
     "lead_time_days": 2, "reorder_cost": 42,  "holding_cost_per_unit": 0.08,
     "demand_profile": "slow",  "base_demand": 25,  "seasonal": "none"},

    {"product_id": "P035", "product_name": "Rye Bread 500g",
     "category": "Bakery", "supplier": "ArtisanBake Co",
     "unit_price": 2.90, "unit_cost": 1.25,
     "lead_time_days": 2, "reorder_cost": 40,  "holding_cost_per_unit": 0.07,
     "demand_profile": "slow",  "base_demand": 18,  "seasonal": "none"},

    # ── FROZEN FOODS (5 products) ────────────────────────────────────────
    {"product_id": "P036", "product_name": "Frozen Pizza 400g",
     "category": "Frozen Foods", "supplier": "IceBite Foods",
     "unit_price": 4.20, "unit_cost": 1.90,
     "lead_time_days": 5, "reorder_cost": 70,  "holding_cost_per_unit": 0.13,
     "demand_profile": "fast", "base_demand": 75,  "seasonal": "winter"},

    {"product_id": "P037", "product_name": "Frozen Peas 1kg",
     "category": "Frozen Foods", "supplier": "IceBite Foods",
     "unit_price": 2.50, "unit_cost": 1.10,
     "lead_time_days": 5, "reorder_cost": 55,  "holding_cost_per_unit": 0.08,
     "demand_profile": "fast", "base_demand": 60,  "seasonal": "none"},

    {"product_id": "P038", "product_name": "Frozen Chips 750g",
     "category": "Frozen Foods", "supplier": "FrostFarm Ltd",
     "unit_price": 2.80, "unit_cost": 1.20,
     "lead_time_days": 5, "reorder_cost": 58,  "holding_cost_per_unit": 0.09,
     "demand_profile": "fast", "base_demand": 65,  "seasonal": "none"},

    {"product_id": "P039", "product_name": "Ice Cream 1L",
     "category": "Frozen Foods", "supplier": "CoolCreams Co",
     "unit_price": 4.99, "unit_cost": 2.10,
     "lead_time_days": 4, "reorder_cost": 65,  "holding_cost_per_unit": 0.14,
     "demand_profile": "fast", "base_demand": 70,  "seasonal": "summer"},

    {"product_id": "P040", "product_name": "Frozen Fish Fillets 500g",
     "category": "Frozen Foods", "supplier": "FrostFarm Ltd",
     "unit_price": 6.50, "unit_cost": 3.00,
     "lead_time_days": 6, "reorder_cost": 90,  "holding_cost_per_unit": 0.18,
     "demand_profile": "slow",  "base_demand": 22,  "seasonal": "none"},
]

print(f"[✓] Product catalogue created: {len(products)} products across 7 categories")


# ─────────────────────────────────────────────
# 3.  STORE & REGION DEFINITIONS
# ─────────────────────────────────────────────
stores = [
    {"store_id": "S01", "region": "North"},
    {"store_id": "S02", "region": "South"},
    {"store_id": "S03", "region": "East"},
    {"store_id": "S04", "region": "West"},
    {"store_id": "S05", "region": "Central"},
]


# ─────────────────────────────────────────────
# 4.  DEMAND HELPER FUNCTIONS
# ─────────────────────────────────────────────

def seasonal_multiplier(d: date, season: str) -> float:
    """
    Returns a demand multiplier based on the month and declared season.
    'summer' products peak in June–August; 'winter' products peak in Nov–Jan.
    'none' means no seasonal effect (multiplier always ~1.0).
    """
    month = d.month
    if season == "summer":
        # Smooth bell curve peaking in July (month 7)
        return 1.0 + 0.8 * np.exp(-0.5 * ((month - 7) / 2.5) ** 2)
    elif season == "winter":
        # Peak in December (month 12); wrap around January
        dist_to_dec = min(abs(month - 12), abs(month - 12 + 12))
        return 1.0 + 0.7 * np.exp(-0.5 * (dist_to_dec / 2.0) ** 2)
    else:
        return 1.0


def day_of_week_multiplier(d: date) -> float:
    """
    Retail sales are typically higher on weekends.
    Monday=0 … Sunday=6
    """
    dow = d.weekday()
    if dow == 4:   # Friday
        return 1.15
    elif dow in (5, 6):   # Saturday, Sunday
        return 1.30
    else:
        return 1.0


def demand_spike_multiplier(profile: str) -> float:
    """
    For 'spike' products, randomly introduce a big demand surge
    on roughly 5% of days (flash sales, promotions, viral moments, etc.).
    """
    if profile == "spike" and random.random() < 0.05:
        return random.uniform(2.5, 5.0)   # 2.5× – 5× surge
    return 1.0


def generate_units_sold(base_demand: int, profile: str,
                        seasonal_mult: float, dow_mult: float,
                        spike_mult: float) -> int:
    """
    Combine all multipliers with a Poisson-distributed base demand
    to get a realistic integer units_sold value.
    Fast-moving products also get a slightly higher noise floor.
    """
    noise_sigma = 0.20 if profile == "fast" else 0.30   # relative std

    # Compute the expected demand for this day
    expected = base_demand * seasonal_mult * dow_mult * spike_mult

    # Add proportional Gaussian noise; floor at 0
    noisy = expected * (1 + np.random.normal(0, noise_sigma))
    noisy = max(0, noisy)

    # Draw from a Poisson distribution for integer count
    units = np.random.poisson(noisy)
    return int(units)


# ─────────────────────────────────────────────
# 5.  CURRENT STOCK SIMULATION
# ─────────────────────────────────────────────
# We maintain a simple per-product running stock level.
# Stock is replenished whenever it falls below a reorder threshold.

def initialise_stock(products: list) -> dict:
    """Set a sensible starting stock for each product."""
    stock = {}
    for p in products:
        # Start with ~30 days of expected demand
        stock[p["product_id"]] = int(p["base_demand"] * 30)
    return stock


def update_stock(stock: dict, product_id: str, units_sold: int,
                 lead_time_days: int, base_demand: int) -> int:
    """
    Subtract units_sold from current stock.
    Trigger a replenishment order when stock falls below safety threshold
    (lead_time × daily_demand × 1.5 safety factor).
    Replenishment arrives instantly in this simplified simulation
    (sufficient for generating realistic stock variation).
    """
    reorder_point = int(lead_time_days * base_demand * 1.5)
    order_qty     = int(base_demand * 30)   # one-month order

    stock[product_id] -= units_sold

    # Avoid negative stock (back-orders modelled as 0 stock day)
    if stock[product_id] < 0:
        stock[product_id] = 0

    # Reorder trigger
    if stock[product_id] <= reorder_point:
        stock[product_id] += order_qty

    return stock[product_id]


# ─────────────────────────────────────────────
# 6.  MAIN DATA GENERATION LOOP
# ─────────────────────────────────────────────
print("[…] Generating rows — this may take a moment …")

stock_levels = initialise_stock(products)   # running stock tracker

rows = []   # we'll build a list of dicts, then convert to DataFrame

for current_date in all_dates:
    for product in products:
        for store in stores:

            pid     = product["product_id"]
            profile = product["demand_profile"]

            # ── Demand multipliers ──────────────────────────────────────
            s_mult  = seasonal_multiplier(current_date, product["seasonal"])
            dow_m   = day_of_week_multiplier(current_date)
            spk_m   = demand_spike_multiplier(profile)

            # Store-level multiplier: small random offset per store each day
            store_m = np.random.uniform(0.85, 1.15)

            # ── Units sold ──────────────────────────────────────────────
            units_sold = generate_units_sold(
                base_demand   = product["base_demand"],
                profile       = profile,
                seasonal_mult = s_mult * store_m,
                dow_mult      = dow_m,
                spike_mult    = spk_m
            )

            # ── Revenue ─────────────────────────────────────────────────
            sales_revenue = round(units_sold * product["unit_price"], 2)

            # ── Stock level (shared across stores for simplicity) ───────
            # Use a composite key per store to track separately
            stock_key = f"{pid}_{store['store_id']}"
            if stock_key not in stock_levels:
                stock_levels[stock_key] = int(product["base_demand"] * 30)

            current_stock = update_stock(
                stock        = stock_levels,
                product_id   = stock_key,
                units_sold   = units_sold,
                lead_time_days = product["lead_time_days"],
                base_demand  = product["base_demand"]
            )

            # ── Assemble the row ─────────────────────────────────────────
            rows.append({
                "date"                  : current_date.strftime("%Y-%m-%d"),
                "product_id"            : pid,
                "product_name"          : product["product_name"],
                "category"              : product["category"],
                "supplier"              : product["supplier"],
                "unit_price"            : product["unit_price"],
                "unit_cost"             : product["unit_cost"],
                "units_sold"            : units_sold,
                "sales_revenue"         : sales_revenue,
                "current_stock"         : current_stock,
                "lead_time_days"        : product["lead_time_days"],
                "reorder_cost"          : product["reorder_cost"],
                "holding_cost_per_unit" : product["holding_cost_per_unit"],
                "region"                : store["region"],
                "store_id"              : store["store_id"],
            })

# ─────────────────────────────────────────────
# 7.  BUILD DATAFRAME & SAVE
# ─────────────────────────────────────────────
df = pd.DataFrame(rows)

# Ensure correct dtypes
df["date"]           = pd.to_datetime(df["date"])
df["units_sold"]     = df["units_sold"].astype(int)
df["current_stock"]  = df["current_stock"].astype(int)
df["sales_revenue"]  = df["sales_revenue"].astype(float)

# Sort for a clean, chronological CSV
df.sort_values(["date", "store_id", "product_id"], inplace=True)
df.reset_index(drop=True, inplace=True)

# Save to CSV
df.to_csv(OUTPUT_FILE, index=False)
print(f"[✓] Dataset saved → {OUTPUT_FILE}")


# ─────────────────────────────────────────────
# 8.  SUMMARY REPORT
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  DATASET SUMMARY")
print("=" * 60)
print(f"  Total rows          : {len(df):,}")
print(f"  Date range          : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"  Unique products     : {df['product_id'].nunique()}")
print(f"  Unique categories   : {df['category'].nunique()}")
print(f"  Unique suppliers    : {df['supplier'].nunique()}")
print(f"  Unique stores       : {df['store_id'].nunique()}")
print(f"  Unique regions      : {df['region'].nunique()}")
print(f"  Total units sold    : {df['units_sold'].sum():,}")
print(f"  Total sales revenue : £{df['sales_revenue'].sum():,.2f}")
print(f"  Avg daily stock     : {df['current_stock'].mean():.1f} units")
print(f"  Zero-stock days     : {(df['current_stock'] == 0).sum():,}")
print("=" * 60)

print("\n  Units sold per category:")
cat_summary = (
    df.groupby("category")["units_sold"]
      .sum()
      .sort_values(ascending=False)
)
for cat, total in cat_summary.items():
    print(f"    {cat:<20} {total:>10,} units")

print("\n  Top 5 products by revenue:")
top5 = (
    df.groupby(["product_id", "product_name"])["sales_revenue"]
      .sum()
      .sort_values(ascending=False)
      .head(5)
)
for (pid, pname), rev in top5.items():
    print(f"    {pid}  {pname:<30}  £{rev:>12,.2f}")

print("\n  Columns in dataset:")
for col in df.columns:
    print(f"    - {col}")

print("\n[✓] data_generator.py completed successfully.")