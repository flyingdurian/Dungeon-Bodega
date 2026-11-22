# V0.6.4 — Expressive Dialogue and Natural Conversation (2026-11-18)

## Fixes shipped in source
- Removed the literal repetitive policy fallback: "We can talk about it, but no price is agreed until we formally settle the trade."
- Trade dialogue now filters explicit AI-only cash or item commitments at the game boundary while retaining safe surrounding personality and social comments. Side-offer banter is allowed; settlement remains authoritative.
- Removed the forced auto-offer reminder every third off-topic turn. Model instructions now invite natural jokes, romance banter, contemporary references, and genuine character voice with an <800-char first-turn instruction budget.
- Fixed a typewriter animation problem: glyph entrance tweens arm when each glyph becomes visible, rather than while hidden. Kept Hermes PCM-based approximate speech pacing.
- Added native `EmotionGlyph.gd` per-glyph BBCode effects for angry red vibration, gleaming gold price emphasis, cyan underlined persuasion, warm delighted bounce, and violet doubtful waves. Rebuilt phrase recognition in English and Simplified Chinese, ranked effects by salience instead of matching the first five words. Five-color effect system; at most four major highlights per line.
- Responsive portrait expression reacts to key dialogue, with an emotionally colored dialogue frame and reaction glyph. No new concept screenshot used as interface.
- Confirmed Hermes Studio manifest contains the same 30 voice IDs as the Hermes Engine's voice manifest. Locks named preset/voice/instruction per encounter and sends `speed=1.0`, `pitch_shift=0.0` to avoid server-side speed resampling that changes pitch on Qwen/Chatterbox. F4 displays named preset, locked voice, preset speed vs actual sent speed, instruction, Hermes run ID/model where the server reports them, and text effect categories.
- Preserved Groq (`transport: api`), Gemini API (`api`), DeepSeek/ChatGPT/Gemini (`browser`) on `/api/command/tasks/game-dialogue`. No credentials in game.

## Installation
For a clean install, extract full-project ZIP into a new folder, copy your existing `.env` and any save data you intend to retain, start backend with `start_windows.ps1`, then open `godot/project.godot`.
For overlay update, stop game and Godot and extract overlay directly **inside your existing `The_Living_Counter_POC` folder**, preserving relative subpaths. Restart both backend and Godot.

## Acceptance checks
1. Confirm F4 model/source shows Groq API and `exodia_live` on freeform turns with no model API errors.
2. Ask Maya for a movie/date (without actual monetary quote). Confirm she plays along rather than reciting transaction policy.
3. Suggest a Switch plus 67 gold and ensure no untracked item transfer or false settled price occurs.
4. Test "That's ridiculous!", "better deal", "wonderful", "really?", and Mandarin `这个价格有点高啊` with expected red/cyan/gold/violet phrase animations, visible character reaction and low-level typing audio.
5. Speak several replies with same customer; F4 should show same profile ID, voice ID, instructions, natural 1.00× speed, zero pitch shift. Listen for consistency on the Hermes server.
6. Try F6/F7 pacing. The text is still approximate audio-timeline sync—not word alignment.

## Verification / limitations
Automated Python/API/source-contract suite passes. Native Godot and actual Hermes/Exodia audio were not run in the build environment. If the OS model still speaks slowly at `1.0`, inspect the Hermes model, run metadata and logs; the game cannot guarantee identical TTS prosody from separate generations.
