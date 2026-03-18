/**
 * Tests for install.sh
 *
 * Verifies that the install script correctly installs rules for
 * HTML, CSS, and JavaScript (all covered by the `javascript` language rules).
 *
 * Run with: node tests/scripts/install.test.js
 */

const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { spawnSync } = require('child_process');

const INSTALL_SH = path.join(__dirname, '..', '..', 'install.sh');
const RULES_DIR = path.join(__dirname, '..', '..', 'rules');

// Run install.sh with given args, optionally overriding CLAUDE_RULES_DIR
function run(args = [], env = {}) {
  const result = spawnSync('bash', [INSTALL_SH, ...args], {
    encoding: 'utf8',
    stdio: ['pipe', 'pipe', 'pipe'],
    env: { ...process.env, ...env },
    timeout: 15000
  });
  return {
    stdout: result.stdout || '',
    stderr: result.stderr || '',
    code: result.status !== null ? result.status : 1
  };
}

// Test helper — matches ECC's custom test pattern
function test(name, fn) {
  try {
    fn();
    console.log(`  \u2713 ${name}`);
    return true;
  } catch (err) {
    console.log(`  \u2717 ${name}`);
    console.log(`    Error: ${err.message}`);
    return false;
  }
}

function makeTmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'ecc-install-test-'));
}

function cleanupDir(dir) {
  try {
    fs.rmdirSync(dir, { recursive: true });
  } catch (_) {
    // best-effort cleanup
  }
}

