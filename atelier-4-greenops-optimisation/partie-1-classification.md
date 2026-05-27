# Partie 1 — Classification selon les 8 principes GSF

> Exercice 1 de l'atelier 4 (voir `README.md` §1.3). À compléter en binôme.

## Rappel des 8 principes

| # | Principe              | En une phrase                                                  |
|---|------------------------|----------------------------------------------------------------|
| 1 | Carbon Efficiency      | Émettre le moins possible par fonction réalisée                |
| 2 | Energy Efficiency      | Consommer le moins d'énergie possible                          |
| 3 | Carbon Awareness       | Faire plus quand l'élec est "verte", moins quand elle est "sale"|
| 4 | Hardware Efficiency    | Utiliser au max le matériel existant, prolonger sa durée de vie|
| 5 | Measurement            | Ce qui n'est pas mesuré ne peut être amélioré                  |
| 6 | Climate Commitments    | S'aligner sur des engagements vérifiables (Net Zero, SBTi)     |
| 7 | Networking             | Réduire la donnée transportée et la distance parcourue         |
| 8 | Demand Shifting        | Décaler la demande dans le temps ou l'espace                   |

## Consigne

Pour chaque proposition d'amélioration ci-dessous :

1. Cocher **le ou les principes** auxquels elle se rattache (plusieurs possibles).
2. Justifier brièvement (1 ligne).
3. Identifier le **principe dominant** si plusieurs s'appliquent.

## 15 propositions à classer

| # | Proposition | Principe(s) | Principe dominant | Justification |
|---|-------------|-------------|-------------------|---------------|
| 1 | Remplacer une boucle Python par une opération vectorisée NumPy | | | |
| 2 | Lancer les entraînements ML la nuit, quand le mix électrique français a plus de nucléaire et moins de gaz | | | |
| 3 | Migrer le cluster Kubernetes de `us-east-1` (Virginie, ~400 gCO2e/kWh) vers `eu-north-1` (Stockholm, ~30 gCO2e/kWh) | | | |
| 4 | Refactoriser les images Docker (multi-stage build, base `alpine`) — passe de 800 Mo à 80 Mo | | | |
| 5 | Mettre en place un **dashboard SCI** par service applicatif et le suivre en revue mensuelle | | | |
| 6 | Prolonger de 2 ans la durée d'usage des laptops avant renouvellement | | | |
| 7 | Activer la compression Brotli sur le CDN | | | |
| 8 | Adopter des objectifs **SBTi 1.5°C** validés par un tiers, publier le rapport annuel | | | |
| 9 | Remplacer un service tournant 24/7 sur EC2 par une fonction Lambda à la demande | | | |
| 10 | Convertir les API REST en GraphQL pour ne renvoyer que les champs utilisés par le client | | | |
| 11 | Compresser les images uploadées par les utilisateurs côté client avant envoi | | | |
| 12 | Passer la flotte de serveurs d'AMD EPYC Gen 2 à Gen 4 (perf/W +35%) | | | |
| 13 | Mettre en cache CDN les pages les plus consultées (TTL 1h) | | | |
| 14 | Mettre en place CodeCarbon dans la CI pour mesurer chaque PR | | | |
| 15 | Configurer la GitHub Action Carbon-Aware qui décale les builds nocturnes vers la fenêtre la plus verte | | | |

## Pistes de classement (à valider en correction)

> *Spoilers volontaires : la grille suivante est une **réponse-type**, à ne consulter qu'après avoir cherché par soi-même.*

<details>
<summary>Cliquer pour afficher la grille de correction</summary>

| #  | Principe dominant         | Autres principes activés                           |
|----|---------------------------|----------------------------------------------------|
| 1  | 2 — Energy Efficiency     | 1                                                  |
| 2  | 3 — Carbon Awareness      | 8                                                  |
| 3  | 8 — Demand Shifting (spatial) | 1, 3                                           |
| 4  | 7 — Networking            | 4 (moins de stockage = moins d'usure)              |
| 5  | 5 — Measurement           | 6                                                  |
| 6  | 4 — Hardware Efficiency   | 6                                                  |
| 7  | 7 — Networking            | 2                                                  |
| 8  | 6 — Climate Commitments   | —                                                  |
| 9  | 2 — Energy Efficiency     | 1, 4 (densité hardware côté provider)              |
| 10 | 7 — Networking            | 1                                                  |
| 11 | 7 — Networking            | 2                                                  |
| 12 | 4 — Hardware Efficiency   | 2 (perf/W meilleure)                               |
| 13 | 7 — Networking            | 2                                                  |
| 14 | 5 — Measurement           | —                                                  |
| 15 | 3 — Carbon Awareness      | 8 (temporal shifting)                              |

</details>

## Réflexion

Après classement, répondre en 4-6 phrases :

- Quel(s) principe(s) sont **les plus présents** dans la liste ? Pourquoi à votre avis ?
- Quel(s) principe(s) ne sont **pas du tout** illustrés par les 15 propositions ? Pourquoi ?
- Lequel des 8 principes vous paraît le **plus difficile à activer** dans un contexte M2 / projet étudiant ?

---

> À reporter dans `RAPPORT.md` (section « Partie 1 »).
