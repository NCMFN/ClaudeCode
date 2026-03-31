---
name: log-plus
description: Fermeture de session — bilan consommation tokens, score efficacite, optimisations
version: 2.0.0
category: Process
priority: 0
author: Richard Cusey
notion_pages:
  - "Semantic Compression — LOG+"
  - "TOKEN COMPRESSOR — Guide Humain"
---

# Log+ — Fermeture de Session

> Bilan de fin de conversation. Mesurer ce qu'on a consomme, ce qu'on a produit, et comment optimiser la prochaine session.
> Invocable via `LOG+`, `/log+`, ou "on ferme".
> Compatible Token Compressor : Richard peut juste ecrire `LOG+` et tout se declenche.

## When to Use

- En fin de conversation, avant de quitter
- Quand Richard dit `LOG+`, `/log+` ou "on ferme"
- Quand le contexte window approche la limite (~80%)
- Claude peut le proposer si la session est longue (> 30 min ou > 40k tokens estimes)

## How It Works

### 1. Bilan de Session

Generer automatiquement :

```
LOG+ — FERMETURE SESSION
=========================
Date : [date]
Duree estimee : [timestamp fin - timestamp debut]
Objectif initial : [rappel du /log]
Objectif atteint : OUI / PARTIEL / NON

PRODUCTION :
  [ ] [Action 1 realisee — ex: "3 relances redigees"]
  [ ] [Action 2 realisee — ex: "Devis Maison Isor envoye"]
  [ ] [Action 3 realisee — ex: "Skill qualification-client creee"]
  ...

NON FAIT (reporte) :
  [ ] [Tache non terminee → a reprendre]
  ...
```

### 2. Consommation Tokens

Estimation basee sur l'activite de la session :

```
CONSOMMATION ESTIMEE :
  Tokens input  : ~[XX]k  (contexte + questions + outils)
  Tokens output : ~[XX]k  (reponses + code + skills)
  Total session : ~[XX]k

  DETAIL PAR POSTE :
  ├── Echanges texte        : ~[X]k (XX%)
  ├── Lecture fichiers/Notion: ~[X]k (XX%)
  ├── Recherche web (Exa)   : ~[X]k (XX%)
  ├── Creation/edition skills: ~[X]k (XX%)
  └── Overhead (system/rules): ~[X]k (XX%)

  MODELE UTILISE : [Opus/Sonnet/Haiku]
  COUT API EQUIVALENT : ~$[X.XX]
```

### 3. Analyse d'Efficacite

```
EFFICACITE SESSION :
  Ratio production/tokens : [eleve/moyen/faible]

  CE QUI A COUTE CHER EN TOKENS :
  - [Ex: "3 recherches web Exa → ~8k tokens chacune"]
  - [Ex: "Lecture de 4 pages Notion → ~12k tokens"]
  - [Ex: "Fichier de resultats crawl trop gros → ~15k tokens"]

  CE QUI ETAIT OPTIMISE :
  - [Ex: "Skills chargees = pas de re-explication du workflow"]
  - [Ex: "Scoring client en 1 passe grace a la matrice"]

  GASPILLAGE DETECTE :
  - [Ex: "2 recherches web redondantes"]
  - [Ex: "Relu un fichier deja lu"]
  - [Ex: "Reponse trop longue quand le mode etait Focus"]
```

### 4. Recommandations pour la Prochaine Session

```
OPTIMISATIONS SUGGEREES :

  MODELE :
  → [Ex: "Cette session aurait pu etre faite en Sonnet
     au lieu d'Opus — economie ~60% tokens output"]
  → [Ex: "Garder Opus, la complexite le justifiait"]

  SKILLS :
  → [Ex: "La skill X a ete utile, charger direct la prochaine fois"]
  → [Ex: "Il manque une skill pour Y — a creer"]
  → [Ex: "La skill Z n'a pas ete utilisee — pas besoin de la charger"]

  PROCESS :
  → [Ex: "Preparer le brief AVANT la session pour eviter
     3 allers-retours de cadrage (economie ~2k tokens)"]
  → [Ex: "Regrouper les recherches web en 1 batch
     au lieu de 3 appels separes"]

  NOTION :
  → [Ex: "Les donnees CRM sont a jour — pas besoin de
     relire toute la base la prochaine fois"]
  → [Ex: "Ajouter le champ X dans Notion pour eviter
     de recalculer a chaque session"]
```

### 5. Score de Session /10

```
CRITERES DE SCORE :

  Objectif atteint ?          /3  (0=non, 1=partiel, 3=oui)
  Ratio tokens/production ?   /3  (1=faible, 2=moyen, 3=eleve)
  Modele adapte ?             /2  (0=surdimensionne, 2=optimal)
  Gaspillage evite ?          /2  (0=beaucoup, 1=un peu, 2=propre)

  SCORE SESSION : [X]/10
```

