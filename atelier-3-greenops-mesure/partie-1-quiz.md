# Atelier 3 — Quiz de positionnement (Partie 1)

> Répondez en autonomie. Les questions portent sur les concepts vus en Partie 1 : ordres de grandeur, PUE/WUE, Scope, embodied vs operational, GreenOps vs FinOps.

## Q1. La part du numérique dans les émissions mondiales de GES est estimée à environ…

- [ ] A. 0,1 %
- [ ] B. 2,5 à 4 %
- [ ] C. 15 à 20 %
- [ ] D. 40 %

## Q2. Dans l'impact environnemental d'un équipement informatique grand public, la part **fabrication (embodied)** représente typiquement…

- [ ] A. Moins de 5 %
- [ ] B. Autour de 20 %
- [ ] C. 50 à 80 %
- [ ] D. 100 % (l'usage est négligeable)

## Q3. Le **PUE** (Power Usage Effectiveness) d'un datacenter se définit comme…

- [ ] A. Énergie IT / énergie totale du datacenter
- [ ] B. Énergie totale du datacenter / énergie IT
- [ ] C. Énergie renouvelable / énergie totale
- [ ] D. Émissions CO2 / énergie consommée

## Q4. Un datacenter moderne très efficace a un PUE proche de…

- [ ] A. 0,8
- [ ] B. 1,1 – 1,2
- [ ] C. 2,5
- [ ] D. 5,0

## Q5. L'**intensité carbone** de l'électricité (gCO2e/kWh) varie principalement en fonction de…

- [ ] A. La marque du fournisseur
- [ ] B. Le mix électrique du pays et l'heure de la journée
- [ ] C. La consommation du serveur
- [ ] D. La température extérieure uniquement

## Q6. Dans le **GHG Protocol**, les émissions liées à l'**électricité achetée** relèvent du…

- [ ] A. Scope 1
- [ ] B. Scope 2
- [ ] C. Scope 3
- [ ] D. Scope 4

## Q7. Quelle différence principale entre **GreenOps** et **éco-conception logicielle** ?

- [ ] A. GreenOps cible l'infrastructure et l'exploitation, l'éco-conception cible le design du logiciel lui-même
- [ ] B. Ce sont deux noms pour la même pratique
- [ ] C. L'éco-conception ne concerne que le frontend
- [ ] D. GreenOps ne mesure que le coût financier

## Q8. FinOps et GreenOps **se recoupent à 80 %** parce que…

- [ ] A. Les outils sont identiques
- [ ] B. Moins de ressources consommées signifie généralement moins de coût ET moins d'impact
- [ ] C. Les deux disciplines partagent la même certification
- [ ] D. Ils s'opposent toujours

## Q9. Parmi ces affirmations sur la **mesure énergétique en VM mutualisée** (type Codespaces), laquelle est correcte ?

- [ ] A. Les compteurs RAPL Intel sont accessibles normalement
- [ ] B. Les chiffres mesurés sont absolus et directement comparables à ceux d'une machine bare-metal
- [ ] C. CodeCarbon bascule en mode estimation (TDP × CPU%) — les valeurs sont indicatives, pas absolues
- [ ] D. La mesure est impossible, aucun outil ne fonctionne

## Q10. Le **WUE** (Water Usage Effectiveness) mesure…

- [ ] A. Le rendement énergétique d'un serveur
- [ ] B. Les litres d'eau consommés par kWh IT (refroidissement principalement)
- [ ] C. Le coût de l'eau dans la facture du datacenter
- [ ] D. La qualité de l'eau rejetée

---

## ✏️ Question de calcul

> Un serveur de **500 W** tourne **24/7** dans un datacenter français
> (intensité carbone moyenne : **60 gCO2e/kWh**, **PUE 1.5**).
> Quel est son **impact opérationnel annuel** en kgCO2e ?

Détaillez votre raisonnement :

```
Énergie IT annuelle (kWh)        = …
Énergie totale avec PUE (kWh)    = …
Émissions annuelles (kgCO2e)     = …
```

**Bonus** : refaire le même calcul si le serveur était hébergé en Pologne
(~700 gCO2e/kWh). Quel est le ratio entre les deux ?

---

## Vos réponses

Notez ici vos choix :

```
Q1: …  Q2: …  Q3: …  Q4: …  Q5: …
Q6: …  Q7: …  Q8: …  Q9: …  Q10: …

Calcul France  : … kgCO2e/an
Calcul Pologne : … kgCO2e/an
Ratio PL/FR    : … ×
```
