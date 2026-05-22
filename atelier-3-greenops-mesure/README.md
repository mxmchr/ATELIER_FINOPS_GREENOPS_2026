# Atelier 3 — GreenOps : Mesurer l'empreinte environnementale du code

> **Durée** : 6-7h • **Niveau** : M2 Informatique • **Format** : tutoriel guidé pas à pas

## 🎯 Objectifs d'apprentissage

À la fin de cet atelier, vous saurez :

1. Distinguer **GreenOps**, **éco-conception logicielle** et **Green IT**
2. Définir les notions de **PUE**, **WUE**, **Scope 1/2/3**, **embodied vs operational carbon**
3. Mesurer l'**énergie consommée** par un programme (CodeCarbon, Scaphandre)
4. Comparer l'**empreinte carbone** de deux implémentations algorithmiques
5. Estimer l'**impact carbone d'un cluster Kubernetes** avec Kepler
6. Construire un **dashboard d'observabilité énergétique**

## 🧰 Outils utilisés

- **GitHub Codespaces**
- **CodeCarbon** (Python — mesure côté application)
- **Scaphandre** (mesure système, Linux uniquement)
- **Kepler** (Kubernetes-based Efficient Power Level Exporter)
- **electricityMaps API** (intensité carbone temps réel)
- **Boavizta API** (impact embodied)
- **Grafana + Prometheus** (visualisation)

## ⚠️ Note importante sur la mesure en Codespaces

Codespaces tourne sur des VMs Azure mutualisées. Les **compteurs RAPL Intel** (energy hardware counters) ne sont **pas accessibles** depuis une VM. CodeCarbon utilise alors un **mode estimation** basé sur la TDP du processeur. C'est une limitation pédagogique importante à expliciter aux étudiants. Pour des mesures réelles, il faudrait du métal nu.

---

## 📖 Partie 1 — Comprendre l'impact environnemental du numérique (1h)

### 1.1 Quelques ordres de grandeur

| Indicateur | Valeur | Source |
|------------|--------|--------|
| Part du numérique dans les émissions GES mondiales | 2,5% à 4% | ADEME/Arcep 2023, The Shift Project |
| Croissance annuelle des émissions du numérique | +6% | The Shift Project |
| Part des terminaux dans l'impact (vs datacenters/réseaux) | 65-80% | ADEME |
| Part du fait de fabrication (embodied) vs usage | 50-80% selon équipement | ADEME |

➡️ **L'enjeu n'est pas seulement de réduire la consommation électrique** : c'est aussi de **prolonger la durée de vie du matériel** et limiter le besoin de nouveaux serveurs.

### 1.2 Concepts clés

| Concept | Définition |
|---------|-----------|
| **GES** | Gaz à Effet de Serre (CO2, CH4, N2O…) exprimés en **CO2 équivalent (CO2e)** |
| **PUE** | Power Usage Effectiveness — total / IT (datacenter efficient : 1.1-1.2) |
| **WUE** | Water Usage Effectiveness — litres d'eau par kWh IT |
| **Intensité carbone** | gCO2e/kWh (varie selon mix électrique du pays/heure) |
| **Embodied carbon** | Émissions liées à la fabrication du matériel |
| **Operational carbon** | Émissions liées à l'usage (électricité) |
| **Scope 1/2/3** | Émissions directes / électricité / chaîne de valeur (GHG Protocol) |

### 1.3 GreenOps vs FinOps vs éco-conception

```
            ┌──────────────────────────────────────┐
            │           Cloud / Infra              │
            │                                      │
            │   FinOps  ──→  $    (coût)           │
            │   GreenOps ──→ kg CO2e (impact env.) │
            │                                      │
            └─────────────┬────────────────────────┘
                          │
            ┌─────────────▼────────────────────────┐
            │   Éco-conception logicielle          │
            │   (algorithmes, UX, architecture)    │
            └──────────────────────────────────────┘
```

Les optimisations FinOps et GreenOps **se recoupent à 80%** (moins de ressources = moins cher ET moins d'impact). Les **divergences** : énergies renouvelables (peu d'impact CO2 mais pas forcément moins cher), prolongation matérielle (cher à court terme).

