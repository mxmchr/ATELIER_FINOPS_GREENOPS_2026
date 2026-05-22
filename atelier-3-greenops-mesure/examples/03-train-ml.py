"""
Atelier 3 — Exemple 3 : Empreinte d'un entraînement ML (MNIST simplifié).

Modèle : 2 couches denses (volontairement petit pour tenir dans Codespaces).
Mesure : énergie totale, émissions, durée par epoch.

Exécuter : python examples/03-train-ml.py
"""

import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from codecarbon import EmissionsTracker

torch.manual_seed(42)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🖥  Device : {DEVICE}")

# ─── Données factices (évite téléchargement) ────────────────────────
N_TRAIN = 50_000
X = torch.randn(N_TRAIN, 784)
y = torch.randint(0, 10, (N_TRAIN,))
loader = DataLoader(TensorDataset(X, y), batch_size=128, shuffle=True)


# ─── Modèle ─────────────────────────────────────────────────────────
class SmallMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(784, 256), nn.ReLU(),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, 10),
        )

    def forward(self, x):
        return self.net(x)


model = SmallMLP().to(DEVICE)
opt = optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.CrossEntropyLoss()


# ─── Entraînement instrumenté ───────────────────────────────────────
tracker = EmissionsTracker(
    project_name="mnist-mlp",
    country_iso_code="FRA",
    measure_power_secs=2,
    save_to_file=True,
    output_dir="./outputs",
)
tracker.start()

start = time.time()
N_EPOCHS = 5
for epoch in range(N_EPOCHS):
    epoch_start = time.time()
    losses = []
    for xb, yb in loader:
        xb, yb = xb.to(DEVICE), yb.to(DEVICE)
        opt.zero_grad()
        loss = loss_fn(model(xb), yb)
        loss.backward()
        opt.step()
        losses.append(loss.item())
    print(f"Epoch {epoch+1}/{N_EPOCHS} — loss {sum(losses)/len(losses):.4f} "
          f"— durée {time.time() - epoch_start:.1f}s")

total_time = time.time() - start
emissions_kg = tracker.stop()

# ─── Synthèse ───────────────────────────────────────────────────────
print()
print(f"⏱  Durée totale : {total_time:.1f} s")
print(f"⚡ Énergie estimée : {tracker.final_emissions_data.energy_consumed * 1000:.3f} Wh")
print(f"🌍 Émissions : {emissions_kg * 1000:.3f} g CO2e")
print()
print("Si on ré-entraîne 100× (hyperparameter tuning) :")
print(f"  → {emissions_kg * 100 * 1000:.1f} g CO2e")
print(f"  → équivalent ~{(emissions_kg * 100 * 1000) / 150:.2f} km voiture")
