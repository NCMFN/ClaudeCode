---
name: suivi-post-livraison
description: Suivi client apres livraison — satisfaction, avis, temoignage, upsell, portfolio
version: 1.0.0
category: Business
priority: 1
author: Richard Cusey
---

# Suivi Post-Livraison

> Gerer la relation client apres la livraison pour maximiser satisfaction, avis, et recurrence.

## When to Use

- Apres livraison d'un projet video
- Pour relancer un client satisfait (upsell)
- Pour obtenir un avis Google ou un temoignage
- Pour la revue hebdomadaire des clients en post-livraison

## How It Works

### 1. Calendrier Post-Livraison

| Etape | Delai | Action |
|-------|-------|--------|
| Satisfaction | J+3 | Message de suivi : "tout vous convient ?" |
| Avis Google | J+14 | Demande d'avis avec lien direct |
| Temoignage | J+21 | Proposition de temoignage structure |
| Upsell | J+90 | Proposition de contenu supplementaire |
| Anniversaire | J+365 | Message "ca fait 1 an" + proposition |

### 2. Messages Templates

#### J+3 — Satisfaction

```
Bonjour [prenom],

J'espere que la video vous plait ! Si vous avez des retours
ou une derniere petite modif, n'hesitez pas.

Sinon, je serais curieux de savoir : comment votre equipe
/ vos clients ont reagi en la voyant ?

Bonne journee,
Richard
```

#### J+14 — Avis Google

```
Bonjour [prenom],

Content que la video fonctionne bien !

Si vous avez 2 minutes, un petit avis Google m'aiderait
beaucoup pour ma visibilite : [lien direct]

Merci beaucoup, et a bientot !
Richard
```

#### J+21 — Temoignage

```
Bonjour [prenom],

Est-ce que vous seriez d'accord pour un court temoignage
sur notre collaboration ? Ca prend 5 min, je vous envoie
les questions et vous repondez quand vous voulez.

Ca m'aide pour montrer aux futurs clients ce que
je peux faire pour eux.

Merci !
Richard
```

#### J+90 — Upsell

```
Bonjour [prenom],

Ca fait 3 mois depuis la video — comment ca se passe
de votre cote ? La video a eu de bons retours ?

Je pensais a vous parce que [raison specifique :
nouvelle saison, nouveau produit, evenement a venir...].

Si vous voulez qu'on en reparle, je suis dispo.

Richard
```

### 3. Temoignage Structure

Questions a poser (5 questions, 5 min) :

```
1. Quel etait le contexte de votre projet video ?
2. Qu'est-ce qui vous a convaincu de travailler avec moi ?
3. Comment s'est passe le tournage ?
4. Quel impact la video a eu pour vous / votre business ?
5. Recommanderiez-vous mes services ? Pourquoi ?
```

Format de sortie :

```
TEMOIGNAGE CLIENT
==================
Client : [Nom / Entreprise]
Projet : [Description courte]
Date : [date projet]
Score satisfaction : [1-5]

Citation cle :
"[phrase impactante extraite des reponses]"

Resume (2-3 lignes) :
[Resume du temoignage utilisable sur le site / reseaux]
```

### 4. Documentation Portfolio

Apres chaque projet livre, documenter :

```
FICHE PORTFOLIO
================
Client : [Nom]
Secteur : [Restauration / Immobilier / etc.]
Type : [Brand content / Evenementiel / etc.]
Date : [date]
Budget : [fourchette]

Delivrables :
  - [Video 1 : description, duree]
  - [Video 2 : description, duree]

Lien(s) : [URL video]

Impact mesure :
  - [Vues / engagement si disponible]
  - [Retour client]

Ce qui a bien marche :
  - [Point fort technique ou creatif]

A ameliorer :
  - [Point a travailler pour la prochaine fois]

Tags : [mots-cles pour recherche future]
```

### 5. Suivi Notion

Champs a mettre a jour dans le CRM apres livraison :

```
CHAMPS POST-LIVRAISON :
  Statut : Livre
  Date livraison : [date]
  Satisfaction : [1-5 etoiles]
  Avis Google : [oui/non + date]
  Temoignage : [oui/non + date]
  Portfolio : [oui/non + lien]
  Upsell potentiel : [description]
  Prochaine relance : [date J+90]
```

## Examples

### Exemple : Suivi restaurant

```
Richard : "J'ai livre la video du restaurant, on lance le suivi"

SUIVI POST-LIVRAISON — Restaurant Le Marais
=============================================
Livre le : 2026-04-10
Budget : 900€

CALENDRIER :
  [x] J+3 (13 avril) : Message satisfaction → envoyer
  [ ] J+14 (24 avril) : Demande avis Google
  [ ] J+21 (1er mai) : Proposition temoignage
  [ ] J+90 (9 juillet) : Upsell menu d'ete
  [ ] J+365 (10 avril 2027) : Anniversaire

MESSAGE J+3 prepare :
"Bonjour Thomas, j'espere que la video vous plait !
Comment votre equipe a reagi ? Si vous avez un dernier
retour, je suis dispo. Bonne journee !"
```

## References

- Depend de : `devis-facturation` (la livraison suit le devis accepte)
- Alimente : `prospect-coach` (un client satisfait = referral potentiel)
- Alimente : `weekly-review` (metriques satisfaction, avis, portfolio)
- Lie a : `qualification-client` (le suivi enrichit le profil client)