function runTests() {
  console.log('\n=== Testing install.sh (HTML/CSS/JS support) ===\n');

  let passed = 0;
  let failed = 0;

  // ── Usage / no-args ───────────────────────────────────────────────────

  console.log('Usage:');

  if (test('shows usage when called with no arguments', () => {
    const result = run([]);
    assert.strictEqual(result.code, 1, 'Should exit 1 with no args');
    assert.ok(
      result.stdout.includes('Usage:') || result.stderr.includes('Usage:'),
      'Should print usage'
    );
  })) passed++; else failed++;

  if (test('lists javascript as an available language in usage', () => {
    const result = run([]);
    const output = result.stdout + result.stderr;
    assert.ok(output.includes('javascript'), 'Should list javascript as available language');
  })) passed++; else failed++;

  // ── javascript install (claude target) ───────────────────────────────

  console.log('\njavascript rules (claude target):');

  if (test('exits 0 when installing javascript rules', () => {
    const tmpDir = makeTmpDir();
    try {
      const result = run(['javascript'], { CLAUDE_RULES_DIR: tmpDir });
      assert.strictEqual(result.code, 0, `Expected exit 0, got ${result.code}. stderr: ${result.stderr}`);
    } finally {
      cleanupDir(tmpDir);
    }
  })) passed++; else failed++;

  if (test('installs common rules', () => {
    const tmpDir = makeTmpDir();
    try {
      run(['javascript'], { CLAUDE_RULES_DIR: tmpDir });
      const commonDir = path.join(tmpDir, 'common');
      assert.ok(fs.existsSync(commonDir), `common/ dir should exist at ${commonDir}`);
      const files = fs.readdirSync(commonDir);
      assert.ok(files.length > 0, 'common/ should contain files');
    } finally {
      cleanupDir(tmpDir);
    }
  })) passed++; else failed++;

  if (test('installs javascript/ rule directory', () => {
    const tmpDir = makeTmpDir();
    try {
      run(['javascript'], { CLAUDE_RULES_DIR: tmpDir });
      const jsDir = path.join(tmpDir, 'javascript');
      assert.ok(fs.existsSync(jsDir), `javascript/ dir should exist at ${jsDir}`);
    } finally {
      cleanupDir(tmpDir);
    }
  })) passed++; else failed++;

  // Verify each javascript rule file is installed
  const jsRuleFiles = fs.readdirSync(path.join(RULES_DIR, 'javascript'));
  for (const ruleFile of jsRuleFiles) {
    if (!test(`installs javascript/${ruleFile}`, () => {
      const tmpDir = makeTmpDir();
      try {
        run(['javascript'], { CLAUDE_RULES_DIR: tmpDir });
        const dest = path.join(tmpDir, 'javascript', ruleFile);
        assert.ok(fs.existsSync(dest), `${ruleFile} should be installed`);
        const content = fs.readFileSync(dest, 'utf8');
        assert.ok(content.trim().length > 0, `${ruleFile} should not be empty`);
      } finally {
        cleanupDir(tmpDir);
      }
    })) failed++; else passed++;
  }

  if (test('javascript coding-style.md has HTML/CSS/JS path matchers', () => {
    const tmpDir = makeTmpDir();
    try {
      run(['javascript'], { CLAUDE_RULES_DIR: tmpDir });
      const codingStyle = path.join(tmpDir, 'javascript', 'coding-style.md');
      const content = fs.readFileSync(codingStyle, 'utf8');
      assert.ok(content.includes('**/*.html'), 'Should include *.html path matcher');
      assert.ok(content.includes('**/*.css'), 'Should include *.css path matcher');
      assert.ok(content.includes('**/*.js'), 'Should include *.js path matcher');
    } finally {
      cleanupDir(tmpDir);
    }
  })) passed++; else failed++;

  if (test('output confirms installation path', () => {
    const tmpDir = makeTmpDir();
    try {
      const result = run(['javascript'], { CLAUDE_RULES_DIR: tmpDir });
      assert.ok(
        result.stdout.includes('Done') || result.stdout.includes('javascript'),
        'Should confirm installation in output'
      );
    } finally {
      cleanupDir(tmpDir);
    }
  })) passed++; else failed++;

  // ── Multiple languages ─────────────────────────────────────────────────

  console.log('\nMultiple languages:');

  if (test('can install javascript alongside another language', () => {
    const tmpDir = makeTmpDir();
    try {
      const result = run(['javascript', 'python'], { CLAUDE_RULES_DIR: tmpDir });
      assert.strictEqual(result.code, 0);
      assert.ok(fs.existsSync(path.join(tmpDir, 'javascript')), 'javascript/ should exist');
      assert.ok(fs.existsSync(path.join(tmpDir, 'python')), 'python/ should exist');
    } finally {
      cleanupDir(tmpDir);
    }
  })) passed++; else failed++;

  // ── Unknown language ──────────────────────────────────────────────────

  console.log('\nUnknown language:');

  if (test('warns but succeeds when an unknown language is given', () => {
    const tmpDir = makeTmpDir();
    try {
      const result = run(['unknown-lang-xyz'], { CLAUDE_RULES_DIR: tmpDir });
      assert.strictEqual(result.code, 0, 'Should still exit 0 (only warns)');
      const output = result.stdout + result.stderr;
      assert.ok(output.toLowerCase().includes('warning') || output.toLowerCase().includes('skip'),
        'Should warn about unknown language');
    } finally {
      cleanupDir(tmpDir);
    }
  })) passed++; else failed++;

  if (test('still installs common rules even if language is unknown', () => {
    const tmpDir = makeTmpDir();
    try {
      run(['unknown-lang-xyz'], { CLAUDE_RULES_DIR: tmpDir });
      assert.ok(fs.existsSync(path.join(tmpDir, 'common')), 'common/ should always be installed');
    } finally {
      cleanupDir(tmpDir);
    }
  })) passed++; else failed++;

  // ── Unknown target ────────────────────────────────────────────────────

  console.log('\nUnknown target:');

  if (test('exits 1 for unknown --target value', () => {
    const result = run(['--target', 'invalid-target', 'javascript']);
    assert.strictEqual(result.code, 1);
    assert.ok(
      result.stderr.includes('unknown target') || result.stderr.includes('Error'),
      'Should print error about unknown target'
    );
  })) passed++; else failed++;

  // ── Cursor target ─────────────────────────────────────────────────────

  console.log('\nCursor target:');

  if (test('exits 0 for cursor target with javascript', () => {
    const origDir = process.cwd();
    const tmpDir = makeTmpDir();
    try {
      const result = spawnSync('bash', [INSTALL_SH, '--target', 'cursor', 'javascript'], {
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: tmpDir,
        timeout: 15000
      });
      assert.strictEqual(result.status !== null ? result.status : 1, 0,
        `Expected exit 0, got ${result.status}. stderr: ${result.stderr}`);
    } finally {
      process.chdir(origDir);
      cleanupDir(tmpDir);
    }
  })) passed++; else failed++;

  // ── Summary ───────────────────────────────────────────────────────────

  const total = passed + failed;
  console.log(`\nPassed: ${passed}`);
  console.log(`Failed: ${failed}`);
  console.log(`Total:  ${total}`);

  process.exit(failed > 0 ? 1 : 0);
}

runTests();
