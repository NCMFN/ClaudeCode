#!/usr/bin/env node
/**
 * Stop Hook — LOG+ Reminder
 *
 * Runs after each Claude response (Stop event).
 * Checks if the session has been going for a while without a LOG+ close.
 * Sends a gentle reminder to close the session properly.
 *
 * Non-blocking, async. Only triggers after significant activity.
 */

'use strict';

const path = require('path');
const fs = require('fs');
const { log } = require('../lib/utils');

function getSessionStateDir() {
  const home = process.env.HOME || process.env.USERPROFILE || '';
  return path.join(home, '.claude', 'sessions');
}

/**
 * Exportable run() for in-process execution via run-with-flags.js.
 */
function run(rawInput) {
  let input = {};
  try {
    if (rawInput && typeof rawInput === 'string' && rawInput.trim()) {
      input = JSON.parse(rawInput);
    }
  } catch {
    // stdin might not be JSON
  }

  const transcriptPath = input.transcript_path || process.env.CLAUDE_TRANSCRIPT_PATH || '';

  if (!transcriptPath || !fs.existsSync(transcriptPath)) {
    return { exitCode: 0 };
  }

  // Count messages in transcript to estimate session length
  let messageCount = 0;
  let content = '';
  try {
    content = fs.readFileSync(transcriptPath, 'utf8');
    const lines = content.split('\n').filter(Boolean);
    messageCount = lines.length;
  } catch {
    return { exitCode: 0 };
  }

  // Only suggest LOG+ after substantial activity (15+ messages)
  if (messageCount < 15) {
    return { exitCode: 0 };
  }

  // Check if LOG+ was already done in this session
  if (content.includes('LOG+') || content.includes('FERMETURE SESSION')) {
    return { exitCode: 0 };
  }

  // Check if we already reminded (don't spam)
  const stateDir = getSessionStateDir();
  const reminderFile = path.join(stateDir, 'log-plus-reminded.tmp');

  if (fs.existsSync(reminderFile)) {
    try {
      const stat = fs.statSync(reminderFile);
      const age = Date.now() - stat.mtimeMs;
      if (age < 30 * 60 * 1000) {
        return { exitCode: 0 }; // Reminded less than 30 min ago
      }
    } catch {
      // Continue
    }
  }

  // Estimate tokens based on message count
  const estimatedTokens = messageCount * 2000; // rough estimate
  const isHeavy = estimatedTokens > 50000;

  if (!isHeavy) {
    return { exitCode: 0 };
  }

  // Write reminder state
  try {
    fs.mkdirSync(stateDir, { recursive: true });
    fs.writeFileSync(reminderFile, new Date().toISOString());
  } catch {
    // Non-critical
  }

  const message = [
    '',
    `[Session longue detectee (~${messageCount} messages, ~${Math.round(estimatedTokens / 1000)}k tokens)]`,
    `Pense a faire LOG+ pour fermer proprement et tracker la consommation.`,
    '',
  ].join('\n');

  return { exitCode: 0, stdout: message };
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
    log('session-log-close', `Error: ${err.message}`);
  }
  process.exit(0);
});
