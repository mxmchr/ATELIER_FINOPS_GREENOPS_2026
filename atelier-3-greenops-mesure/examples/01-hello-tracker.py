"""
Atelier 3 — Exemple 1 : Hello world du tracking carbone.
Mesure les émissions d'une charge de travail simple (multiplications de matrices).

Exécuter : python examples/01-hello-tracker.py
"""

import numpy as np
from codecarbon import EmissionsTracker

tracker = EmissionsTracker(
    project_name="hello-carbon",
    country_iso_code="FRA",  # ~60 gCO2e/kWh
    measure_power_secs=1,
    save_to_file=True,
    output_dir="./outputs",
)

print("⏱  Démarrage du tracking...")
tracker.start()

# ─── Charge de travail ──────────────────────────────────────────────
# 20 multiplications de matrices 2000x2000
for i in range(20):
    a = np.random.rand(2000, 2000).astype(np.float32)
    b = np.random.rand(2000, 2000).astype(np.float32)
    _ = a @ b
    print(f"  Itération {i+1}/20 terminée")

# ────────────────────────────────────────────────────────────────────
emissions_kg = tracker.stop()
print()
print(f"✅ Émissions estimées : {emissions_kg * 1000:.4f} g CO2e")
print(f"   Soit l'équivalent de ~{(emissions_kg * 1000) / 150:.3f} km en voiture (150 g/km)")
print()
print("📂 Détails écrits dans : outputs/emissions.csv")
