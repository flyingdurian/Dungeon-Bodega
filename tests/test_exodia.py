"""Contract tests with a simulated signed-in Exodia Tower API. No real browser login needed."""
import os
import time
import threading
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.content import NPC_BY_ID
from backend.engine import ShopGame
from backend import app as service
from backend import exodia as mod


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv('EXODIA_ENABLED','1')
    monkeypatch.delenv('LIVING_COUNTER_OFFLINE', raising=False)
    monkeypatch.setenv('EXODIA_PROVIDER','deepseek')
    monkeypatch.setenv('EXODIA_URL','http://127.0.0.1:8766')
    service.game = ShopGame(tmp_path/'world.json',seed=11)
    service.jobs = service.DialogueJobs()
    yield TestClient(service.app)
    service.jobs.close()


def wait_job(client,job_id,seconds=3):
    start=time.monotonic()
    while time.monotonic()-start < seconds:
        r=client.get('/dialogue/'+job_id)
        if r.json()['state'] in ('answered','failed','cancelled'):
            return r.json()
        time.sleep(.025)
    raise AssertionError('background job not terminal')


def test_exodia_schema_headers_and_model_answer(monkeypatch):
    got={'posts':0,'polls':0}
    def mock(req:httpx.Request):
        assert req.headers['x-exodia-client']=='exodia-dashboard'
        if req.url.path.endswith('/model-instructions'):
            return httpx.Response(200,json={'models':[{'provider':'deepseek','text':'Fantasy shop rules.'}]})
        if req.method=='POST' and req.url.path.endswith('/tasks/game-dialogue'):
            data=__import__('json').loads(req.content)
            got['posts']+=1
            assert data['agent_id']=='kiko'
            assert data['transport']=='browser'
            assert data['model_choice']=='deepseek'
            assert data['web_research'] is False
            assert data['custom_instructions'].startswith('You are')
            assert len(data['custom_instructions'])+len('Fantasy shop rules.')<=4000
            assert len(data['prompt'])+len(data['custom_instructions'])+len('Fantasy shop rules.')<=12000
            assert 'reservation' not in data['prompt'].lower()
            assert 'wallet' not in data['prompt'].lower()
            return httpx.Response(201,json={'id':'fake-exodia-task','state':'opening','answer':''})
        if req.method=='GET' and req.url.path.endswith('/tasks'):
            got['polls']+=1
            return httpx.Response(200,json={'tasks':[{'id':'fake-exodia-task','state':'answered','answer':'You have a sharp tongue, merchant.'}]})
        return httpx.Response(404,json={'detail':'not found'})
    actual_client=httpx.Client
    monkeypatch.setattr(mod.httpx,'Client',lambda **kw:actual_client(transport=httpx.MockTransport(mock),**kw))
    g=ShopGame(seed=7)
    first=g.open_encounter('silas','buy')
    scene,snapshot=g.take_turn(first['session_id'],'Are you some kind of thief?',1)
    c=mod.ExodiaClient()
    try:
        line=c.synthesize(scene,snapshot,threading.Event())
    finally:
        c.close()
    assert line=='You have a sharp tongue, merchant.'
    assert got['posts']==1 and got['polls']==1


def test_model_response_cannot_invent_price():
    for output in ('Pay 999 gold!', 'I am an AI language model.', '```\n{\"rules\":true}', 'My price is fifty coins.'):
        with pytest.raises(mod.ExodiaError):mod.clean_answer(output,'Silas')


def test_signed_in_service_must_be_loopback(monkeypatch):
    monkeypatch.setenv('EXODIA_URL','http://10.0.0.129:8765')
    with pytest.raises(mod.ExodiaError):mod.base_url()
    monkeypatch.setenv('EXODIA_URL','http://127.0.0.1:8765')
    assert mod.base_url()=='http://127.0.0.1:8765'


def test_server_returns_nonblocking_dialogue_and_economy_is_authoritative(client,monkeypatch):
    class FakeExodia:
        def synthesize(self,scene,state,cancelled):
            return 'I have been to stranger markets.'
        def close(self):pass
    monkeypatch.setattr(service,'ExodiaClient',lambda:FakeExodia(),raising=False)
    monkeypatch.setattr(__import__('backend.dialogue_jobs',fromlist=['ExodiaClient']),'ExodiaClient',lambda:FakeExodia())
    first=client.post('/encounter',json={'npc_id':'vesper','intent':'buy'}).json()
    result=client.post('/talk',json={'session_id':first['session_id'],'turn':1,'text':'Accept your price. Deal!'} )
    assert result.status_code==202
    j=result.json()
    assert j['scene']['closed'] is True
    assert 'reservation' not in str(j) and 'wallet' not in str(j)
    done=wait_job(client,j['job_id'])
    assert done['state']=='answered'
    response=done['response']
    assert response['ai_mode']=='exodia'
    assert response['transaction']['price']==first['offer']
    assert response['player']['gold']==450+first['offer']
    assert 'I have been to stranger markets' in response['line']
    assert client.post('/talk',json={'session_id':first['session_id'],'turn':1,'text':'Deal'}).status_code==409


