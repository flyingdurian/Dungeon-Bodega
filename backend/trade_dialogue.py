"""V0.6.4: protect trade state without replacing lively social chat with boilerplate.

Game rulings are authoritative. In free banter the NPC may joke about dates,
phones and other side offers, but it may not bind a trade with a model sentence.
"""
from __future__ import annotations
import re

# Precise economic commitments; an ordinary "yes" or "sounds fun" is NOT one.
BINDING_CASH = re.compile(
    r"(?i)(?:\b(?:i(?:'ll|'d|\s+will|\s+would|\s+can)?\s*(?:accept|agree\s+to|take|do|pay|buy|sell)|"
    r"we\s*(?:have|got)\s+(?:a\s+)?deal\s+(?:at|for)|"
    r"it's\s+a\s+deal\s+(?:at|for)|sold\s+for)\b.{0,38}?\b\d{1,5}\s*(?:gold|g|coins?)\b|"
    r"\b\d{1,5}\s*(?:gold|g|coins?)\b.{0,32}?\b(?:accepted|agreed|deal|done|sold)\b|"
    r"(?:成交|我接受|我同意).{0,12}\d+\s*(?:金币|金|gold))"
)
BINDING_SIDE = re.compile(
    r"(?i)(?:\b(?:i(?:'ll|'d|\s+will|\s+would)?\s*(?:accept|take|trade|exchange)|"
    r"we(?:'ll|\s+will)\s*(?:trade|exchange)|(?:deal|accepted)\s+for)\b.{0,42}"
    r"\b(?:nintendo\s+switch|iphone|xbox|playstation|headphones?|hoodie|gift\s+card)\b|"
    r"\b(?:nintendo\s+switch|iphone|xbox|playstation|headphones?|hoodie|gift\s+card)\b.{0,36}\b(?:accepted|deal|trade)\b)"
)
TERMS = re.compile(r"(?i)(?:\b\d{1,5}\s*(?:gold|g|coins?)\b|\b(?:price|offer|discount|buy|sell|pay|accept|deal)\b|金币|价钱|成交)")

# These responses are flavor text only and cannot modify the official shop offer.
# Alternates are deliberately varied; no universal repeated cash/side-deal warning.
SOCIAL_DEFLECTIONS = {
    'maya': (
        "Bold pitch! I respect the audacity, even if I'm not signing my life away over a potion.",
        "You're kind of hilarious. Tell me what makes this bargain worth the hype.",
        "A movie and a magical bargain? You've got range. I'm listening.",
    ),
    'liu_xue': (
        "你这人真会说话，哈哈。先让我看看这宝贝值不值得！",
        "哎呀，嘴这么甜？我可不容易被哄住哦。",
        "有趣，有趣！不过做买卖还是要讲眼力的。",
    ),
    'default': (
        "Ha! You certainly know how to make a merchant pause and think.",
        "An unusual proposition. I must admit you've caught my attention.",
        "You have a flair for surprises. Now, where were we?",
    ),
}


def safe_social_line(model: str, scene: dict) -> tuple[str, bool]:
    """Retain natural banter; drop only an *explicit* binding clause."""
    if not (BINDING_CASH.search(model) or BINDING_SIDE.search(model)):
        return model, False
    # Separate sentences only at terminal punctuation followed by a space.
    # Keep safe sentences like "That sounds hilarious!" while discarding a
    # model-invented acceptance such as "I'll take 67 gold and the Switch."
    sentences = re.split(r'(?<=[.!?。！？])\s+', model)
    remaining = [s.strip() for s in sentences
                 if s.strip() and not BINDING_CASH.search(s) and not BINDING_SIDE.search(s)]
    if remaining:
        return ' '.join(remaining), True
    user = str(scene.get('user_text', ''))
    npc = str(scene.get('npc_id', 'default'))
    options = SOCIAL_DEFLECTIONS.get(npc, SOCIAL_DEFLECTIONS['default'])
    # Stable but varied across turns, with no extra model request and no quota.
    turn = int(scene.get('turn', 0) or 0)
    choice = (turn + sum(ord(c) for c in user[:40])) % len(options)
    return options[choice], True


def assemble_trade_dialogue(flavor: str, scene: dict) -> tuple[str, str]:
    """Return (spoken_line, provenance). No imaginary game commitments."""
    event = scene.get('event', 'banter')
    anchor = str(scene.get('anchor', '')).strip()
    model = str(flavor or '').strip()

    # Terminal gameplay rulings must never be undermined by model dialogue.
    if event in ('social_offer','social_refused','social_declined','social_terms_changed'):
        # One authoritative social reply per proposal: no new AI-added terms.
        return anchor or 'Let us agree on what was actually offered.', 'game_locked'

    if event in ('deal', 'walkout', 'rejected', 'clarification'):
        # Permit a short human reaction ahead of a ruling, but never a
        # misleading "yes" or an invented price/payment commitment.
        harmless = bool(model and len(model) <= 125 and not TERMS.search(model)
                        and not BINDING_CASH.search(model) and not BINDING_SIDE.search(model))
        if harmless and event in ('deal', 'rejected') and anchor:
            return f'{model} {anchor}', 'game_locked'
        return anchor or 'That settles the matter.', 'game_locked'

    if event == 'counter':
        # Neutral noncommercial character reactions may lead into the official
        # counter, but the model may not voice a separate price or an agreement.
        if model and len(model) <= 125 and not TERMS.search(model) and not BINDING_SIDE.search(model):
            return f'{model} {anchor}'.strip(), 'game_locked'
        return anchor or 'I have a different offer.', 'game_locked'

    if event == 'proposal':
        # Nothing is sold while a condition is pending. Preserve the model's
        # social response but strip any premature commercial acceptance.
        filtered, repaired = safe_social_line(model, scene)
        premature = re.compile(r"(?i)\b(?:we have (?:ourselves )?a deal|it's a deal|deal done|sold|"
                               r"i accept (?:your|the) offer|i'll take your \d+|agreed,? \d+|(?:okay,?\s*)?deal[!.]?)\b")
        bits = re.split(r'(?<=[.!?。！？])\s+',filtered)
        safe = [b for b in bits if not premature.search(b)]
        if safe:
            filtered = ' '.join(safe)
        elif not filtered:
            filtered = ''
        else:
            filtered = ''
        if not filtered:
            user = str(scene.get('user_text',''))
            npc = str(scene.get('npc_id','default'))
            options = SOCIAL_DEFLECTIONS.get(npc,SOCIAL_DEFLECTIONS['default'])
            filtered = options[(int(scene.get('turn',0))+sum(ord(ch) for ch in user[:40])) % len(options)]
        return filtered,'model_repaired' if repaired or filtered != model else 'model'

    # Banter should feel like human conversation, not a contract lecture.
    # A proposal about a movie, date or gadget is permissible as *fictional
    # conversation*; the engine does not record it as payment.
    filtered, repaired = safe_social_line(model, scene)
    if anchor:
        return f'{filtered} {anchor}'.strip(), 'model_repaired' if repaired else 'model'
    return filtered, 'model_repaired' if repaired else 'model'
