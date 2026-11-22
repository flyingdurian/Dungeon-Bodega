"""V1.2 deterministic object examination and appraisal.

The model cannot mutate these facts, create stock, authenticate an unknown object,
or commit a trade. Inspection exposes authored observations; appraisals are explicitly
estimates and do not change the shop's sale price or reservation limits.
"""
from __future__ import annotations

import hashlib
import re

CONDITIONS = ('excellent', 'worn', 'restored')
ITEM_DETAILS = {
    'mana_potion': ('Tiny bubbles cling to the inner glass; the wax seal is intact.', 'The apothecary label shows a guild batch number.'),
    'healing_draught': ('Sediment settles in a fine crimson ring beneath the stopper.', 'A handwritten brewer mark appears below the label.'),
    'moonblade': ('Fine tool marks trace the blade near its hilt.', 'A smith-mark is etched beneath the guard.'),
    'sun_charm': ('The gold-toned finish is smoother along the edges where fingers have rubbed it.', 'The reverse bears a stamped maker symbol.'),
    'ember_scroll': ('The paper fibers show a deliberate repair near the lower edge.', 'The binding ribbon carries a workshop seal.'),
    'wyvern_scale': ('A hairline ridge runs along the underside of the scale.', 'A collector ink mark is visible on the mounting.'),
    'silver_buckle': ('The pin has a small scrape where it meets the frame.', 'The clasp carries a faint caravan maker stamp.'),
    'storm_vial': ('Blue arcs flicker in the liquid, never quite touching the lid.', 'An old shipment code is etched into the bottle base.'),
    'sage_salve': ('The salve remains evenly blended beneath the glass.', 'The maker date is pressed into the lid rim.'),
    'rune_stone': ('The carved groove catches light at an odd angle.', 'A tiny scribe symbol is cut along the base.'),
}

ACTIONS = ('examine', 'check_origin', 'appraise')


def make(item: dict, day: int, salt: str) -> dict:
    digest = hashlib.sha256(f'{day}/{item["id"]}/{salt}'.encode('utf-8')).digest()
    condition = CONDITIONS[digest[0] % len(CONDITIONS)]
    provenance = ('incomplete', 'plausible', 'documented')[digest[1] % 3]
    return {'item_id':item['id'], 'item_name':item['name'], 'base_price':int(item['price']),
            'condition': condition, 'provenance': provenance,
            'observations': list(ITEM_DETAILS.get(item['id'], ('Visible wear is consistent with handling.', 'An old maker mark is present.'))),
            'actions_taken': [], 'notes': [], 'rotation_deg': 0, 'estimated_range':None}


def public(desk: dict | None) -> dict | None:
    if desk is None: return None
    done = set(desk['actions_taken'])
    return {'item_id':desk['item_id'], 'item_name':desk['item_name'],
            'condition':desk['condition'] if 'examine' in done else 'Unexamined',
            'provenance':desk['provenance'] if 'check_origin' in done else 'Unverified',
            'notes':list(desk['notes']),
            'estimated_range':list(desk['estimated_range']) if desk['estimated_range'] else None,
            'actions': [{'id':'examine','label':'Examine', 'done':'examine' in done},
                        {'id':'check_origin','label':'Check maker mark','done':'check_origin' in done},
                        {'id':'appraise','label':'Appraise value','done':'appraise' in done}],
            'kind':'illustrated_item_inspection'}


def perform(desk: dict, action: str) -> tuple[str, bool]:
    if action not in ACTIONS: raise ValueError('Unknown trade desk action')
    if action in desk['actions_taken']:
        return 'The inspection notes are already recorded. You can review them on the trade desk.', False
    if action == 'appraise' and 'examine' not in desk['actions_taken']:
        return 'Examine the object first; there is not enough evidence for an appraisal.', False
    desk['actions_taken'].append(action)
    if action == 'examine':
        detail = desk['observations'][0]
        note = f'Condition: {desk["condition"]}. {detail}'
        desk['notes'].append(note)
        return note, True
    if action == 'check_origin':
        detail = desk['observations'][1]
        note = f'Maker record: {desk["provenance"]}. {detail}'
        desk['notes'].append(note)
        return note, True
    # The range is advice, not a binding quote or invisible adjustment to NPC cash.
    factors = {'excellent': (0.91, 1.19), 'worn': (0.64, 0.91), 'restored': (0.75, 1.03)}
    lo,hi = factors[desk['condition']]
    if desk['provenance']=='documented': lo+=0.05;hi+=0.09
    elif desk['provenance']=='incomplete': lo-=0.05;hi-=0.05
    if 'check_origin' not in desk['actions_taken']:
        lo-=0.05;hi+=0.07
    base=desk['base_price']
    low=max(1,round(base*lo));high=max(low,round(base*hi))
    desk['estimated_range']=[low,high]
    note=f'Estimated value: {low}–{high} gold (nonbinding; based on visible evidence).'
    desk['notes'].append(note)
    return note, True


def recognize_spoken_action(text: str) -> str | None:
    """High-specificity spoken equivalents; never hijack ordinary price offers."""
    t=text.strip().lower()
    if re.search(r'^(?:please\s+)?(?:appraise|estimate (?:the )?value|value (?:the|this) item)(?:\s+(?:this|that|the)\s+(?:item|object))?[.!?]?$', t):
        return 'appraise'
    if re.search(r'^(?:please\s+)?(?:examine (?:the )?(?:surface|condition)|check (?:the )?condition|inspect (?:the )?condition)[.!?]?$', t):
        return 'examine'
    if re.search(r'^(?:please\s+)?(?:check (?:the )?(?:maker.?s? mark|maker stamp|origin stamp)|verify (?:the )?(?:maker|mark))[.!?]?$', t):
        return 'check_origin'
    return None
