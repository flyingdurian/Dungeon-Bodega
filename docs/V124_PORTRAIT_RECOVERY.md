# V1.2.4 Portrait Recovery — factual status and owner acceptance

This is an **engineering and art-review preview**, not the seven-character production-art release.

## Implemented
- Corrected undefined `REJECTED_ART_IDS` constant in the Godot client.
- F2 now cycles only available **independent** original art-review candidates for the selected rejected character; no Exodia request.
- Master Chen: four *new* native 1024×1536 transparent RGBA character candidates: thinking, skeptical, suspicious, amused.
- Art candidates stored under `godot/assets/art_review/`; no unsigned art replaces runtime portraits.
- Normal dialogue, 5-provider Exodia, Hermes, economy, microphone, current UI navigation and audio waveforms preserved.

## Blocked / not represented as done
- Master Chen is **4/12 candidate states**; other 6 rejected characters still lack approved 12-state rigs.
- Generated images need owner visual signoff and runtime screenshot checks. Art checker strict gate still fails intentionally.
- Godot native parser/playback cannot be certified from this environment.

## How to test
1. Apply overlay to `The_Living_Counter_POC` or install clean package with `.env` carried across.
2. Open the game, select **Master Chen Wei** via F11 gallery / Settings.
3. Press **F2** to inspect four distinct independent art candidates (thinking, skeptical, suspicious, amused); status line shows unapproved count.
4. End F2 review by advancing dialogue; the normal approved-art policy is restored.
5. Confirm microphone/visitor waveforms and direct Shelves/Ledger/Relationships/Leads remain functional.

**Do not approve the entire character from the new images or a passing backend suite.** Twelve owner-accepted masters, identity-registration review, and native Godot screenshot proof remain release gates.
