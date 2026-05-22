"""
Atelier 3 — Exemple 2 : Comparer l'empreinte de deux algorithmes équivalents.

Versions :
  - search_linear : O(n*m) — recherche linéaire dans une liste
  - search_set    : O(n+m) — conversion en set puis lookup

Objectif : montrer qu'un changement de complexité algorithmique a un
impact DIRECT et MESURABLE sur l'empreinte carbone.

Exécuter : python examples/02-algo-comparison.py
"""

import random
import statistics
from codecarbon import EmissionsTracker

# ─── Setup ──────────────────────────────────────────────────────────
random.seed(42)
HAYSTACK = [random.randint(0, 1_000_000) for _ in range(100_000)]
NEEDLES = [random.randint(0, 1_000_000) for _ in range(5_000)]
N_RUNS = 5

COUNTRY = "FRA"  # essayez aussi POL, SWE, USA


# ─── Algorithmes ────────────────────────────────────────────────────
def search_linear(haystack, needles):
    """O(n*m) — pour chaque needle, parcourt toute la liste."""
    return [n for n in needles if n in haystack]


def search_set(haystack, needles):
    """O(n+m) — convertit en set (O(n)) puis lookup en O(1)."""
    haystack_set = set(haystack)
    return [n for n in needles if n in haystack_set]


def measure(func, label):
    """Mesure plusieurs runs et retourne moyenne / écart-type."""
    emissions_list = []
    for run in range(N_RUNS):
        tracker = EmissionsTracker(
            project_name=f"{label}-run{run}",
            country_iso_code=COUNTRY,
            measure_power_secs=1,
            save_to_file=False,
            log_level="error",
        )
        tracker.start()
        result = func(HAYSTACK, NEEDLES)
        emissions = tracker.stop()
        emissions_list.append(emissions or 0)
        assert len(result) > 0, "Vérification d'intégrité"
    return statistics.mean(emissions_list), statistics.stdev(emissions_list) if N_RUNS > 1 else 0


# ─── Mesure ─────────────────────────────────────────────────────────
print(f"🔬 Mesure sur {N_RUNS} runs, pays = {COUNTRY}\n")
print("Algorithme linéaire (O(n*m))...")
mean_lin, std_lin = measure(search_linear, "linear")
print(f"  → {mean_lin * 1000:.4f} ± {std_lin * 1000:.4f} g CO2e\n")

print("Algorithme avec set (O(n+m))...")
mean_set, std_set = measure(search_set, "set")
print(f"  → {mean_set * 1000:.4f} ± {std_set * 1000:.4f} g CO2e\n")

# ─── Synthèse ───────────────────────────────────────────────────────
ratio = mean_lin / mean_set if mean_set > 0 else float("inf")
print(f"📉 Ratio (linéaire / set) = {ratio:.1f}×")
print(f"   Économie : {(1 - 1/ratio) * 100:.1f}%")
print()

# Extrapolation
calls_per_day = 1_000_000
year_lin_g = mean_lin * 1000 * calls_per_day * 365
year_set_g = mean_set * 1000 * calls_per_day * 365
saved_kg = (year_lin_g - year_set_g) / 1000
print(f"🌍 Pour {calls_per_day:,} appels/jour pendant 1 an :")
print(f"   Linéaire : {year_lin_g / 1000:,.0f} kg CO2e")
print(f"   Set      : {year_set_g / 1000:,.0f} kg CO2e")
print(f"   Économie : {saved_kg:,.0f} kg CO2e (~{saved_kg / 150:.0f} km voiture)")