### 6. Sauvegarde — Notion Usage Tracker

Enregistrer 1 ligne dans la base Notion (ou en memoire si Notion desactive) :

```
FORMAT HISTORIQUE (1 ligne par session) :

[DATE] | [HEURE] | [TYPE] | [ENERGIE] | [MODELE] | [TOKENS~] | [COUT~] | [SCORE/10] | [NOTE]
2026-03-31 | 14h-15h30 | CRM+Skills | G[4] | Opus | ~95k | ~$8.50 | 8/10 | crawl web trop lourd
2026-03-31 | 18h-18h15 | Relances | G[3] | Sonnet | ~12k | ~$0.20 | 9/10 | clean
2026-03-30 | 10h-11h | Strategie | G[5] | Opus | ~65k | ~$5.50 | 7/10 | trop de brainstorm

METRIQUES CUMULEES (weekly-review) :
  Tokens total semaine : [somme]
  Cout API equivalent : [somme]
  Score moyen : [moyenne /10]
  Sessions : [nombre]
  Modele le plus utilise : [nom]
  Gaspillage #1 recurrent : [pattern]
```

### 7. Codes courts de fermeture

Richard peut enchainer apres `LOG+` :

```
LOG+ → BILAN     (log+ complet + bilan journee)
LOG+ → WEEKLY    (log+ + lance la weekly review)
LOG+ → PLAN[n]h  (log+ + planifie la prochaine session de n heures)
LOG+             (log+ seul, juste le bilan)
```

## Examples

### Exemple 1 : Session courte et efficace

```
Richard : "/log+"

LOG+ — FERMETURE SESSION
=========================
Date : 2026-03-31
Duree : ~15 min
Objectif : Relancer 3 prospects en retard
Atteint : OUI

PRODUCTION :
  [x] 3 messages de relance rediges et valides
  [x] CRM Notion mis a jour (dates relance)
  [x] 1 prospect passe en "Perdu" (J+45 sans reponse)

CONSOMMATION :
  Tokens total : ~11k
  Cout API eq. : ~$0.18 (Sonnet)
  Detail : texte 4k | Notion 5k | overhead 2k

EFFICACITE : elevee
  Gaspillage : aucun
  Skill prospect-coach → charge direct, zero re-explication

OPTIMISATIONS :
  → Haiku suffirait pour les relances simples (economie ~40%)
  → Preparer la liste des prospects AVANT le /log

SCORE : 9/10
```

### Exemple 2 : Session lourde

```
Richard : "/log+"

LOG+ — FERMETURE SESSION
=========================
Date : 2026-03-31
Duree : ~1h30
Objectif : Creer skills manquantes + benchmark tarifs + systeme client
Atteint : OUI

PRODUCTION :
  [x] 5 skills creees (devis, tournage, derushage, post-livraison, qualification)
  [x] Benchmark tarifs marche (7 sources web)
  [x] 8 champs ajoutes au CRM Notion
  [x] Prospect-coach v2 avec scoring integre
  [x] Analyse economies tokens

NON FAIT :
  [ ] Devis design (en attente doc Richard)
  [ ] Test scoring sur prospect reel

CONSOMMATION :
  Tokens total : ~95k
  Cout API eq. : ~$8.50 (Opus)
  Detail : texte 20k | Notion 25k | web search 20k | skills 25k | overhead 5k

EFFICACITE : elevee (beaucoup produit)

  Gaspillage detecte :
  - Crawl web → fichier 75k trop gros, oblige de re-lire en morceaux (~5k tokens perdus)
  - Recherche Romain C Productions → pas de tarifs concrets (recherche inutile)

OPTIMISATIONS PROCHAINE FOIS :
  → Limiter maxCharacters a 2000 sur les crawls web (pas 4000)
  → Rechercher sur Malt directement (tarifs plus precis que blogs)
  → Les skills sont maintenant creees — les sessions devis/prospect
    seront beaucoup plus legeres (~60% tokens en moins)

SCORE : 8/10 (un point perdu sur le crawl trop lourd)

HISTORIQUE :
2026-03-31 | Skills+benchmark+CRM | Normal | Opus | ~95k | ~$8.50 | 8/10
```

## References

- Depend de : `log` (les compteurs sont initialises au /log)
- Alimente : memoire projet (historique sessions)
- Alimente : `weekly-review` (metriques d'utilisation Claude)
- Lie a : `energy-gate` (correler energie/efficacite)
- Lie a : `confidence-calibration` (precision des estimations)
