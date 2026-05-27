# Partie 3 — Rightsizing avec VPA et HPA

> Exercice 3 de l'atelier 2 (voir `README.md` §3.4). À remplir après ~15 min d'attente VPA + un cycle complet de test k6.

## 1. Recommandations VPA par service

`kubectl describe vpa -n boutique` fournit pour chaque container un `target`, un `lowerBound` et un `upperBound`. Reporter :

| Service          | CPU actuel (req/lim) | CPU recommandé (target) | RAM actuel (req/lim) | RAM recommandé (target) |
|------------------|----------------------|-------------------------|----------------------|-------------------------|
| frontend         |                      |                         |                      |                         |
| productcatalog   |                      |                         |                      |                         |
| cartservice      |                      |                         |                      |                         |
| checkoutservice  |                      |                         |                      |                         |
| paymentservice   |                      |                         |                      |                         |
| shippingservice  |                      |                         |                      |                         |
| emailservice     |                      |                         |                      |                         |
| recommendation   |                      |                         |                      |                         |

## 2. Gain estimé en coût

Mesurer **avant / après** application des recommandations (attendre 30 min pour stabilisation OpenCost).

| Indicateur                  | Avant | Après | Variation |
|-----------------------------|-------|-------|-----------|
| Coût horaire `boutique` ($) |       |       |           |
| CPU requests total (vCPU)   |       |       |           |
| RAM requests total (GiB)    |       |       |           |
| Ratio requests / usage CPU  |       |       |           |
| Idle cost du cluster        |       |       |           |

## 3. HPA vs VPA pour `productcatalog`

> Argumenter en 4-6 phrases. Indices :
> - Charge constante ou variable ?
> - Latence sensible aux démarrages à froid ?
> - Limitations connues (HPA et VPA ne se cumulent pas sur la même métrique sans précaution) ?

Réponse :

…

## 4. Risques d'application aveugle du VPA en production

Lister au moins **4 risques** concrets, par exemple :

- [ ] Recommandations basées sur trop peu d'historique (premières heures)
- [ ] Saisonnalités non capturées (jour/nuit, week-end, soldes)
- [ ] Mode `Auto` qui **redémarre les pods** → indisponibilité si pas de PDB
- [ ] …
- [ ] …

Pour chaque risque, proposer **une protection** (ex. mode `Off` recommender, PDB, fenêtre de maintenance, garde-fou min/max).

---

> À reporter dans `RAPPORT.md` (section « Partie 3 »). Joindre une capture du `kubectl get hpa -n boutique -w` pendant le test k6.
