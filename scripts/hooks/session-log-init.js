#!/usr/bin/env node
/**
 * SessionStart Hook — LOG Protocol
 *
 * Injects the LOG questionnaire into Claude's context at session start.
 * Works with Richard's Token Compressor codes (G[n], CRM?, etc.)
 *
 * Output goes to stdout -> Claude reads it as context.
 */

'use strict';

const { log } = require('../lib/utils');

function getTimeSlot() {
  const hour = new Date().getHours();
  if (hour >= 6 && hour < 12) return { slot: 'matin', peak: false, recommendation: 'Opus OK — heure creuse' };
  if (hour >= 12 && hour < 14) return { slot: 'midi', peak: false, recommendation: 'Sonnet recommande — pause courte' };
  if (hour >= 14 && hour < 22) return { slot: 'apres-midi/soir', peak: true, recommendation: 'Heure de pointe — Sonnet prefere, Opus peut throttle' };
  return { slot: 'nuit', peak: false, recommendation: 'Opus OK — heure creuse' };
}

function getDayContext() {
  const day = new Date().getDay();
  const days = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];
  const dayName = days[day];

  // Richard's schedule: boulot alimentaire 11h-14h et 17h30-22h
  // Repos: lundi + mardi matin
  const hour = new Date().getHours();

  let availability = 'disponible';
  if (day >= 3 && day <= 6) { // mercredi-samedi
    if (hour >= 11 && hour < 14) availability = 'boulot alimentaire';
    if (hour >= 17 && hour < 22) availability = 'boulot alimentaire';
  }

  const isRestDay = (day === 1) || (day === 2 && hour < 12);

  return { dayName, availability, isRestDay };
}

/**
 * Exportable run() for in-process execution via run-with-flags.js.
 */
function run(rawInput) {
  const time = getTimeSlot();
  const day = getDayContext();
  const date = new Date().toISOString().split('T')[0];
  const heure = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });

  const lines = [
    `[LOG — OUVERTURE SESSION]`,
    `Date: ${date} | ${day.dayName} ${heure}`,
    `Modele: ${time.recommendation}`,
  ];

  if (day.availability === 'boulot alimentaire') {
    lines.push(`Richard est probablement au boulot alimentaire — session courte recommandee`);
  }

  if (day.isRestDay) {
    lines.push(`Jour de repos — session perso/creative possible`);
  }

  if (time.peak) {
    lines.push(`Heure de pointe Anthropic — privilegier Sonnet pour eviter le throttle`);
  }

  lines.push('');
  lines.push('Pose les 3 questions LOG a Richard :');
  lines.push('  Q1. Energie ? (G[n] ou 1-5)');
  lines.push('  Q2. Type session ? (CRM, devis, tournage, montage, ecriture, IA, sport...)');
  lines.push('  Q3. Session lourde ? (PDF, artifact HTML, skills -> oui/non)');
  lines.push('');
  lines.push('Richard peut repondre en codes courts : "G[4] -> CRM?" = energie 4, session prospection');
  lines.push('Ou en francais normal. Les deux marchent.');

  const output = lines.join('\n');

  return { exitCode: 0, stdout: output };
}

module.exports = { run };

// Stdin fallback for spawnSync execution
const MAX_STDIN = 1024 * 1024;
let data = '';

process.stdin.setEncoding('utf8');
process.stdin.on('data', c => {
  if (data.length < MAX_STDIN) {
    const remaining = MAX_STDIN - data.length;
    data += c.substring(0, remaining);
  }
});

process.stdin.on('end', () => {
  try {
    const result = run(data);
    if (result.stdout) {
      process.stdout.write(result.stdout);
    }
  } catch (err) {
    log('session-log-init', `Error: ${err.message}`);
    process.exit(0);
  }
});
