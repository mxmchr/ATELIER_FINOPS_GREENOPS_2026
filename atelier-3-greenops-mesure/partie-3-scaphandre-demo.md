# Partie 3 — Scaphandre : démo et lecture commentée

> Support de lecture pour la §3.2 du README. À lire en remplacement de la manipulation directe (Codespaces ne donne pas accès aux compteurs RAPL).

## Pourquoi cette partie est une démo, pas une manipulation

Scaphandre lit l'énergie consommée par le CPU via les compteurs **RAPL** (*Running Average Power Limit*) exposés par Intel et AMD. Ces compteurs sont accessibles sur **bare-metal Linux** mais sont **masqués** dans la plupart des VMs (Azure, AWS, GCP) — y compris les VMs hôtes de GitHub Codespaces.

Conséquences :
- Dans Codespaces, lancer `scaphandre stdout` retourne le plus souvent `0 W` ou une erreur `/sys/class/powercap/intel-rapl: permission denied`.
- L'**exporter Prometheus** démarre mais ne publie aucune mesure exploitable.
- Cette partie sert donc à **comprendre l'architecture** d'un outil de mesure système et à **savoir quand on peut l'utiliser**.

---

## 1. Architecture de Scaphandre

```
        ┌─────────────────────────────────────────────────────┐
        │                Espace utilisateur                   │
        │                                                     │
        │   ┌──────────────┐     ┌─────────────────────────┐  │
        │   │  scaphandre  │ ──▶ │  Exporters (stdout,     │  │
        │   │   (daemon)   │     │  prometheus, json,      │  │
        │   │              │     │  warp10, qemu)          │  │
        │   └──────┬───────┘     └─────────────────────────┘  │
        │          │                                          │
        └──────────┼──────────────────────────────────────────┘
                   │
                   ▼   lecture périodique (par défaut 2 s)
        ┌──────────────────────────────────────────────────┐
        │              Noyau Linux                         │
        │  /sys/class/powercap/intel-rapl/intel-rapl:0/    │
        │      └── energy_uj  ← compteur cumulatif (µJ)    │
        │  /proc/<pid>/stat   ← temps CPU par processus    │
        │  /proc/<pid>/cgroup ← attribution container      │
        └──────────────────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────────────────────┐
        │   CPU — Model-Specific Registers (MSR)           │
        │   RAPL domains : PKG, CORE, UNCORE, DRAM         │
        └──────────────────────────────────────────────────┘
```

### Les domaines RAPL

| Domaine  | Couvre                                   | Toujours dispo ? |
|----------|------------------------------------------|------------------|
| `PKG`    | Tout le package processeur (cores + cache + IO interne) | Oui (Intel ≥ Sandy Bridge, AMD ≥ Zen) |
| `CORE`   | Les cœurs uniquement                     | Souvent          |
| `UNCORE` | iGPU intégré                             | Sur clients only |
| `DRAM`   | Barrettes mémoire                        | Serveurs Intel surtout |

Scaphandre **somme les domaines disponibles** et calcule un delta entre deux lectures pour obtenir une puissance instantanée (W).

### Attribution par processus / container

L'énergie totale lue ne distingue pas qui consomme quoi. Scaphandre **répartit au prorata du temps CPU** mesuré dans `/proc/<pid>/stat` sur la même fenêtre.

```
power(pid) = power_pkg × (cpu_time(pid) / cpu_time(total))
```