### ✏️ Exercice 1 — Vocabulaire et ordres de grandeur

Compléter le QCM dans `partie-1-quiz.md`. Inclut des questions de calcul :

> Un serveur de 500W tourne 24/7 dans un DC français (60 gCO2e/kWh, PUE 1.5).
> Quel est son impact opérationnel annuel en kgCO2e ?

---

## 🧪 Partie 2 — Mesurer côté application avec CodeCarbon (1h30)

### 2.1 Installation et premier tracking

```bash
cd atelier-3-greenops-mesure
pip install -r requirements.txt
```

Vérifier l'installation :
```bash
python -c "from codecarbon import EmissionsTracker; print('OK')"
```

### 2.2 Hello world du tracking carbone

Ouvrir `examples/01-hello-tracker.py` :

```python
from codecarbon import EmissionsTracker
import numpy as np

tracker = EmissionsTracker(
    project_name="hello-carbon",
    country_iso_code="FRA",
    measure_power_secs=1,
    save_to_file=True,
    output_dir="./outputs",
)

tracker.start()
# Charge de travail : multiplication de matrices
for _ in range(20):
    a = np.random.rand(2000, 2000)
    b = np.random.rand(2000, 2000)
    _ = a @ b
emissions = tracker.stop()

print(f"Émissions : {emissions * 1000:.4f} g CO2e")
```

Exécuter et inspecter le fichier `outputs/emissions.csv` produit.

### 2.3 Comprendre le calcul

CodeCarbon estime :

```
energy_kwh = power_W × duration_h / 1000
emissions_kg = energy_kwh × intensity_gCO2e_per_kWh / 1000
```

Avec :
- **power_W** = via RAPL (si dispo) ou TDP × CPU% + RAM × 0.375 W/Go + GPU
- **intensity** = par défaut : moyenne nationale du pays, ou via API electricityMaps (clé requise)

### ✏️ Exercice 2 — Comparer deux algorithmes

Le fichier `examples/02-algo-comparison.py` propose **deux implémentations d'un même calcul** (recherche d'éléments dans une liste de 100 000 entiers) :

```python
# Version A : recherche linéaire
def search_linear(haystack, needles):
    return [n for n in needles if n in haystack]  # O(n*m)

# Version B : avec set
def search_set(haystack, needles):
    haystack_set = set(haystack)
    return [n for n in needles if n in haystack_set]  # O(n+m)
```

Tâches :

1. Instrumenter chaque fonction avec un `EmissionsTracker` séparé
2. Faire 5 runs de chaque pour avoir une moyenne
3. Reporter dans `partie-2-comparison.md` :
   - Temps moyen
   - Énergie moyenne (kWh)
   - Émissions moyennes (g CO2e)
   - Ratio entre les deux versions
4. **Réflexion** : si cette fonction est appelée 1 M fois par jour en production, quel est l'impact annuel évité par la version optimisée ?

### 2.4 Variation par localisation

Modifier `examples/02-algo-comparison.py` pour comparer les émissions en :
- **France** (`country_iso_code="FRA"`, ~60 gCO2e/kWh)
- **Pologne** (`country_iso_code="POL"`, ~700 gCO2e/kWh)
- **Suède** (`country_iso_code="SWE"`, ~40 gCO2e/kWh)

Observer que **le même calcul a un impact 10-20× supérieur selon le pays d'exécution**.

### ✏️ Exercice 3 — Impact d'un entraînement ML

Dans `examples/03-train-ml.py`, un petit modèle PyTorch (MNIST, 5 epochs) est instrumenté. **Exécuter et reporter** :

