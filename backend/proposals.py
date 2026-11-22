"""Authoritative interpretation of *conditional* and inventory-backed offers.

Do not equate the presence of a cash number with unconditional consent.
No external speech/model output is allowed to create an item or promise.
"""
from __future__ import annotations
import re
from .content import ITEMS

# A broad grammatical guard catches conditions before price parsing. It is NOT
# permission to enforce social promises; those are conversation only.
IF_CLAUSE = re.compile(r"(?i)\b(?:if\s+(?:you|we|i|she|he|they)|only\s+if|provided\s+(?:that|you)|as\s+long\s+as|on\s+(?:the\s+)?condition\s+that|in\s+exchange\s+for|assuming\s+(?:you|we)|but\s+only\s+if)\b")
SIDE_GOODS = re.compile(r"(?i)\b(?:iphone|nintendo(?:\s+switch)?|playstation|xbox|gta\s*6|laptop|console|movie\s+tickets?|smartphone|headphones?|gift\s+card|dinner|date|kiss|relationship|go\s+out\s+with)\b")
EXTRA_ITEM = re.compile(r"(?i)\b(?:plus|and\s+(?:a|an|the)?|throw\s+in|include|along\s+with|on\s+top\s+of|bundle(?:\s+with)?)\b")
BONUS_CONTEXT = re.compile(r"(?i)\b(?:plus|throw\s+in|include|along\s+with|on\s+top\s+of|bundle\s+with)\b")
FOR_UNTRACKED = re.compile(r"(?i)\b(?:for|in\s+return\s+for)\s+(?:a|an|the|your|this|that)?\s*(?:iphone|nintendo(?:\s+switch)?|playstation|xbox|gta\s*6|console|laptop|headphones?|date|dinner|kiss|movie)\b")
CONFIRM = re.compile(r"(?i)^\s*(?:confirm\s+(?:the\s+)?(?:bundle|trade|offer)|finali[sz]e\s+(?:the\s+)?(?:bundle|trade)|complete\s+(?:the\s+)?bundle)\s*[.!]?\s*$")
CANCEL = re.compile(r"(?i)^\s*(?:cancel\s+(?:the\s+)?(?:bundle|offer)|forget\s+(?:the\s+)?(?:extras?|bundle)|drop\s+(?:the\s+)?condition|never\s*mind\s+(?:about\s+)?(?:the\s+)?bundle)\s*[.!]?\s*$")

# Do not add arbitrary items by hallucination. Only these catalogued item names
# and explicit spoken shorthand aliases are recognized, and only when stock > 0.
ALIASES = {
    'mana_potion': ['mana potion', 'mana pot', 'greater mana potion'],
    'healing_draught': ['healing draught', 'crimson healing draught'],
    'moonblade': ['moonsteel dagger', 'moonblade'],
    'sun_charm': ['charm of dawn', 'sun charm'],
    'ember_scroll': ['scroll of emberlight', 'ember scroll'],
    'wyvern_scale': ['wyvern scale'],
    'silver_buckle': ['silver road buckle'],
    'storm_vial': ['bottled storm', 'storm vial'],
    'sage_salve': ['sageleaf salve', 'sage salve'],
    'rune_stone': ['whispering runestone', 'rune stone'],
}
CATALOG_IDS = frozenset(i['id'] for i in ITEMS)


def mentioned_bonus_items(text: str, current_item: str) -> list[str]:
    # Spoken "70 gold and a mana potion" is a bundle, even without "plus".
    if not BONUS_CONTEXT.search(text) and not (
        re.search(r'(?i)\b\d+\s*(?:gold|coins?|g)\b', text)
        and re.search(r'(?i)\band\s+(?:a|an|the)?\s+',text)
    ):
        return []
    lowered = text.casefold()
    found = []
    for item_id, aliases in ALIASES.items():
        if item_id == current_item:
            continue
        if any(re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', lowered) for alias in aliases):
            found.append(item_id)
    return found[:2]


def interpret_offer(text: str, money: int | None, kind: str, bonus_items: list[str] | None,
                    current_item: str, stock: dict) -> dict:
    """Return nonbinding proposal metadata; only explicit, owned stock can be traded."""
    selected = list(dict.fromkeys((bonus_items or []) + mentioned_bonus_items(text, current_item)))
    if len(selected) > 2 or any(x not in CATALOG_IDS or x == current_item for x in selected):
        return {'error': 'Choose up to two valid bonus items other than the negotiated item.'}
    if any(int(stock.get(x, 0)) < 1 for x in selected):
        return {'error': 'One of the bonus items is not in your shelves.'}
    has_condition = bool(IF_CLAUSE.search(text))
    has_unsupported = bool(SIDE_GOODS.search(text)) and (
        (has_condition and (money is not None or kind == 'accept'))
        or (money is not None and bool(EXTRA_ITEM.search(text) or FOR_UNTRACKED.search(text)))
    )
    # Do not quietly sell the current target if the shopkeeper names a
    # *different* catalog item as the primary thing being purchased.
    another_item = False
    if money is not None:
        lowered=text.casefold()
        for item_id, aliases in ALIASES.items():
            if item_id == current_item:
                continue
            if any(re.search(r'(?i)\bfor\s+(?:a|an|the|your|this|that)?\s*'+re.escape(alias)+r'\b',lowered) for alias in aliases):
                another_item=True
                break
    has_unsupported = has_unsupported or another_item
    has_goods = bool(selected)
    # Explicit condition *before* a price agreement must override the ordinary
    # quote/accept parser, regardless of what the conditional request refers to.
    conditional = has_condition and (money is not None or kind == 'accept')
    is_proposal = conditional or has_goods or (has_unsupported and money is not None)
    return {'proposal': is_proposal, 'conditional': conditional,
            'cash': money, 'items': selected,
            'unsupported': has_unsupported, 'text': text[:500]}
