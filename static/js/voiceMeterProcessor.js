/* Runs on AudioWorkletGlobalScope. Always return true so silence does not
 * garbage-collect the meter (the spec VU example returns false below a
 * threshold and then never recovers). Output stays zeros so connecting to
 * destination pulls the graph without playing the microphone.
 * RMS is averaged across several 128-frame quanta and posted without PCM
 * copies so the main thread can barge-in during TTS playback. */
registerProcessor('voice-meter', class extends AudioWorkletProcessor {
  constructor() {
    super();
    this._sum = 0;
    this._count = 0;
  }
  process(inputs, outputs) {
    const channels = inputs[0];
    const samples = channels && channels[0];
    if (samples && samples.length) {
      let sum = 0;
      for (let i = 0; i < samples.length; i += 1) sum += samples[i] * samples[i];
      this._sum += sum;
      this._count += samples.length;
      if (this._count >= 1536) {
        this.port.postMessage({
          rms: Math.sqrt(this._sum / this._count),
          samples: this._count,
        });
        this._sum = 0;
        this._count = 0;
      }
    }
    const out = outputs && outputs[0] && outputs[0][0];
    if (out) out.fill(0);
    return true;
  }
});
