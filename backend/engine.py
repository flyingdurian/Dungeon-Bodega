"""Deterministic authoritative bargaining world, separate from any AI narration."""
from __future__ import annotations
import json, os, random, re, threading, time, uuid, copy
from pathlib import Path
from typing import Optional
from .content import NPCS, ITEMS, NPC_BY_ID, ITEM_BY_ID
from .relationship_memory import extract_player_moment, remember, sanitize_moments, public_relationship
from .proposals import interpret_offer, CONFIRM, CANCEL
from .shop_progression import supply_cost, shop_ledger, MAX_STOCK, spotlight
from .social_contracts import (social_topic, physical_goods, is_confirmation, decide_social_offer,
                               social_line, ACCEPT_WORDS, NEW_TERMS)
from . import living_encounters as living
from . import intuition
from . import trade_desk

class GameError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message); self.status = status

PRICE_RE = re.compile(r"(?<!\w)(\d{1,5})\s*(?:gold|coins?|g)(?!\w)", re.I)
OFFER_RE = re.compile(r"\b(?:for|at|offer|pay|give|take|charge|asking|price|bid|do)\s+(\d{1,5})\b", re.I)
NUMBERS = {'ten':10,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90,'hundred':100}
WORD_PRICE_RE = re.compile(r"\b(" + '|'.join(NUMBERS) + r")\s+(?:gold|coins?)\b", re.I)


def parse_money(text: str) -> Optional[int]:
    # Only explicitly priced dialogue counts: 'GTA 6', 'iPhone 16' won't be bids.
    for rx in (PRICE_RE, OFFER_RE):
        matches = rx.findall(text)
        if matches:
            value = int(matches[-1]); return value if 1 <= value <= 10000 else None
    word = WORD_PRICE_RE.search(text)
    return NUMBERS[word.group(1).lower()] if word else None


def classify(text: str) -> tuple[str, Optional[int]]:
    normalized = text.lower().strip()
    if re.search(r"\b(?:goodbye|farewell|go away|get out|leave my shop|leave now|no deal|never mind)\b", normalized):
        return 'walk', None
    # Quoting someone else's earlier statement is not a new cash offer.
    if re.search(r"(?i)\b(?:you (?:just |already |previously )?(?:said|agreed|accepted|promised|offered|told me)|\b(?:didn't|did not) you (?:agree|accept|say)|\bremember when you)\b", text):
        return 'chat', None
    # Responding to a social invitation is NOT accepting the shop's price.
    # "I accept your movie invitation" must not silently sell a potion.
    social_context = bool(re.search(r"(?i)\b(?:date|movies?|cinema|dinner|invitation|apology|gift|nintendo|iphone|challenge)\b", text))
    trade_context = bool(re.search(r"(?i)\b(?:\d+\s*(?:gold|g|coins?)|price|my offer|your offer|cash|for the item)\b", text))
    if social_context and not trade_context and re.search(r"(?i)\b(?:i accept|i agree|agreed|deal|fine,? yes|i'll take it)\b", text):
        return 'chat', None
    amount = parse_money(text)
    # "I won't accept less than 40 gold" is a firm ask, but
    # "I won't pay 40 gold" is NOT a positive offer.
    refusing = bool(re.search(r"\b(?:won't|will not|cannot|can't|don't|do not)\s+(?:pay|accept|give|take)\b",normalized))
    floor = bool(re.search(r"\b(?:less than|under|below|anything beneath|minimum)\b",normalized))
    if amount is not None and (not refusing or floor):
        return 'quote', amount
    if refusing or re.search(r"\b(?:not a deal|no thanks)\b",normalized):
        return 'chat', None
    if re.search(r"\b(?:deal|agreed|i accept|i'll take it|i will take it|sold|you have a deal|fine,? yes)\b", normalized):
        return 'accept', None
    return 'chat', None


SIDE_PAYMENT = re.compile(
    r"(?i)\b(?:movies?|cinema|date|dinner|lunch|kiss|concert|tickets?|nintendo|switch|" 
    r"playstation|xbox|phone|iphone|console|gift card|gift|laptop)\b")
SIDE_CONDITION = re.compile(r"(?i)\b(?:if you|if we|provided that|in exchange|as well as|plus|throw in|along with|on top of)\b")
COMPOSITE_SIDE = re.compile(r"(?i)\b(?:\d{1,5}\s*(?:gold|g|coins?)\b.{0,35}\b(?:and|with)\b.{0,45}\b(?:nintendo|iphone|switch|movie|dinner|gift|phone|ticket)|\b(?:nintendo|iphone|switch|movie|dinner|gift|phone|ticket)\b.{0,35}\b(?:and|with)\b.{0,35}\d{1,5}\s*(?:gold|g|coins?))")


def is_conditional_side_deal(text: str, kind: str) -> bool:
    # Only disallow off-ledger considerations when the player requests a transaction.
    return kind in ('quote', 'accept') and bool(SIDE_PAYMENT.search(text)) and bool(SIDE_CONDITION.search(text) or COMPOSITE_SIDE.search(text))

def clamp(n, a, b): return max(a, min(b, n))

# Targeted severe personal attacks; do NOT punish normal bargaining or casual
# modern slang (e.g. 'that price is insane', 'that's bullshit').
SEVERE_INSULT = re.compile(r"\b(?:fuck\s+you|fuck\s+off|go\s+fuck\s+yourself|piece\s+of\s+shit|worthless\s+(?:idiot|bastard|moron)|(?:you\s+are|you're)\s+(?:a\s+)?(?:stupid\s+)?(?:cunt|bitch|motherfucker)|shut\s+the\s+fuck\s+up)\b", re.I)
PERSONAL_INSULT = re.compile(r"\b(?:you\s+(?:are|re|'re)\s+(?:a\s+)?(?:idiot|moron|loser|scammer)|stupid\s+(?:merchant|customer|fool)|go\s+to\s+hell)\b", re.I)

