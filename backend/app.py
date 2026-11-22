"""Dungeon Bodega — thin FastAPI encounter service, distinct from Hermes TTS."""
from __future__ import annotations
import os, time
from pathlib import Path
from typing import Optional, Literal
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
import httpx
from .engine import ShopGame, GameError
from .brain import offline_flavor
from .dialogue_jobs import DialogueJobs
from . import stt_local, trade_desk
import anyio

SAVE = Path(os.environ.get('LIVING_COUNTER_SAVE',str(Path(__file__).resolve().parent.parent/'save'/'world.json')))
game=ShopGame(save_path=SAVE)
jobs=DialogueJobs()

def exodia_enabled():
    return os.getenv("EXODIA_ENABLED", "1").strip().lower() in ("1", "true", "yes") and os.getenv("LIVING_COUNTER_OFFLINE", "0").strip().lower() not in ("1", "true", "yes")
app=FastAPI(title='Dungeon Bodega — Crossroads Negotiation Prototype',version='1.2.4.4',description='Authoritative barter economy + personality narration; Hermes-Engine runs independently on port 8000.')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['GET','POST'],allow_headers=['*'])

class Start(BaseModel):
    model_config=ConfigDict(extra='forbid')
    npc_id: Optional[str]=None
    intent: Optional[Literal['buy','sell']]=None
    era: Optional[Literal['fantasy','modern','mixed']]=None

class Turn(BaseModel):
    model_config=ConfigDict(extra='forbid')
    session_id: str=Field(min_length=32,max_length=32,pattern=r'^[0-9a-f]{32}$')
    turn: int=Field(ge=1,le=10000)
    text: str=Field(min_length=1,max_length=500)
    interrupt_before: bool=False
    heard_text: str=Field(default='',max_length=220)
    bonus_items: list[str]=Field(default_factory=list,max_length=2)

class Session(BaseModel):
    model_config=ConfigDict(extra='forbid')
    session_id: str=Field(min_length=32,max_length=32,pattern=r'^[0-9a-f]{32}$')
    heard_text: str=Field(default='',max_length=220)

@app.exception_handler(GameError)
async def game_error_handler(_req: Request,exc:GameError):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status,content={'detail':str(exc)})

@app.get('/health')
def health():
    return {'status':'ok','game':'Dungeon Bodega','version':'1.2.4.4',
            'ai_mode':'exodia_configured' if exodia_enabled() else 'offline',
            'exodia_provider':os.getenv('EXODIA_PROVIDER','deepseek'),
            'exodia_endpoint':'local' if exodia_enabled() else 'disabled',
            'hermes_url':os.getenv('HERMES_URL','http://10.0.0.129:8000'),
            'transcription':'local_whisper',
            'stt':stt_local.status(),
            'offline_gameplay':True}

@app.get('/catalog')
def catalog():return game.catalog()

class RestockRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
    item_id: str=Field(min_length=2,max_length=50)
    quantity: int=Field(ge=1,le=3)

@app.get('/ledger')
def ledger():return game.ledger()

@app.post('/restock')
def restock(request:RestockRequest):
    return game.restock(request.item_id,request.quantity)

class EncounterAction(BaseModel):
    model_config=ConfigDict(extra='forbid')
    session_id: str=Field(min_length=32,max_length=32,pattern=r'^[0-9a-f]{32}$')
    turn: int=Field(ge=1,le=10000)
    action: Literal['inspect','ask_origin','offer_help']

@app.get('/intuition/{session_id}')
def intuition_read(session_id: str):
    if len(session_id) != 32 or any(c not in '0123456789abcdef' for c in session_id):
        raise HTTPException(status_code=404, detail='Encounter not found')
    return game.intuition_read(session_id)

@app.get('/leads')
def leads():
    return {'leads':game.leads()}

@app.post('/encounter/action')
def encounter_action(request:EncounterAction):
    return game.encounter_action(request.session_id,request.action,request.turn)

class TradeDeskAction(BaseModel):
    model_config=ConfigDict(extra='forbid')
    session_id: str=Field(min_length=32,max_length=32,pattern=r'^[0-9a-f]{32}$')
    turn: int=Field(ge=1,le=10000)
    action: Literal['examine','check_origin','appraise']

@app.post('/trade-desk/action')
def trade_desk_action(request:TradeDeskAction):
    return game.trade_desk_action(request.session_id,request.action,request.turn)

@app.post('/encounter')
def encounter(request:Start):
    response=game.open_encounter(request.npc_id,request.intent,request.era)
    response['ai_mode']='exodia' if exodia_enabled() else 'offline'
    return response

