"""V0.6.3 release gates: economy continuity, expressive typing, voice stability, API providers."""
import json
import threading
from pathlib import Path

import httpx
import pytest

from backend.engine import ShopGame, classify, is_conditional_side_deal
from backend.trade_dialogue import assemble_trade_dialogue
from backend import exodia
from backend.content import NPCS

ROOT=Path(__file__).resolve().parents[1]
MAIN=(ROOT/'godot/scripts/Main.gd').read_text()
HERMES=(ROOT/'godot/scripts/HermesStream.gd').read_text()


def _start_maya(seed=50):
    game=ShopGame(seed=seed)
    first=game.open_encounter('maya','buy')
    s=game.sessions[first['session_id']]
    s['reservation']=100
    s['wallet']=140
    s['offer']=61
    game.rng.random=lambda:0.0  # favorable offer is accepted for deterministic test
    return game,first,s


def test_movie_date_not_binding_cash_side_payment():
    game,first,s=_start_maya()
    before=game.world['gold']
    scene,state=game.take_turn(first['session_id'],"I'd take you to a movie if you accept 67 gold",1)
    assert scene['event']=='social_offer' and scene['side_deal']
    assert scene['proposal']['kind']=='social' and scene['anchor']
    assert game.world['gold']==before and s['offer']==61 and not s['closed']
    assert assemble_trade_dialogue('Give me a hoodie and a Switch!',scene)[0] == scene['anchor']


def test_nintendo_switch_cannot_become_untracked_payment():
    game,first,s=_start_maya()
    scene,_=game.take_turn(first['session_id'],"I'll give you a Nintendo Switch if you accept 70 gold",1)
    assert scene['event']=='social_refused' and not s['closed']
    assert s['offer']==61


def test_cash_only_67_accepted_and_visible_price_is_67():
    game,first,s=_start_maya()
    scene,_=game.take_turn(first['session_id'],'I offer 67 gold for the item.',1)
    assert scene['event']=='deal'
    assert scene['transaction']['price']==67
    assert s['offer']==67 and s['closed']
    assert game.public(s,scene['anchor'],scene['mood'],'idle')['offer']==67


def test_previous_offer_clarification_never_creates_new_offer():
    assert classify('You just accepted 67 gold!')==('chat',None)
    assert classify("Didn't you agree to 67 gold?")==('chat',None)
    game,first,s=_start_maya()
    s['last_player_offer']=67
    s['last_offer_result']='counter'
    scene,_=game.take_turn(first['session_id'],'You just accepted 67 gold!',1)
    assert scene['event']=='clarification'
    assert 'did not accept' in scene['anchor']
    assert '61 gold' in scene['anchor']
    assert s['offer']==61 and not s['closed']


def test_contradicting_ai_reply_is_never_spoken_before_counter():
    scene={'event':'counter','anchor':'My current offer is 61 gold.'}
    got,source=assemble_trade_dialogue('Yes, I accept 67 gold and dinner!',scene)
    assert got=='My current offer is 61 gold.'
    assert source=='game_locked'
    got,source=assemble_trade_dialogue('You have good taste.',scene)
    assert got=='You have good taste. My current offer is 61 gold.'


@pytest.mark.parametrize('name,transport',[
    ('groq','api'),('gemini-api','api'),('gemini','browser'),('deepseek','browser'),('chatgpt','browser')])
def test_provider_route_contract_without_early_sentence(name,transport,monkeypatch):
    monkeypatch.setenv('EXODIA_PROVIDER',name)
    monkeypatch.setenv('EXODIA_URL','http://127.0.0.1:8766')
    exodia.REMOTE_UNCONFIRMED.clear()
    exodia.INSTRUCTION_CACHE.clear()
    calls=[]
    def respond(req):
        if req.url.path.endswith('/model-instructions'):
            return httpx.Response(200,json={'models':[]})
        if req.method=='POST':
            calls.append((req.url.path,json.loads(req.content)))
            return httpx.Response(201,json={'id':'sample-id'})
        if req.method=='GET' and req.url.path.endswith('/tasks'):
            return httpx.Response(200,json={'tasks':[{'id':'sample-id','state':'answered',
                         'answer':'Hello! I will think about that.', 'metrics':{'profile':'game_dialogue_fast'}}]})
        return httpx.Response(404)
    real=httpx.Client
    monkeypatch.setattr(exodia.httpx,'Client',lambda **kw:real(transport=httpx.MockTransport(respond),**kw))
    game=ShopGame(seed=4)
    first=game.open_encounter('maya','buy')
    scene,snapshot=game.take_turn(first['session_id'],'What do you think of my idea?',1)
    c=exodia.ExodiaClient()
    try:
        line=c.synthesize(scene,snapshot,threading.Event())
    finally:
        c.close()
    assert line=='Hello! I will think about that.'
    assert calls[0][0]=='/api/command/tasks/game-dialogue'
    assert calls[0][1]['transport']==transport
    assert calls[0][1]['model_choice']==name
    assert c.metrics['transport']==transport
    assert c.metrics['provider']==name


