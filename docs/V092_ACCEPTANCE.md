# V0.9.2 Windows playtest checklist

1. **Startup** — open `godot/project.godot`; run and inspect Debugger for parser errors. Use `tools/windows_godot_preflight.ps1` first if your system can find `godot`.
2. **Fast API** — `.env` has `EXODIA_PROVIDER=groq` and `EXODIA_URL=http://127.0.0.1:8766`; F4 must show the live API provider, not scripted fallback. No provider-contract changes were made.
3. **Conditional date** — when Maya asks for an item, say `I will give you 100 gold if you go on a date with me`. Expected: no shop-gold or stock change; she reacts to the specific condition, and the encounter remains open.
4. **Condition pending** — say `I accept` or `confirm trade` after the unsupported date condition. Expected: still no trade.
5. **Ordinary offer** — submit an unconditional valid cash offer. Expected: existing bargaining rules still apply.
6. **Shelf bonus (two steps)** — Open **Shelves**, click a stocked bonus item other than the negotiated target, then click **Add Item to Trade**. Say e.g. `I offer 70 gold and this extra item`. Expected: pending bundle status, no stock/gold mutation yet. If valuation qualifies, say `confirm trade`. Expected: actual item and bonus inventories and gold change once, together.
7. **Untracked item** — offer `100 gold and a Nintendo Switch`. Expected: playful conversation without invented inventory or a completed sale.
8. **Legibility** — inspect right-side trade status and completed-deal label at 1280x800. They should sit on an opaque backdrop, not the bright floor art.
9. **Microphone** — verify OFF, HOLD RECORDING and OPEN MIC states. Listening is voice activity only, **not** anger/flirt recognition.
10. **Expressive dialogue** — use F8 to compare anger/doubt/delight/persuasion and sadness; test with actual Hermes playback. F5 should show a profile, 1.00x speed, PCM duration, glyphs/sec and underruns.

Report actual screenshots and F4/F5 timings for any issues. There is no native Godot or live Hermes proof from the build environment.
