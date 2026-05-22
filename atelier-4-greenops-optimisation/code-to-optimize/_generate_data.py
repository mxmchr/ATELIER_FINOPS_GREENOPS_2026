"""Génère des données factices pour l'atelier 4 (ETL à optimiser)."""

import csv
import random
from pathlib import Path

random.seed(42)
OUT_DIR = Path(__file__).parent.parent / "data"
OUT_DIR.mkdir(exist_ok=True)

N_USERS = 5_000
N_PRODUCTS = 1_000
N_TRANSACTIONS = 200_000
CATEGORIES = ["electronics", "books", "clothing", "food", "sports", "garden", "toys", "beauty"]

# Users
with (OUT_DIR / "users.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["user_id", "name", "country", "signup_year"])
    for i in range(N_USERS):
        w.writerow([f"u{i:05d}", f"User {i}",
                    random.choice(["FR", "DE", "IT", "ES", "BE", "NL"]),
                    random.randint(2018, 2025)])

# Products
with (OUT_DIR / "products.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["product_id", "name", "category", "unit_price"])
    for i in range(N_PRODUCTS):
        w.writerow([f"p{i:05d}", f"Product {i}",
                    random.choice(CATEGORIES),
                    round(random.uniform(5, 500), 2)])

# Transactions
with (OUT_DIR / "transactions.csv").open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["tx_id", "user_id", "product_id", "amount", "date"])
    for i in range(N_TRANSACTIONS):
        w.writerow([
            f"t{i:07d}",
            f"u{random.randint(0, N_USERS-1):05d}",
            f"p{random.randint(0, N_PRODUCTS-1):05d}",
            round(random.uniform(5, 1000), 2),
            f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        ])

print(f"Generated in {OUT_DIR}: {N_USERS} users, {N_PRODUCTS} products, {N_TRANSACTIONS} transactions")
