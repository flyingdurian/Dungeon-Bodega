"""V1.1 Living Encounters: compact deterministic encounter beats and discovery.

AI dialogue may portray these facts, but never invents items, completes a trade,
or awards leads. An action can be taken through a native UI button or the same
natural-language phrase spoken through the microphone.
"""
from __future__ import annotations
import re

# Three replayable situation variants for each of the featured cast.
# 'insight' is a narrated *fact* in that scenario, never inventory creation.
SITUATIONS = {
    'maya': [
        ('A suspicious collector', 'Maya needs to know whether the item is genuinely collectible.',
         'She spotted a mismatched serial mark in another shop.',
         'The maker stamp is slightly different from the item in the catalogue.',
         'A shuttered gaming arcade might still have its original appraisal records.'),
        ('A limited-run mystery', 'Maya has a buyer waiting and needs to judge the item quickly.',
         'She is afraid of disappointing the buyer.',
         'The packaging has an older market label underneath the current one.',
         'A local collector once documented a complete set of these labels.'),
        ('The midnight trade', 'Maya wants to make the deal before a weekend convention.',
         'She does not know whether the convention buyer is reliable.',
         'A handwritten provenance number appears on the back.',
         'A convention contact could independently verify the origin.'),
    ],
    'liu_xue': [
        ('The absent seal', 'Liu Xue has doubts about the history of the item.',
         '我在商队的旧账簿上见过同样的匠人印记。',
         '包装褶皱下面，还留着一枚小小的印章痕迹。',
         '丝路上有户商家，也许还留着这件货物的来历记录。'),
        ('A merchant’s promise', 'Liu Xue is weighing trust as heavily as price.',
         '有人提醒我，一位商人曾仿造真正的匠人印记。',
         '磨损的题字中，能看见一行更古老的笔迹。',
         '我认识一位书法家，也许能从题字认出匠人的身份。'),
        ('The caravan record', 'Liu Xue wants a fair exchange before her caravan leaves.',
         '我担心这件东西的旧主人从未得到公正的估价。',
         '装箱单显示，这件货物至少转过两次手。',
         '商队的管事也许还记得它的上一位主人。'),
    ],
    'mara_copperwell': [
        ('The slipping escapement','Mara suspects a hairline mechanical defect.',
         'She needs the mechanism to work, not merely sparkle.',
         'A small polished gear has a tooth that was repaired.',
         'An old workshop invoice may explain the replacement part.'),
        ('The silent clock','Mara is hunting for a lost maker stamp.',
         'She recognizes a style used by a vanished foundry.',
         'An almost erased workshop glyph lies beneath the hinge.',
         'A clockmaker in the river quarter once copied these glyphs.'),
        ('The trade of tools','Mara needs dependable materials before a repair contract.',
         'Her apprentice spent the last copper on broken tools.',
         'One fastener uses a nonstandard alloy.',
         'A scrapyard foreman may have a matching spare.'),
    ],
    'tarek_ashwood': [
        ('The crossed-out trail','Tarek is questioning the route by which an item arrived.',
         'The map he carries contradicts a merchant seal.',
         'Fine dust in the binding matches a remote quarry.',
         'A caravan lookout could identify the missing route.'),
        ('The border toll','Tarek wants evidence that old trade duties were paid.',
         'His company was once cheated at this crossing.',
         'An old toll notch remains on the clasp.',
         'The border ledger has a disputed name worth searching.'),
        ('The lost waystone','Tarek recognizes a symbol from a collapsed mountain road.',
         'He needs help locating an old survey archive.',
         'A hand-scored compass line appears near the base.',
         'A frontier cartographer may know the road it once marked.'),
    ],
    'yuna_seo': [
        ('The cloudy gemstone','Yuna wants to verify a cloudy inclusion.',
         'She worries the seller polished away evidence of a repair.',
         'A faint line crosses the surface under angled light.',
         'A laboratory register could confirm how the stone was treated.'),
        ('The absent certificate','Yuna has found paperwork that does not match a piece.',
         "A collector's certificate lists an older serial number.",
         'The mounting shows a different maker punch.',
         'The originating auction house may have photographs.'),
        ('The heirloom setting','Yuna is evaluating whether a family item was reset.',
         'She does not want to mislead the present owner.',
         'Different metal tones are visible at the clasp.',
         'A conservator might identify the original setting.'),
    ],
    'felix_rowe': [
        ('The rival bidder','Felix hints that a private buyer is interested.',
         'He does not have a signed bid in hand.',
         'A lot tag bears a crossed-out estimate.',
         'A public auction record could verify the competing claim.'),
        ('The lost catalogue','Felix thinks a rare item was miscatalogued.',
         'He wants to be first to report the discovery.',
         'A handwritten inventory number survives under the label.',
         'An archived sale book may contain its original listing.'),
        ('A private preview','Felix is seeking a special buyer invitation.',
         'He knows an attendee who prefers anonymous purchases.',
         'The back of the item has a discreet gallery seal.',
         'A gallery curator might identify the last exhibition.'),
    ],
    'garrick': [
        ('The battered relic', 'Garrick needs to know whether the item will survive field use.',
         'He has seen merchants disguise damaged fittings.',
         'One edge shows old repair marks beneath the polish.',
         'A retired armorer in the northern pass may know who repaired it.'),
        ('Urgent supplies', 'Garrick is preparing for a difficult expedition.',
         'His companions are short of dependable equipment.',
         "The item's material is sound, but its fastening needs attention.",
         'A supply caravan is heading toward the ridge before nightfall.'),
        ('The disputed insignia', 'Garrick recognizes a marking that troubles him.',
         'The insignia resembles that of an old rival company.',
         'The engraved mark has been partly filed away.',
         'An old veteran may identify the original unit.'),
    ],
}
ACTIONS = (
    {'id':'inspect','label':'Inspect object','icon':'⌕'},
    {'id':'ask_origin','label':'Ask about origin','icon':'✧'},
    {'id':'offer_help','label':'Offer assistance','icon':'♡'},
)


