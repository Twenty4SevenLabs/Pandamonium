const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../static/js/jarvisVoice.js'), 'utf8');

assert.match(source, /function bargeEnergyDecision\(/);
assert.match(source, /BARGE_RMS_THRESHOLD = 0\.045/);
assert.match(source, /BARGE_RMS_RATIO = 2\.5/);
assert.match(source, /BARGE_IN_MS = 550/);
assert.match(source, /BARGE_GRACE_MS = 900/);
assert.match(source, /function transcriptLooksLikeTtsEcho\(/);
assert.match(source, /resetArm: false/);
assert.match(source, /let lastSpokenPlain = ''/);
assert.match(source, /function trimListenChunksToTail\(/);
assert.match(source, /function startFreshListenTurn\(/);
assert.doesNotMatch(source, /BARGE_IN_BYTES/);
assert.match(source, /echoCancellation: false/);
assert.doesNotMatch(source, /echoCancellation: true/);

const excerpt = source.match(
  /const BARGE_IN_MS[\s\S]*?function bargeEnergyDecision\([^)]*\) \{[\s\S]*?\n\}/,
)?.[0];
assert.ok(excerpt, 'bargeEnergyDecision and its RMS constants must live together');

const echoExcerpt = source.match(
  /function normalizeVoiceText\([\s\S]*?\nfunction transcriptLooksLikeTtsEcho\([\s\S]*?\n\}/,
)?.[0];
assert.ok(echoExcerpt, 'TTS echo detector must live next to normalizeVoiceText');

const sandbox = {};
vm.runInNewContext(
  `${excerpt}\nthis.bargeEnergyDecision = bargeEnergyDecision;\n${echoExcerpt}\nthis.transcriptLooksLikeTtsEcho = transcriptLooksLikeTtsEcho;`,
  sandbox,
);

const sampleMs = 32;
const armedAt = 900;

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

const ttsBleed = runWindow(now => (now < 1500 ? 0.003 : 0.031), 4000);
assert.equal(
  ttsBleed.interruptedAt,
  null,
  'desk-mic Chatterbox leak just over 0.03 after a quiet baseline must not barge-in',
);

const speech = runWindow(now => (now < armedAt ? 0.02 : 0.12), 2500);
assert.ok(
  speech.interruptedAt != null && speech.interruptedAt >= armedAt + 500,
  'unducked user speech over TTS leak must barge-in',
);

const spoken = 'I can see the currently active brain model unsloth Qwen3.5-9B-GGUF TTS M1 chatterbox';
assert.equal(
  sandbox.transcriptLooksLikeTtsEcho(
    'I can see the currently active brain model on slough 1359B GJUF UDQ4K XL TTS M1',
    spoken,
  ),
  true,
  'Whisper of the agent own Chatterbox audio must be dropped',
);
assert.equal(
  sandbox.transcriptLooksLikeTtsEcho('enable the hermes worker first', spoken),
  false,
  'a real barge-in prompt must still reach the brain',
);
