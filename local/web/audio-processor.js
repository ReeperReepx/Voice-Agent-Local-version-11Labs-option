/**
 * AudioWorkletProcessor for capturing mic input.
 *
 * Buffers 16kHz mono PCM, converts float32 → Int16, computes RMS for VAD.
 * Posts { pcmData: Int16Array, rms: number } to the main thread.
 *
 * Registration: new AudioWorkletNode(ctx, 'pcm-capture-processor')
 */

class PCMCaptureProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._buffer = [];
    this._bufferLen = 0;
    // 2048 samples ≈ 128ms at 16kHz (AudioContext runs at 48kHz by default,
    // but we resample to 16kHz on the main thread before sending).
    // At the native 48kHz rate the worklet receives 128 samples per process()
    // call, so we accumulate until we have a decent chunk.
    this._targetSamples = 2048;
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;

    const channelData = input[0]; // mono
    this._buffer.push(new Float32Array(channelData));
    this._bufferLen += channelData.length;

    if (this._bufferLen >= this._targetSamples) {
      // Concatenate buffered samples
      const merged = new Float32Array(this._bufferLen);
      let offset = 0;
      for (const chunk of this._buffer) {
        merged.set(chunk, offset);
        offset += chunk.length;
      }
      this._buffer = [];
      this._bufferLen = 0;

      // Compute RMS amplitude for VAD
      let sumSq = 0;
      for (let i = 0; i < merged.length; i++) {
        sumSq += merged[i] * merged[i];
      }
      const rms = Math.sqrt(sumSq / merged.length);

      // Convert float32 [-1,1] → Int16 PCM
      const pcmData = new Int16Array(merged.length);
      for (let i = 0; i < merged.length; i++) {
        const s = Math.max(-1, Math.min(1, merged[i]));
        pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }

      this.port.postMessage({ pcmData, rms }, [pcmData.buffer]);
    }

    return true;
  }
}

registerProcessor('pcm-capture-processor', PCMCaptureProcessor);
