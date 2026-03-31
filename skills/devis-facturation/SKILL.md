---
name: devis-facturation
description: Creation de devis videaste freelance — grille tarifaire, CGV, cycle de paiement, suivi Notion
version: 2.0.0
category: Business
priority: 1
author: Richard Cusey
---

# Devis & Facturation

> Generer des devis professionnels pour les prestations video de Richard.
> Tarifs bases sur sa grille reelle (Notion), statut auto-entrepreneur.

## When to Use

- Quand Richard demande de faire un devis
- Quand un prospect demande un prix
- Pour preparer une proposition commerciale
- Pour verifier si un tarif est coherent

## How It Works

### 1. Grille Tarifaire (source: Notion)

```
TARIFS RICHARD CUSEY — Auto-entrepreneur
TVA non applicable, art. 293 B du CGI

TARIF JOURNALIER (TJM) :
  Junior / Simple      : 250€/jour
  Standard             : 350€/jour
  Expert / Complexe    : 450€/jour

BRAND CONTENT :
  Interview simple     :  600€
  Reportage entreprise : 1000€
  Film corporate       : 1400€

EVENEMENTIEL :
  Captation 1/2 journee:  400€
  Captation journee    :  700€
  Multi-camera (2+)    : 1200€

DRONE :
  Supplement drone     : +200€/jour
  Drone seul (plans)   :  350€

MONTAGE / POST-PRODUCTION :
  Montage simple       : 200€/jour
  Montage complexe     : 350€/jour
  Etalonnage           : 150€/jour
  Motion design simple : 250€/jour

LIVRABLES SUPPLEMENTAIRES :
  Format reseaux sociaux (adaptation) : +100€/format
  Sous-titrage                        : +80€/video
  Version courte (teaser)             : +150€
```

### 2. Structure du Devis

```
DEVIS N° [ANNEE]-[NUMERO]
Date : [date]
Validite : 30 jours

CLIENT :
  [Nom / Entreprise]
  [Adresse]
  [SIRET si applicable]

PRESTATION :
  [Description detaillee]

  Ligne 1 : [Prestation] — [Quantite] x [Prix unitaire] = [Total]
  Ligne 2 : [Prestation] — [Quantite] x [Prix unitaire] = [Total]
  ...

  TOTAL HT : [montant]€
  TVA non applicable, art. 293 B du CGI
  TOTAL TTC : [montant]€

CONDITIONS :
  Acompte : 30% a la commande ([montant]€)
  Solde : 70% a la livraison
  Delai de paiement : 30 jours
```

### 3. CGV Essentielles

```
CONDITIONS GENERALES (resume) :
  - Devis valable 30 jours
  - Acompte 30% obligatoire pour bloquer la date
  - Annulation < 48h : acompte non rembourse
  - Droits d'utilisation : web + reseaux sociaux (sauf mention contraire)
  - Droits etendus (TV, affichage) : +30% sur le total
  - Revision incluse : 1 aller-retour
  - Revisions supplementaires : 80€/h
  - Materiel fourni (camera, audio, eclairage, drone si applicable)
```

### 4. Cycle de Paiement

```
ETAPES :
  1. Devis envoye → attente validation
  2. Devis signe → acompte 30% demande
  3. Acompte recu → date bloquee, production lancee
  4. Livraison → facture solde (70%)
  5. Paiement solde → cloture

RELANCES PAIEMENT :
  J+7 apres facture : relance douce
  J+15 : relance ferme
  J+30 : mise en demeure
  J+45 : transmission a un service de recouvrement
```

### 5. Adaptation selon l'archetype client

```
DIRIGEANT PME :
  → Devis clair, 1 page, pas d'options multiples
  → Insister sur le multi-livrable (valeur percue)
  → Proposition "Pack" si recurrence possible

RESP. COMM :
  → Devis detaille avec ligne par ligne
  → Ajouter une section ROI estime
  → Prevoir les formats reseaux sociaux

STARTUP :
  → Devis court et direct
  → Proposer un tarif "premiere collab" si score > 60
  → Livraison rapide mise en avant

CLIENT LUXE :
  → Devis premium (pas de discount)
  → Mettre en avant la direction artistique
  → Presentation soignee
```

## Examples

### Exemple : Devis restaurant

```
Richard : "Fais un devis pour un restaurant dans le 11e, ils veulent une video de presentation"

DEVIS N° 2026-015
Date : 2026-03-31
Validite : 30 jours

CLIENT : [Nom du restaurant]

PRESTATION : Video de presentation restaurant

  1. Tournage 1/2 journee (4h)        :  400€
     Captation ambiance, cuisine, equipe
  2. Supplement drone (plans exterieurs):  200€
  3. Montage (1 jour)                  :  200€
     Version principale 60-90 sec
  4. Adaptation reseaux sociaux        :  100€
     Format vertical Instagram/TikTok

  TOTAL HT : 900€
  TVA non applicable, art. 293 B du CGI

  Acompte 30% : 270€
  Solde livraison : 630€

  Delai : livraison sous 10 jours ouvres
  Revision : 1 aller-retour inclus
```

## References

- Depend de : `qualification-client` (le score determine le tarif applique)
- Depend de : `math-verifier` (verification des calculs)
- Alimente : `suivi-post-livraison` (une fois le devis accepte)
- Lie a : `prospect-coach` (le devis suit la qualification)
