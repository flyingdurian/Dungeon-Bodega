"""Local-first Windows microphone transcription (faster-whisper / CTranslate2).

Runs ONLY in the game director. No Anthropic/OpenAI credentials or Exodia calls.
Never expose recorded audio in logs, diagnostics, or persistent files.
"""
from __future__ import annotations

import io
import os
import threading
import time
from typing import Any

_MODEL: Any = None
_MODEL_KEY = None
_LOCK = threading.RLock()
_STATE = {'status': 'not_loaded', 'model': '', 'device': '', 'error': ''}


class STTUnavailable(RuntimeError):
    pass


def settings() -> tuple[str, str, str]:
    model = os.getenv('STT_MODEL_SIZE', 'tiny.en').strip() or 'tiny.en'
    device = os.getenv('STT_DEVICE', 'cpu').strip().lower() or 'cpu'
    compute = os.getenv('STT_COMPUTE_TYPE', 'int8' if device == 'cpu' else 'float16').strip().lower()
    if device not in ('cpu', 'cuda'):
        raise STTUnavailable('STT_DEVICE must be cpu or cuda')
    if not 1 <= len(model) <= 80:
        raise STTUnavailable('STT_MODEL_SIZE invalid')
    return model, device, compute


def status() -> dict:
    with _LOCK:
        return dict(_STATE)


def get_model():
    global _MODEL, _MODEL_KEY
    key = settings()
    with _LOCK:
        if _MODEL is not None and _MODEL_KEY == key:
            return _MODEL
        _STATE.update(status='loading', model=key[0], device=key[1], error='')
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            _STATE.update(status='missing_dependency', error='Install requirements-stt-windows.txt')
            raise STTUnavailable('Local STT not installed. Run: .venv\\Scripts\\python.exe -m pip install -r requirements-stt-windows.txt') from exc
        try:
            _MODEL = WhisperModel(key[0], device=key[1], compute_type=key[2], cpu_threads=4)
            _MODEL_KEY = key
            _STATE.update(status='ready', error='')
        except Exception as exc:
            _STATE.update(status='error', error=type(exc).__name__)
            raise STTUnavailable(f'Whisper model initialization failed ({type(exc).__name__}); try CPU/int8 or inspect local model cache') from exc
        return _MODEL


def prewarm() -> None:
    def worker():
        try:
            get_model()
        except STTUnavailable:
            pass  # status() gives the owner an actionable, nonsecret error
    threading.Thread(target=worker, daemon=True, name='whisper-prewarm').start()


def transcribe(wav: bytes) -> dict:
    if len(wav) < 44 or wav[:4] != b'RIFF' or wav[8:12] != b'WAVE':
        raise ValueError('Expected WAV audio')
    t0 = time.perf_counter()
    model = get_model()
    language_choice = os.getenv('STT_LANGUAGE', 'en').strip().lower() or 'en'
    if language_choice == 'auto' and settings()[0].endswith('.en'):
        raise STTUnavailable('Auto multilingual transcription requires a multilingual Whisper model (e.g. STT_MODEL_SIZE=base)')
    recognition_language = None if language_choice == 'auto' else language_choice
    try:
        segments, info = model.transcribe(
            io.BytesIO(wav),
            language=recognition_language,
            beam_size=1,
            best_of=1,
            temperature=0,
            vad_filter=True,
            vad_parameters={'min_silence_duration_ms': 500},
            condition_on_previous_text=False,
        )
        text = ' '.join(x.text.strip() for x in segments).strip()
    except Exception as exc:
        raise STTUnavailable(f'Local transcription failed ({type(exc).__name__})') from exc
    return {'text': text[:500], 'stt_ms': round((time.perf_counter() - t0)*1000),
            'model': settings()[0], 'source': 'local_whisper'}
