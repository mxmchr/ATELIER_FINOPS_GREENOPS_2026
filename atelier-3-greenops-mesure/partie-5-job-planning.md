# Partie 5 — Job planning carbon-aware

> Exercice 6 de l'atelier 3 (voir `README.md` §5). À compléter après avoir implémenté `best_window` dans `notebooks/carbon-intensity.ipynb`.

## Contexte

Un job de batch quotidien de **2 heures** doit être lancé une fois par jour. La fenêtre est libre (toute heure de la journée acceptable). Objectif : **minimiser les émissions** en exploitant les variations diurnes de l'intensité carbone.

Méthode : sur 7 jours d'historique ElectricityMaps, calculer la moyenne horaire de l'intensité carbone, puis trouver la fenêtre glissante de 2 h **la plus basse**.

## Signature attendue

```python
def best_window(zone: str, duration_hours: int, lookback_days: int = 7) -> dict:
    """
    Retourne :
    {
      "start_hour": int,          # heure de début optimale (0-23)
      "end_hour": int,            # heure de fin (peut être > 23 si wrap)
      "avg_intensity": float,     # gCO2e/kWh moyenne sur la fenêtre
      "vs_daily_avg": float,      # ratio vs moyenne journalière (ex. 0.65 = -35%)
    }
    """
```

## Résultats par zone

Reporter ici après exécution :

| Zone     | Fenêtre optimale (h locales) | Intensité moyenne (gCO2e/kWh) | Moyenne journalière | Économie relative |
|----------|------------------------------|-------------------------------|---------------------|-------------------|
| FR       |                              |                               |                     |                   |
| DE       |                              |                               |                     |                   |
| PL       |                              |                               |                     |                   |
| SE       |                              |                               |                     |                   |
| US-CAL   |                              |                               |                     |                   |

## Observations attendues

À commenter en 1-2 paragraphes :

- **FR** : la fenêtre optimale se situe-t-elle plutôt la nuit (nucléaire dominant, peu de variabilité) ou en milieu de journée ?
- **DE / US-CAL** : observe-t-on un **creux solaire de midi** ? De combien (%) baisse l'intensité ?
- **PL** : la marge de manœuvre est-elle significative ou le mix charbon écrase-t-il tout ?
- **SE** : que vaut le gain quand l'intensité de base est déjà très basse ? Est-ce que l'effort de carbon-aware scheduling est rentable ici ?

## Impact à l'échelle

Si le job consomme **5 kWh par exécution** et qu'il tourne **365 jours/an** :

| Zone   | Émissions annuelles "naive" (kg CO2e) | Émissions annuelles "optimal" (kg CO2e) | Gain (kg) |
|--------|---------------------------------------|------------------------------------------|-----------|
| FR     |                                       |                                          |           |
| DE     |                                       |                                          |           |
| PL     |                                       |                                          |           |
| SE     |                                       |                                          |           |
| US-CAL |                                       |                                          |           |

> Hypothèse "naive" : exécution à **midi heure locale** chaque jour (heuristique habituelle).

## Limites

- L'historique 7 jours n'est qu'**une approximation** ; la prévision réelle (ElectricityMaps forecast API ou Carbon Aware SDK) serait plus juste.
- Le job suppose une **flexibilité totale** sur l'heure de démarrage — irréaliste si le résultat doit être disponible à 8h.
- Si **plusieurs équipes** exécutent leurs jobs dans la même fenêtre optimale, on **déplace le pic** au lieu de l'éliminer (effet rebond).
- Le **demand response** réel des opérateurs prend en compte beaucoup plus que la moyenne historique (météo, marché spot…).

---

> À reporter dans `RAPPORT.md` (section « Partie 5 »). Joindre les courbes superposées (matplotlib OK) issues du notebook.
