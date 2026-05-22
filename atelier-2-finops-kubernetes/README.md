# Atelier 2 — FinOps sur Kubernetes : Coûts, rightsizing et autoscaling

> **Durée** : 6-7h • **Niveau** : M2 Informatique • **Format** : tutoriel guidé pas à pas

## 🎯 Objectifs d'apprentissage

À la fin de cet atelier, vous saurez :

1. Comprendre pourquoi **Kubernetes complique le FinOps** (multi-tenant, ressources partagées)
2. Déployer **OpenCost** sur un cluster Kubernetes local et lire ses métriques
3. Identifier le **sur-provisionnement** de pods (requests/limits trop élevés)
4. Implémenter un **HPA** (Horizontal Pod Autoscaler) et un **VPA** (Vertical Pod Autoscaler)
5. Choisir entre **Spot/Preemptible**, **Reserved** et **On-Demand** sur des charges réalistes
6. Construire un **rapport de showback** par namespace/équipe

## 🧰 Outils utilisés

- **GitHub Codespaces** (environnement de travail)
- **Kind** (Kubernetes in Docker, cluster local)
- **kubectl, helm**
- **OpenCost** (cost monitoring open-source)
- **Prometheus + Grafana**
- **Kube-prometheus-stack** (pour les métriques)
- **k6** (générateur de charge pour les tests d'autoscaling)

## 🚀 Démarrer le Codespace

Le `devcontainer.json` de cet atelier installe automatiquement Docker-in-Docker, kubectl, helm, kind et k6. Au premier lancement :

```bash
cd atelier-2-finops-kubernetes
./scripts/00-setup-cluster.sh
```

Le script crée un cluster Kind à 3 nœuds (1 control-plane + 2 workers) avec des **labels d'instance simulés** (`node.kubernetes.io/instance-type=t3.medium`, etc.) pour qu'OpenCost puisse estimer des coûts AWS.

Vérifier :
```bash
kubectl get nodes -o wide --show-labels
```

---

## 📖 Partie 1 — Le défi FinOps de Kubernetes (45 min)

### 1.1 Pourquoi Kubernetes complique tout

Sur une VM, c'est simple : 1 VM = 1 ligne de facture = 1 propriétaire.

Sur Kubernetes :
- **N pods de M équipes** partagent un même nœud
- Les **ressources sont demandées (`requests`)** mais peuvent en consommer plus (`limits`)
- Le **scheduler** déplace les pods entre nœuds
- Les **services partagés** (ingress, monitoring, DNS) servent tout le monde

➡️ La question « combien coûte l'application X ? » devient **non triviale**.

### 1.2 Les concepts clés

| Concept | Définition | Impact FinOps |
|---------|-----------|---------------|
| **Requests** | Ressources réservées par le scheduler | Détermine la capacité achetée |
| **Limits** | Plafond d'utilisation | Protège du noisy neighbor |
| **Utilization** | Conso réelle / capacité | Mesure du gaspillage |
| **Efficiency** | Requests / Capacité | Densité du cluster |
| **Idle cost** | Coût des ressources non allouées | Coût « invisible » |

### 1.3 Les méthodes d'allocation OpenCost

OpenCost calcule un coût par pod via plusieurs stratégies. Lire la doc :
[https://www.opencost.io/docs/specification](https://www.opencost.io/docs/specification)

La formule de base :

```
cost(pod) = cpu_cost × max(cpu_request, cpu_usage) × duration
         + ram_cost × max(ram_request, ram_usage) × duration
         + storage_cost × storage_used × duration
         + network_cost × network_egress
```

### ✏️ Exercice 1 — Cas d'école

Compléter le tableau dans `partie-1-cas-decole.md` :

> Un nœud `t3.large` coûte 0.0832 $/h. Il dispose de 2 vCPU et 8 GiB de RAM.
> Sur ce nœud tournent :
> - Pod A : request 500m CPU, 1Gi RAM, conso réelle 200m / 700Mi
> - Pod B : request 1000m CPU, 2Gi RAM, conso réelle 1500m / 1.5Gi (dépasse les requests!)
> - Pod C : request 200m CPU, 500Mi RAM, conso réelle 50m / 200Mi
>
> Calculer le coût horaire alloué à chaque pod ET le coût « idle » du nœud.

---

## 🛠️ Partie 2 — Déployer OpenCost et Prometheus (1h30)

### 2.1 Installation via Helm

```bash
# Ajouter les repos Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add opencost https://opencost.github.io/opencost-helm-chart
helm repo update

# Installer kube-prometheus-stack (Prometheus + Grafana)
kubectl create namespace monitoring
helm install kps prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values manifests/prometheus-values.yaml \
  --wait

# Installer OpenCost
helm install opencost opencost/opencost \
  --namespace opencost --create-namespace \
  --values manifests/opencost-values.yaml \
  --wait
```

### 2.2 Accéder aux UIs

Depuis le terminal Codespaces, ouvrir 3 onglets :

```bash
# Onglet 1 — Grafana (admin / prom-operator)
kubectl port-forward -n monitoring svc/kps-grafana 3000:80

# Onglet 2 — OpenCost UI
kubectl port-forward -n opencost svc/opencost 9090:9090

# Onglet 3 — Prometheus
kubectl port-forward -n monitoring svc/kps-kube-prometheus-stack-prometheus 9091:9090
```

Codespaces ouvrira automatiquement les ports dans l'onglet "Ports". Cliquer pour ouvrir.

### 2.3 Premier tour d'horizon

Dans **OpenCost UI** (port 9090) :
- Aller dans **Allocations**
- Grouper par `namespace`
- Période : *Last 24h*

Initialement le cluster est presque vide. Déployer maintenant l'application de démo :

```bash
kubectl apply -k manifests/demo-app/
```

L'application `boutique` simule un site e-commerce avec 8 microservices, dont certains **volontairement mal dimensionnés**.

Attendre 5 minutes que les métriques se stabilisent, puis refaire un tour dans OpenCost.

### ✏️ Exercice 2 — Premier diagnostic

Dans `partie-2-diagnostic.md`, répondre :

1. Quel **namespace** consomme le plus ?
2. Quel **workload** a le **plus mauvais ratio Requests/Usage** ?
3. Identifier le **service "idle"** : il existe mais ne sert pas de requêtes.
4. Capture d'écran : la vue "Allocations" filtrée sur les 24 dernières heures.

---

## 🎯 Partie 3 — Rightsizing : HPA et VPA (1h30)

### 3.1 Théorie du dimensionnement

Le bon dimensionnement d'un pod suit une logique :

```
requests = P95(usage_normal) × marge_securite
limits   = P99(usage_pic)    × marge_OOM
```

- **Marge_securite** typique : 1.2 à 1.5
- **Marge_OOM** : éviter `limits = requests` (CPU throttling, OOMKill)

### 3.2 Le VPA en mode "recommender"

Le **Vertical Pod Autoscaler** peut tourner en mode **recommendation only** (sans modifier les pods). C'est **l'outil de référence** pour le rightsizing.

```bash
# Installer le VPA
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-1.1.2/vpa-v1.yaml

# Créer une VerticalPodAutoscaler en mode "Off" (recommandation seulement)
kubectl apply -f manifests/vpa-recommender.yaml
```

Attendre ~15 min puis :

```bash
kubectl describe vpa -n boutique
```

Vous obtenez pour chaque container des **recommandations** : `target`, `lowerBound`, `upperBound`.

### 3.3 Implémenter le HPA

Le **Horizontal Pod Autoscaler** multiplie/réduit le nombre de pods selon une métrique.

Déployer un HPA basé sur le CPU sur le service `frontend` :

```bash
kubectl apply -f manifests/hpa-frontend.yaml
```

Inspecter :
```bash
kubectl get hpa -n boutique -w
```

### 3.4 Test de charge avec k6

Lancer un test de charge progressif :

```bash
k6 run scripts/load-test.js
```

Pendant le test (10 minutes), observer dans une autre fenêtre :

```bash
watch kubectl get pods,hpa -n boutique
```

Vous devez voir le nombre de pods **augmenter** quand la charge monte, puis **redescendre** après le test.

### ✏️ Exercice 3 — Optimisation

Dans `partie-3-rightsizing.md` :

1. Pour chaque service de l'app `boutique`, donner les **nouvelles requests/limits recommandées** par le VPA.
2. Calculer le **gain estimé en coût** (utiliser OpenCost avant/après — attendre 30 min pour stabilisation).
3. Pour le service `productcatalog`, **est-ce qu'un HPA ou un VPA est plus adapté** ? Justifier.
4. Quels sont les **risques** d'appliquer aveuglément les recommandations VPA en production ?

---

## 💰 Partie 4 — Stratégies d'achat : Spot, Reserved, On-Demand (1h)

### 4.1 Les 3 modes d'achat

| Mode | Réduction | Engagement | Disponibilité | Cas d'usage |
|------|-----------|-----------|---------------|-------------|
| **On-Demand** | 0% (référence) | Aucun | Garantie | Charges imprévisibles |
| **Reserved Instances (1 an)** | -40% | 1 an | Garantie | Baseline stable |
| **Reserved (3 ans)** | -60% | 3 ans | Garantie | Très stable, long terme |
| **Savings Plans** | -50% | 1-3 ans (flex) | Garantie | Flexibilité supérieure aux RI |
| **Spot/Preemptible** | -70% à -90% | Aucun | **Non garantie** (eviction 2 min) | Stateless, tolérant aux pannes |

### 4.2 Simuler des node pools mixtes

Le fichier `notebooks/cost-strategy.ipynb` propose un calculateur. Y répondre :

> Pour la baseline de 10 vCPU stables 24/7 + des pics jusqu'à 40 vCPU 4h/jour ouvré :
> 
> Comparer 4 stratégies :
> - 100% On-Demand
> - 10 vCPU Reserved 1 an + reste On-Demand
> - 10 vCPU Reserved 1 an + reste Spot
> - 100% Savings Plan + bursting Spot

Vous devriez constater **40-65% d'économies** entre la pire et la meilleure stratégie.

### 4.3 Anti-pattern : tout en Spot

Lire `partie-4-spot-pitfalls.md` qui liste les **erreurs classiques** :
- StatefulSet sur Spot sans PodDisruptionBudget
- Pas de diversification des types d'instance → eviction massive simultanée
- Pas de fallback On-Demand pour le control plane des apps

### ✏️ Exercice 4 — Recommandation d'architecture

Pour l'application `boutique` analysée précédemment, **rédiger une recommandation de pool node** :

- Quels services peuvent tourner sur Spot ?
- Lesquels exigent du On-Demand ?
- Quelle taille de pool Reserved acheter ?

Format : 1 page Markdown dans `RAPPORT.md`.

---

## 📊 Partie 5 — Construire un dashboard de showback (1h30)

### 5.1 Tagging par labels Kubernetes

Sur Kubernetes, les "tags" sont des **labels** au niveau Pod/Namespace. Convention recommandée :

```yaml
metadata:
  labels:
    team: payments
    env: production
    cost-center: cc-1234
    app.kubernetes.io/name: frontend
```

OpenCost peut **agréger par label**. Configurer dans les valeurs Helm :

```yaml
opencost:
  exporter:
    extraEnv:
      EMIT_NAMESPACE_LABELS: "true"
      EMIT_POD_LABELS: "true"
```

### 5.2 Importer un dashboard Grafana

```bash
kubectl apply -f manifests/grafana-dashboard-finops.yaml
```

Le dashboard `FinOps Showback` apparaît dans Grafana. Il affiche :

- **Coût total cluster** (jour, mois)
- **Coût par namespace** (treemap)
- **Coût par équipe** (label `team`)
- **Idle cost** (capacité non allouée)
- **Top 10 workloads les plus chers**

### 5.3 Export hebdomadaire automatisé

Le script `scripts/weekly-report.py` interroge l'API OpenCost et génère un rapport Markdown :

```bash
python scripts/weekly-report.py --output reports/showback-$(date +%Y-W%V).md
```

### ✏️ Exercice 5 — Personnaliser

1. Ajouter un **panneau Grafana** qui affiche le **ratio Requests/Usage** par namespace
2. Modifier le script de rapport pour ajouter une section **"Top 3 actions recommandées"** basée sur des règles simples (idle > 30%, requests > 3× usage…)
3. Configurer une **GitHub Action** (`.github/workflows/weekly-report.yml`) qui exécute le rapport tous les lundis et ouvre une issue

---

## 📝 Partie 6 — Synthèse et rendu (30 min)

### 6.1 Livrables — Pull Request

- [ ] `RAPPORT.md` : réponses aux exercices, recommandation d'architecture, captures
- [ ] `manifests/` modifié avec requests/limits ajustés
- [ ] Notebook de stratégie d'achat complété
- [ ] Dashboard Grafana exporté en JSON
- [ ] GitHub Action de reporting hebdomadaire
- [ ] 3 captures : OpenCost avant/après, HPA pendant test de charge, dashboard final

### 6.2 Questions de réflexion

- Pourquoi le **« idle cost »** est-il particulièrement difficile à attribuer ?
- En production, quelles **protections** mettriez-vous avant d'appliquer un VPA en mode `Auto` ?
- Quelles **limites du FinOps Kubernetes** voyez-vous (ex: coûts inter-cluster, multi-cloud) ?

---

## 📚 Pour aller plus loin

- 📘 [OpenCost docs](https://www.opencost.io/docs/)
- 🌐 [Kubecost (offre commerciale au-dessus d'OpenCost)](https://www.kubecost.com/)
- 🛠️ [Karpenter](https://karpenter.sh/) (autoscaler AWS de nouvelle génération)
- 📊 [Goldilocks](https://github.com/FairwindsOps/goldilocks) (UI pour les recommandations VPA)
- 🎥 KubeCon talks : *"FinOps for Kubernetes"* (chaîne CNCF YouTube)

---

## 🔑 Notes pour l'enseignant

<details>
<summary>Cliquer pour afficher</summary>

### Timing détaillé

| Bloc | Durée | Format |
|------|-------|--------|
| Setup cluster + intro | 30 min | Magistral + manip |
| Partie 1 (théorie) | 45 min | Magistral + exercice papier |
| Partie 2 (OpenCost) | 1h30 | Pratique |
| Pause déjeuner | 1h | — |
| Partie 3 (HPA/VPA) | 1h30 | Pratique |
| Partie 4 (Spot/RI) | 1h | Pratique + théorie |
| Pause | 15 min | — |
| Partie 5 (showback) | 1h15 | Pratique |
| Synthèse | 30 min | Q&A |

### Points de vigilance

- **Ressources Codespaces** : prendre une machine **4-core minimum** pour Kind avec 3 nœuds. Le devcontainer demande `machine_type=premiumLinux-4core-16gb`
- Le VPA met **10-15 minutes** à fournir des recommandations stables : prévoir une pause pendant ce temps
- Le test k6 génère du CPU sur le cluster : vérifier qu'OpenCost reste responsive
- Les **prix simulés** par OpenCost sont configurés via `customPricing` (voir `opencost-values.yaml`) — adaptables à AWS/Azure/GCP au choix de l'enseignant

### Variantes possibles

- Remplacer Kind par **k3s** si problèmes de performance Codespaces
- Au lieu de l'app `boutique`, utiliser **Google's microservices-demo** (plus lourde mais plus réaliste)
- Pour groupe avancé : ajouter **Karpenter** simulation via les `instance-type` labels

</details>