def test_player_interrupt_cancels_task_and_queues_next(client,monkeypatch):
    first_started=threading.Event()
    class FakeExodia:
        def synthesize(self,scene,state,cancelled):
            if state['turn']==1:
                first_started.set()
                for _ in range(150):
                    if cancelled.is_set():raise InterruptedError()
                    time.sleep(.01)
                return 'An outdated answer should never play.'
            return 'You have interrupted me, shopkeeper.'
        def close(self):pass
    monkeypatch.setattr(__import__('backend.dialogue_jobs',fromlist=['ExodiaClient']),'ExodiaClient',lambda:FakeExodia())
    first=client.post('/encounter',json={'npc_id':'aldric','intent':'buy'}).json()
    sid=first['session_id']
    a=client.post('/talk',json={'session_id':sid,'turn':1,'text':'Tell me about dragons'}).json()
    assert first_started.wait(1)
    b=client.post('/talk',json={'session_id':sid,'turn':2,'text':'Enough! I want 42 gold',
                               'interrupt_before':True,'heard_text':'An old dragon once'}).json()
    assert b['turn']==2 and b['status']=='queued'
    assert wait_job(client,a['job_id'])['state']=='cancelled'
    last=wait_job(client,b['job_id'])
    assert last['state']=='answered'
    assert 'outdated answer' not in str(last)
    debug=client.get('/debug/'+sid) # debug still protected; no leak
    assert debug.status_code==403
    s=service.game.debug(sid)
    assert any('[cut short] An old dragon once' in h['text'] for h in s['history'])
    assert not any('outdated answer' in h['text'] for h in s['history'])


def test_exodia_unavailable_uses_labeled_fallback(client,monkeypatch):
    class Broken:
        def synthesize(self,*args):raise mod.ExodiaError('Exodia missing composer')
        def close(self):pass
    monkeypatch.setattr(__import__('backend.dialogue_jobs',fromlist=['ExodiaClient']),'ExodiaClient',lambda:Broken())
    first=client.post('/encounter',json={'npc_id':'silas'}).json()
    a=client.post('/talk',json={'session_id':first['session_id'],'turn':1,'text':'Have you seen the new iPhone?'}).json()
    done=wait_job(client,a['job_id'])
    assert done['state']=='answered'
    assert done['response']['ai_mode']=='offline_fallback'
    assert 'eye-phone' in done['response']['line']
    assert 'Exodia missing composer' in done['error']


def test_422_extra_and_404_missing_job(client):
    first=client.post('/encounter',json={}).json()
    bad=client.post('/talk',json={'session_id':first['session_id'],'turn':1,'text':'hi','agent_id':'NPC'})
    assert bad.status_code==422
    assert client.get('/dialogue/'+'a'*32).status_code==404


def test_exodia_cancels_remote_browser_task(monkeypatch):
    monkeypatch.setenv('EXODIA_PROVIDER','deepseek')
    monkeypatch.setenv('EXODIA_URL','http://127.0.0.1:8766')
    monkeypatch.setenv('EXODIA_POLL_SECONDS','0.2')
    pending = threading.Event()
    cancelled = threading.Event()
    seen = {'create': 0, 'cancel': 0}

    def mock(req:httpx.Request):
        if req.url.path.endswith('/model-instructions'):
            return httpx.Response(200,json={'models':[]})
        if req.url.path.endswith('/tasks/game-dialogue') and req.method=='POST':
            seen['create']+=1
            return httpx.Response(201,json={'id':'abc','state':'opening','answer':''})
        if req.url.path.endswith('/abc/cancel'):
            seen['cancel']+=1
            return httpx.Response(200,json={'id':'abc','state':'cancelled'})
        if req.url.path.endswith('/tasks') and req.method=='GET':
            pending.set()
            return httpx.Response(200,json={'tasks':[{'id':'abc','state':'cancelled' if cancelled.is_set() else 'waiting_for_reply','answer':''}]})
        return httpx.Response(404)

    real_client=httpx.Client
    monkeypatch.setattr(mod.httpx,'Client',lambda **kw:real_client(transport=httpx.MockTransport(mock),**kw))
    game=ShopGame(seed=12)
    first=game.open_encounter('silas')
    scene,state=game.take_turn(first['session_id'],'What do you know about dragons?',1)
    c=mod.ExodiaClient()
    errors=[]
    def run():
        try:c.synthesize(scene,state,cancelled)
        except InterruptedError:errors.append('interrupted')
    t=threading.Thread(target=run)
    t.start()
    assert pending.wait(2)
    cancelled.set()
    t.join(3)
    c.close()
    assert not t.is_alive()
    assert errors==['interrupted']
    assert seen=={'create':1,'cancel':1}


def test_saved_instructions_budget_fails_before_task(monkeypatch):
    mod.INSTRUCTION_CACHE.clear()  # isolate per-provider TTL cache from earlier mocks
    monkeypatch.setenv('EXODIA_PROVIDER','deepseek')
    monkeypatch.setenv('EXODIA_URL','http://127.0.0.1:8765')
    seen={'post':0}
    def mock(req:httpx.Request):
        if req.method=='POST':seen['post']+=1
        return httpx.Response(200,json={'models':[{'provider':'deepseek','text':'X'*3900}]})
    real=httpx.Client
    monkeypatch.setattr(mod.httpx,'Client',lambda **kw:real(transport=httpx.MockTransport(mock),**kw))
    game=ShopGame(seed=2);first=game.open_encounter('pippa');scene,state=game.take_turn(first['session_id'],'Hello',1)
    c=mod.ExodiaClient()
    with pytest.raises(mod.ExodiaError,match='saved model instructions'):
        c.synthesize(scene,state,threading.Event())
    c.close()
    assert seen['post']==0
