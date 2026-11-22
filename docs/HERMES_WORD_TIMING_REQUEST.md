# Future Hermes enhancement proposal — accurate caption alignment

The Living Counter currently sends `POST /stream` and receives raw PCM16. It cannot know which word falls at which sample frame. In V0.9 it improves weighted subtitle pacing using actual played and generated sample counts plus per-voice calibration. This is only approximate.

An optional **nonbreaking** addition from Hermes would provide word or phrase timing aligned with the audio samples for each synthesis request. Proposed schema (not currently supplied by Hermes):

```
{ "run_id": "...", "sample_rate": 24000, "alignment": [
  { "text": "What a deal", "start_sample": 0, "end_sample": 26000 },
  { "text": "!", "start_sample": 26000, "end_sample": 28500 }
] }
```

Suggested constraints: exactly match the spoken text including punctuation and Mandarin Unicode; stable `run_id`, sample offsets from the first PCM sample, no voice-cloning changes, no API keys in the game, and an explicit unknown/unavailable status when alignment cannot be measured. A sidecar endpoint keyed by `run_id` would be viable only if its alignment is available before or during playback; a late alignment report alone won't solve live captions.

Other useful optional server telemetry: actual applied speed and pitch, engine/voice identifier after resolution, audio sample rate, synthesis queue wait, first PCM latency, and underrun-safe chunk streaming semantics. Current V0.9 does not depend on any of these additions.
