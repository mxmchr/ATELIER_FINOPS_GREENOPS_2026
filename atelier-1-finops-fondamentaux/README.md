# Atelier 1 — FinOps Fondamentaux : Visibilité et allocation des coûts

> **Durée** : 6-7h • **Niveau** : M2 Informatique • **Format** : tutoriel guidé pas à pas

## 🎯 Objectifs d'apprentissage

À la fin de cet atelier, vous saurez :

1. Définir les **3 phases du framework FinOps** (Inform, Optimize, Operate) et les rôles impliqués
2. Lire et interpréter un **rapport de facturation cloud** (Cost and Usage Report)
3. Mettre en place une **stratégie de tagging** et allouer des coûts par équipe/projet
4. Détecter les **gaspillages courants** (ressources orphelines, sur-provisionnement)
5. Calculer un **showback** et construire un **dashboard de coûts** simple

## 🧰 Outils utilisés

- **GitHub Codespaces** (environnement de travail)
- **Python 3.11 + Pandas + Plotly** (analyse de données de facturation)
- **Jupyter** (notebooks d'exploration)
- **Dataset synthétique** d'un Cost and Usage Report (CUR) AWS sur 90 jours
- **Streamlit** (dashboard interactif simple)

## 🚀 Démarrer le Codespace

1. Sur la page GitHub du dépôt, cliquer **Code → Codespaces → Create codespace**
2. Une fois ouvert, dans le terminal VS Code intégré :
   ```bash
   cd atelier-1-finops-fondamentaux
   pip install -r requirements.txt
   ```
3. Vérifier que Jupyter démarre : `jupyter lab --no-browser`

---

## 📖 Partie 1 — Contexte et théorie (45 min)

### 1.1 Pourquoi le FinOps ?

Le **cloud public** transforme la dépense IT : on passe d'un modèle **CAPEX** (achat de serveurs amortis) à un modèle **OPEX** (paiement à l'usage, par seconde). Cette flexibilité a un revers : **les coûts deviennent variables, distribués, et souvent invisibles** pour les équipes qui les génèrent.

Le **FinOps** (Cloud Financial Operations) est une discipline culturelle et opérationnelle pour reprendre le contrôle.

### 1.2 Le framework FinOps Foundation

