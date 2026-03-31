---
name: log
description: Ouverture de session — cadrage rapide compatible Token Compressor et Session INIT Notion
version: 2.0.0
category: Process
priority: 0
author: Richard Cusey
notion_pages:
  - "Session INIT — Protocole d'ouverture"
  - "TOKEN COMPRESSOR — Guide Humain"
  - "Semantic Compression — LOG"
---

# Log — Ouverture de Session

> Diagnostic de debut de conversation. Fusionne le protocole Session INIT (Notion) + Token Compressor (codes courts) en un seul flux.
> Compatible avec les codes courts : `G[n] → SYNC → P?`

## When to Use

- Au tout debut de chaque nouvelle conversation Claude
- Quand Richard dit "bonjour", "salut", ou envoie `LOG`
- Invocable via `/log` en debut de session
- Declenchement automatique au premier message

## How It Works

### 1. Flux d'ouverture (3 questions — pas 5)

Richard peut repondre en codes courts OU en francais. Les deux marchent.

```
LOG — OUVERTURE SESSION
========================

Q1. ENERGIE + ETAT ?
   Code court : G[n] ou G[n+contexte]
   Francais : "3/5, un peu fatigue"
   Echelle : 1-2 = leger | 3 = normal | 4-5 = focus

Q2. TYPE DE SESSION ?
   Code court : un des types ci-dessous
   Francais : "je veux relancer mes prospects"

   Types reconnus :
   → Prospection / CRM     (charge: prospect-coach, qualification-client)
   → Devis / Tarif          (charge: devis-facturation, qualification-client)
   → Tournage / Prep        (charge: tournage-regie, ecriture-brand)
   → Montage / Derushage    (charge: derushage, video-editing)
   → Ecriture / Script      (charge: ecriture-brand/reseaux/documentaire)
   → Client / Livraison     (charge: suivi-post-livraison)
   → IA / Skills            (charge: skills systeme)
   → Analyse / Strategie    (charge: qualification-client, rex-assistant)
   → Sport / Marathon        (charge: contexte sport)
   → Alternance             (charge: contexte alternance)

Q3. SESSION LOURDE ?
   → PDF a analyser / Artifact HTML / Skills a ecrire → OUI
   → Relances, devis, montage workflow → NON

   Si OUI :
   Desactiver Notion MCP pendant l'analyse lourde
   1 document max par conversation
   Artifact HTML = conversation dediee
```

### Reponse rapide avec Token Compressor

Richard peut tout envoyer en 1 ligne :

```
EXEMPLES D'OUVERTURE COMPRESSEES :

  "G[4] → CRM?"
  → Energie 4/5, session prospection, charge prospect-coach

  "G[2+fatigue] → MONTAGE[Maya]+[3]h"
  → Energie 2/5, session montage Maya 3h, mode leger

  "G[5] → devis resto 11e"
  → Energie 5/5, session devis, charge devis-facturation + qualification-client

  "G[3] → WEEKLY"
  → Energie 3/5, revue hebdomadaire

  "salut, je veux preparer mon tournage demain"
  → Energie non precisee (demander), session tournage, charge tournage-regie
```

### 2. Initialisation de session

Claude affiche un bloc compact (pas un roman) :

```
SESSION INITIALISEE
====================
[date] | Energie [n]/5 | [type session]
Skills : [liste courte]
Mode : [focus/normal/exploration]
Tokens estimes : [faible/moyen/lourd]
[alerte si applicable : lourde, killer tokens, etc.]

→ [premiere action directe]
```

**Regle : la session demarre immediatement apres ce bloc.** Pas de "tu veux commencer par quoi ?", pas de recap du systeme. On enchaine.

### 3. Calibrage automatique selon l'energie

```
ENERGIE 1-2 :
  Mode = leger
  - Pas de session intensive
  - Taches simples uniquement (relances, formatage)
  - Privilegier Haiku
  - Alerte surmenage si 3 sessions a 1-2 consecutives

ENERGIE 3 :
  Mode = normal
  - Reponses structurees mais concises
  - Proposer 2-3 options si pertinent
  - Sonnet par defaut

ENERGIE 4-5 :
  Mode = focus
  - Zero blabla, reponses courtes
  - Action directe, pas d'options multiples
  - Opus si strategie/architecture, Sonnet sinon
```

### 4. Les 3 Killers de Tokens (blocage automatique)

Source : Session INIT Notion. A verifier a CHAQUE ouverture.

```
KILLER 1 : Documents uploades pour analyse
  → 1 document max par conversation
  → Si 2+ documents → recommander de splitter en sessions

KILLER 2 : Artifact HTML massif (cockpit, dashboard)
  → Conversation dediee systematiquement
  → Ne pas melanger avec du travail CRM/skills

KILLER 3 : Tous les MCP actifs pendant session creative
  → Desactiver Notion MCP pendant analyse PDF
  → Reactiver au moment du sync
```

### 5. Compteur de session

Initialiser les compteurs a zero au demarrage :

```
SESSION = {
  start     : [timestamp],
  date      : [date],
  energie   : [1-5],
  type      : [type session],
  mode      : [focus/normal/leger],
  skills    : [liste chargees],
  tokens_in : 0,
  tokens_out: 0,
  tools     : 0,
  notion    : 0,    // appels Notion MCP
  web       : 0,    // recherches Exa
  files     : 0,    // fichiers crees/modifies
  actions   : [],   // liste des actions realisees
}
```

Ces compteurs sont fermes par `/log+` en fin de session.

## Examples

### Exemple 1 : Session focus rapide

```
Richard : "/log"

Claude :
  1. Objectif ?
  2. Priorite ?
  3. Energie ?
  4. Modele ?
  5. Contexte ?

Richard :
  1. Relancer 3 prospects en retard
  2. Urgent
  3. Focus
  4. Sonnet
  5. RAS

Claude :
  SESSION INITIALISEE
  Date : 2026-03-31
  Objectif : Relancer 3 prospects en retard
  Priorite : Urgent
  Mode : Focus
  Modele : Sonnet
  Skills : prospect-coach, qualification-client
  Estimation : faible (< 10k tokens)

  Je lis ton CRM. [action directe, zero blabla]
```

### Exemple 2 : Session exploration

```
Richard : "/log"
  1. Je veux reflechir a ma strategie tarifaire an 2
  2. Fond
  3. Exploration
  4. Opus
  5. J'ai eu 3 refus de devis ce mois-ci

Claude :
  SESSION INITIALISEE
  Date : 2026-03-31
  Objectif : Strategie tarifaire an 2
  Priorite : Fond
  Mode : Exploration
  Modele : Opus
  Skills : qualification-client, devis-facturation, rex-assistant
  Estimation : lourd (> 30k tokens — brainstorm + analyse)
  Contexte note : 3 refus devis ce mois → analyser les patterns

  On commence par regarder les 3 devis refuses ?
```

## References

- Alimente : `log+` (les compteurs initialises ici sont fermes par log+)
- Depend de : toutes les skills (le mapping objectif → skills les charge)
- Lie a : `energy-gate` (le niveau d'energie influence le mode de travail)