- Énergie totale et émissions
- Répartition CPU / RAM / GPU (s'il y a un GPU dispo)
- Si vous deviez ré-entraîner 100 fois ce modèle pour de l'hyperparameter tuning, quel serait l'impact ?
- **Comparer à un trajet en voiture** : 1 km = ~150 g CO2e ; à combien de km cela correspond ?

---

## 🐧 Partie 3 — Mesure système avec Scaphandre (1h) — Démo et discussion

### 3.1 Pourquoi Scaphandre ?

CodeCarbon mesure **par processus**. Scaphandre mesure **au niveau système** via les compteurs **RAPL** (Running Average Power Limit), avec une granularité par container/processus.

⚠️ **Codespaces ne donne pas accès à RAPL.** Cette partie est principalement **démonstrative**. Sur machine bare-metal Linux, Scaphandre serait directement utilisable.

### 3.2 Lecture commentée

Lire le fichier `partie-3-scaphandre-demo.md` qui décrit, captures à l'appui :

- L'architecture de Scaphandre (sensors RAPL, MSR registers)
- L'exporter Prometheus
- Un dashboard Grafana exemple

### 3.3 Alternative en Codespaces : `powerstat` / `turbostat`

Dans le terminal :
```bash
sudo powerstat -R -d 0 5
```

Ces outils s'appuient sur les mêmes compteurs mais peuvent fonctionner partiellement en VM. Documenter ce qui marche / ne marche pas dans votre Codespace.

### ✏️ Exercice 4 — Note de synthèse

Rédiger 1/2 page : **« Quels sont les avantages et limites de chaque approche de mesure (application vs système vs cluster) ? Dans quel cas privilégier laquelle ? »**

---

## ☸️ Partie 4 — Mesurer un cluster avec Kepler (1h30)

### 4.1 Kepler — Kubernetes Efficient Power Level Exporter

[Kepler](https://sustainable-computing.io/) est un projet CNCF Sandbox qui :
- Lit les **compteurs hardware** (RAPL, eBPF) quand disponibles
- À défaut, **estime via un modèle ML** entraîné sur des traces réelles
- Exporte les métriques au format **Prometheus**, par pod/namespace

➡️ Sur Codespaces (VM), Kepler tourne en **mode estimation pure**. Les chiffres sont **indicatifs**, pas absolus.

### 4.2 Déployer le cluster

```bash
./scripts/00-setup-cluster.sh        # Crée un cluster Kind 2 nœuds
./scripts/01-deploy-monitoring.sh    # Prometheus + Grafana
./scripts/02-deploy-kepler.sh        # Kepler en DaemonSet
./scripts/03-deploy-workloads.sh     # 3 apps représentatives
```

Vérifier que Kepler exporte des métriques :
```bash
kubectl port-forward -n kepler ds/kepler-exporter 9102:9102 &
curl -s localhost:9102/metrics | grep kepler_container_joules_total | head
```

### 4.3 Dashboard Grafana

Un dashboard pré-configuré est appliqué automatiquement. Y accéder :

```bash
kubectl port-forward -n monitoring svc/kps-grafana 3000:80
```

Dashboard : **"Kepler — Container Energy & Carbon"**

Panels disponibles :
- **Watts par namespace**
- **Joules consommés (cumulatif)**
- **g CO2e estimés** (croisement avec intensité carbone configurée)
- **Top 5 pods énergivores**

### 4.4 Workloads déployés

Le script déploie 3 applications volontairement contrastées :

| Workload | Profil | Énergie attendue |
|----------|--------|------------------|
| `idle-app` | Ne fait quasi rien | Faible |
| `cpu-intensive` | Calcul de matrices en boucle | Forte |
| `cache-friendly` | Même calcul mais avec cache LRU | Moyenne |

### ✏️ Exercice 5 — Profiling

Laisser tourner 20 minutes puis :

1. Capturer le dashboard sur cette période
2. Calculer le **ratio d'efficacité** (utile / énergie) en proposant une définition
3. Si `cpu-intensive` tournait en France vs Pologne, calculer l'impact annuel (24/7)
4. Identifier dans le dashboard **un comportement contre-intuitif** et en discuter

---

## 📊 Partie 5 — Croiser avec l'intensité carbone temps réel (1h)

### 5.1 L'API ElectricityMaps

L'intensité carbone d'un kWh **varie dans le temps** : entre 30 et 800 gCO2e/kWh selon l'heure et le pays. Pourquoi ?

- **Renouvelables intermittentes** (solaire = 0 la nuit, éolien variable)
- **Centrales pilotables** (gaz, charbon) qui montent en charge aux pics
- **Imports/exports** entre pays interconnectés

L'API [ElectricityMaps](https://www.electricitymaps.com/) fournit l'intensité **temps réel** par zone géographique. Une clé API gratuite est disponible pour les usages académiques.

### 5.2 Récupérer l'intensité carbone

```python
import requests
import os

API_KEY = os.environ["ELECTRICITYMAPS_API_KEY"]
zone = "FR"

response = requests.get(
    f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone}",
    headers={"auth-token": API_KEY},
)
data = response.json()
print(f"Intensité actuelle en {zone} : {data['carbonIntensity']} gCO2e/kWh")
```

Le notebook `notebooks/carbon-intensity.ipynb` propose :
- Récupérer 7 jours d'historique sur 5 zones (FR, DE, PL, SE, US-CAL)
- Tracer les courbes superposées
- Calculer la **part de renouvelables** par zone
- Identifier les **fenêtres optimales** (intensité minimale) pour planifier des jobs

### ✏️ Exercice 6 — Job planning

Vous devez planifier un job de batch quotidien de 2h. Question : **à quelle heure le lancer dans chaque zone** pour minimiser les émissions ?

Implémenter une fonction :
```python
def best_window(zone: str, duration_hours: int, lookback_days: int = 7) -> dict:
    """
    Retourne la fenêtre horaire optimale (heure de début) pour un job
    de durée donnée, basée sur la moyenne historique.
    """
    pass
```

Tester sur les 5 zones et reporter dans `partie-5-job-planning.md`.

---

## 📝 Partie 6 — Synthèse et rendu (30 min)

### 6.1 Livrables — Pull Request

- [ ] Notebooks `02-algo-comparison.py`, `03-train-ml.py` instrumentés et exécutés
- [ ] Captures Grafana (Kepler) sur les workloads
- [ ] `RAPPORT.md` répondant à tous les exercices
- [ ] Fonction `best_window` documentée et testée
- [ ] Une synthèse 1 page : « **3 leviers GreenOps qu'une équipe dev peut activer dès lundi** »

### 6.2 Questions de réflexion

- Pourquoi le **mode estimation** des outils en VM est-il problématique pour communiquer des chiffres ?
- L'**embodied carbon** est-il pris en compte par ces outils ? Comment l'ajouter ?
- Comment éviter le **greenwashing** quand on présente des métriques GreenOps ?

---

## 📚 Pour aller plus loin

- 📘 [Green Software Foundation — Principles](https://principles.green/)
- 🌐 [The Shift Project — Rapports Lean ICT](https://theshiftproject.org/)
- 🛠️ [Boavizta](https://boavizta.org/) — outils open source sur l'embodied carbon
- 📊 [Cloud Carbon Footprint](https://www.cloudcarbonfootprint.org/) (équivalent multi-cloud)
- 🎓 Formation gratuite **Green Software Practitioner** (LF + GSF)

---

## 🔑 Notes pour l'enseignant

<details>
<summary>Cliquer pour afficher</summary>

### Timing détaillé

| Bloc | Durée |
|------|-------|
| Partie 1 (théorie) | 1h |
| Partie 2 (CodeCarbon) | 1h30 |
| Pause déjeuner | 1h |
| Partie 3 (Scaphandre démo) | 1h |
| Partie 4 (Kepler) | 1h30 |
| Partie 5 (ElectricityMaps) | 1h |
| Synthèse | 30 min |

### Points de vigilance majeurs

⚠️ **Mesure en VM = estimation** : insister auprès des étudiants. Ne pas faire publier les chiffres comme s'ils étaient absolus.

⚠️ **CodeCarbon nécessite parfois un téléchargement** du fichier d'intensité carbone au premier run : prévoir un accès internet.

⚠️ **Clé ElectricityMaps** : l'enseignant doit créer un compte académique en amont et la distribuer via Codespaces secrets (variable d'env `ELECTRICITYMAPS_API_KEY`).

### Variantes / extensions

- Pour M2 R&D : remplacer l'algo "search" par un modèle ML plus lourd (BERT inference vs distillé)
- Ajouter un volet **Frontend** : mesurer l'impact d'une page web (WebPageTest API + Sustainable Web Design model)
- Inviter un intervenant : un FinOps practitioner ou un consultant éco-conception

</details>
