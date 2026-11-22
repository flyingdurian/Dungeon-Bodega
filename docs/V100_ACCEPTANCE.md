# V1.0.0 Owner Acceptance Checklist

1. Extract complete project to new directory; copy only working `.env`, back up `save/world.json` before copying saves. Run `start_windows.ps1` and open `godot/project.godot`.
2. **Godot compile gate**: no red GDScript errors on opening, especially `VisitorGallery.gd`, `Main.gd`, `HermesStream.gd`. Report exact script/line on error.
3. Confirm new **Jade Atelier** background. Settings → Backdrop switches between Jade Atelier and Dynasty Shop without UI overlay duplication.
4. Select **VISITORS** on left or press F11. Four new visitors appear in illustrated gallery. Clicking each launches that named customer; each also appears in Settings cast chooser.
5. Check Safiya full-portrait transparency; Elara/Rin/Master Chen are framed bust previews, not complete 5-emotion rigs. Do not approve their final art until new original registered expressions are delivered.
6. Try English/Mandarin, anger, delight, persuasion and doubt with F8; phrase echoes should animate only as words reveal, and the chatbox should remain readable.
7. With `EXODIA_PROVIDER=groq`, verify a live shop line has source `exodia_live` and no error; API route `POST /api/command/tasks/game-dialogue` with `transport:api`. Switch to `gemini-api` and repeat. Browser providers must remain `transport:browser`.
8. Test 50 gold with a date condition, headphones refusal, and 70 gold plus owned stocked item; ensure no hidden transactions occur before confirmation.
9. Compare Hermes Studio to the game's F5 PCM playback for the exact same sentence and preset; report any pitch or pacing drift.
10. Confirm no overlap at the actual 1280x800 window: visitor gallery, navigation, dialogue, input, card and action rail.
