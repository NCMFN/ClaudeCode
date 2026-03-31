---
name: tournage-regie
description: Gestion de journee de tournage — checklist materiel, plan de tournage, gestion des imprevus
version: 1.0.0
category: Production
priority: 1
author: Richard Cusey
---

# Tournage & Regie

> Gerer une journee de tournage de A a Z : preparation, execution, debriefing.

## When to Use

- Quand Richard prepare un tournage
- La veille ou le matin d'un tournage
- Pour generer un plan de tournage
- Pour gerer un imprevu sur le terrain

## How It Works

### 1. Checklist Materiel

```
CAMERA :
  [ ] Boitier principal + objectifs
  [ ] Batteries (3 min) chargees
  [ ] Cartes memoire formatees (2 min)
  [ ] Stabilisateur / trepied
  [ ] Filtre ND (exterieur)

AUDIO :
  [ ] Micro-cravate (+ pile de rechange)
  [ ] Micro shotgun
  [ ] Enregistreur externe (si applicable)
  [ ] Casque de monitoring
  [ ] Bonnette anti-vent (exterieur)

ECLAIRAGE :
  [ ] LED panel (+ batteries / secteur)
  [ ] Reflecteur
  [ ] Diffuseur

DRONE (si applicable) :
  [ ] Drone + batteries (3 min)
  [ ] Telecommande chargee
  [ ] Cartes memoire drone
  [ ] Autorisation de vol (zone, DGAC)
  [ ] Verification meteo vent

KIT PERSONNEL :
  [ ] Gaffer tape
  [ ] Rallonge electrique
  [ ] Chargeur telephone
  [ ] Eau + snack
  [ ] Carte de visite
```

### 2. Plan de Tournage

Template de plan de tournage avec blocs horaires :

```
PLAN DE TOURNAGE
=================
Projet : [nom]
Date : [date]
Lieu : [adresse]
Contact client : [nom + tel]

SEQUENCE 1 — [HH:MM - HH:MM] : [Description]
  Setup : [materiel specifique]
  Plans : [liste des plans a capter]
  Notes : [contraintes, direction artistique]

SEQUENCE 2 — [HH:MM - HH:MM] : [Description]
  Setup : [materiel specifique]
  Plans : [liste des plans a capter]
  Notes : [contraintes]

PAUSE — [HH:MM - HH:MM]

SEQUENCE 3 — [HH:MM - HH:MM] : [Description]
  ...

MARGE SECURITE : 30 min en fin de journee
DEPART CLIENT : [HH:MM]
```

### 3. Regles Jour J

```
AVANT :
  - Arriver 30 min avant le client
  - Reperer les lieux, la lumiere, le son
  - Tester tout le materiel sur place
  - Briefer le client (deroulement, timing)

PENDANT :
  - Tourner PLUS que necessaire (ratio 3:1 minimum)
  - Varier les valeurs de plan (large, moyen, serre)
  - Capter des plans de coupe (details, ambiance)
  - Verifier les rushes toutes les 30 min
  - Communiquer avec le client regulierement

APRES :
  - Sauvegarder les rushes IMMEDIATEMENT (double copie)
  - Debriefer avec le client (5 min)
  - Noter les moments forts pendant que c'est frais
  - Ranger et verifier le materiel
```

### 4. Gestion des Imprevus

| Imprevu | Solution |
|---------|----------|
| Pluie | Repli interieur, plans atmospheriques, protection materiel |
| Bruit ambiant | Micro-cravate plus pres, enregistrement son seul apres, changer d'emplacement |
| Client en retard | Capter des plans de coupe en attendant, confirmer par SMS |
| Batterie morte | Toujours 3 batteries minimum, chargeur en backup |
| Carte memoire pleine | 2 cartes minimum, transfert rapide si laptop present |
| Lumiere difficile | Reflecteur, changer l'angle, attendre un moment |
| Figurant absent | Adapter le sequencier, filmer sans, reporter la scene |

### 5. Checklist Depart

```
AVANT DE PARTIR :
  [ ] Toutes les cartes memoire recuperees
  [ ] Rushes verifies (pas de fichier corrompu)
  [ ] Materiel complet (rien oublie sur place)
  [ ] Client debriefe
  [ ] Prochaine etape communiquee (delai livraison)
  [ ] Photo du lieu range (preuve si besoin)
```

## Examples

### Exemple : Tournage restaurant

```
Richard : "Je prepare mon tournage au restaurant demain"

PLAN DE TOURNAGE
=================
Projet : Video presentation restaurant
Date : 2026-04-01
Lieu : [adresse restaurant]

08:30 — Arrivee, reperage lumiere + son
09:00 — SEQUENCE 1 : Plans exterieurs + drone
  Setup : Drone + boitier principal
  Plans : facade, terrasse, enseigne, rue
09:45 — SEQUENCE 2 : Ambiance interieure
  Setup : Stabilisateur + LED panel
  Plans : salle, bar, details deco, eclairage
10:30 — SEQUENCE 3 : Cuisine en action
  Setup : Micro-cravate chef + boitier
  Plans : preparation plat signature, gestes, flambage
11:15 — SEQUENCE 4 : Interview patron/chef
  Setup : 2 angles, micro-cravate, eclairage 3 points
11:45 — Plans de coupe supplementaires
12:00 — Depart + debriefing client

MARGE : 30 min integree
LIVRAISON : J+10
```

## References

- Depend de : `devis-facturation` (le devis valide declenche la prep tournage)
- Alimente : `derushage` (les rushes du tournage sont derushed ensuite)
- Lie a : `ecriture-brand` (la direction artistique influence le plan de tournage)