def build(npc_id: str, day: int, item_name: str) -> dict | None:
    cases = SITUATIONS.get(npc_id)
    if not cases:
        return None
    # Stable per character/day; no extra LLM randomness or private state.
    case = cases[(max(1,day)-1) % len(cases)]
    return {'id':f'{npc_id}:{(max(1,day)-1)%len(cases)}', 'title':case[0],
            'motive':case[1], 'private_concern':case[2], 'inspection':case[3],
            'lead':case[4], 'item_name':item_name, 'npc_id':npc_id, 'beat':'arrival',
            'actions_taken':[], 'insights':[], 'lead_awarded':False, 'turns':0}


def public(state: dict | None) -> dict | None:
    if not state:
        return None
    if state['beat']=='resolved':
        actions=[]
    else:
        actions=[dict(a, disabled=a['id'] in state['actions_taken']) for a in ACTIONS]
    return {'id':state['id'], 'title':state['title'], 'motive':state['motive'],
            'beat':state['beat'], 'insights':list(state['insights'][-3:]),
            'actions':actions, 'lead_awarded':bool(state['lead_awarded'])}


def recognize(text: str) -> str | None:
    value=text.lower().strip()
    # Strict verb phrases. Casual mentions of 'look', 'origin' or 'help'
    # must not steal a normal line of conversation or a priced offer.
    if re.search(r'\b(?:inspect|examine|appraise|check the markings|take a closer look|look closely at)\b',value):
        return 'inspect'
    if re.search(r'\b(?:where (?:did|does) (?:this|that|you get|you find)|tell me (?:where|the history)|ask about (?:the )?origin|who owned|provenance|how did you get)\b',value):
        return 'ask_origin'
    if re.search(r'\b(?:can i help you|let me help|i can assist|offer assistance|help you find|follow up on that lead)\b',value):
        return 'offer_help'
    return None


def perform(state: dict, action: str, npc_name: str, day: int) -> tuple[str, str, dict | None]:
    """Mutate one session state, returning (line, mood, earned lead or None)."""
    if action not in {a['id'] for a in ACTIONS}:
        raise ValueError('Unknown living-encounter action')
    if state['beat']=='resolved':
        return 'We have already settled that question. What else is on your mind?', 'neutral', None
    if action in state['actions_taken']:
        return 'We already looked into that. There may be another angle worth exploring.', 'neutral', None
    if action=='offer_help' and not any(a in state['actions_taken'] for a in ('inspect','ask_origin')):
        return f'{npc_name} appreciates the offer, but asks you to look into the item first.', 'amused', None
    state['actions_taken'].append(action)
    state['beat']='discovery'
    if action=='inspect':
        detail=state['inspection']
        state['insights'].append(detail)
        line=('你仔细看，这里有个细节：'+detail if state['npc_id']=='liu_xue' else 'Look closely at this detail: '+detail)
        return line, 'thinking', None
    if action=='ask_origin':
        detail=state['private_concern']
        state['insights'].append(detail)
        line=('说来话长……'+detail if state['npc_id']=='liu_xue' else 'All right, here is what concerns me: '+detail)
        return line, 'skeptical', None
    # Offer-help action is a lasting, bounded world change, separate from trade.
    lead={'id':state['id'], 'day':int(day), 'npc':npc_name,
          'title':state['title'], 'description':state['lead']}
    state['insights'].append(state['lead'])
    state['lead_awarded']=True
    state['beat']='resolved'
    line=('多谢你！我想到了一个线索：'+state['lead'] if state['npc_id']=='liu_xue' else 'Thank you. Here is a lead worth following: '+state['lead'])
    return line, 'happy', lead


def next_initiative(state: dict, npc_name: str) -> str | None:
    """One natural customer-initiated development per encounter."""
    if state['beat']!='arrival':
        return None
    state['turns']+=1
    if state['turns']<4:
        return None
    state['beat']='concern'
    return ('等等，还有件事……'+state['private_concern'] if state['npc_id']=='liu_xue' else 'Before we settle this, there is something else: '+state['private_concern'])