@app.post('/talk')
def talk(request:Turn):
    start=time.perf_counter()
    # Interruption and subsequent turn update occur in this endpoint, not in a
    # race between separate Godot RPCs. The previous browser task is cancelled
    # while the next one is queued by the single-thread dialogue dispatcher.
    if request.interrupt_before:
        jobs.cancel_session(request.session_id)
        game.interruption(request.session_id,request.heard_text)
    # Narrow voice phrases are the same authoritative action as the native
    # trade-desk buttons. They never go to Exodia or create fabricated stock.
    spoken_inspection = trade_desk.recognize_spoken_action(request.text) if not request.bonus_items else None
    if spoken_inspection:
        response = game.trade_desk_action(request.session_id, spoken_inspection, request.turn)
        response['performance'] = {'source':'game_authoritative', 'provider':'trade_desk'}
        return response
    scene,state=game.take_turn(request.session_id,request.text,request.turn,request.bonus_items)
    if scene['event'] in ('encounter_action','encounter_initiative','trade_inspection'):
        response=game.finalize(request.session_id,scene['anchor'],scene,used_ai=False)
        response['ai_mode']='game_authoritative'
        response['performance']={'source':'game_authoritative','provider':'encounter_director'}
        return response
    if exodia_enabled():
        response=jobs.start(game,request.session_id,scene,state)
        response['thinking_ms']=round((time.perf_counter()-start)*1000)
        return JSONResponse(status_code=202,content=response)
    line=f"{offline_flavor(scene,state)} {scene['anchor']}".strip()
    response=game.finalize(request.session_id,line,scene,False)
    response['thinking_ms']=round((time.perf_counter()-start)*1000)
    return response

@app.get('/dialogue/{job_id}')
def dialogue(job_id:str):
    if len(job_id)!=32 or any(c not in '0123456789abcdef' for c in job_id):
        raise HTTPException(404,'Dialogue job not found')
    result=jobs.get(job_id)
    if result is None: raise HTTPException(404,'Dialogue job not found')
    return result

@app.get('/diagnostics/dialogue')
def dialogue_diagnostics(request: Request):
    """Local-only, opt-in source/failure history; no NPC dialogue or Exodia prompts."""
    if (os.getenv('LIVING_COUNTER_DEBUG','0') != '1' or request.client is None
            or request.client.host not in ('127.0.0.1','::1','testclient')):
        raise HTTPException(status_code=403,detail='Enable local LIVING_COUNTER_DEBUG=1 for diagnostics')
    with jobs.lock:
        recent = list(jobs.jobs.values())[-30:]
        rows = [{'job_id':j['id'], 'state':j['status'],
                 'source':j.get('source','pending'),
                 'error':j.get('error'),
                 'performance':j.get('metrics',{})}
                for j in recent]
    results = sorted([int(r['performance'].get('elapsed_ms',0)) for r in rows
                      if r['state']=='answered' and r['source']=='exodia_live'
                      and r['performance'].get('elapsed_ms') is not None])
    med = results[len(results)//2] if results else None
    p90 = results[min(len(results)-1, int((len(results)-1)*0.9))] if results else None
    return {'total_recent':len(rows), 'live_samples':len(results),
            'live_median_ms':med, 'live_p90_ms':p90,
            'target_ms':4000, 'jobs':list(reversed(rows))}

@app.post('/interrupt')
def interrupt(req:Session):
    jobs.cancel_session(req.session_id)
    return game.interruption(req.session_id,req.heard_text)

@app.get('/debug/{session_id}')
def debug(session_id:str, request:Request):
    if os.getenv('LIVING_COUNTER_DEBUG','0')!='1' or request.client is None or request.client.host not in ('127.0.0.1','::1','testclient'):
        raise HTTPException(status_code=403,detail='Debug unavailable (loopback only, requires LIVING_COUNTER_DEBUG=1)')
    return game.debug(session_id)

@app.get('/stt/health')
def stt_health():
    """Local microphone recognition state; no remote credentials are used."""
    return stt_local.status()


@app.post('/transcribe')
async def transcribe(request:Request):
    """Local, no-key, CPU/GPU faster-whisper STT of a Godot-recorded WAV."""
    length = int(request.headers.get('content-length', '0') or '0')
    if length > 6_000_000:
        raise HTTPException(status_code=413, detail='Recording too large')
    wav = await request.body()
    if not 44 <= len(wav) <= 6_000_000 or wav[:4] != b'RIFF' or wav[8:12] != b'WAVE':
        raise HTTPException(status_code=422, detail='Expected RIFF/WAVE microphone audio')
    try:
        return await anyio.to_thread.run_sync(stt_local.transcribe, wav)
    except stt_local.STTUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.on_event('startup')
def warm_local_stt():
    if os.getenv('STT_PREWARM', '0').lower() in ('1', 'true', 'yes'):
        stt_local.prewarm()

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8010)
