# Atelier 4 — GreenOps : Optimiser le code et l'infrastructure

> **Durée** : 6-7h • **Niveau** : M2 Informatique • **Format** : tutoriel guidé pas à pas

## 🎯 Objectifs d'apprentissage

À la fin de cet atelier, vous saurez :

1. Appliquer les **principes Green Software** (carbon-aware, energy efficient, hardware efficient)
2. **Optimiser** un code Python existant pour réduire son empreinte carbone
3. Concevoir un **système carbon-aware** qui décale les calculs vers les fenêtres bas-carbone
4. Mettre en place une **CI/CD carbon-aware** avec GitHub Actions
5. Définir et suivre des **SCI (Software Carbon Intensity)** dans un projet
6. Rédiger un **plan de progrès GreenOps** sur 6 mois

## 🧰 Outils utilisés

- **GitHub Codespaces**
- **GitHub Actions** (CI/CD carbon-aware)
- **CodeCarbon** (suite de l'atelier 3)
- **Carbon Aware SDK** (Microsoft Green Software Foundation)
- **py-spy / scalene** (profiling Python)
- **DuckDB** (exemple d'optimisation data-intensive)

## 🚀 Démarrer

```bash
cd atelier-4-greenops-optimisation
pip install -r requirements.txt
```

---

## 📖 Partie 1 — Les principes du Green Software (45 min)

### 1.1 Les 8 principes de la Green Software Foundation

La GSF publie un référentiel structuré : [https://learn.greensoftware.foundation/](https://learn.greensoftware.foundation/)

| # | Principe | En une phrase |
|---|----------|---------------|
| 1 | **Carbon Efficiency** | Émettre le moins possible par fonction réalisée |
| 2 | **Energy Efficiency** | Consommer le moins d'énergie possible |
| 3 | **Carbon Awareness** | Faire plus quand l'électricité est "verte", moins quand elle est "sale" |
| 4 | **Hardware Efficiency** | Utiliser au maximum le matériel existant et prolonger sa durée de vie |
| 5 | **Measurement** | Ce qui n'est pas mesuré ne peut être amélioré |
| 6 | **Climate Commitments** | S'aligner sur des engagements vérifiables (Net Zero, SBTi) |
| 7 | **Networking** | Réduire la donnée transportée et la distance parcourue |
| 8 | **Demand Shifting** | Décaler la demande dans le temps ou l'espace |

### 1.2 SCI — Software Carbon Intensity

La **SCI** est la métrique officielle de la GSF :

```
SCI = (E × I + M) / R

E : énergie consommée (kWh)
I : intensité carbone de cette énergie (gCO2e/kWh)
M : carbone embodied amorti sur la période
R : unité fonctionnelle (1 requête, 1 utilisateur, 1 transaction…)
```

➡️ **Une SCI est une vitesse** : "X gCO2e par requête". On compare des SCI **avant/après optimisation**, pas des totaux absolus.

### 1.3 Carbon-aware vs Energy-efficient : la nuance

Deux stratégies différentes, parfois opposées :

| Stratégie | Action | Exemple |
|-----------|--------|---------|
| **Energy efficient** | Réduire l'énergie totale | Optimiser un algo de O(n²) à O(n log n) |
| **Carbon aware** | Faire au bon moment / bon endroit | Lancer un training ML la nuit (vent) ou en Suède |

➡️ Les deux sont complémentaires. Énergie efficiente d'abord, carbon-aware ensuite.

### ✏️ Exercice 1 — Classification

Dans `partie-1-classification.md`, classer 15 propositions d'amélioration selon les 8 principes GSF.

---

## ⚡ Partie 2 — Optimiser du code Python (1h30)

### 2.1 Cas d'étude

Le dossier `code-to-optimize/etl.py` contient un script ETL réaliste mais **délibérément peu efficient**. Il :

1. Lit 3 fichiers CSV (totalisant ~200 Mo)
2. Effectue plusieurs jointures et agrégations
3. Calcule un score par utilisateur
4. Écrit un rapport CSV

Mesurer la baseline :

```bash
python -m codecarbon.cli monitor --output-file=baseline.csv -- python code-to-optimize/etl.py
```

Noter : temps, énergie (kWh), émissions (gCO2e), pic mémoire.

### 2.2 Profilage

Utiliser `scalene` pour profiler ligne par ligne **CPU, mémoire et copies** :

```bash
scalene --html --outfile profile.html code-to-optimize/etl.py
```

Ouvrir `profile.html` dans Codespaces (panneau Ports).

### 2.3 Les 5 catégories d'optimisations à explorer

| Catégorie | Exemple | Gain typique |
|-----------|---------|--------------|
| **Algorithme** | Set lookup vs liste, tri vectoriel | 10×-1000× |
| **Structure de données** | Pandas → Polars/DuckDB | 5×-20× |
| **I/O** | CSV → Parquet, lecture lazy | 3×-10× |
| **Concurrence** | Multiprocessing, async I/O | 2×-N× (cores) |
| **Précision** | float64 → float32, int32 → int16 | 2× mémoire |

### ✏️ Exercice 2 — Optimisation itérative

Produire **5 versions successives** du script (`v1.py` à `v5.py`), chacune appliquant **une** optimisation à la fois. Pour chaque version :

1. Décrire l'optimisation appliquée
2. Mesurer (CodeCarbon)
3. Reporter dans un tableau Markdown :

| Version | Optimisation | Temps (s) | Énergie (Wh) | gCO2e | Gain vs v0 |
|---------|--------------|-----------|--------------|-------|-----------|
| v0 (baseline) | — | … | … | … | — |
| v1 | … | … | … | … | …% |
| … | … | … | … | … | … |

**Objectif** : viser **au moins 50% de réduction** d'émissions entre v0 et v5.

### 2.4 Le piège du micro-benchmark

Attention :
- Mesurer **plusieurs runs** (variance possible)
- Réinitialiser les caches OS entre runs (`sync && echo 3 | sudo tee /proc/sys/vm/drop_caches` — peut ne pas marcher en Codespaces)
- Exécuter **dans la même fenêtre temporelle** (intensité carbone identique)
- **Vérifier que le résultat est identique** entre versions (pas d'optimisation incorrecte!)

---

## ⏰ Partie 3 — Carbon-aware computing (1h30)

### 3.1 Principe du demand shifting

Si un job peut être différé de quelques heures sans impact métier, on peut :

- Le **déplacer dans le temps** (off-peak, fenêtre éolienne…)
- Le **déplacer dans l'espace** (région à mix plus propre)

Exemples concrets :
- Build CI/CD nocturnes
- Backups, rotations de logs
- Entraînements ML
- Reporting analytique
- Génération de thumbnails, optimisation d'images

### 3.2 Le Carbon Aware SDK

Le [Carbon Aware SDK](https://github.com/Green-Software-Foundation/carbon-aware-sdk) est une bibliothèque officielle GSF. Elle expose une API :

```
GET /emissions/forecasts/current?location=FR&windowSize=240
```

Réponse : prévisions d'intensité carbone heure par heure pour les 240 minutes à venir, avec **identification de la fenêtre optimale**.

### 3.3 Démarrer le SDK en local

```bash
docker compose -f docker/carbon-aware-sdk.yml up -d
```

Tester :
```bash
curl "http://localhost:8080/emissions/forecasts/current?location=france&dataDuration=60&windowSize=60"
```

### ✏️ Exercice 3 — Scheduler carbon-aware

Implémenter dans `examples/carbon-aware-scheduler.py` une fonction :

```python
def schedule_job(
    job_callable,
    location: str,
    earliest: datetime,
    latest: datetime,
    duration_minutes: int,
):
    """
    Détermine la fenêtre optimale entre earliest et latest pour exécuter
    le job de durée donnée à la zone donnée. Attend puis exécute.
    """
    # 1. Appeler le Carbon Aware SDK pour récupérer les forecasts
    # 2. Identifier la fenêtre optimale
    # 3. Si la fenêtre optimale est dans le futur, sleep jusque-là
    # 4. Exécuter le job (en trackant avec CodeCarbon)
    # 5. Retourner les métriques
    pass
```

**Tester** : planifier un job factice (`time.sleep(60) + boucle CPU`) sur les 12 prochaines heures à Paris.

Comparer avec un run **immédiat** : quel est le delta d'émissions ?

### 3.4 Au-delà du temps : le spatial shifting

Pour les workloads stateless, on peut router vers la région la plus verte. Lire `partie-3-spatial-shifting.md` qui décrit :

- Architecture multi-région avec routage carbon-aware
- Cas concret : Google a publié des résultats sur des transferts de batch entre datacenters
- Limites légales (résidence des données, RGPD)

---

## 🤖 Partie 4 — Intégrer dans la CI/CD (1h)

### 4.1 Une PR ne devrait jamais aggraver le SCI

Idée : à chaque pull request, **mesurer automatiquement** l'impact carbone des tests et le **commenter dans la PR**.

### 4.2 GitHub Action de mesure carbone

Le fichier `.github/workflows/carbon-tracking.yml` est fourni. Il :

1. Exécute la suite de tests dans un runner GitHub
2. Mesure avec CodeCarbon
3. Compare au baseline stocké en cache
4. Commente la PR avec un tableau

```yaml
name: Carbon Tracking
on: [pull_request]

jobs:
  measure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install codecarbon -r requirements.txt
      - name: Run measured tests
        run: |
          python scripts/measure_ci.py
      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('ci-report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: report
            });
```

### 4.3 Carbon-aware GitHub Actions

GitHub propose une [Carbon Aware GitHub Action officielle](https://github.com/marketplace/actions/carbon-aware-action). Elle peut **retarder un workflow** jusqu'à la fenêtre optimale.

Exemple `.github/workflows/nightly-training.yml` :

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # tous les jours minuit
jobs:
  wait-for-green:
    runs-on: ubuntu-latest
    outputs:
      go: ${{ steps.carbon.outputs.go }}
    steps:
      - uses: green-software-foundation/carbon-aware-github-action@v1
        id: carbon
        with:
          location: 'francecentral'
          duration-minutes: 60
          # cherchera la meilleure heure dans les 12h à venir
  train:
    needs: wait-for-green
    if: needs.wait-for-green.outputs.go == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: python train.py
```

### ✏️ Exercice 4 — Mettre en place sur votre fork

1. Activer GitHub Actions sur votre fork
2. Faire une PR qui **ajoute volontairement du code inefficace** (boucle inutile, copie excessive)
3. Vérifier que le commenteur PR alerte
4. Faire une 2e PR qui corrige et vérifier le gain

Livrable : captures des 2 PRs commentées, dans `RAPPORT.md`.

---

## 🏗️ Partie 5 — Architecturer un système GreenOps complet (1h30)

### 5.1 Cas pratique : optimiser une plateforme

Description du cas dans `cas-pratique/platform.md` :

> Une plateforme SaaS de gestion documentaire pour PME (~10 000 utilisateurs, 50 GB de stockage/mois). Stack actuelle :
> - 3 instances EC2 m5.xlarge (toujours allumées)
> - RDS PostgreSQL db.m5.large (production + replica)
> - S3 (50 TB, classe Standard)
> - Lambda pour conversion documents (PDF, DOCX)
> - CloudFront pour les assets
>
> Budget mensuel : ~$4500
> Mix énergétique : us-east-1 (Virginie, ~400 gCO2e/kWh)

### 5.2 Votre mission

Produire un **document de recommandation GreenOps** (`cas-pratique/recommandations.md`) couvrant :

#### 5.2.1 Audit (mesure)
- Quelles métriques mettre en place ?
- Quel objectif SCI fixer ?

#### 5.2.2 Quick wins (3 mois)
- Au moins **5 actions** à coût/risque faible
- Estimer le gain pour chaque (en gCO2e/mois ET en $)

#### 5.2.3 Optimisations structurantes (6 mois)
- Stratégie de stockage (S3 IA, Glacier, lifecycle policies)
- Rightsizing avec données réelles
- Migration vers une région plus propre (us-west-2 Oregon ~70 gCO2e/kWh)
- Carbon-aware scheduling pour la conversion de documents

#### 5.2.4 Transformations long terme (12-18 mois)
- Refonte serverless ?
- ARM (Graviton) pour 20% de moins d'énergie ?
- Compression intelligente côté client ?

### ✏️ Exercice 5 — Présenter votre recommandation

Format attendu :
- 4 pages Markdown
- Au moins 1 schéma d'architecture (mermaid accepté)
- Tableau de chiffrage CO2e + $
- Roadmap visuelle (gantt mermaid ou tableau)
- Section « **risques et anti-patterns** » que vous écartez

### 5.3 Discussion collective (30 min)

Les groupes présentent leurs recommandations (5 min chacun), confrontation des choix. **Aucune réponse n'est absolument correcte** — c'est l'argumentation qui compte.

---

## 📝 Partie 6 — Synthèse et rendu final (45 min)

### 6.1 Livrables — Pull Request finale du module

Le rendu de l'atelier 4 sert également de **synthèse du module entier** :

- [ ] Optimisations de la partie 2 (`v0` à `v5`) avec mesures
- [ ] Scheduler carbon-aware testé
- [ ] GitHub Actions opérationnelles sur votre fork
- [ ] Document de recommandation du cas pratique
- [ ] **Manifeste personnel GreenOps** : 1 page exposant les **3 convictions** que vous retenez de ce module et **3 choses que vous ferez différemment** dans vos futurs projets

### 6.2 Auto-évaluation finale

Compléter `auto-evaluation.md` (grille à 4 niveaux : ne sait pas / sait expliquer / sait faire / sait enseigner) sur 12 compétences clés du module.

---

## 📚 Pour aller plus loin

- 📘 [Building Green Software](https://www.oreilly.com/library/view/building-green-software/9781098150617/) (Anne Currie et al., O'Reilly)
- 🎓 [Green Software for Practitioners (Linux Foundation, gratuit)](https://training.linuxfoundation.org/training/green-software-for-practitioners-lfc131/)
- 🌐 [Green Software Foundation — Patterns](https://patterns.greensoftware.foundation/)
- 🛠️ [Cloud Carbon Footprint](https://www.cloudcarbonfootprint.org/)
- 📊 [SDIA — Roadmap Sustainable Digital Infrastructure](https://sdialliance.org/)

---

## 🔑 Notes pour l'enseignant

<details>
<summary>Cliquer pour afficher</summary>

### Timing détaillé

| Bloc | Durée |
|------|-------|
| Partie 1 (théorie + classif) | 45 min |
| Partie 2 (optimisation Python) | 1h30 |
| Pause déjeuner | 1h |
| Partie 3 (carbon-aware) | 1h30 |
| Partie 4 (CI/CD) | 1h |
| Partie 5 (cas pratique, en groupes) | 1h30 |
| Présentations + synthèse | 45 min |

### Points de vigilance

- **GitHub Actions free tier** : 2000 min/mois sur compte gratuit, large suffisant
- **Carbon Aware SDK** : peut être instable, prévoir un fallback (intensité statique)
- **Partie 5 est intentionnellement ouverte** : noter l'argumentation, pas la "bonne réponse"
- Pour groupes faibles : fournir un **template de recommandation** plus structuré

### Évaluation suggérée

| Item | Poids |
|------|-------|
| Optimisations partie 2 (mesures réelles) | 25% |
| Scheduler partie 3 fonctionnel | 15% |
| GitHub Actions partie 4 | 10% |
| Recommandation cas pratique | 30% |
| Présentation orale | 15% |
| Manifeste personnel | 5% |

### Variantes possibles

- Cas pratique : adapter au contexte (PME locale, ESN, secteur public…)
- Partie 2 : remplacer ETL Python par un cas plus proche du M2 (deep learning, web service)
- Inviter un retour d'expérience industriel en clôture

</details>