Lire en autonomie : [https://www.finops.org/framework/](https://www.finops.org/framework/)

Le framework définit **3 phases itératives** :

| Phase | Question clé | Activités typiques |
|-------|--------------|-------------------|
| **Inform** | Qui dépense quoi ? | Tagging, allocation, showback, benchmarking |
| **Optimize** | Comment dépenser mieux ? | Rightsizing, RI/Savings Plans, suppression du gaspillage |
| **Operate** | Comment industrialiser ? | Automatisation, gouvernance, KPIs, intégration CI/CD |

**Personas impliqués** : FinOps Practitioner, Engineering, Finance, Product, Leadership.

### ✏️ Exercice 1 — QCM de positionnement

Ouvrir le fichier `partie-1-quiz.md` et y répondre. Les réponses sont à la fin de cet atelier.

---

## 🛠️ Partie 2 — Explorer un Cost and Usage Report (1h30)

### 2.1 Comprendre le format CUR

Le **Cost and Usage Report (CUR)** d'AWS — équivalents : *Cost Details* sur Azure, *Billing Export* sur GCP — est un export CSV/Parquet horaire de toute la consommation cloud d'une organisation. Il contient typiquement 100+ colonnes.

Nous travaillons avec un dataset synthétique (`ressources/datasets/cur_sample.csv`) qui contient les colonnes essentielles :

| Colonne | Description |
|---------|-------------|
| `usage_date` | Date d'utilisation (jour) |
| `account_id` | Compte AWS (ex: prod, dev, staging) |
| `service` | Service AWS (EC2, S3, RDS, Lambda…) |
| `region` | Région (eu-west-1, us-east-1…) |
| `usage_type` | Type d'usage détaillé (BoxUsage:t3.medium…) |
| `usage_amount` | Quantité consommée |
| `unblended_cost` | Coût brut en USD |
| `tag_team` | Équipe responsable (tag) |
| `tag_env` | Environnement (prod/dev/staging) |
| `tag_project` | Projet métier |

### 2.2 Ouvrir le notebook d'exploration

```bash
jupyter lab notebooks/01-exploration-cur.ipynb
```

Suivre les 12 cellules du notebook qui guident :
- Le chargement du CSV avec Pandas
- L'agrégation par service, par compte, par jour
- La visualisation avec Plotly
- L'identification des top dépenses

### ✏️ Exercice 2 — Répondez en lisant les données

Dans `partie-2-exercices.md`, répondre :

1. Quel est le **top 3 des services** par coût sur les 90 jours ?
2. Quel jour a connu le **pic de dépense** et de combien ?
3. Quel **compte** consomme le plus ? Est-ce attendu pour de la production ?
4. Identifier une **anomalie visuelle** (pic isolé, tendance bizarre) et formuler une hypothèse.

---

## 🏷️ Partie 3 — Tagging et allocation (1h30)

### 3.1 Le problème du tagging

Sans tags, **impossible d'attribuer un coût à une équipe** ou un projet. Or :
- Les équipes créent des ressources avec ou sans tags
- Les politiques de tagging sont **rarement appliquées rétroactivement**
- Certains coûts sont **non-taggables** (data transfer, services partagés)

### 3.2 Analyse du taux de couverture

Ouvrir `notebooks/02-tagging-coverage.ipynb` et exécuter les cellules. Le notebook calcule :

- Le **pourcentage de coûts taggés** par dimension (team, env, project)
- Les **services orphelins** (sans tag)
- Une matrice de couverture par compte × service

### 3.3 Stratégie de répartition des coûts partagés

Les coûts non-taggables (ex: NAT Gateway, support payant, data transfer inter-AZ) doivent être répartis. Les 3 approches :

| Méthode | Principe | Avantage | Inconvénient |
|---------|----------|----------|--------------|
| **Even split** | Diviser également entre équipes | Simple | Injuste pour petites équipes |
| **Proportional** | Proportionnel à la conso taggée | Plus juste | Pénalise les gros consommateurs |
| **Custom weights** | Pondération métier | Adapté au contexte | Politiquement sensible |

### ✏️ Exercice 3 — Implémenter une allocation

Dans `notebooks/03-allocation-exercice.ipynb`, compléter les fonctions :

```python
def allocate_proportional(df_tagged: pd.DataFrame, df_untagged: pd.DataFrame) -> pd.DataFrame:
    """
    Répartit les coûts non taggés proportionnellement aux coûts taggés par équipe.
    Retourne un DataFrame avec le coût total alloué par équipe.
    """
    # TODO: calculer le total taggé par équipe
    # TODO: calculer la part de chaque équipe (en %)
    # TODO: répartir les coûts non taggés selon ces parts
    # TODO: retourner le DataFrame consolidé
    pass
```

Cas de test fourni : la somme totale doit rester égale (conservation des coûts).

---

## 🔍 Partie 4 — Détecter les gaspillages (1h)

### 4.1 Les "low hanging fruits" du FinOps

Les gaspillages classiques détectables sans accès à la production :

| Gaspillage | Signal dans le CUR | Économie potentielle |
|------------|-------------------|---------------------|
| **EBS non attachés** | Coût EBS sans EC2 associé | 100% du coût EBS |
| **Snapshots anciens** | Stockage croissant lent | 50-90% |
| **Elastic IP non utilisées** | Coût horaire IP sans instance | 100% |
| **Instances surdimensionnées** | CPU < 10% en moyenne | 30-70% |
| **Environnements 24/7 non-prod** | Coût constant week-end | 60-70% |
| **Snapshots/AMI orphelins** | Coût sans usage | 100% |
| **Logs CloudWatch infinis** | Croissance linéaire constante | 80% (rétention) |

### 4.2 Notebook de chasse au gaspillage

Ouvrir `notebooks/04-waste-detection.ipynb`. Ce notebook applique 5 heuristiques au dataset :

1. Détection de coûts EBS dans des comptes sans EC2 actif ce jour-là
2. Identification des ressources avec coût constant 24/7 en environnement `dev`
3. Calcul du coût week-end vs semaine sur les environnements non-prod
4. Top 10 des `usage_type` avec coût > $1000 et utilisation décroissante
5. Détection d'instances EC2 dont la famille semble surdimensionnée

### ✏️ Exercice 4 — Construire votre propre détecteur

Implémenter une 6e heuristique : **détecter les services dont la croissance MoM (Month over Month) dépasse +50%** et qui ne sont pas tagués comme `tag_project=growth`.

Livrable : fonction Python documentée + liste des services concernés.

---

## 📊 Partie 5 — Construire un dashboard de showback (1h30)

### 5.1 Showback vs Chargeback

- **Showback** : on **montre** aux équipes leur consommation (sans facturer)
- **Chargeback** : on **refacture** réellement aux centres de coûts

En M2, on se concentre sur le showback : **plus pédagogique, moins politique**.

### 5.2 Application Streamlit

Le fichier `app/dashboard.py` est un squelette de dashboard Streamlit. Le lancer :

```bash
streamlit run app/dashboard.py
```

Codespaces ouvrira automatiquement le port 8501. Le dashboard contient :
- Un **sélecteur de période**
- Un **filtre par équipe**
- Un **graphique de tendance**
- Une **table des top usages**

### ✏️ Exercice 5 — Compléter le dashboard

Ajouter 3 fonctionnalités :

1. Un **KPI "% de couverture tagging"** affiché en haut de page
2. Un graphique **comparaison budget vs réel** (budget fourni dans `ressources/datasets/budgets.json`)
3. Une **alerte visuelle** quand une équipe dépasse 110% de son budget mensuel

**Bonus** : un **forecast linéaire** des coûts sur les 30 prochains jours en utilisant `numpy.polyfit`.

---

## 📝 Partie 6 — Synthèse et rendu (30 min)

### 6.1 Livrables attendus

Créer une **Pull Request** sur votre fork contenant :

- [ ] Les notebooks complétés (parties 2, 3, 4)
- [ ] Un fichier `RAPPORT.md` répondant aux exercices
- [ ] Le dashboard Streamlit enrichi (`app/dashboard.py`)
- [ ] Une capture d'écran du dashboard final (`captures/dashboard.png`)
- [ ] Une synthèse de 1 page : « **5 actions prioritaires** que vous recommanderiez à la direction IT de cette entreprise »

### 6.2 Questions de réflexion (à intégrer au rapport)

- En quoi le FinOps diffère-t-il d'une démarche d'audit financier classique ?
- Pourquoi le **tagging à la création** est-il préférable au tagging rétroactif ?
- Quelle métrique vous semble la plus pertinente pour suivre la maturité FinOps d'une organisation ?

---

## 📚 Pour aller plus loin

- 📘 *Cloud FinOps* (J.R. Storment & M. Fuller, O'Reilly, 2e édition)
- 🌐 [FinOps Foundation — Framework officiel](https://www.finops.org/framework/)
- 🛠️ [OpenCost](https://www.opencost.io/) (préparation à l'atelier 2)
- 📊 [AWS Cost Explorer documentation](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html)

---

## 🔑 Notes pour l'enseignant

<details>
<summary>Cliquer pour afficher</summary>

### Timing détaillé

| Bloc | Durée | Format |
|------|-------|--------|
| Accueil + intro | 15 min | Magistral |
| Partie 1 (théorie + quiz) | 45 min | Magistral + QCM individuel |
| Pause | 15 min | — |
| Partie 2 (exploration CUR) | 1h30 | Pratique guidée |
| Pause déjeuner | 1h | — |
| Partie 3 (tagging) | 1h30 | Pratique guidée |
| Partie 4 (gaspillages) | 1h | Pratique guidée |
| Pause | 15 min | — |
| Partie 5 (dashboard) | 1h30 | Pratique guidée |
| Synthèse + Q&A | 30 min | Discussion |

### Points de vigilance

- **Codespaces gratuit** : 60h/mois suffisent largement pour la journée (4-5h actives)
- Si les étudiants n'ont pas vu Pandas, prévoir 30 min de rappel avant la partie 2
- Le dataset est volontairement « sale » (tags manquants, valeurs nulles) pour forcer une analyse rigoureuse
- L'exercice 5 (forecast) est difficile : peut être traité en bonus

### Corrigés

Disponibles dans le dossier privé `_corriges/` (non distribué aux étudiants).

</details>
