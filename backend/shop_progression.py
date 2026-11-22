"""Deterministic market and daily shop operations; no model-owned money."""
from __future__ import annotations
from .content import ITEMS, ITEM_BY_ID

MAX_STOCK = 12


def spotlight(day: int) -> dict:
    item = ITEMS[(max(1, int(day)) - 1) % len(ITEMS)]
    return {'item_id': item['id'], 'name': item['name'],
            'day': max(1, int(day)), 'buyback_modifier': 1.10}


def supply_cost(item_id: str, day: int) -> int:
    item = ITEM_BY_ID[item_id]
    # The market spotlight makes replenishment 15% more costly; it may also
    # improve buying interest on new encounters. Both are deterministic.
    multiplier = 0.77 if spotlight(day)['item_id'] == item_id else 0.67
    return max(1, round(item['price'] * multiplier))


def shop_ledger(world: dict) -> dict:
    day = max(1, int(world.get('day', 1)))
    deals = max(0, int(world.get('deals', 0)))
    reputation = max(0, min(100, int(world.get('reputation', 50))))
    earned = max(0, int(world.get('earned_gold', 0)))
    spent = max(0, int(world.get('spent_gold', 0)))
    supplies = max(0, int(world.get('restock_spend', 0)))
    inventory_value = sum(int(world['stock'].get(i['id'], 0)) * int(i['price']) for i in ITEMS)
    return {'day': day, 'deals': deals, 'reputation': reputation,
            'shop_rank': 'Guild Merchant' if deals >= 20 else 'Trusted Trader' if deals >= 8 else 'New Shopkeeper',
            'earned_gold': earned, 'purchases_gold': spent,
            'supplies_gold': supplies, 'net_trade_cash': earned - spent - supplies,
            'stock_value': inventory_value, 'market': spotlight(day)}
