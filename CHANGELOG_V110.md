# V1.1.0 — Living Encounters (Playtest Candidate)

## Shipped in source

- A deterministic Living Encounter Director with **three authored situations each** for Maya, Liu Xue, and Garrick (9 total). Character goal, one undisclosed concern, inspection detail, and a follow-up opportunity are authored rather than free-invented by an LLM.
- Three functional contextual actions: **Inspect Object**, **Ask Origin**, **Offer Assistance**. The player can also say corresponding phrases through local microphone STT, processed as the same actions by the authoritative server.
- Bounded discovery states and one customer-initiated revelation during a longer casual conversation; revealed facts become a meaningful persistent lead. A customer cannot repeatedly reward the same action or append arbitrary new terms.
- New `POST /encounter/action` and `GET /leads` endpoints. Leads persist in existing `save/world.json`, using a backward-compatible optional `leads` list.
- Native Godot visitor-rail layout, refined speech-box placement, compact case title and 3 actionable context buttons. The reference art's bottom promotional strip was deliberately omitted.
- F12 **World Leads** journal. V1.0 F3/F4/F5/F8/F9/F10/F11 remain intact.
- New Elara Veyne illustrated **8-expression study**: neutral, thinking, amused, skeptical, delighted, annoyed, surprised, sad. Individual RGBA files and composite source included.
- Project-local, reusable `.agents/skills/living-counter-visual-bible/SKILL.md`, detailed art bible, manifest and strict validator.
- Exodia adapter **not changed** from V1.0.0. Five-provider API/browser transport, existing Hermes voice profile mappings, current bargaining economy, and microphone input remain untouched.

## Outstanding production gates — not yet approved

- **Illustration**: Safiya, Rin, Master Chen still require independent native-resolution 8-expression rigs. Elara has eight independently drawn expression variations but they originate from 384×512 cells in an authored sheet and are upscaled to 768×1024, below the required 1024×1536 native pixel detail. `python tools/validate_visual_art_v11.py --strict` currently fails, intentionally.
- **Native Godot**: no Godot executable was available in this build environment. Python/API tests and offline GDScript lint do not certify an in-engine render. Run `tools/preflight_v11_windows.ps1` and inspect the real 1280×800 gameplay window.
- **Real voice**: Live Hermes Studio vs Godot F5 timing comparison remains pending; V1.1 doesn't claim to fix slow PCM generation or change voice speed.

**Build classification: playable V1.1.0 candidate, NOT production art complete.**
