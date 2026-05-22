# Ateliers FinOps & GreenOps

## 🎯 Objectifs pédagogiques

Ce module propose **4 ateliers** pour comprendre et mettre en pratique les disciplines **FinOps** (gestion financière du cloud) et **GreenOps** (optimisation environnementale du numérique).

Chaque atelier est conçu sous forme de **tutoriel guidé pas à pas**, exécutable intégralement dans **GitHub Codespaces**, sans installation locale.

## 📚 Prérequis

- Familiarité avec **Docker** et **Kubernetes** (manifests YAML, kubectl, pods/deployments/services)
- Bases de **Git** et **GitHub** (fork, clone, pull request)
- Notions de **Python** et de lecture de fichiers JSON/CSV
- Un **compte GitHub** (l'offre gratuite Codespaces de 60h/mois suffit)

## 🗂️ Structure du module

| # | Atelier | Thème | Durée | Outils principaux |
|---|---------|-------|-------|-------------------|
| 1 | [FinOps Fondamentaux](./atelier-1-finops-fondamentaux/) | Visibilité et allocation des coûts cloud | Python, Pandas, simulateur AWS Cost Explorer |
| 2 | [FinOps sur Kubernetes](./atelier-2-finops-kubernetes/) | Cost monitoring et rightsizing K8s | Kind, OpenCost, Prometheus, Grafana |
| 3 | [GreenOps — Mesurer](./atelier-3-greenops-mesure/) | Empreinte carbone et énergétique du code | CodeCarbon, Scaphandre, Kepler |
| 4 | [GreenOps — Optimiser](./atelier-4-greenops-optimisation/) | Éco-conception logicielle et infrastructure | Carbon-aware SDK, GitHub Actions, Python profiling |

## 🚀 Démarrage rapide

1. **Forker** ce dépôt sur votre compte GitHub
2. Cliquer sur le bouton **Code → Codespaces → Create codespace on main**
3. Attendre 2-3 minutes que l'environnement se construise
4. Ouvrir le `README.md` de l'atelier du jour et suivre les instructions

> ⚠️ Chaque atelier dispose d'un `devcontainer.json` spécifique. Si vous changez d'atelier, recréez un Codespace pour bénéficier des bons outils préinstallés.

## 🧭 Progression recommandée

```
Atelier 1 (FinOps fondamentaux)
        ↓
Atelier 2 (FinOps Kubernetes) ──┐
        ↓                       │ (parallélisables)
Atelier 3 (GreenOps mesure) ────┘
        ↓
Atelier 4 (GreenOps optimisation)
```

Les ateliers 2 et 3 peuvent être inversés ou menés en parallèle selon les groupes.

## 📊 Évaluation

| Modalité | Pondération | Description |
|----------|-------------|-------------|
| Rendu de chaque atelier (Pull Request) | 4 × 15% | Captures, fichiers produits, réponses aux questions |
| Mini-projet final | 30% | Optimisation FinOps **ET** GreenOps d'une application au choix |
| Présentation orale | 10% | 10 min + 5 min de questions |

