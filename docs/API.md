# The Living Counter — v0.2 Game Director API

Game frontend connects **only** to the Python game director on `http://127.0.0.1:8010` and the independently running Hermes server (`http://10.0.0.129:8000`, or the owner's port `8880`). **Godot must never connect directly to Exodia**; it runs on `127.0.0.1:8765` or `8766` and is called privately by the game director.

The director exposes FastAPI interactive docs at `/docs` and JSON schema at `/openapi.json`.

| Method | Endpoint | Request | Response |
| --- | --- | --- | --- |
| GET | `/health` | — | `status`, `version:0.2.0`, `ai_mode` (`exodia_configured` or `offline`), `exodia_provider`, `hermes_url`, `transcription` |
| GET | `/catalog` | — | public items, stock, gold, NPC names |
| POST | `/encounter` | `{"npc_id":"silas","intent":"buy"}` (both optional) | Initial full scene, offer, `session_id`, `turn:0` |
| POST | `/talk` | `{"session_id":"32hex","turn":1,"text":"I want 40 gold","interrupt_before":false,"heard_text":""}` | **202** queued Exodia dialogue job, or **200** complete offline scene |
| GET | `/dialogue/{job_id}` | — | `state:queued/working/answered/cancelled`, `response` when answered; optional sanitized error |
| POST | `/interrupt` | `{"session_id":"32hex","heard_text":"..."}` | Penalty/reaction; signals outstanding dialogue job to cancel |
| POST | `/transcribe` | raw PCM16 WAV (`Content-Type: audio/wav`) | Transcribed text **only with independent STT API key** |
| GET | `/debug/{session_id}` | — | Private state only on loopback AND `LIVING_COUNTER_DEBUG=1` |

## Non-blocking Exodia loop

1. `POST /encounter` returns the NPC arrival and initial public quote immediately.
2. `POST /talk` validates and applies the bargain immediately. In Exodia mode it returns HTTP **202**:

```json
{
  "job_id":"0123456789abcdef0123456789abcdef",
  "status":"queued",
  "turn":1,
  "scene":{"session_id":"...","turn":1,"line":"","offer":31,"emotion":"suspicious"}
}
```

The `scene` also contains the ordinary public inventory, NPC, offer and transaction fields. Its empty `line` means **do not start Hermes yet**.

3. `GET /dialogue/{job_id}` about twice a second. While queued/working, leave text input and microphone interrupt enabled. On `answered`, read the complete `response.line`, then start Hermes `POST /stream` with the response's engine-specific voice ID.
4. On interruption, immediately stop local audio and freeze the typewriter. The next `POST /talk` includes `interrupt_before:true` and a `heard_text` fragment of the **actual revealed/spoken** words, maximum 220 characters. The game director signals cancellation of the previous Exodia job and applies its patience penalty before processing the next turn, while its serial worker confirms remote cancellation before sending the next browser-model task. An out-of-order, late response must never play.
5. `POST /interrupt` is available if playback is stopped without submitting another turn, or when moving to another NPC. It also accepts an optional heard fragment.

An interrupted or cancelled turn is **not refunded**: the economy decision was applied before narration. A transaction can be irreversible even when audio is skipped. Exodia is never allowed to commit money, inventory, prices or patience.

## Exodia browser-task contract (internal only)

The server reads the Exodia URL from `EXODIA_URL`, default `http://127.0.0.1:8765`; `8766` is the Cursor test service if that's signed in. Set `EXODIA_PROVIDER` to `chatgpt`, `gemini`, or `deepseek` (default `deepseek`). It sends `X-Exodia-Client: exodia-dashboard` and `Content-Type: application/json` on every call.

- GET `/api/command/model-instructions` to measure the saved text length. **Does not overwrite existing saved instructions**; an incompatible saved blob can affect behavior and one too long blocks the live job.
- POST `/api/command/tasks` with `agent_id:"kiko"` (never the shop NPC name), `model_choice` configured provider, `transport:"browser"`, `web_research:false`, `prompt` recent untrusted shop transcript + latest player speech, `custom_instructions` current NPC profile/world/safety.
- Validates saved + custom <=4000 characters, and composed <=12000. Reduces transcript to eight turns. Exodia's 422 results become a labeled offline fallback.
- Poll GET `/api/command/tasks` (latest 75) for the exact returned `id`, approximately every 500ms, until `answered`, `failed`, or `cancelled`.
- When active task is interrupted POST `/api/command/tasks/{task_id}/cancel` and await cancelled/terminal status. HTTP 409 means already finished; discard the previous playback locally. In-flight tasks for this game use one serial worker, regardless of provider. If a cancelled task cannot be confirmed terminal due to Exodia network failure, the adapter blocks further browser submissions until a safe service restart.
- A missing signed-in browser composer requires sign-in by the owner. The service does NOT use `chatgpt:api`, `gemini:api`, or `deepseek:api`.

**Output safety:** the model produces just a short character *reaction*. Its response is checked for price/currency/digit/meta leaks; the *game* appends the authoritative line containing the current offer, acceptance or departure. The model never receives secret price thresholds, wallet, or hidden patience values. Prompt injection protections are layered with strict economic isolation, not presumed foolproof from text instructions alone.

## Hermes speech transport

The game uses the existing Hermes `POST /stream`: raw **PCM16 signed little-endian mono**; no WAV header. Godot's `HermesStream.gd` decodes it into an `AudioStreamGeneratorPlayback`. Make sure the client setting points to the port that actually exposes `/stream` and `/health` (`8000` default; `8880` alternate on this Mac). The Hermes server is not responsible for Exodia polling or STT.

## Errors

- 200 `POST /talk` offline response, 202 in Exodia mode; 404 unknown job/encounter, 409 duplicate/stale/closed turns, 422 invalid body.
- When Exodia is unreachable, invalid, not signed in, times out, or its output violates voice constraints: dialogue jobs still resolve to `answered` with `response.ai_mode="offline_fallback"` and a sanitized `error`, unless explicitly interrupted. This prevents a frozen economy and labels simulated rather than AI conversation.
- `/transcribe` returns 503 if no independent STT provider key, 502 on remote failure. Exodia browser tasks do not transcribe microphone audio.

Both services are local/private-dev prototypes, not authenticated public APIs. Do not port-forward.
