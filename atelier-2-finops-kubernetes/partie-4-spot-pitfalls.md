# Partie 4 — Spot/Preemptible : pièges classiques

> Support de lecture pour la §4.3 du README. À lire avant l'exercice 4 (recommandation de pool node).

Le mode Spot/Preemptible offre **-70 % à -90 %** sur le prix On-Demand. En contrepartie, le cloud provider peut **récupérer l'instance avec un préavis très court** (2 min sur AWS, 30 s sur GCP). Voici les erreurs les plus fréquentes en pratique.

---

## 1. StatefulSet sur Spot sans `PodDisruptionBudget`

**Symptôme.** Une base de données ou un broker (Kafka, RabbitMQ) tourne en Spot pour économiser. À la première eviction, le pod redémarre sur un autre nœud, mais le **volume EBS attaché** met 30-90 s à se réattacher → cluster en quorum dégradé, lectures/écritures bloquées.

**Cause.** Pas de PDB → toutes les répliques peuvent être evictées simultanément. Volumes block storage = couplage géographique fort.

**Mitigation.**
- PDB avec `minAvailable` ≥ quorum.
- Au moins **2-3 zones de disponibilité** différentes.
- Préférer **On-Demand** pour les workloads stateful **avec quorum**.

---

## 2. Pas de diversification des types d'instance

**Symptôme.** Le node pool n'utilise qu'un seul type (`m5.large` Spot). Quand le marché Spot se tend sur ce type précis, **tous les nœuds sont evictés en quelques minutes**. Le cluster perd 80 % de sa capacité d'un coup.

**Cause.** Concentration de la demande sur une seule pool de capacité.

**Mitigation.**
- Configurer **5-10 types d'instance compatibles** dans le node pool (ex. `m5.large`, `m5a.large`, `m5d.large`, `m4.large`, `t3.large`…).
- Sur AWS : utiliser **EC2 Fleet** ou **Karpenter** avec `instance-types: [...]`.
- Sur GCP : `instance-templates` multiples derrière le même MIG.

---

## 3. Pas de fallback On-Demand pour le control plane applicatif

**Symptôme.** Tout est en Spot, y compris l'**ingress controller** et le **service mesh**. Une eviction simultanée fait tomber le routage → tout le cluster est injoignable pendant le rescheduling.

**Cause.** Les composants "transverses" sont traités comme des workloads ordinaires.

**Mitigation.**
- Pool **On-Demand minoritaire** (10-20 % de la capacité) avec `nodeSelector` ou `taints` réservés au control plane applicatif et aux composants critiques (ingress, DNS, monitoring).
- Affinités explicites : `requiredDuringSchedulingIgnoredDuringExecution` pour épingler ces pods au pool On-Demand.

---

## 4. Pas de handler de signal `SIGTERM` correct

**Symptôme.** Lors de l'eviction, Kubernetes envoie `SIGTERM` avec un `terminationGracePeriodSeconds` (30 s par défaut). Si l'app ne **draine pas proprement** ses connexions, on perd les requêtes en cours.

**Cause.** Application non-cloud-native — vieille app web sans handler de shutdown, jobs longs sans checkpoint.

**Mitigation.**
- Logique de **graceful shutdown** : arrêter d'accepter de nouvelles requêtes, finir celles en cours, fermer les connexions DB.
- Pour les jobs > 2 min : **checkpointing** régulier sur S3/GCS.
- `terminationGracePeriodSeconds` aligné avec la durée de drainage observée.

---

## 5. Sous-estimer le temps de rescheduling

**Symptôme.** Le node pool autoscaler met 2-5 min à provisionner un nouveau nœud. Si toutes les Spot sont récupérées, l'application **reste indisponible** pendant cet intervalle.

**Mitigation.**
- Pool tampon de **headroom** (capacity reservation, "overprovisioning pods" en `PriorityClass` basse).
- Surveiller le **Spot interruption rate** par type d'instance (AWS Spot Advisor) et éviter les pires.

---

## 6. Confondre "Spot" et "gratuit"

**Symptôme.** Le coût Spot reste élevé pendant un événement de marché (ex. fin de mois, Black Friday). On découvre **après coup** que la facture Spot était proche du tarif On-Demand.

**Mitigation.**
- Définir un **prix maximum** (`spot_price` ou Spot Fleet `MaxPrice`).
- Alerter au-delà d'un % du tarif On-Demand.

---

## Checklist avant de mettre un workload en Spot

- [ ] Le workload est **stateless** OU dispose d'un mécanisme de réplication/checkpoint.
- [ ] Le workload tolère un redémarrage **sous 2 minutes**.
- [ ] Au moins **3 types d'instance** différents sont autorisés.
- [ ] Un **PodDisruptionBudget** est défini.
- [ ] Le control plane applicatif (ingress, monitoring) **n'est pas** sur Spot.
- [ ] Le `terminationGracePeriodSeconds` est dimensionné.
- [ ] Le coût Spot est **monitoré** (pas seulement supposé bas).

---

## Pour aller plus loin

- AWS — [Spot Best Practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-best-practices.html)
- GCP — [Preemptible / Spot VM documentation](https://cloud.google.com/compute/docs/instances/spot)
- [Karpenter](https://karpenter.sh/) — autoscaler AWS qui gère nativement la diversification Spot
- Article : *"Stop using Spot for your databases"* (à chercher, plusieurs retours d'expérience publiés)
