---
name: derushage
description: Revue structuree des rushes — log, notation, EDL pour montage efficace
version: 1.0.0
category: Production
priority: 1
author: Richard Cusey
---

# Derushage

> Transformer des heures de rushes bruts en un plan de montage clair et efficace.

## When to Use

- Apres un tournage, pour organiser les rushes
- Avant de commencer le montage
- Pour evaluer la qualite et la couverture des prises

## How It Works

### 1. Organisation des Fichiers

```
STRUCTURE DOSSIER PROJET :
  [NOM_PROJET]/
  ├── 01_RUSHES/
  │   ├── CAM_A/         (camera principale)
  │   ├── CAM_B/         (2e angle si applicable)
  │   ├── DRONE/         (plans aeriens)
  │   └── AUDIO/         (son separe si applicable)
  ├── 02_SELECTS/        (meilleurs plans)
  ├── 03_TIMELINE/       (projets de montage)
  ├── 04_EXPORTS/        (exports finaux)
  ├── 05_GFX/            (motion design, titres)
  └── 06_ASSETS/         (musique, SFX, logos client)
```

### 2. Log Brut

Premier passage rapide — noter chaque clip :

```
LOG BRUT — [NOM PROJET]
========================
Date tournage : [date]
Duree totale rushes : [XX] min
Nombre de clips : [XX]

CLIP | TIMECODE | DESCRIPTION | NOTE
-----|----------|-------------|------
001  | 00:00:15 | Plan large facade restaurant | Lumiere OK, passants genants
002  | 00:00:22 | Facade drone altitude | Excellent, garder
003  | 00:00:08 | Entree restaurant steadicam | Legere vibration, utilisable
...
```

### 3. Systeme de Notation

```
NOTATION DES CLIPS :

★★★  EXCELLENT — A utiliser en priorite
     Technique parfaite + emotion/impact fort

★★   BON — Utilisable, bonne qualite
     Technique correcte, contenu pertinent

★    MOYEN — Backup si necessaire
     Petit defaut technique ou contenu faible

✗    INUTILISABLE — A ne pas monter
     Flou, mauvais son, raté, doublon inférieur
```

### 4. Transcription (Interviews)

Pour les clips avec parole (interview, temoignage) :

```
TRANSCRIPTION — CLIP [N]
Locuteur : [Nom]
Timecode : [debut] → [fin]

"[Transcription exacte de ce qui est dit]"

MOMENTS CLES :
  [TC] — [phrase impactante ou information cle]
  [TC] — [autre moment fort]

NOTE : ★★★ / ★★ / ★ / ✗
UTILISABLE POUR : [sequence du montage]
```

### 5. Log Narratif

Deuxieme passage — organiser par sequence du film final :

```
LOG NARRATIF — [NOM PROJET]
=============================

SEQUENCE 1 : INTRODUCTION / ACCROCHE
  Clips retenus : 002 (★★★), 008 (★★), 015 (★★★)
  Son : musique ambiance
  Duree estimee : 15 sec
  Notes : commencer par le plan drone, impact visuel

SEQUENCE 2 : PRESENTATION LIEU / EQUIPE
  Clips retenus : 003 (★★), 012 (★★★), 025 (★★)
  Son : interview patron en voix off
  Duree estimee : 20 sec

SEQUENCE 3 : COEUR DU SUJET
  Clips retenus : 030 (★★★), 031 (★★★), 035 (★★)
  Son : son direct + musique sous
  Duree estimee : 30 sec

SEQUENCE 4 : CONCLUSION / CTA
  Clips retenus : 040 (★★), 042 (★★★)
  Son : musique montante
  Duree estimee : 10 sec

DUREE TOTALE ESTIMEE : 75 sec
RATIO RUSHES/FINAL : [XX]:1
```

### 6. Edit Decision List (EDL)

Pour les projets multi-livrables :

```
EDL — [NOM PROJET]
====================

LIVRABLE 1 : Video principale (60-90 sec)
  SEQ1: clips 002, 008, 015
  SEQ2: clips 003, 012, 025
  SEQ3: clips 030, 031, 035
  SEQ4: clips 040, 042
  AUDIO: musique + voix off interview
  GFX: titre entree + CTA fin

LIVRABLE 2 : Version courte Instagram (30 sec)
  Clips: 002, 030, 031, 042
  AUDIO: musique seule
  FORMAT: 9:16 vertical
  GFX: sous-titres + CTA

LIVRABLE 3 : Story/Reel (15 sec)
  Clips: 030, 031
  AUDIO: musique trending
  FORMAT: 9:16 vertical
  GFX: texte overlay
```

## Examples

### Exemple : Derushage apres tournage restaurant

```
Richard : "J'ai fini le tournage du restaurant, on derush"

LOG BRUT — Restaurant Le Marais
================================
Date : 2026-04-01
Duree rushes : 47 min | 62 clips

TOP SELECTS (★★★) :
  002 — Facade drone coucher de soleil (15s)
  018 — Chef flambant le plat (22s)
  031 — Interview patron "on cuisine avec le coeur" (45s)
  045 — Plan serre assiette fumante (8s)

COUVERTURE :
  Exterieur : OK (drone + sol)
  Interieur ambiance : OK
  Cuisine action : Excellent (beaucoup de plans)
  Interview : OK (2 angles)
  Plans de coupe : OK (details deco, clients)

MANQUE :
  - Plan equipe complete (pas eu le moment)
  - Plan dessert (pas prepare pendant le tournage)

→ On a assez pour le livrable principal + version RS
→ Ratio 47min / 1min30 final = 31:1 (correct)
```

## References

- Depend de : `tournage-regie` (les rushes viennent du tournage)
- Alimente : `video-editing` (le log narratif guide le montage)
- Lie a : `ecriture-brand` (la direction artistique du brief influence les choix)
