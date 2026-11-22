# V1.2.4.3 — Installation and acceptance

## Recommended: overlay over V1.2.4.2
Close Godot and stop the local game backend. Unzip the overlay **inside the existing `The_Living_Counter_POC` directory** with directory structure preserved, and allow overwrite. Restart backend and open `godot/project.godot`. You do not need to change `.env`, Exodia keys, Hermes, or your save.

## Clean installation
Extract the full project into a new folder. Copy your own `.env` and, optionally, a backed-up save from the working install. Restart as usual using `start_windows.ps1`, then open `godot/project.godot`.

## Verify
1. Godot window title shows V1.2.4.3.
2. Persistent left dock: Shelves, Shop Ledger, Relationships, World Leads; no Visitors portrait rail.
3. During Hold to Talk, cyan player waveform visibly responds to microphone input.
4. During Hermes speech, pink visitor waveform responds to audible sound, then becomes flat.
5. Two meters stay opaque and separate from dialogue text and buttons at 1280×800.
6. F4 opens diagnostics alone; F8 opens dialogue performance studio.
7. With an emotional phrase, check for modest audio-level-responsive text motion (exact word timestamps are not available).
8. With Tarek and Rin, F4 still reports the honest neutral fallback for unavailable production expression assets.

## Release blocker
The owner-rejected seven characters have NOT been approved. Missing complete full-size 12-state expression sets are a hard art-production blocker; do not crop concept sheets or promote old low-resolution reaction crops. The Rin PNG still contains embedded background scenery.

Source-level checks cannot replace Windows Godot runtime verification.
