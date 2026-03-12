# API Incident Dashboard

## Contexte

Dans le cadre du suivi de production des APIs, les incidents sont remontés par email Outlook sous forme de fichiers `.msg`.

Chaque email contient généralement :
- la date d'envoi
- un ou plusieurs signalements d'API en défaut
- l'URL de l'API concernée

Jusqu'à présent, l'analyse de ces incidents était réalisée manuellement à partir des emails, ce qui rendait le travail long et peu pratique pour obtenir des statistiques globales.

L'objectif de ce projet est de proposer un outil simple permettant d'analyser rapidement ces incidents.

---

## Principe de l'outil

Le dashboard permet de :

1. déposer des fichiers Outlook `.msg`
2. extraire automatiquement les informations utiles
3. calculer différentes statistiques sur les incidents API
4. afficher les résultats sous forme de graphiques

L'utilisateur n'a qu'à :
- déposer les fichiers incidents
- indiquer le nombre total d'APIs concernées sur la période analysée

Le reste des calculs est fait automatiquement.

---

## Données extraites des emails

Pour chaque email incident, le script récupère :

- la **date d'envoi**
- le **signalement de l'API en défaut**
- l'**URL de l'API**

Certains emails peuvent contenir **plusieurs signalements**.  
Chaque signalement est donc compté comme un **incident distinct**.

---

## Calcul du nombre d'incidents

Le nombre d'incidents correspond simplement au :

Si un email contient 3 signalements, cela représente **3 incidents**.

---

## Calcul des APIs impactées

Les APIs impactées correspondent au nombre d'APIs différentes ayant généré au moins un incident.

Concrètement, on compte le nombre de **signalements uniques**.

---

## Calcul des APIs stables

Les APIs stables correspondent aux APIs qui **n'ont généré aucun incident**.

Formule utilisée :

---

## Calcul de la disponibilité des APIs

Pour estimer la disponibilité globale, on utilise les hypothèses suivantes :

- une API fonctionne **12 heures par jour**
- un incident correspond en moyenne à **4 heures de panne**
- seuls les **jours ouvrés (lundi à vendredi)** sont pris en compte

### Temps total théorique
Temps total = Nombre de jours ouvrés
× Nombre d'APIs
× 12 heures

### Temps de panne

### Temps de panne


Temps de panne = Nombre d'incidents × 4 heures


### Disponibilité


Disponibilité = 1 - (Temps de panne / Temps total)


Le résultat est affiché en **pourcentage de disponibilité**.

---

## Visualisations

Le dashboard propose plusieurs graphiques :

### Incidents par mois
Permet d'observer l'évolution du nombre d'incidents dans le temps.

### Top APIs générant des incidents
Classement des APIs ayant généré le plus d'incidents.

### Répartition des incidents
Graphique en camembert montrant la distribution des incidents par API.

---

## Utilisation

1. ouvrir le dashboard
2. saisir le nombre total d'APIs sur la période analysée
3. déposer les fichiers Outlook `.msg`
4. consulter les statistiques générées automatiquement

---

## Technologies utilisées

- Python
- Streamlit
- Pandas
- Plotly
- extract-msg

---

## Objectif

L'objectif est de fournir un **outil simple et rapide** permettant aux équipes de suivre les incidents API à partir des emails de production, sans avoir besoin de retraiter les données manuellement.