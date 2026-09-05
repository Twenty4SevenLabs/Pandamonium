const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../static/js/jarvisVoice.js'), 'utf8');

assert.match(source, /function bargeEnergyDecision\(/);
assert.match(source, /BARGE_RMS_THRESHOLD = 0\.03/);
assert.match(source, /BARGE_RMS_RATIO = 2\.5/);
assert.match(source, /BARGE_IN_MS = 180/);
assert.match(source, /BARGE_GRACE_MS = 400/);
assert.match(source, /function trimListenChunksToTail\(/);
assert.match(source, /function startFreshListenTurn\(/);
assert.doesNotMatch(source, /BARGE_IN_BYTES/);
assert.match(source, /echoCancellation: false/);
assert.doesNotMatch(source, /echoCancellation: true/);

const excerpt = source.match(
  /const BARGE_IN_MS[\s\S]*?function bargeEnergyDecision\([^)]*\) \{[\s\S]*?\n\}/,
)?.[0];
assert.ok(excerpt, 'bargeEnergyDecision and its RMS constants must live together');

const sandbox = {};
vm.runInNewContext(
  `${excerpt}\nthis.bargeEnergyDecision = bargeEnergyDecision;`,
  sandbox,
);

const sampleMs = 32;
const armedAt = 400;

function runWindow(rmsFn, durationMs, start = { baseline: 0, voicedMs: 0 }) {
  let baseline = start.baseline;
  let voicedMs = start.voicedMs;
  let interruptedAt = null;
  for (let now = 0; now <= durationMs; now += sampleMs) {
    const decision = sandbox.bargeEnergyDecision(
      rmsFn(now),
      baseline,
      voicedMs,
      sampleMs,
      now,
      armedAt,
    );
    baseline = decision.baseline;
    voicedMs = decision.voicedMs;
    if (decision.interrupt) {
      interruptedAt = now;
      break;
    }
  }
  return { baseline, voicedMs, interruptedAt };
}

const leak = runWindow(() => 0.02, 4000);
assert.equal(leak.interruptedAt, null, 'headset leak learned as baseline must not barge-in');

const speech = runWindow(now => (now < armedAt ? 0.02 : 0.12), 2000);
assert.ok(
  speech.interruptedAt != null && speech.interruptedAt >= armedAt + 150,
  'unducked user speech over TTS leak must barge-in',
);
