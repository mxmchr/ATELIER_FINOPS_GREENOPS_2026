# Partie 2 — Comparaison de deux algorithmes

> Exercice 2 de l'atelier 3 (voir `README.md` §2.3). À compléter après avoir exécuté `examples/02-algo-comparison.py` (5 runs par version).

## Protocole

- 5 exécutions de **`search_linear`** (O(n·m))
- 5 exécutions de **`search_set`** (O(n+m))
- Mêmes données d'entrée (haystack = 100 000 entiers aléatoires, needles = 1 000 entiers)
- Mesure par `EmissionsTracker` distinct pour chaque fonction
- Pays par défaut : `country_iso_code="FRA"` (~60 gCO2e/kWh)

## Résultats moyens

| Version           | Temps moyen (s) | Énergie moyenne (kWh) | Émissions moyennes (g CO2e) |
|-------------------|-----------------|-----------------------|-----------------------------|
| A — `search_linear` |                 |                       |                             |
| B — `search_set`    |                 |                       |                             |
| **Ratio A/B**       |                 |                       |                             |

> Reporter aussi l'écart-type entre runs si la variance est notable.

## 2.4 — Variation par localisation

Mêmes runs, **uniquement sur `search_linear`**, en faisant varier `country_iso_code` :

| Pays      | Intensité (~gCO2e/kWh) | Énergie (kWh) | Émissions (g CO2e) |
|-----------|------------------------|---------------|--------------------|
| France    | 60                     |               |                    |
| Pologne   | 700                    |               |                    |
| Suède     | 40                     |               |                    |

> L'énergie devrait être quasi identique (même calcul) — c'est **l'intensité du mix électrique** qui fait varier les émissions d'un facteur **10-20**.

## Réflexion : impact à l'échelle de la production

Si la fonction `search_*` est appelée **1 million de fois par jour** :

- Émissions annuelles de la version A : ___ kg CO2e/an
- Émissions annuelles de la version B : ___ kg CO2e/an
- **Économie annuelle** (A → B) : ___ kg CO2e/an

Équivalences pour donner de l'intuition (sources : ADEME 2024) :

| Référence                | gCO2e |
|--------------------------|-------|
| 1 km en voiture thermique | ~150  |
| 1 km en TGV (France)     | ~3    |
| 1 mail avec PJ 1 Mo      | ~20   |
| 1 h de visio HD          | ~150  |

➡️ L'économie correspond à ____ km en voiture / ____ h de visio.

## Limites et biais à mentionner

- Codespaces = VM → pas d'accès RAPL → CodeCarbon est en **mode estimation TDP**.
- L'intensité carbone réelle varie dans la journée (cf. partie 5).
- Le coût **embodied** des serveurs n'est **pas** compté ici.

---

> À reporter dans `RAPPORT.md` (section « Partie 2 »).
