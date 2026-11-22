"""V0.5 prompt-diet, privacy and local STT contract regression checks."""
from __future__ import annotations
import io
import wave
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from backend.engine import ShopGame
from backend import app as service
from backend import exodia
from backend import stt_local


def sample(npc='maya'):
    game=ShopGame(seed=13)
    first=game.open_encounter(npc, 'buy')
    scene,state=game.take_turn(first['session_id'], 'Can you talk about GTA 6 and iPhones?', 1)
    return game, scene, state


def test_prompt_budget_below_1200_on_first_turn():
    _, scene, state=sample()
    profile=exodia.build_instructions(scene,state)
    prompt=exodia.build_prompt(scene,state)
    assert len(profile)<800
    assert len(prompt)<500
    assert len(profile)+len(prompt)<1200
    assert prompt.count('Can you talk about GTA 6') == 1
    assert 'GTA 6' in prompt
    assert 'reservation' not in prompt.lower()
    assert 'wallet' not in prompt.lower()


def test_prompt_two_recent_exchanges_with_long_history():
    _, scene, state=sample()
    state['history']=[{'speaker':'npc' if i%2==0 else 'player',
                       'text':'Long anecdote ' + 'x'*450}
                      for i in range(20)]
    state['history'].append({'speaker':'player','text':scene['user_text']})
    prompt=exodia.build_prompt(scene,state)
    assert len(prompt)<=1600
    assert prompt.count('Long anecdote')<=4
    assert prompt.count('Can you talk about GTA 6')==1
    assert 'Prior dialogue:' in prompt


def test_era_identity_not_lost_to_prompt_diet():
    _,scene,state=sample('aldric')
    instruction=exodia.build_instructions(scene,state)
    assert 'medieval' in instruction.lower()
    assert 'modern terms unknown' in instruction
    _,scene,state=sample('maya')
    instruction=exodia.build_instructions(scene,state)
    assert 'Modern visitor' in instruction


def test_local_stt_rejects_invalid_wav_and_never_needs_cloud_key(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    with TestClient(service.app) as client:
        r=client.post('/transcribe',data=b'not wav',headers={'content-type':'audio/wav'})
        assert r.status_code==422
        assert 'WAVE' in r.json()['detail']
        assert client.get('/stt/health').status_code==200


def test_local_stt_mock_binary_contract_and_timing(monkeypatch):
    def fake_transcribe(wav):
        assert wav[:4]==b'RIFF'
        return {'text':'This is a spoken offer.', 'stt_ms':101,'model':'tiny.en','source':'local_whisper'}
    monkeypatch.setattr(stt_local,'transcribe',fake_transcribe)
    buf=io.BytesIO()
    with wave.open(buf,'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(16000)
        out.writeframes(b'\0\0'*160)
    with TestClient(service.app) as client:
        r=client.post('/transcribe',content=buf.getvalue(),headers={'content-type':'audio/wav'})
        assert r.status_code==200
        assert r.json()['source']=='local_whisper'
        assert r.json()['stt_ms']==101


def test_dialogue_metrics_available_even_if_ai_fails(monkeypatch,tmp_path):
    from backend import dialogue_jobs
    class Broken:
        def synthesize(self,*args): raise exodia.ExodiaError('Browser composer missing')
        def close(self):pass
    monkeypatch.setenv('EXODIA_ENABLED','1')
    monkeypatch.setenv('LIVING_COUNTER_OFFLINE','0')
    monkeypatch.setattr(dialogue_jobs,'ExodiaClient',lambda:Broken())
    game=ShopGame(tmp_path/'world.json',seed=14)
    job_mgr=dialogue_jobs.DialogueJobs()
    try:
        initial=game.open_encounter('maya')
        scene,state=game.take_turn(initial['session_id'],'Hello there',1)
        job=job_mgr.start(game,initial['session_id'],scene,state)
        import time
        for _ in range(100):
            answer=job_mgr.get(job['job_id'])
            if answer['state']=='answered': break
            time.sleep(.01)
        assert answer['state']=='answered'
        assert answer['response']['ai_mode']=='offline_fallback'
        assert answer['metrics']['input_chars']==11
        assert answer['metrics']['elapsed_ms']>=0
    finally:
        job_mgr.close()


def test_five_consistent_premium_maya_states_exist():
    assets=Path(__file__).resolve().parent.parent/'godot'/'assets'
    from PIL import Image
    for state in ('neutral','thinking','amused','skeptical','annoyed'):
        file=assets/f'vn_maya_{state}.png'
        assert file.exists()
        image=Image.open(file)
        assert image.size[1]>=700
        assert image.mode=='RGBA'


def test_mic_and_godot_include_real_open_mic_and_barge_in():
    base=Path(__file__).resolve().parent.parent/'godot'/'scripts'
    mic=(base/'MicrophoneCapture.gd').read_text()
    game=(base/'Main.gd').read_text()
    assert 'signal speech_detected()' in mic
    assert 'end_silence_seconds' in mic
    assert 'func begin_open()' in mic
    assert 'func _on_open_mic_detected()' in game
    assert '_barge_in()' in game
    assert 'func _refresh_timing()' in game