def evaluate_abuse(text: str) -> int:
    if SEVERE_INSULT.search(text): return 80
    if PERSONAL_INSULT.search(text): return 28
    return 0

class ShopGame:
    def __init__(self, save_path: Optional[Path] = None, seed: Optional[int] = None):
        self.lock = threading.RLock()
        self.rng = random.Random(seed)
        self.sessions: dict[str, dict] = {}
        self.save_path = Path(save_path) if save_path else None
        self.world = {'gold':450, 'day':1, 'deals':0, 'stock':{i['id']:i['stock'] for i in ITEMS}, 'relationships':{}, 'encounters':0, 'reputation':50,
                      'earned_gold':0, 'spent_gold':0, 'restock_spend':0, 'leads':[]}
        if self.save_path and self.save_path.exists():
            try:
                loaded = json.loads(self.save_path.read_text())
                if isinstance(loaded,dict) and isinstance(loaded.get('stock'),dict):
                    self.world.update({k:loaded[k] for k in ('gold','day','deals','stock','relationships','encounters',
                                                  'reputation','earned_gold','spent_gold','restock_spend','leads') if k in loaded})
            except (ValueError, OSError): pass
        if not isinstance(self.world.get('relationships'), dict):
            self.world['relationships'] = {}
        if not isinstance(self.world.get('leads'), list): self.world['leads'] = []
        self.next_npc_pool: list[str] = []
        self.era = "mixed"

    def _save(self):
        if not self.save_path: return
        self.save_path.parent.mkdir(parents=True,exist_ok=True)
        t = self.save_path.with_suffix('.tmp')
        t.write_text(json.dumps(self.world,indent=2))
        os.replace(t,self.save_path)

    def _next_npc(self):
        if not self.next_npc_pool:
            self.next_npc_pool = [p['id'] for p in NPCS if self.era == 'mixed' or p.get('era','fantasy') == self.era]
            self.rng.shuffle(self.next_npc_pool)
        return self.next_npc_pool.pop()

    def reset(self):
        with self.lock:
            self.sessions = {}; self.world = {'gold':450,'day':1,'deals':0,'stock':{i['id']:i['stock'] for i in ITEMS},'relationships':{},'encounters':0,
                                                   'reputation':50,'earned_gold':0,'spent_gold':0,'restock_spend':0,'leads':[]}
            self.next_npc_pool = []; self._save()

    def open_encounter(self, npc_id: Optional[str] = None, intent: Optional[str] = None, era: Optional[str] = None):
        with self.lock:
            if era is not None:
                if era not in ('fantasy','modern','mixed'): raise GameError(422,'Unknown customer era')
                if era != self.era:
                    self.era = era
                    self.next_npc_pool = []
            npc_id = npc_id or self._next_npc()
            if self.era != 'mixed' and NPC_BY_ID.get(npc_id, {}).get('era', 'fantasy') != self.era:
                raise GameError(422,'Customer is outside the selected roster')
            if npc_id not in NPC_BY_ID: raise GameError(422,'Unknown customer')
            if intent is not None and intent not in ('buy','sell'): raise GameError(422,'Unknown transaction direction')
            kind = intent or ('sell' if self.rng.random() < 0.28 else 'buy')
            available = [i for i in ITEMS if self.world['stock'].get(i['id'],0)>0]
            if kind=='buy' and not available: kind='sell'
            item = self.rng.choice(ITEMS if kind=='sell' else available)
            npc=NPC_BY_ID[npc_id]
            seen=self.world['relationships'].get(npc_id,{})
            if not isinstance(seen, dict):
                seen = {}
            patience = clamp(npc['patience']+self.rng.randint(-13,12),12,98)
            trust = clamp(npc['trust']+seen.get('trust_delta',0)+
                          (int(self.world.get('reputation',50))-50)//10+self.rng.randint(-7,7),4,95)
            price=item['price']
            if spotlight(self.world['day'])['item_id']==item['id']:
                price=round(price*1.10)
            urgency=self.rng.uniform(.72,1.21) if npc_id not in ('vesper','elio') else self.rng.uniform(.85,1.43)
            if kind=='buy':
                limit= max(3,round(price*urgency))
                offer=max(1,round(price*self.rng.uniform(.43,.70)))
                wallet=max(limit,round(limit*self.rng.uniform(1.0,1.8)))
            else:
                limit=max(2,round(price*self.rng.uniform(.48,.86)))
                offer=max(limit+1, round(price*self.rng.uniform(1.02,1.45)))
                wallet=0
            offer=int(clamp(offer,1,9999))
            sid=uuid.uuid4().hex
            s={'id':sid,'npc_id':npc_id,'item_id':item['id'],'kind':kind,'patience':patience,'trust':trust,'wallet':wallet,'reservation':limit,'offer':offer,'opening_offer':offer,'turn':0,'interrupts':0,'offtopic':0,'banter_streak':0,'closed':False,'outcome':None,'history':[], 'pending_trade':None, 'refused_goods':[], 'living':None, 'trade_desk':None, 'created':time.monotonic()}
            self.sessions[sid]=s
            # Prevent unbounded test/demo session accumulation; keep current and newest 79.
            if len(self.sessions)>80:
                oldest=next(iter(self.sessions)); self.sessions.pop(oldest,None)
            self.world['encounters']+=1
            self.world['day']=1+(self.world['encounters']-1)//5
            s['living']=living.build(npc_id,self.world['day'],item['name'])
            s['trade_desk']=trade_desk.make(item,self.world['day'],sid)
            self._save()
            # Variety comes from the character and the offer, not a repeated
            # "we've met before" announcement that dominates every return visit.
            if npc_id == 'liu_xue':
                openings = [
                    f"老板你好！这件{item['name']}，我出{offer}金币，可以吗？",
                    f"哎呀，这个{item['name']}真有趣。{offer}金币，怎么样？",
                    f"又是好东西呀！{item['name']}，{offer}金币。Good price, yes?",
                ] if kind == 'buy' else [
                    f"老板，我带来一件{item['name']}。{offer}金币，看看吧！",
                    f"我这件{item['name']}可是精挑细选的，{offer}金币。",
                ]
            elif npc.get('era') == 'modern':
                openings = ([
                    f"Hey, I brought this {item['name']}. I'm hoping for {offer} gold.",
                    f"Got a minute? I have a {item['name']} worth discussing. {offer} gold?",
                    f"Look what turned up: a {item['name']}. I'm asking {offer} gold.",
                ] if kind == 'sell' else [
                    f"Hey, that {item['name']} looks interesting. Would you take {offer} gold?",
                    f"Okay, I need to ask about your {item['name']}. How about {offer} gold?",
                    f"That {item['name']} is calling my name. Think {offer} gold is fair?",
                ])
            else:
                openings = ([
                    f"I brought a {item['name']} from the road. {offer} gold is my asking price.",
                    f"Take a look at this {item['name']}; shall we discuss {offer} gold?",
                    f"A fair merchant might pay {offer} gold for this {item['name']}.",
                ] if kind == 'sell' else [
                    f"That {item['name']} caught my eye. I'll offer {offer} gold.",
                    f"I seek a {item['name']}. Might {offer} gold tempt you?",
                    f"There's fine craft in that {item['name']}; {offer} gold for it?",
                ])
            opening = self.rng.choice(openings)
            # Acknowledge prior history occasionally, naturally, without the
            # same high-frequency spoken line every encounter.
            if seen.get('visits', 0) > 0 and self.rng.random() < 0.22:
                # Revisit a concrete *player-stated* topic occasionally, without
                # claiming that an imaginary gift or date was ever agreed.
                notes = sanitize_moments(seen.get('moments'))
                if notes and self.rng.random() < 0.65:
                    topic = notes[-1]['topic']
                    opening = ((f"上回你提到了{topic}，挺有意思的。" if npc_id == 'liu_xue'
                                else f"You mentioned {topic} before. Still thinking about it? ") + opening)
                else:
                    extra = (["又见面啦！", "老朋友，今天还有什么好东西？"] if npc_id == 'liu_xue' else
                             ["Good to see you again. ", "I remember this counter. ", "Fancy another round? "])
                    opening = self.rng.choice(extra) + opening
            if s.get('living'):
                opening += ' ' + ('Something about this trade troubles me.' if npc_id!='liu_xue' else '这件东西呀，还有些来历要说。')
            s['history'].append({'speaker':'npc','text':opening})
            return self.public(s,opening,'neutral','enter',event='arrival')

    def _memory(self,s, success: bool):
        p=s['npc_id']; history=self.world['relationships'].setdefault(p,{'visits':0,'deals':0,'trust_delta':0})
        if not isinstance(history, dict):
            history = {'visits':0,'deals':0,'trust_delta':0}
            self.world['relationships'][p] = history
        history['visits']=int(history.get('visits', 0))+1
        if success: history['deals']=int(history.get('deals', 0))+1
        history['trust_delta']=clamp(round((s['trust']-NPC_BY_ID[p]['trust'])*.55),-27,27)
        history['last_outcome']='deal' if success else 'walkout'
        history['last_item']=s['item_id']
        self._save()

    def public(self,s,line,emotion,gesture,event='chat',transaction=None):
        p=NPC_BY_ID[s['npc_id']]; item=ITEM_BY_ID[s['item_id']]
        cue=('Their patience is wearing thin.' if s['patience']<20 else 'They seem restless.' if s['patience']<44 else 'They are watching you carefully.' if s['trust']<42 else 'They seem open to discussion.')
        voice={k:p[k] for k in ('voice','kokoro','chatterbox','reaction')}
        seen = self.world['relationships'].get(s['npc_id'], {})
        return {'session_id':s['id'],'turn':s['turn'],'relationship':public_relationship(seen),'customer':{'id':p['id'],'name':p['name'],'title':p['title'],'color':p['color'],'style':p['style'],'era':p.get('era','fantasy')},
                'item':{'id':item['id'],'name':item['name'],'price':item['price'],'icon':item['icon'],'description':item['description']},
                'kind':s['kind'],'offer':s['offer'],'line':line,'emotion':emotion,'gesture':gesture,'event':event,'cue':cue,
                'closed':s['closed'],'outcome':s['outcome'],'transaction':transaction,
                'player':{'gold':self.world['gold'],'deals':self.world['deals'],'day':self.world['day']},
                'stock':copy.deepcopy(self.world['stock']),'voice':voice,
                'pending_trade':self._public_pending(s.get('pending_trade')),
                'living_encounter':living.public(s.get('living')),
                'trade_desk':trade_desk.public(s.get('trade_desk')),
                'world_leads':len(self.world.get('leads',[]))}

    def intuition_read(self, sid: str) -> dict:
        """An optional non-binding player-skill impression; does not consume a turn."""
        with self.lock:
            s = self.sessions.get(sid)
            if not s: raise GameError(404, 'Encounter not found')
            if s['closed']: raise GameError(409, 'Encounter has ended')
            return intuition.read(s, int(self.world.get('reputation', 50)))

    def interruption(self,sid,heard_text=""):
        with self.lock:
            s=self.sessions.get(sid)
            if not s: raise GameError(404,'Encounter not found')
            if s['closed']: return {'ok':False,'reason':'closed'}
            heard_text=str(heard_text).strip()[:220]
            if heard_text:
                # Only speech actually heard may enter the fictional transcript.
                s['history'].append({'speaker':'npc', 'text':'[cut short] '+heard_text})
            s['interrupts']+=1
            s['patience']=clamp(s['patience']-4,0,100)
            s['trust']=clamp(s['trust']-1,0,100)
            return {'ok':True,'interrupts':s['interrupts'],'reaction':'groan' if s['patience']<45 else 'gasp'}

    def _public_pending(self, pending):
        if not isinstance(pending,dict):
            return None
        return {'cash':pending.get('cash'), 'items':list(pending.get('items', [])),
                'ready':bool(pending.get('ready', False)), 'status':str(pending.get('status','')),
                'kind':pending.get('kind',''), 'topic':pending.get('topic'),
                'locked':pending.get('kind')=='social' and bool(pending.get('ready',False))}

    def _social_cash_feasible(self,s:dict,cash:int)->bool:
        if cash<1:return False
        if s['kind']=='buy':
            return cash<=s['wallet'] and self.world['stock'].get(s['item_id'],0)>0
        return cash<=self.world['gold']

    def _bundle_feasible(self, s: dict, cash: int, bonus: list[str]) -> bool:
        # Cash and all bonus items are shop-owned resources. A bonus is valued
        # conservatively, not at the player's stated price.
        extra_value=sum(round(ITEM_BY_ID[x]['price']*.60) for x in bonus)
        if cash < 1 or any(self.world['stock'].get(x,0)<1 for x in bonus):
            return False
        if s['kind']=='buy':
            return (cash <= s['wallet'] and cash-extra_value <= s['reservation']
                    and self.world['stock'].get(s['item_id'],0)>0)
        return (cash <= self.world['gold'] and cash+extra_value >= s['reservation'])

    def _commit(self,s,amount,bonus_items=None):
        item_id=s['item_id']; item=ITEM_BY_ID[item_id]
        bonus_items=list(bonus_items or [])
        if (len(set(bonus_items))!=len(bonus_items)
                or any(x==item_id or x not in ITEM_BY_ID or self.world['stock'].get(x,0)<1 for x in bonus_items)):
            raise GameError(409,'Bonus items are no longer available')
        if s['kind']=='buy':
            if self.world['stock'].get(item_id,0)<1: raise GameError(409,'Item no longer in stock')
            if amount>s['wallet']: raise GameError(409,'Customer cannot pay that much')
            self.world['stock'][item_id]-=1; self.world['gold']+=amount; s['wallet']-=amount
            self.world['earned_gold']=int(self.world.get('earned_gold',0))+amount
            action='sold'
        else:
            if self.world['gold']<amount: raise GameError(409,'Shop cannot afford that purchase')
            self.world['gold']-=amount; self.world['stock'][item_id]=self.world['stock'].get(item_id,0)+1
            self.world['spent_gold']=int(self.world.get('spent_gold',0))+amount
            action='purchased'
        for bonus in bonus_items:
            self.world['stock'][bonus]-=1
        self.world['deals']+=1
        self.world['reputation']=clamp(int(self.world.get('reputation',50))+2,0,100)
        s['pending_trade']=None
        s['offer']=amount  # The accepted price must be the visible final price.
        s['closed']=True; s['outcome']='deal'; self._memory(s, True)
        return {'action':action,'item_id':item_id,'item':item['name'],'price':amount,'shop_gold':self.world['gold'],'bonus_item_ids':bonus_items,'bonus_items':[ITEM_BY_ID[x]['name'] for x in bonus_items]}

    def trade_desk_action(self, sid: str, action: str, turn: int) -> dict:
        """One idempotent evidence reveal per request, preserving money and stock."""
        with self.lock:
            s=self.sessions.get(sid)
            if not s: raise GameError(404,'Encounter not found')
            if s['closed']: raise GameError(409,'Encounter has ended')
            if turn!=s['turn']+1: raise GameError(409,'Stale trade desk action')
            if action not in trade_desk.ACTIONS: raise GameError(422,'Unknown trade desk action')
            s['turn']+=1
            line, changed = trade_desk.perform(s['trade_desk'],action)
            if changed:
                s['history'].append({'speaker':'player','text':'[Trade desk: '+action+']'})
                s['history'].append({'speaker':'npc','text':line})
                s['history']=s['history'][-12:]
                if action=='appraise':
                    # Reward evidence gathering, without moving the reserve price.
                    s['trust']=clamp(s['trust']+2,0,100)
            response=self.public(s,line,'thinking' if action=='examine' else 'skeptical' if action=='check_origin' else 'amused','inspect',event='trade_inspection')
            response['ai_mode']='game_authoritative'
            return response

    def encounter_action(self, sid: str, action: str, turn: int) -> dict:
        """Authoritative, voiced action; no new Exodia request or gold transfer."""
        with self.lock:
            s=self.sessions.get(sid)
            if not s: raise GameError(404,'Encounter not found')
            if s['closed']: raise GameError(409,'Encounter has ended')
            if turn!=s['turn']+1: raise GameError(409,'Stale encounter action')
            if not s.get('living'): raise GameError(422,'This customer has no living encounter')
            if action not in {a['id'] for a in living.ACTIONS}:raise GameError(422,'Unknown encounter action')
            s['turn']+=1
            return self._apply_encounter_action(s,action)

    def _apply_encounter_action(self,s:dict,action:str)->dict:
        npc=NPC_BY_ID[s['npc_id']]
        state=s['living']
        before_actions=len(state['actions_taken'])
        line,mood,lead=living.perform(state,action,npc['name'],self.world['day'])
        s['history'].append({'speaker':'player','text':'[Encounter action: '+action+']'})
        s['history'].append({'speaker':'npc','text':line})
        if len(state['actions_taken'])>before_actions:
            s['trust']=clamp(s['trust']+(3 if action=='offer_help' else 1),0,100)
        if lead:
            entries=self.world.setdefault('leads',[])
            lead['id']=lead['id']+':day'+str(self.world['day'])
            if not any(x.get('id')==lead['id'] for x in entries):
                entries.append(lead)
                self.world['leads']=entries[-24:]
        self._save()
        response=self.public(s,line,mood,'consider',event='encounter_action')
        response['ai_mode']='game_authoritative'
        response['performance']={'source':'game_authoritative','provider':'encounter_director'}
        return response

    def leads(self)->list[dict]:
        with self.lock:
            return copy.deepcopy(self.world.get('leads',[]))

    def take_turn(self,sid,text,turn,bonus_items=None):
        text=text.strip()
        if not text or len(text)>500: raise GameError(422,'Message length must be 1-500 characters')
        with self.lock:
            s=self.sessions.get(sid)
            if not s: raise GameError(404,'Encounter not found')
            if s['closed']: raise GameError(409,'Encounter closed; invite next customer')
            if turn != s['turn']+1: raise GameError(409,'Stale or duplicate turn; refresh encounter state')
            kind,money=classify(text)
            proposed=interpret_offer(text,money,kind,bonus_items,s['item_id'],self.world['stock'])
            if proposed.get('error'):
                raise GameError(422,str(proposed['error']))
            s['turn']+=1
            old_pending=s.get('pending_trade')
            confirm_pending=bool(CONFIRM.fullmatch(text))
            cancel_pending=bool(CANCEL.fullmatch(text))
            prior_social = old_pending if isinstance(old_pending,dict) and old_pending.get('kind')=='social' else None
            social_confirm = bool(prior_social and is_confirmation(text,prior_social))
            incoming_physical = physical_goods(text)
            incoming_social = social_topic(text)
            # A previously locked social proposal cannot be silently expanded
            # by another NPC turn or a newly mentioned object.
            social_ack = bool(prior_social and ACCEPT_WORDS.search(text))
            social_changed = bool(social_ack and not social_confirm and prior_social.get('ready') and
                                  (incoming_physical or NEW_TERMS.search(text) or
                                   (money is not None and money != prior_social.get('cash'))))
            # Never let an 'I agree' sentence close an outstanding conditional
            # trade as the *ordinary* listed-price transaction.
            pending_reply=bool(old_pending and kind=='accept' and not confirm_pending)
            unsupported_side_offer=bool(proposed.get('unsupported',False) or
                                         (proposed.get('conditional',False) and not proposed.get('items')))
            # Severe personal abuse should be a decisive game event, not
            # colorful dialogue followed by yet another commercial offer.
            abuse = evaluate_abuse(text)
            if abuse:
                s['patience'] = clamp(s['patience'] - abuse, 0, 100)
                s['trust'] = clamp(s['trust'] - max(8, abuse//2), 0, 100)
                if abuse >= 50 or s['patience'] < 22:
                    kind = 'walk'
            s['history'].append({'speaker':'player','text':text[:500]})
            # V0.8 structured memory: player-stated topics are not validated
            # promises or NPC agreements. Keep the last three meaningful notes.
            moment = extract_player_moment(text, side_deal=unsupported_side_offer)
            if moment is not None:
                relationship = self.world['relationships'].setdefault(s['npc_id'], {})
                if not isinstance(relationship, dict):
                    relationship = {}
                    self.world['relationships'][s['npc_id']] = relationship
                relationship['moments'] = remember(relationship.get('moments'), moment)
                self._save()
            npc=NPC_BY_ID[s['npc_id']]
            s['patience']=clamp(s['patience']-self.rng.randint(2,5),0,100)
            if kind != 'chat': s['banter_streak'] = 0
            scene={'event':kind,'mood':'neutral','gesture':'idle','anchor':'','transaction':None,'npc_id':s['npc_id'],'turn':s['turn'],
                   'interrupted':s['interrupts']>0,'user_text':text,'offer_amount':money,
                   'memory_topic':moment['topic'] if moment else None}
            encounter_action=(living.recognize(text) if kind=='chat' and money is None and
                              s.get('living') and not old_pending else None)
            if encounter_action:
                line,mood,lead=living.perform(s['living'],encounter_action,npc['name'],self.world['day'])
                if lead:
                    lead['id'] += ':day'+str(self.world['day'])
                    entries=self.world.setdefault('leads',[])
                    if not any(x.get('id')==lead['id'] for x in entries):
                        entries.append(lead)
                        self.world['leads']=entries[-24:]
                    self._save()
                scene.update(event='encounter_action',mood=mood,gesture='consider',anchor=line)
            elif cancel_pending:
                s['pending_trade']=None
                scene.update(event='banter',mood='neutral',gesture='talk',
                             anchor='All right, we can try something else.')
            elif social_confirm and prior_social:
                # One explicit yes completes precisely the locked terms, with
                # no opportunity for the AI to add new promises or objects.
                cash=int(prior_social['cash'])
                if not prior_social.get('ready') or not self._social_cash_feasible(s,cash):
                    s['pending_trade']=None
                    scene.update(event='social_declined',mood='skeptical',gesture='consider',
                                 anchor='That offer is no longer possible. We can make a fresh cash offer.')
                else:
                    s['trust']=clamp(s['trust']+4,0,100)
                    scene['transaction']=self._commit(s,cash)
                    social_record=self.world['relationships'].setdefault(s['npc_id'],{})
                    social_record['last_social_roleplay']={'topic':prior_social['topic'],
                                                          'day':self.world['day'], 'status':'roleplay_agreed'}
                    self._save()
                    scene.update(event='deal',mood='delighted',gesture='celebrate',
                                 anchor=social_line(s,prior_social,'accepted'),
                                 social_topic=prior_social['topic'])
            elif social_changed and prior_social:
                prior_social['revision_count']=int(prior_social.get('revision_count',0))+1
                if prior_social['revision_count']>=2:
                    s['pending_trade']=None
                    anchor='We have gone in circles. Those extra terms are off the table; make a fresh offer.'
                else:
                    s['pending_trade']=prior_social
                    anchor=social_line(s,prior_social,'changed_terms')
                scene.update(event='social_terms_changed',mood='skeptical',gesture='consider',anchor=anchor)
            elif social_ack and prior_social and not prior_social.get('ready'):
                s['pending_trade']=None
                scene.update(event='social_declined',mood='skeptical',gesture='consider',
                             anchor='I appreciate the enthusiasm, but I never agreed to those terms.')
            elif s.get('last_condition_refused',False) and kind=='accept':
                scene.update(event='social_declined',mood='skeptical',gesture='consider',
                             anchor='My personal things are not included. Please make a separate cash offer.')
            elif confirm_pending:
                pending=s.get('pending_trade')
                if pending and pending.get('ready') and pending.get('kind')=='inventory':
                    try:
                        scene['transaction']=self._commit(s,int(pending['cash']),list(pending['items']))
                        scene.update(event='deal',mood='happy',gesture='celebrate',
                                     anchor=f"{scene['transaction']['price']} gold plus " +
                                            ', '.join(scene['transaction']['bonus_items']) + '. A deal!')
                    except GameError:
                        s['pending_trade']=None
                        scene.update(event='rejected',mood='skeptical',gesture='consider',
                                     anchor='That bundle is no longer available. Let us reconsider.')
                else:
                    scene.update(event='banter',mood='skeptical',gesture='consider',anchor='',
                                 proposal_status='not_confirmable')
            elif incoming_physical and re.search(r'(?i)\b(?:give\s+me|trade\s+me|sell\s+me|hand\s+over|want\s+your|for\s+your|borrow\s+your)\b',text) and kind!='walk':
                for name in incoming_physical:
                    if name not in s['refused_goods']:s['refused_goods'].append(name)
                s['pending_trade']=None
                s['last_condition_refused']=True
                scene.update(event='social_refused',mood='skeptical',gesture='consider',
                             anchor=social_line(s,{},'refused_goods'), side_deal=True)
            elif proposed['proposal'] and kind != 'walk':
                # V0.9.5: social invitations and untracked physical goods must
                # never be turned into an endless AI-authored counter-offer.
                cash=proposed['cash']
                items=proposed['items']
                if incoming_physical and not items:
                    for name in incoming_physical:
                        if name not in s['refused_goods']:
                            s['refused_goods'].append(name)
                    s['pending_trade']=None
                    s['last_condition_refused']=True
                    scene.update(event='social_refused',mood='annoyed' if len(s['refused_goods'])>2 else 'skeptical',
                                 gesture='consider',anchor=social_line(s,{},'refused_goods'),side_deal=True,
                                 refused_goods=list(s['refused_goods']))
                elif incoming_social and cash is not None and not items:
                    s['_shop_gold']=self.world['gold']
                    fixed=decide_social_offer(s,cash,incoming_social,self.world['stock'])
                    s.pop('_shop_gold',None)
                    fixed['created_turn']=s['turn']
                    s['pending_trade']=fixed
                    s['last_player_offer']=cash
                    s['last_offer_result']='social_ready' if fixed['ready'] else 'social_declined'
                    scene.update(event='social_offer',mood='amused' if fixed['ready'] else 'skeptical',
                                 gesture='consider',proposal=copy.deepcopy(fixed),
                                 anchor=social_line(s,fixed,'ready' if fixed['ready'] else 'declined'),
                                 social_topic=incoming_social,side_deal=True)
                else:
                    inventory_only=bool(items) and not proposed['unsupported'] and not incoming_social and not incoming_physical and (not proposed['conditional'] or bool(re.search(r'(?i)\bif\s+(?:you|we)\s+(?:add|include|throw\s+in|give|bundle)\b',text)))
                    ready=bool(inventory_only and cash is not None and self._bundle_feasible(s,cash,items))
                    s['pending_trade']={'cash':cash,'items':items,
                                        'kind':'inventory' if inventory_only else 'unsupported',
                                        'ready':ready,'status':'ready' if ready else 'discussion'}
                    s['last_player_offer']=cash
                    s['last_offer_result']='conditional_pending'
                    scene.update(event='proposal',mood='amused' if s['patience']>40 else 'skeptical',
                                 gesture='consider', proposal=copy.deepcopy(s['pending_trade']),
                                 anchor='',side_deal=True,
                                 proposal_status='ready' if ready else 'discussion')
            elif pending_reply:
                # A bare 'I accept' cannot retroactively remove a real bundle;
                # social consent is resolved in the explicit lock path above.
                scene.update(event='banter',mood='skeptical',gesture='talk',
                             anchor='', proposal_status='pending')
            elif unsupported_side_offer and kind != 'walk':
                scene.update(event='rejected',mood='skeptical',gesture='consider',side_deal=True,
                    anchor=(f"{self._side_offer_reaction(s, moment)} Are you offering {money} gold alone?"
                            if money is not None else
                            f"{self._side_offer_reaction(s, moment)} What is your cash offer?"))
                s['last_player_offer']=money
                s['last_offer_result']='side_payment_not_supported'
            elif kind=='walk':
                s['closed']=True; s['outcome']='walkout';s['trust']=clamp(s['trust']-7,0,100)
                self.world['reputation']=clamp(int(self.world.get('reputation',50))-1,0,100)
                self._memory(s,False)
                scene.update(event='walkout',mood='furious' if abuse else 'annoyed',gesture='exit',anchor="This conversation is over. I'm leaving." if abuse else "Very well. Keep your wares; I'll take my business elsewhere.")
            elif kind=='accept':
                s['pending_trade']=None
                amount=s['offer']
                if s['kind']=='sell' and amount>self.world['gold']:
                    scene.update(event='rejected',mood='skeptical',anchor="You have not the gold to buy it. Can you make a real offer?")
                else:
                    scene['transaction']=self._commit(s,amount)
                    scene.update(event='deal',mood='delighted',gesture='celebrate',anchor=f"Agreed. {amount} gold, and we have a deal!")
            elif kind=='quote':
                s['last_condition_refused']=False
                s['pending_trade']=None
                amount=money
                s['last_player_offer']=amount
                if (s['kind']=='sell' and amount>self.world['gold']):
                    scene.update(event='rejected',mood='suspicious',anchor='You cannot afford that offer. Shall we try a sensible number?')
                elif amount<1:
                    scene.update(event='rejected',mood='annoyed',anchor='That is not a serious offer.')
                elif (s['kind']=='buy' and amount<=s['reservation'] and amount<=s['wallet']) or (s['kind']=='sell' and amount>=s['reservation']):
                    # A favorable offer can still be rebuffed for a round; agency is seeded.
                    relative=(s['reservation']-amount)/max(1,s['reservation']) if s['kind']=='buy' else (amount-s['reservation'])/max(1,s['reservation'])
                    chance=clamp(.38+relative*1.9+s['trust']/500+(100-s['patience'])/800,0.15,.98)
                    if s['turn']>3: chance=clamp(chance+.20,0.15,1)
                    if self.rng.random()<chance:
                        scene['transaction']=self._commit(s,amount)
                        scene.update(event='deal',mood='happy',gesture='celebrate',anchor=f"{amount} gold. Done. We have ourselves a bargain!")
                    else:
                        s['offer']=self._concede(s)
                        scene.update(event='counter',mood='skeptical',gesture='consider',anchor=self._offer_line(s))
                else:
                    # Do not promise approval above NPC's reservation. Bluff or counter within fixed bounds.
                    if s['kind']=='buy':
                        s['offer']=self._concede(s)
                    else:
                        s['offer']=self._concede(s)
                    s['patience']=clamp(s['patience']-self.rng.randint(3,8),0,100)
                    scene.update(event='counter',mood='annoyed' if s['patience']<45 else 'suspicious',gesture='consider',anchor=self._offer_line(s))
            else:
                s['banter_streak'] += 1
                if re.search(r"(?i)\b(?:you (?:just |already |previously )?(?:said|agreed|accepted|promised|offered)|didn't you (?:agree|accept|say))\b",text):
                    last=s.get('last_player_offer')
                    if last is not None and s.get('last_offer_result')=='counter':
                        reminder=(f"I heard your {last}-gold proposal, but I did not accept it. "
                                  f"My current offer remains {s['offer']} gold.")
                    else:
                        reminder=(f"No new price was agreed. My current offer is {s['offer']} gold.")
                    scene.update(event='clarification',mood='skeptical',gesture='consider',anchor=reminder)
                off_topic=bool(re.search(r'\b(?:iphone|smartphone|gta\s*6|internet|youtube|bitcoin|wifi|smartwatch|playstation|computer)\b', text, re.I))
                if off_topic and npc.get('era') != 'modern': s['offtopic']+=1
                if s['offtopic']>=3: s['patience']=clamp(s['patience']-7,0,100)
                s['trust']=clamp(s['trust']+(1 if any(w in text.lower() for w in ('please','thank','friend','sorry')) else -1 if any(w in text.lower() for w in ('idiot','fool','stupid')) else 0),0,100)
                if scene['event'] != 'clarification':
                    scene.update(event='banter',mood='amused' if s['patience']>45 else 'skeptical',gesture='talk',anchor='')
            if scene['event']=='banter' and s.get('living') and not s.get('pending_trade'):
                initiative=living.next_initiative(s['living'],npc['name'])
                if initiative:
                    scene.update(event='encounter_initiative',mood='thinking',gesture='consider',anchor=initiative)
            if s['patience']<=0 and not s['closed']:
                s['closed']=True;s['outcome']='walkout';self._memory(s,False)
                scene.update(event='walkout',mood='furious',gesture='exit',anchor="Enough. I am leaving. We are finished here.",transaction=None)
            if scene['event'] in ('counter','rejected','deal','walkout'):
                s['last_offer_result']=scene['event']
            s['interrupts']=0
            snapshot=copy.deepcopy(s)
            snapshot['relationship']=copy.deepcopy(self.world['relationships'].get(s['npc_id'], {}))
            snapshot['history']=snapshot['history'][-12:]
            # Final text is generated separately; all mutations above are authoritative.
            return scene,snapshot

    def _side_offer_reaction(self, s: dict, moment: dict | None) -> str:
        """Personality-scaled, varied side-payment boundary; not an AI lecture."""
        topic = moment['topic'] if moment else 'that extra'
        idx = (s['turn'] + sum(ord(ch) for ch in topic)) % 3
        if s['npc_id'] == 'liu_xue':
            choices = (f"哈哈，{topic}？有趣的提议！", f"哎呀，连{topic}都拿来谈呀！",
                       f"{topic}？你真会出奇招！")
        elif NPC_BY_ID[s['npc_id']].get('era') == 'modern':
            choices = (f"Okay, {topic} is a wild bonus idea!", f"I like the creativity with {topic}.",
                       f"Ha, {topic}? You're full of surprises.")
        else:
            choices = (f"An intriguing thought, this {topic}.", f"You offer curious extras: {topic}!",
                       f"Even {topic} enters our bargaining tale!")
        return choices[idx]

    def _concede(self,s):
        gap=abs(s['reservation']-s['offer'])
        inc=max(1,round(gap*self.rng.uniform(.16,.39))) if gap else 0
        if s['kind']=='buy': return min(s['reservation'],s['offer']+inc)
        return max(s['reservation'],s['offer']-inc)

    def _offer_line(self,s):
        if NPC_BY_ID[s['npc_id']].get('era') == 'modern':
            return (f"I could do {s['offer']} gold for the {ITEM_BY_ID[s['item_id']]['name']}. Sound fair?" if s['kind']=='buy' else f"How about {s['offer']} gold for the {ITEM_BY_ID[s['item_id']]['name']}?")
        if s['kind']=='buy': return f"I can offer {s['offer']} gold for the {ITEM_BY_ID[s['item_id']]['name']}. What do you say?"
        return f"I'll let the {ITEM_BY_ID[s['item_id']]['name']} go for {s['offer']} gold. Your answer?"

    def apply_npc_departure(self, sid: str, expected_turn: int, scene: dict) -> bool:
        """Let a live NPC leave when it clearly says so; economy still owns state.

        Invoked only for a validated current-turn AI answer, under dispatcher lock.
        Never undoes a completed deal or applies a price quoted by the model.
        """
        with self.lock:
            s = self.sessions.get(sid)
            if not s or s['closed'] or s['turn'] != expected_turn:
                return False
            s['closed'] = True
            s['outcome'] = 'walkout'
            s['patience'] = clamp(s['patience']-18,0,100)
            s['trust'] = clamp(s['trust']-8,0,100)
            self._memory(s,False)
            scene.update(event='walkout',mood='annoyed',gesture='exit',anchor='I have heard enough. Goodbye.',transaction=None)
            return True

    def finalize(self,sid,line,scene,used_ai=False):
        with self.lock:
            s=self.sessions.get(sid)
            if not s: raise GameError(404,'Encounter not found')
            s['history'].append({'speaker':'npc','text':line})
            out=self.public(s,line,scene['mood'],scene['gesture'],event=scene['event'],transaction=scene['transaction'])
            out['ai_mode']='live' if used_ai else 'offline'
            return out

    def debug(self,sid):
        with self.lock:
            s=self.sessions.get(sid)
            if not s: raise GameError(404,'Encounter not found')
            return copy.deepcopy(s)

    def restock(self,item_id:str,quantity:int=1)->dict:
        """Purchase real supplies; atomic operation and backward-compatible save."""
        with self.lock:
            if item_id not in ITEM_BY_ID: raise GameError(422,'Unknown supply item')
            if not isinstance(quantity,int) or isinstance(quantity,bool) or quantity not in (1,2,3):
                raise GameError(422,'Restock quantity must be 1, 2, or 3')
            previous=int(self.world['stock'].get(item_id,0))
            if previous+quantity>MAX_STOCK: raise GameError(409,'Shelf capacity is 12 units')
            cost=supply_cost(item_id,self.world['day'])*quantity
            if cost>self.world['gold']: raise GameError(409,'Insufficient shop gold for these supplies')
            self.world['gold']-=cost
            self.world['stock'][item_id]=previous+quantity
            self.world['restock_spend']=int(self.world.get('restock_spend',0))+cost
            self._save()
            return {'item_id':item_id,'name':ITEM_BY_ID[item_id]['name'],
                    'quantity':quantity,'gold_spent':cost,'gold_remaining':self.world['gold'],
                    'stock':self.world['stock'][item_id], 'ledger':shop_ledger(self.world)}

    def ledger(self)->dict:
        with self.lock:return shop_ledger(self.world)

    def catalog(self):
        with self.lock:
            return {'items':[dict(i,stock=self.world['stock'].get(i['id'],0),
                                  restock_cost=supply_cost(i['id'],self.world['day'])) for i in ITEMS],
                    'player':{'gold':self.world['gold'],'day':self.world['day'],'deals':self.world['deals']},
                    'ledger':shop_ledger(self.world),
                    'customers':[{'id':p['id'],'name':p['name'],'title':p['title'],'style':p['style'],'era':p.get('era','fantasy')} for p in NPCS]}
