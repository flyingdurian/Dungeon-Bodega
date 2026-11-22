"""Bounded social negotiation rulings, separate from transfers of real goods.

No language-model text changes these terms. A social invitation is roleplay
consent, not an enforceable promise, and never creates an inventory object.
"""
from __future__ import annotations

import re

SOCIAL_TOPICS = (
    ('date', re.compile(r'(?i)\b(?:date|go\s+out\s+with|go\s+on\s+a\s+date|romantic\s+evening)\b')),
    ('movie', re.compile(r'(?i)\b(?:movies?|cinema|film\s+night)\b')),
    ('dinner', re.compile(r'(?i)\b(?:dinner|lunch|meal\s+out|take\s+you\s+out)\b')),
    ('music', re.compile(r'(?i)\b(?:music|playlist|choose\s+the\s+songs?)\b')),
)
UNTRACKED_GOODS = re.compile(
    r'(?i)\b(?:headphones?|hoodie|nintendo(?:\s+switch)?|iphone|(?:smart)?phone|'
    r'xbox|playstation|gta\s*6|laptop|console|jacket|sneakers?|watch|gift\s+card|car|bike)\b'
)
ACCEPT_WORDS = re.compile(
    r"(?i)\b(?:yes|yep|yeah|okay|ok|sure|agreed|accept|sounds\s+good|deal|"
    r"confirm\s+trade|you\s+got\s+it|fine|i\s+am\s+in|count\s+me\s+in)\b"
)
NEW_TERMS = re.compile(r'(?i)\b(?:but|instead|except|unless|only\s+if|if\s+you|throw\s+in|plus|additional|extra|on\s+top\s+of)\b')
NEGATION = re.compile(r"(?i)\b(?:no|nope|not|never|won't|refuse|can't|cannot|don't)\b")


def social_topic(text: str) -> str | None:
    for topic, pattern in SOCIAL_TOPICS:
        if pattern.search(text):
            return topic
    return None


def physical_goods(text: str) -> list[str]:
    return list(dict.fromkeys(match.group(0).lower() for match in UNTRACKED_GOODS.finditer(text)))[:4]


def is_confirmation(text: str, pending: dict) -> bool:
    """Accept locked terms once, without accepting a new conditional upsell."""
    if not pending or pending.get('kind') != 'social' or not pending.get('ready'):
        return False
    if not ACCEPT_WORDS.search(text) or NEGATION.search(text) or NEW_TERMS.search(text):
        return False
    if physical_goods(text):
        return False
    cash_numbers = [int(x) for x in re.findall(r'(?i)\b(\d{1,5})\s*(?:gold|g|coins?)\b', text)]
    spelled = {'ten':10,'twenty':20,'thirty':30,'forty':40,'fifty':50,
               'sixty':60,'seventy':70,'eighty':80,'ninety':90,
               'hundred':100,'one hundred':100,'two hundred':200}
    for match in re.finditer(r'(?i)\b([a-z]+(?:\s+hundred)?)\s+(?:gold|coins?)\b',text):
        word=match.group(1).lower()
        if word in spelled:cash_numbers.append(spelled[word])
    if cash_numbers and any(amount != int(pending['cash']) for amount in cash_numbers):
        return False
    mentioned = [topic for topic, rx in SOCIAL_TOPICS if rx.search(text)]
    # Music is a playful activity, not an additional commercial condition.
    if any(topic not in (pending['topic'], 'music') for topic in mentioned):
        return False
    return True


def decide_social_offer(state: dict, cash: int | None, topic: str, stock: dict) -> dict:
    """Personality, consent and hard economic bounds; no AI-authored contracts."""
    trust = int(state['trust'])
    patience = int(state['patience'])
    npc_id = state['npc_id']
    thresholds = {'maya': 32, 'zoe': 39, 'fenwick': 44, 'pippa': 44,
                  'liu_xue': 64, 'garrick': 95, 'vesper': 82}
    boundary = thresholds.get(npc_id, 63)
    willing = trust >= boundary and patience >= 22
    # Pure social goodwill can nudge the reservation slightly, but cannot
    # give the customer money they do not possess or create shop stock.
    goodwill = min(6, max(0, (trust - 30) // 11))
    if cash is None or cash < 1:
        affordable = False
    elif state['kind'] == 'buy':
        affordable = (cash <= int(state['wallet']) and cash <= int(state['reservation']) + goodwill
                      and int(stock.get(state['item_id'], 0)) >= 1)
    else:
        affordable = cash <= int(state.get('_shop_gold', 0)) and cash + goodwill >= int(state['reservation'])
    ready = willing and affordable
    return {'kind': 'social', 'cash': cash, 'items': [], 'topic': topic,
            'ready': ready, 'status': 'ready' if ready else 'declined',
            'willing': willing, 'affordable': affordable, 'revision_count': 0}


def social_line(state: dict, pending: dict, outcome: str) -> str:
    """Use short personality-aware, game-truthful remarks on locked decisions."""
    topic = pending.get('topic', 'date')
    amount = pending.get('cash')
    npc_id = state['npc_id']
    if outcome == 'refused_goods':
        if npc_id == 'maya':
            return "My personal stuff isn't part of this sale—not even for extra gold. Try a cash offer, though."
        if npc_id == 'liu_xue':
            return "我的私人物品不卖哦。钱再多也不行，我们还是谈店里的东西吧。"
        return "Those are my personal belongings, not merchandise. More gold won't change that."
    if outcome == 'changed_terms':
        return ("Wait, those weren't the terms we discussed. I won't keep adding extras. "
                "We can stick with the original offer or start a fresh cash bargain.")
    if outcome == 'accepted':
        if npc_id == 'maya':
            return f"Okay, {amount} gold is settled! And I get to choose the music when we go out. Deal done."
        if npc_id == 'liu_xue':
            return f"好啦，{amount}金币成交！约会嘛……那就当我们说定了，哈哈。"
        return f"Then {amount} gold settles our trade. The invitation was a pleasant surprise."
    if outcome == 'ready':
        if npc_id == 'maya':
            return (f"A {topic}? You're bold! I might even pick the playlist. "
                    f"I can do {amount} gold on those terms—say yes if we're settled.")
        if npc_id == 'liu_xue':
            return (f"{topic}？你可真会逗人笑呀！{amount}金币，我可以考虑这份心意。"
                    "你说好，我们就成交。")
        return (f"An invitation to a {topic}? That's unexpected, but rather sweet. "
                f"{amount} gold could work; say yes and we'll settle it.")
    if not pending.get('willing', False):
        if npc_id == 'maya':
            return "That's a sweet pitch, but no date for me. You can still impress me with an actual cash offer."
        if npc_id == 'liu_xue':
            return "哎呀，你太直接啦！约会就免了，我们还是好好做生意吧。"
        return "I appreciate the invitation, but I'll decline. We can still bargain normally."
    return (f"The invitation is flattering, but {amount} gold doesn't quite work for me. "
            f"My offer remains {state['offer']} gold.")
