"""
Atelier 4 — Code à optimiser (baseline v0).

Ce script est VOLONTAIREMENT inefficient. Il :
1. Lit 3 fichiers CSV (utilisateurs, transactions, produits)
2. Joint les transactions aux utilisateurs et produits
3. Calcule un score de fidélité par utilisateur
4. Écrit un rapport CSV

Cible : faire mieux que ce baseline dans v1 à v5.
"""

import csv
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
USERS_CSV = DATA_DIR / "users.csv"
TX_CSV = DATA_DIR / "transactions.csv"
PRODUCTS_CSV = DATA_DIR / "products.csv"
OUT_CSV = Path(__file__).parent / "output_v0.csv"


def load_csv(path):
    """Charge un CSV en liste de dicts (lent et gourmand en mémoire)."""
    with open(path) as f:
        return list(csv.DictReader(f))


def main():
    start = time.time()

    # 1) Chargement (mémoire complète, pas de streaming)
    users = load_csv(USERS_CSV)
    transactions = load_csv(TX_CSV)
    products = load_csv(PRODUCTS_CSV)
    print(f"Loaded: {len(users)} users, {len(transactions)} tx, {len(products)} products")

    # 2) Construire un score par utilisateur — version O(N×M) pure
    scores = []
    for user in users:
        user_id = user["user_id"]
        total_amount = 0.0
        tx_count = 0
        categories = set()

        # 🛑 Pour chaque user, on parcourt TOUTES les transactions (O(U*T))
        for tx in transactions:
            if tx["user_id"] == user_id:
                # 🛑 Recherche linéaire dans products à chaque transaction (O(U*T*P))
                for product in products:
                    if product["product_id"] == tx["product_id"]:
                        total_amount += float(tx["amount"])
                        tx_count += 1
                        categories.add(product["category"])
                        break

        # 🛑 Calcul du score avec un float64 partout
        score = total_amount * 0.1 + tx_count * 5 + len(categories) * 20
        scores.append({
            "user_id": user_id,
            "name": user["name"],
            "total_amount": total_amount,
            "tx_count": tx_count,
            "n_categories": len(categories),
            "loyalty_score": round(score, 2),
        })

    # 3) Tri "à la main" (le tri de Python est O(n log n) déjà, donc OK ici)
    scores.sort(key=lambda x: x["loyalty_score"], reverse=True)

    # 4) Écriture
    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=scores[0].keys())
        writer.writeheader()
        writer.writerows(scores)

    elapsed = time.time() - start
    print(f"✅ Écrit {len(scores)} lignes dans {OUT_CSV} en {elapsed:.2f}s")


if __name__ == "__main__":
    main()
