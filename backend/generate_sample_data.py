"""
Generates a realistic-but-messy sample sales dataset for the Basira demo.
Deliberately includes: missing values, duplicate rows, inconsistent text casing,
currency-formatted numbers as strings, and a genuine declining trend in one
region/category so that natural-language questions like "why did sales drop"
have a real, discoverable answer in the data.

Not part of the running app — run once to (re)generate data/sample_sales.csv.
"""
import random
import csv
from datetime import date, timedelta

random.seed(42)

REGIONS = ["Riyadh", "Jeddah", "Dammam", "Makkah", "Madinah"]
CATEGORIES = {
    "Electronics": ["Wireless Earbuds", "Smart Watch", "Bluetooth Speaker", "Power Bank", "Laptop Stand"],
    "Clothing": ["Cotton T-Shirt", "Denim Jacket", "Running Shoes", "Wool Scarf", "Leather Belt"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Blender", "Non-stick Pan Set", "Vacuum Cleaner"],
    "Beauty": ["Face Serum", "Hair Dryer", "Makeup Kit", "Perfume", "Skincare Set"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Resistance Bands", "Sports Bottle", "Cycling Helmet"],
}
SEGMENTS = ["Retail", "Wholesale", "Online"]

BASE_PRICE = {
    "Wireless Earbuds": 149, "Smart Watch": 399, "Bluetooth Speaker": 199, "Power Bank": 89, "Laptop Stand": 69,
    "Cotton T-Shirt": 59, "Denim Jacket": 249, "Running Shoes": 299, "Wool Scarf": 79, "Leather Belt": 99,
    "Air Fryer": 349, "Coffee Maker": 279, "Blender": 199, "Non-stick Pan Set": 229, "Vacuum Cleaner": 599,
    "Face Serum": 129, "Hair Dryer": 159, "Makeup Kit": 219, "Perfume": 349, "Skincare Set": 259,
    "Yoga Mat": 89, "Dumbbell Set": 249, "Resistance Bands": 59, "Sports Bottle": 39, "Cycling Helmet": 199,
}

start = date(2025, 2, 1)
end = date(2026, 7, 31)
days = (end - start).days

rows = []
order_id = 10000

d = start
while d <= end:
    n_orders = random.randint(3, 9)
    # Deliberate decline: Jeddah + Electronics slows sharply after Feb 2026 (marketing budget cut scenario)
    jeddah_electronics_slump = d >= date(2026, 2, 1)

    for _ in range(n_orders):
        region = random.choice(REGIONS)
        category = random.choice(list(CATEGORIES.keys()))

        # apply the slump: fewer Jeddah+Electronics orders after Feb 2026
        if jeddah_electronics_slump and region == "Jeddah" and category == "Electronics":
            if random.random() < 0.75:
                continue  # skip most of these orders -> visible decline

        product = random.choice(CATEGORIES[category])
        qty = random.randint(1, 6)
        base = BASE_PRICE[product]
        unit_price = round(base * random.uniform(0.9, 1.15), 2)
        revenue = round(unit_price * qty, 2)
        cost_ratio = random.uniform(0.55, 0.72)
        profit = round(revenue * (1 - cost_ratio), 2)
        segment = random.choice(SEGMENTS)

        order_id += 1
        rows.append({
            "Order ID": order_id,
            "Order Date": d.isoformat(),
            "Region": region,
            "Category": category,
            "Product": product,
            "Quantity": qty,
            "Unit Price": unit_price,
            "Revenue": revenue,
            "Profit": profit,
            "Customer Segment": segment,
        })
    d += timedelta(days=1)

print(f"Generated {len(rows)} clean rows before messing them up")

# --- Now deliberately mess the data up, like real exported data ---

messy_rows = []
for r in rows:
    r = dict(r)

    # 1. Inconsistent casing / whitespace on text columns (~15%)
    if random.random() < 0.15:
        r["Region"] = f"  {r['Region'].upper()}  "
    if random.random() < 0.12:
        r["Category"] = r["Category"].lower()

    # 2. Currency-formatted numbers as strings (~20% of revenue/profit cells)
    if random.random() < 0.2:
        r["Revenue"] = f"${r['Revenue']:,.2f}"
    if random.random() < 0.15:
        r["Profit"] = f"SAR {r['Profit']:,.2f}"

    # 3. Missing values (~6% of rows missing Quantity or Unit Price or Customer Segment)
    if random.random() < 0.04:
        r["Quantity"] = ""
    if random.random() < 0.04:
        r["Unit Price"] = ""
    if random.random() < 0.05:
        r["Customer Segment"] = ""
    if random.random() < 0.02:
        r["Region"] = ""

    messy_rows.append(r)

# 4. Inject exact duplicate rows (~2%)
dupes = random.sample(messy_rows, k=max(1, len(messy_rows)//50))
messy_rows.extend(dupes)
random.shuffle(messy_rows)

out_path = "data/sample_sales.csv"
fieldnames = list(rows[0].keys())
with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(messy_rows)

print(f"Wrote {len(messy_rows)} rows (incl. {len(dupes)} injected duplicates) to {out_path}")
