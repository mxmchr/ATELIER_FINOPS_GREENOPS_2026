# Partie 3 — Spatial shifting : déplacer la charge vers les régions vertes

> Support de lecture pour la §3.4 du README. À lire avant l'exercice 3 (scheduler carbon-aware).

Le **temporal shifting** (déplacer dans le temps) est facile pour les batch jobs. Le **spatial shifting** (déplacer dans l'espace, vers une région à mix électrique plus propre) est plus puissant — un facteur **10×** d'intensité carbone entre `eu-north-1` (Suède) et `ap-south-1` (Inde) — mais bien plus contraint.

---

## 1. Le principe

Un même workload exécuté dans deux régions différentes émet des quantités très différentes :

```
emissions = energy_kWh × intensity_gCO2e_per_kWh

energy_kWh est ~ identique (le code est le même).
intensity varie de 30 à 800 gCO2e/kWh selon la région.
```

Exemples d'écarts entre régions d'un même cloud (ordre de grandeur 2024) :

| Région AWS               | Pays    | Intensité (~gCO2e/kWh) |
|--------------------------|---------|------------------------|
| `eu-north-1`             | Suède   | 30                     |
| `eu-west-3`              | France  | 60                     |
| `us-west-2`              | Oregon  | 70                     |
| `eu-central-1`           | Allemagne | 350                  |
| `us-east-1`              | Virginie | 400                   |
| `ap-southeast-2`         | Australie | 600                  |
| `ap-south-1`             | Inde    | 700                    |

➡️ Migrer un workload `us-east-1 → us-west-2` (même continent, ~6× moins carboné) peut diviser les émissions du même facteur **sans** changer une ligne de code applicatif.

---

## 2. Architecture multi-région avec routage carbon-aware

```
                    ┌──────────────────┐
                    │   Edge / CDN     │
                    │  (Cloudflare,    │
                    │   Fastly…)       │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                │   Carbon-aware router   │
                │   (Lambda@Edge ou       │
                │    custom service)      │
                └────────────┬────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
     ┌────────────┐   ┌────────────┐   ┌────────────┐
     │  Région A  │   │  Région B  │   │  Région C  │
     │ (Stockholm)│   │ (Oregon)   │   │ (Sydney)   │
     │  30 gCO2e  │   │  70 gCO2e  │   │  600 gCO2e │
     └────────────┘   └────────────┘   └────────────┘
            ▲                ▲                ▲
            └────────────────┴────────────────┘
                       │
            État partagé : DB répliquée,
            cache distribué, file de jobs
```

Le **routeur** interroge les API d'intensité carbone (ElectricityMaps, WattTime, Carbon Aware SDK) et envoie le trafic vers la région la plus verte parmi celles **éligibles** (cf. limites légales plus bas).

### Plusieurs modèles d'implémentation

| Modèle                    | Quoi                                                      | Limites                              |
|---------------------------|-----------------------------------------------------------|--------------------------------------|
| **Routing par requête**   | Chaque requête HTTP va vers la région la plus verte au moment T | Latence réseau, cache cassé        |
| **Job dispatch**          | Un orchestrateur (Argo, Airflow) lance le job dans la région la plus verte | Réservé aux jobs offline, pas web  |
| **Bursting**              | Région principale fixe, **débordement** vers une région verte aux pics | Compromis raisonnable, ne nécessite pas de réplication totale |
| **Migration périodique**  | Bascule "froide" d'une région à une autre toutes les 24h-7j | Lent, mais marche pour les workloads peu critiques |

---

## 3. Cas concret : Google et le carbon-aware compute

Google a publié plusieurs travaux ([Google Sustainability blog](https://blog.google/outreach-initiatives/sustainability/)) sur le **temporal shifting** (décaler les batch ML training à l'intérieur d'un datacenter) et le **spatial shifting** (déplacer des charges flexibles entre régions).

Points clés de leur retour d'expérience :

- Sur des **batch non temps-réel** (training, indexation, reporting), ils annoncent jusqu'à **40 % de réduction d'émissions** sans dégrader le SLA.
- Le **temporal shifting** est plus simple à mettre en œuvre que le spatial — il n'y a pas de question de résidence des données.
- Le spatial shifting est utilisé surtout pour **les charges internes** (pipelines de données, training de modèles), **pas** pour les services utilisateurs.
- Ils combinent les deux : **"où ET quand"** plutôt que l'un ou l'autre.

> 📄 À lire : *"Carbon-aware computing for datacenters"* (Radovanović et al., 2021), [arXiv:2106.11750](https://arxiv.org/abs/2106.11750).

---

## 4. Microsoft : Carbon Aware Tools

Microsoft via la Green Software Foundation propose une **suite open source** :

- **Carbon Aware SDK** — l'API utilisée en partie 3 de cet atelier.
- **Carbon Aware Kubernetes operator** — déclenche les Jobs / CronJobs uniquement dans les fenêtres optimales.
- **Carbon Aware GitHub Action** — utilisée en partie 4.

Référentiel principal : [github.com/Green-Software-Foundation](https://github.com/Green-Software-Foundation).

---

## 5. Limites légales et opérationnelles

### Résidence des données (RGPD, etc.)

- Les **données personnelles européennes** doivent rester en UE (ou pays adéquat). Pas question de basculer en Inde même pour 700 gCO2e d'économie.
- Certains secteurs (santé, banque, défense) ont des contraintes **encore plus strictes**.
- Le routage carbon-aware doit **filtrer la liste des régions éligibles** avant d'optimiser.

### Latence utilisateur

- Bascule Europe → US : +100-150 ms aller-retour. Inacceptable pour la plupart des sites web.
- Limite : seuls les workloads **insensibles à la latence** (batch, async, queues) sont déplaçables sans dégradation perçue.

### Coût de transfert

- Transférer des données entre régions cloud coûte **~0,02-0,09 $/Go**. Un job qui doit lire 1 To de données distantes annule rapidement le bénéfice carbone.
- Bonne pratique : **déplacer le compute vers la donnée**, pas l'inverse. Donc le spatial shifting est surtout pertinent quand les **données sont déjà répliquées** ou **peu volumineuses**.

### Souveraineté

- Certains clients exigent contractuellement une région précise.
- Réglementation **"sovereign cloud"** (France, Allemagne) en pleine évolution.

### Effet rebond

- Si **tous les acteurs** routent leur charge vers la Suède, on **sature les datacenters suédois** → expansion → embodied carbon supplémentaire. La décision optimale individuelle peut être sub-optimale au niveau système.

---

## 6. Heuristique de décision

Pour un workload donné, est-il candidat au spatial shifting ?

```
Le workload est-il temps-réel utilisateur ?
├── OUI → Non éligible au spatial shifting (mais OK pour temporal léger)
└── NON → est-il flexible sur la résidence des données ?
        ├── NON → Limité à la zone autorisée (peut faire du temporal)
        └── OUI → est-il I/O ou compute ?
                ├── I/O lourd → déplacer la donnée d'abord (coûteux)
                └── Compute → CANDIDAT IDÉAL → spatial shifting OK
```

Bons candidats typiques :
- Entraînements ML sur datasets publics ou répliqués
- Conversion d'images / vidéos batch
- Reporting analytique sur entrepôt déjà multi-région
- Génération de pages statiques pour CDN

Mauvais candidats :
- API utilisateur synchrone
- Workloads touchant à des données personnelles UE
- Bases OLTP (cohérence forte requise)

---

## Pour aller plus loin

- 📘 [Carbon Aware Computing Whitepaper (GSF)](https://greensoftware.foundation/articles/whitepaper-carbon-aware-computing)
- 📊 [Cloud Carbon Footprint](https://www.cloudcarbonfootprint.org/) — intensité par région cloud
- 🛠️ [WattTime API](https://www.watttime.org/) — alternative à ElectricityMaps, granularité réseau US fine
- 📄 *"The carbon footprint of machine learning training will plateau, then shrink"* (Patterson et al., Google, 2022) — analyse spatiale/temporelle du ML