def test_native_godot_text_entrance_fx_and_hermes_timing():
    assert 'DialoguePop.new()' in MAIN
    assert 'install_effect(pop_effect)' in MAIN
    assert '[revealpop]' in MAIN
    assert '_build_speech_times' in MAIN
    assert '_speech_count_at(heard)' in MAIN or '_speech_count_at(heard/maxf(0.01,timing_factor))' in MAIN
    assert 'hermes.heard_seconds()' in MAIN
    director=(ROOT/'godot/scripts/DialogueDirector.gd').read_text()
    assert '[font_size=%d]' in director and '[bgcolor=%s]' in director and '[emote kind=%s' in director
    assert 'kind == "anger"' in (ROOT/'godot/scripts/EmotionGlyph.gd').read_text()
    assert 'typing_fx.play()' in MAIN
    assert (ROOT/'godot/scripts/DialoguePop.gd').exists()
    assert 'char_fx.offset.y' in (ROOT/'godot/scripts/DialoguePop.gd').read_text()
    assert 'var chars_per_second: float=8.5' not in MAIN


def test_voice_lock_uses_merchant_presets_and_consistent_mood():
    manifest=json.loads((ROOT/'godot/assets/hermes_profile_manifest.json').read_text())
    assert len(manifest)>=20
    legacy={'m04_silas_rogue':'m06_finn_rogue',
            'm05_roderic_hunter':'m09_thane_guard',
            'm06_fenwick_merchant':'m04_marcus_merchant'}
    for npc in NPCS:
        assert legacy.get(npc['chatterbox'],npc['chatterbox']) in manifest
    assert 'voice_lock_session' in MAIN
    assert '"mood":"neutral"' in MAIN
    assert 'Hermes preset:' in MAIN
    assert 'profile_speed' in HERMES
    assert '"pitch_shift":0.0' in HERMES


def test_shop_groq_live_job_source_and_error(monkeypatch,tmp_path):
    """Production-equivalent shop dispatcher; external Exodia transport mocked."""
    import time
    from fastapi.testclient import TestClient
    from backend import app as service, dialogue_jobs
    monkeypatch.setenv('EXODIA_PROVIDER','groq')
    monkeypatch.setenv('EXODIA_ENABLED','1')
    monkeypatch.setenv('LIVING_COUNTER_OFFLINE','0')
    service.game=ShopGame(save_path=tmp_path/'world.json',seed=4)
    service.jobs=dialogue_jobs.DialogueJobs()
    class FakeGroq:
        metrics={'provider':'groq','transport':'api','prompt_chars':480}
        def synthesize(self,scene,state,cancelled,on_early_sentence=None):
            return 'That is an interesting idea, merchant.'
        def close(self):pass
    monkeypatch.setattr(dialogue_jobs,'ExodiaClient',lambda:FakeGroq())
    try:
        with TestClient(service.app) as client:
            first=client.post('/encounter',json={'npc_id':'maya','intent':'buy'}).json()
            r=client.post('/talk',json={'session_id':first['session_id'],'turn':1,
                                        'text':'What kind of music do you like?'})
            assert r.status_code==202
            jid=r.json()['job_id']
            done=None
            for _ in range(150):
                done=client.get('/dialogue/'+jid).json()
                if done['state']=='answered':break
                time.sleep(0.01)
            assert done['state']=='answered'
            assert done['source']=='exodia_live'
            assert done['error'] is None
            assert done['response']['performance']['provider']=='groq'
            assert done['response']['performance']['transport']=='api'
    finally:
        service.jobs.close()
