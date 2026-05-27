# Partie 1 — Cas d'école : allocation de coût sur un nœud Kubernetes

> Exercice 1 de l'atelier 2 (voir `README.md` §1.3). À compléter en binôme, sur papier ou ici.

## Contexte

Un nœud **`t3.large`** coûte **0,0832 $/h**. Il dispose de **2 vCPU** et **8 GiB de RAM**.

Sur ce nœud tournent trois pods pendant 1 heure :

| Pod | CPU requests | RAM requests | Conso réelle CPU | Conso réelle RAM |
|-----|--------------|--------------|------------------|------------------|
| A   | 500m         | 1 Gi         | 200m             | 700 Mi           |
| B   | 1000m        | 2 Gi         | 1500m (dépasse!) | 1,5 Gi           |
| C   | 200m         | 500 Mi       | 50m              | 200 Mi           |

## Rappel de la formule OpenCost (simplifiée)

```
cost(pod) = cpu_cost  × max(cpu_request, cpu_usage) × duration
          + ram_cost  × max(ram_request, ram_usage) × duration
```

On considère que le coût du nœud se répartit **au prorata** entre CPU et RAM. Hypothèse usuelle : **50 % CPU / 50 % RAM** du coût horaire.

## Travail demandé

### 1. Décomposer le coût du nœud

- Coût horaire CPU du nœud : ___ $/vCPU·h
- Coût horaire RAM du nœud : ___ $/GiB·h

### 2. Calculer l'allocation par pod (1 h)

| Pod | CPU facturé (vCPU·h) | RAM facturée (GiB·h) | Coût alloué ($) |
|-----|----------------------|----------------------|-----------------|
| A   |                      |                      |                 |
| B   |                      |                      |                 |
| C   |                      |                      |                 |
| **Total alloué** |          |                      |                 |

### 3. Calculer le coût « idle »

```
idle_cost = coût_total_nœud − somme(coûts_alloués)
```

- Coût idle CPU : ___ $
- Coût idle RAM : ___ $
- **Idle total** : ___ $ (soit ___ % du coût du nœud)

### 4. Questions de discussion

- Quel pod est le plus pénalisé par la règle `max(request, usage)` ? Pourquoi est-ce raisonnable du point de vue FinOps ?
- Le pod B **dépasse ses requests** : à qui attribuer le surcoût ? À son équipe ou au "pool partagé" ?
- Si l'idle dépasse 30 %, quelles actions concrètes proposeriez-vous ?

---

> À reporter dans `RAPPORT.md` (section « Partie 1 »).
