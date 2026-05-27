# Partie 2 — Premier diagnostic OpenCost

> Exercice 2 de l'atelier 2 (voir `README.md` §2.3). À remplir après ~5 min de stabilisation des métriques.

## Pré-requis

- OpenCost UI accessible sur `localhost:9090`
- App `boutique` déployée (`kubectl apply -k manifests/demo-app/`)
- Au moins 15 minutes de données collectées (sinon les agrégations 24h sont creuses)

## Questions

### 1. Namespace le plus consommateur

Dans OpenCost UI → **Allocations** → grouper par `namespace`, période **Last 24h**.

- Namespace : ____
- Coût estimé sur 24 h : ____ $
- Part du coût total cluster : ____ %

### 2. Pire ratio Requests / Usage

Pour chaque workload du namespace `boutique`, relever :

| Workload | CPU requests | CPU usage moyen | Ratio req/usage |
|----------|--------------|-----------------|-----------------|
|          |              |                 |                 |
|          |              |                 |                 |
|          |              |                 |                 |

- **Pire ratio** : ____ (workload : ____)
- Interprétation (sur-provisionnement, sous-utilisation, autre ?) :

### 3. Service "idle"

Un service est déployé mais **ne reçoit aucune requête** (regarder la métrique réseau ou les logs).

- Service identifié : ____
- Indice utilisé pour le diagnostic :
- Coût mensuel projeté si on le laisse tourner :

### 4. Capture d'écran

> Joindre dans `RAPPORT.md` la capture de la vue **Allocations**, filtrée sur les 24 dernières heures, groupée par namespace.

Chemin du fichier joint : `screenshots/opencost-allocations-24h.png`

---

## Hypothèses et limites

- Les prix utilisés par OpenCost en local viennent du `customPricing` (cluster Kind). Ce sont **des estimations**, pas des factures.
- Avec moins de 24h de données, OpenCost peut afficher des valeurs partielles : noter explicitement la fenêtre réelle.

---

> À reporter dans `RAPPORT.md` (section « Partie 2 »).