Cette répartition est **approximative** : elle suppose que tous les processus ont le même profil énergétique par cycle CPU, ce qui n'est vrai qu'au premier ordre (les opérations vectorielles AVX-512 consomment plus que de l'arithmétique scalaire).

---

## 2. L'exporter Prometheus

Sur bare-metal, Scaphandre lance un endpoint HTTP :

```bash
scaphandre prometheus --address 0.0.0.0 --port 9100
```

Et expose des métriques au format Prometheus :

```
# HELP scaph_host_power_microwatts Power consumption of the host, measured on the same scale.
# TYPE scaph_host_power_microwatts gauge
scaph_host_power_microwatts 42150000

# HELP scaph_process_power_consumption_microwatts Power consumption per process
# TYPE scaph_process_power_consumption_microwatts gauge
scaph_process_power_consumption_microwatts{exe="/usr/bin/python3",cmdline="python train.py",pid="12345"} 8230000
```

Conventions :
- **Tout est en microwatts** (µW) → diviser par 10⁶ pour avoir des W.
- Une **gauge** par processus actif → la cardinalité peut exploser sur un host chargé. En production, filtrer par regex sur `exe` ou `cmdline`.

### Exemple de requêtes PromQL utiles

```promql
# Puissance totale du host (W)
scaph_host_power_microwatts / 1e6

# Top 10 processus consommateurs sur la dernière heure (Wh)
topk(10, sum by (exe)(avg_over_time(scaph_process_power_consumption_microwatts[1h])) / 1e6)

# Énergie cumulée par container (Wh) — via labels cgroup
sum by (container_label_io_kubernetes_container_name) (
  rate(scaph_process_power_consumption_microwatts[5m])
) * 5 * 60 / 1e6 / 3600
```

---

## 3. Dashboard Grafana exemple

Le projet Scaphandre publie un dashboard officiel ([JSON](https://github.com/hubblo-org/scaphandre/tree/main/docs_src/tutorials)). Les panels typiques :

| Panel                          | Métrique                                                   |
|--------------------------------|------------------------------------------------------------|
| **Host power (W)**             | `scaph_host_power_microwatts / 1e6`                        |
| **Top 5 processes**            | `topk(5, scaph_process_power_consumption_microwatts) / 1e6`|
| **Énergie cumulée (Wh)**       | `sum(increase(scaph_host_energy_microjoules[$__range])) / 3.6e9` |
| **CO2e instantané**            | `host_power_W × intensity_gCO2e_per_kWh / 1000` (variable Grafana) |
| **Par container Kubernetes**   | labels `container_label_io_kubernetes_*`                   |

Capture-type (vue d'ensemble) :

```
┌────────────────────────────────────────────────────────────┐
│  Host power                42 W   ▁▂▂▃▅▅▆▇▆▅▃▂▂           │
│  Energy last 1h             38 Wh                          │
│  CO2e last 1h               2.3 g  (FR mix 60 gCO2e/kWh)   │
├────────────────────────────────────────────────────────────┤
│  Top 5 processes (avg W, last 5 min)                       │
│    python train.py            8.2 W                        │
│    chrome --type=renderer     3.1 W                        │
│    docker-proxy               1.0 W                        │
│    sshd                       0.4 W                        │
│    systemd-journald           0.3 W                        │
└────────────────────────────────────────────────────────────┘
```

---

## 4. Ce qu'on peut faire en Codespaces malgré tout

Pour donner une intuition aux étudiants sans bare-metal :

1. **`turbostat`** — partiellement utilisable, lit certains compteurs. À tester :
   ```bash
   sudo turbostat --interval 5 sleep 30
   ```
2. **`powerstat`** — outil Ubuntu officiel, peut lire RAPL ou estimer par d'autres moyens :
   ```bash
   sudo powerstat -R -d 0 5
   ```
3. **Comparer** avec ce que CodeCarbon estime sur le même workload (partie 2). Discuter des écarts.

Documenter ce qui fonctionne et ce qui retourne `unavailable` dans le rapport — c'est en soi un livrable pédagogique.

---

## 5. Quand utiliser Scaphandre, quand utiliser autre chose ?

| Contexte                                | Outil recommandé             | Pourquoi                                   |
|-----------------------------------------|------------------------------|--------------------------------------------|
| Bare-metal Linux, mesure fine processus | **Scaphandre**               | Accès RAPL direct, exporter Prometheus     |
| Application Python isolée               | **CodeCarbon**               | Instrumentation par code, multi-OS         |
| Cluster Kubernetes                      | **Kepler** (partie 4)        | Intégration native K8s, modèle ML fallback |
| Mesure rapide en CLI (un binaire)       | **powerstat / turbostat**    | Pré-installé sur la plupart des distros    |
| Estimation cloud sans accès host        | **Cloud Carbon Footprint**, modèle Boavizta | Pas de mesure → estimation              |

---

## Pour aller plus loin

- 📘 Documentation officielle : [hubblo-org/scaphandre](https://github.com/hubblo-org/scaphandre)
- 📄 Spec RAPL : *Intel SDM Vol 3B, Chapter 14* (Power and Thermal Management)
- 🎥 Conférence Hubblo à FOSDEM (chercher "Scaphandre FOSDEM" sur YouTube)
- 🔗 Comparaison Scaphandre vs Kepler vs CodeCarbon : article du blog [Boavizta](https://boavizta.org/blog)
