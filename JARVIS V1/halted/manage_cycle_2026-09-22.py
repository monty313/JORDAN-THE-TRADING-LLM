"""Manage-only kill loop for magic 771249. Demo only. No spray."""
from __future__ import annotations

import csv
import math
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import MetaTrader5 as mt5
import numpy as np

MAGIC = 771249
LOGIN = 5056316064
ET = ZoneInfo("America/New_York")
BOARD = r"C:\Users\C2K\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files\jarvis\board.csv"
LOG = r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\LEARNING_LOG.md"
MAX_OPEN = 15
DEADLINE = datetime(2026, 9, 23, 0, 36, tzinfo=ET)
MAX_LOTS = 10.0
MAX_RISK = 2000.0

# ticket -> kill spec (rebuilt from live positions + known kills)
# kind: sma_sell | sma_buy | rail_sell
KNOWN_KILLS = {
    58577170454: {"kind": "rail_sell", "level": 1.33367, "why": "body back through rail_hi 1.33367"},
    58576967692: {"kind": "sma_sell", "level": 0.71066, "why": "M5 close above SMA50 0.71066"},
    58576967748: {"kind": "sma_buy", "level": 1.40603, "why": "M5 close below SMA50 1.40603"},
    58576967843: {"kind": "rail_sell", "level": 1.87709, "why": "body back through rail_hi 1.87709"},
}


def confirm_demo() -> None:
    ai = mt5.account_info()
    if ai is None or ai.login != LOGIN or ai.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
        raise SystemExit(f"not demo/login: {ai}")


def open_book():
    out = []
    for p in mt5.positions_get() or []:
        if p.magic != MAGIC:
            continue
        if (p.comment or "").strip().lower() == "client":
            continue
        out.append(p)
    return out


def filling_mode(symbol: str) -> int:
    info = mt5.symbol_info(symbol)
    modes = info.filling_mode
    if modes & 1:
        return mt5.ORDER_FILLING_FOK
    if modes & 2:
        return mt5.ORDER_FILLING_IOC
    return mt5.ORDER_FILLING_RETURN


def last_closed_m5(symbol: str):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 60)
    if rates is None or len(rates) < 3:
        return None
    # rates[-1] forming, rates[-2] last closed
    return rates[-2], rates


def kill_hit(ticket: int, symbol: str, side: str) -> tuple[bool, str]:
    spec = KNOWN_KILLS.get(ticket)
    if not spec:
        # unknown — do not invent a kill
        return False, "no registered kill"
    bar, rates = last_closed_m5(symbol) or (None, None)
    if bar is None:
        return False, "no M5"
    o, c = float(bar["open"]), float(bar["close"])
    body_hi, body_lo = max(o, c), min(o, c)
    lvl = spec["level"]
    kind = spec["kind"]
    t = datetime.fromtimestamp(int(bar["time"]))
    if kind == "sma_sell":
        if c > lvl:
            return True, f"{spec['why']} (M5 {t} close={c})"
    elif kind == "sma_buy":
        if c < lvl:
            return True, f"{spec['why']} (M5 {t} close={c})"
    elif kind == "rail_sell":
        if body_hi >= lvl or c >= lvl:
            return True, f"{spec['why']} (M5 {t} o={o} c={c})"
    return False, f"ok M5 {t} c={c} lvl={lvl}"


def close_ticket(ticket: int, reason: str) -> dict:
    confirm_demo()
    pos = mt5.positions_get(ticket=ticket)
    if not pos:
        return {"ok": False, "why": "already gone", "ticket": ticket}
    p = pos[0]
    if p.magic != MAGIC or (p.comment or "").strip().lower() == "client":
        return {"ok": False, "why": "refuse non-magic/client", "ticket": ticket}
    confirm_demo()
    pos = mt5.positions_get(ticket=ticket)
    if not pos:
        return {"ok": False, "why": "gone before send", "ticket": ticket}
    p = pos[0]
    tick = mt5.symbol_info_tick(p.symbol)
    order_type = mt5.ORDER_TYPE_BUY if p.type == 1 else mt5.ORDER_TYPE_SELL
    price = tick.ask if p.type == 1 else tick.bid
    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": ticket,
        "symbol": p.symbol,
        "volume": float(p.volume),
        "type": order_type,
        "price": price,
        "deviation": 30,
        "magic": MAGIC,
        "comment": ("J kill " + reason)[:31],
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode(p.symbol),
    }
    r = mt5.order_send(req)
    if r is None:
        time.sleep(1)
        gone = mt5.positions_get(ticket=ticket) is None or not mt5.positions_get(ticket=ticket)
        return {"ok": gone, "ambiguous": True, "ticket": ticket, "why": str(mt5.last_error())}
    if r.retcode != mt5.TRADE_RETCODE_DONE:
        return {"ok": False, "ticket": ticket, "why": f"ret={r.retcode} {r.comment}", "ambiguous": r.retcode in (mt5.TRADE_RETCODE_TIMEOUT, mt5.TRADE_RETCODE_CONNECTION)}
    return {"ok": True, "ticket": ticket, "symbol": p.symbol, "price": r.price, "volume": r.volume, "reason": reason}


def parse_cmp(cmp: str) -> dict:
    out = {}
    for part in cmp.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            try:
                out[k] = float(v)
            except ValueError:
                pass
    return out


def board_best_fires():
    with open(BOARD, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    max_ts = max(r["ts"] for r in rows if r.get("family") == "OFFICIAL")
    fresh = [
        r
        for r in rows
        if r["ts"] == max_ts
        and r.get("family") == "OFFICIAL"
        and r.get("strategy") in ("S1", "S2", "S3", "S4")
    ]
    prio = {"S2": 0, "S4": 1, "S1": 2, "S3": 3}
    sides = {}
    best = {}
    for r in fresh:
        if r["act"] not in ("FIRE_BUY", "FIRE_SELL"):
            continue
        ok_tide = (r["act"] == "FIRE_BUY" and r["tide"] == "long_only") or (
            r["act"] == "FIRE_SELL" and r["tide"] == "short_only"
        )
        ok_reason = any(
            x in r["reason"]
            for x in ("emerged_enter", "pullback", "reclaim", "slingshot", "full_body", "tunnel")
        )
        if not (ok_tide and ok_reason):
            continue
        side = "buy" if r["act"] == "FIRE_BUY" else "sell"
        sides.setdefault(r["symbol"], set()).add(side)
        s = r["symbol"]
        if s not in best or prio[r["strategy"]] < prio[best[s]["strategy"]]:
            best[s] = r
        elif r["strategy"] == best[s]["strategy"] and int(r["set"]) < int(best[s]["set"]):
            best[s] = r
    conflicted = {s for s, v in sides.items() if len(v) > 1}
    return max_ts, best, conflicted


def plan_from_row(row: dict) -> dict | None:
    sym = row["symbol"]
    side = "buy" if row["act"] == "FIRE_BUY" else "sell"
    mt5.symbol_select(sym, True)
    tick = mt5.symbol_info_tick(sym)
    info = mt5.symbol_info(sym)
    if not tick or not info or info.trade_mode == mt5.SYMBOL_TRADE_MODE_DISABLED:
        return None
    entry = tick.ask if side == "buy" else tick.bid
    cmp = parse_cmp(row["cmp"])
    point, digits = info.point, info.digits
    sma50, mid100 = cmp.get("sma50"), cmp.get("mid100")
    rail_hi, rail_lo = cmp.get("rail_hi"), cmp.get("rail_lo")
    strat = row["strategy"]
    if strat == "S2":
        if side == "sell":
            lv = [x for x in (sma50, mid100) if x is not None]
            if not lv:
                return None
            stop = max(lv) + 20 * point
            if stop <= entry:
                stop = entry + 50 * point
            kill_lvl = sma50 if sma50 is not None else mid100
            kill = f"M5 close above SMA50 {kill_lvl}"
            comment = "J S2 pullback"
            kill_kind = "sma_sell"
        else:
            lv = [x for x in (sma50, mid100) if x is not None]
            if not lv:
                return None
            stop = min(lv) - 20 * point
            if stop >= entry:
                stop = entry - 50 * point
            kill_lvl = sma50 if sma50 is not None else mid100
            kill = f"M5 close below SMA50 {kill_lvl}"
            comment = "J S2 pullback"
            kill_kind = "sma_buy"
        kill_level = float(kill_lvl)
    elif strat == "S3":
        if side == "sell":
            stop = (rail_hi if rail_hi else entry + 50 * point) + 20 * point
            if stop <= entry:
                stop = entry + 50 * point
            kill = f"body back through rail_hi {rail_hi}"
            comment = "J S3 envelope"
            kill_kind = "rail_sell"
            kill_level = float(rail_hi if rail_hi else stop)
        else:
            stop = (rail_lo if rail_lo else entry - 50 * point) - 20 * point
            if stop >= entry:
                stop = entry - 50 * point
            kill = f"body back through rail_lo {rail_lo}"
            comment = "J S3 envelope"
            kill_kind = "rail_buy"
            kill_level = float(rail_lo if rail_lo else stop)
    elif strat == "S1":
        if side == "sell":
            stop = (sma50 if sma50 else entry + 40 * point) + 20 * point
            if stop <= entry:
                stop = entry + 50 * point
            kill = "CCI30 loses reclaim vs SMA"
            comment = "J S1 CCI sling"
            kill_kind = "sma_sell"
            kill_level = float(sma50 if sma50 else stop)
        else:
            stop = (sma50 if sma50 else entry - 40 * point) - 20 * point
            if stop >= entry:
                stop = entry - 50 * point
            kill = "CCI30 loses reclaim vs SMA"
            comment = "J S1 CCI sling"
            kill_kind = "sma_buy"
            kill_level = float(sma50 if sma50 else stop)
    elif strat == "S4":
        if side == "sell":
            stop = (mid100 if mid100 else entry + 40 * point) + 20 * point
            if stop <= entry:
                stop = entry + 50 * point
            kill = "RSI2 loses short reclaim"
            comment = "J S4 RSI snap"
            kill_kind = "sma_sell"
            kill_level = float(mid100 if mid100 else stop)
        else:
            stop = (mid100 if mid100 else entry - 40 * point) - 20 * point
            if stop >= entry:
                stop = entry - 50 * point
            kill = "RSI2 loses long reclaim"
            comment = "J S4 RSI snap"
            kill_kind = "sma_buy"
            kill_level = float(mid100 if mid100 else stop)
    else:
        return None
    stop = round(stop, digits)
    if abs(entry - stop) < 10 * point:
        return None
    dist = abs(entry - stop)
    risk1 = (dist / info.trade_tick_size) * info.trade_tick_value
    if risk1 <= 0:
        return None
    raw = min(MAX_LOTS, MAX_RISK / risk1)
    step = info.volume_step or 0.01
    lots = math.floor(raw / step) * step
    lots = max(0.0, min(lots, info.volume_max, MAX_LOTS))
    if lots < info.volume_min:
        return None
    return {
        "symbol": sym,
        "side": side,
        "lots": round(lots, 2),
        "sl": stop,
        "kill": kill,
        "kill_kind": kill_kind,
        "kill_level": kill_level,
        "comment": comment[:31],
        "strategy": strat,
        "reason": row["reason"],
        "risk": risk1 * lots,
    }


def send_replace(plan: dict) -> dict:
    confirm_demo()
    held = {p.symbol for p in open_book()}
    if plan["symbol"] in held:
        return {"ok": False, "why": "symbol already held"}
    if len(open_book()) >= MAX_OPEN:
        return {"ok": False, "why": "at max open"}
    print("KILL_BEFORE_SEND", plan["symbol"], plan["side"], plan["kill"], "sl", plan["sl"], "lots", plan["lots"])
    confirm_demo()
    if plan["symbol"] in {p.symbol for p in open_book()}:
        return {"ok": False, "why": "symbol raced in"}
    tick = mt5.symbol_info_tick(plan["symbol"])
    price = tick.ask if plan["side"] == "buy" else tick.bid
    if plan["side"] == "buy" and plan["sl"] >= price:
        return {"ok": False, "why": "bad buy sl"}
    if plan["side"] == "sell" and plan["sl"] <= price:
        return {"ok": False, "why": "bad sell sl"}
    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": plan["symbol"],
        "volume": float(plan["lots"]),
        "type": mt5.ORDER_TYPE_BUY if plan["side"] == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": float(plan["sl"]),
        "tp": 0.0,
        "deviation": 30,
        "magic": MAGIC,
        "comment": plan["comment"],
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode(plan["symbol"]),
    }
    r = mt5.order_send(req)
    if r is None:
        time.sleep(1)
        found = [p for p in open_book() if p.symbol == plan["symbol"]]
        if found:
            KNOWN_KILLS[found[0].ticket] = {
                "kind": plan["kill_kind"],
                "level": plan["kill_level"],
                "why": plan["kill"],
            }
            return {"ok": True, "reconciled": True, "ticket": found[0].ticket, "symbol": plan["symbol"]}
        return {"ok": False, "ambiguous": True, "why": str(mt5.last_error())}
    if r.retcode != mt5.TRADE_RETCODE_DONE:
        return {"ok": False, "why": f"ret={r.retcode} {r.comment}"}
    # register kill for new ticket
    time.sleep(0.3)
    found = [p for p in open_book() if p.symbol == plan["symbol"]]
    ticket = found[0].ticket if found else r.order
    KNOWN_KILLS[ticket] = {"kind": plan["kill_kind"], "level": plan["kill_level"], "why": plan["kill"]}
    # ensure SL
    if found and (not found[0].sl or abs(found[0].sl - plan["sl"]) > 1e-8):
        confirm_demo()
        mt5.order_send(
            {
                "action": mt5.TRADE_ACTION_SLTP,
                "position": ticket,
                "symbol": plan["symbol"],
                "sl": float(plan["sl"]),
                "tp": 0.0,
            }
        )
    return {
        "ok": True,
        "ticket": ticket,
        "symbol": plan["symbol"],
        "side": plan["side"],
        "lots": plan["lots"],
        "price": r.price,
        "sl": plan["sl"],
        "kill": plan["kill"],
    }


def closed_score_ge1() -> float:
    start_ts = int(datetime(2026, 9, 22, 12, 36, tzinfo=ET).timestamp())
    deals = mt5.history_deals_get(datetime(2026, 9, 22), datetime(2026, 9, 23)) or []
    ins = {}
    for d in deals:
        if d.magic != MAGIC:
            continue
        if d.entry == 0:
            ins[d.position_id] = d.time
    total = 0.0
    for d in deals:
        if d.magic != MAGIC or d.entry != 1:
            continue
        if d.volume < 1.0:
            continue
        ot = ins.get(d.position_id)
        if ot is None or ot < start_ts:
            continue
        total += d.profit + d.swap + d.commission
    return total


def forming_m5_open_time(symbol: str = "EURUSD") -> int | None:
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 2)
    if rates is None:
        return None
    return int(rates[-1]["time"])


def try_replace_one(closed_symbol: str | None = None) -> dict | None:
    now = datetime.now(ET)
    if now >= DEADLINE:
        print("past deadline — no new opens")
        return None
    if len(open_book()) >= MAX_OPEN:
        return None
    max_ts, best, conflicted = board_best_fires()
    print("board", max_ts)
    held = {p.symbol for p in open_book()}
    prefer = [
        "GBPUSD",
        "EURUSD",
        "USDJPY",
        "EURGBP",
        "EURCNH",
        "CADCHF",
        "EURCHF",
        "GBPJPY",
        "NZDUSD",
        "USDCHF",
    ]
    order = []
    if closed_symbol and closed_symbol in best:
        order.append(closed_symbol)
    order += [s for s in prefer if s not in order]
    order += [s for s in best if s not in order]
    for sym in order:
        if sym in held or sym in conflicted or sym not in best:
            continue
        if sym in ("IT40", "XPTUSD"):
            continue
        plan = plan_from_row(best[sym])
        if not plan:
            continue
        print("REPLACE_PLAN", plan)
        return send_replace(plan)
    print("no replace FIRE")
    return None


def one_kill_pass() -> list:
    closed = []
    confirm_demo()
    book = open_book()
    print("--- kill pass ---", datetime.now(ET).isoformat(), "n=", len(book))
    for p in list(book):
        side = "sell" if p.type == 1 else "buy"
        hit, msg = kill_hit(p.ticket, p.symbol, side)
        print(p.ticket, p.symbol, side, "HIT" if hit else "hold", msg, "pl", round(p.profit, 2), "sl", p.sl)
        if hit:
            # do not delete stops; close
            res = close_ticket(p.ticket, msg[:20])
            print("CLOSE", res)
            if res.get("ok"):
                closed.append({"ticket": p.ticket, "symbol": p.symbol, "why": msg, "res": res})
                # replace one for this close if allowed
                time.sleep(0.3)
                rep = try_replace_one(p.symbol)
                if rep:
                    print("REPLACE", rep)
    return closed


def main():
    if not mt5.initialize():
        raise SystemExit(mt5.last_error())
    try:
        confirm_demo()
        all_closed = []
        # Pass 1 immediate
        all_closed.extend(one_kill_pass())

        # Watch until the extended deadline. New opens stop at DEADLINE.
        end_watch = DEADLINE
        open_cutoff = DEADLINE
        bars_seen = 0
        last_forming = forming_m5_open_time()
        print("forming_start", last_forming, datetime.fromtimestamp(last_forming) if last_forming else None)

        while datetime.now(ET) < end_watch and bars_seen < 3:
            time.sleep(15)
            confirm_demo()
            # broker stop fills?
            live_ids = {p.ticket for p in open_book()}
            for tid in list(KNOWN_KILLS):
                if tid not in live_ids and tid not in {c["ticket"] for c in all_closed}:
                    # may have been SL'd
                    print("MISSING_TICKET_maybe_SL", tid)
            cur = forming_m5_open_time()
            if cur and last_forming and cur != last_forming:
                print("NEW_M5_BAR", datetime.fromtimestamp(cur))
                last_forming = cur
                bars_seen += 1
                all_closed.extend(one_kill_pass())
            # if past open cutoff mid-loop, still manage closes only
            if datetime.now(ET) >= open_cutoff:
                print("hit deadline during watch — closes only")
                all_closed.extend(one_kill_pass())
                break

        # final snapshot
        confirm_demo()
        book = open_book()
        fp = sum(p.profit for p in book)
        score = closed_score_ge1()
        print("FINAL_BOOK")
        for p in book:
            print(p.ticket, p.symbol, "sell" if p.type == 1 else "buy", p.volume, p.price_open, p.sl, round(p.profit, 2), p.comment)
        print("FLOAT", round(fp, 2), "CLOSED_SCORE_GE1", round(score, 2))
        print("CLOSED_THIS_RUN", all_closed)

        ts = datetime.now(ET).strftime("%Y-%m-%d %H:%M %Z")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(
                f"\n## {ts}\n"
                f"Manage cycle: closed this run {len(all_closed)} ticket(s). "
                f"New closed score magic 771249 since 12:36 (size>=1): {score:.2f}. "
                f"Floating {fp:.2f}. Not above +38535. Client untouched.\n"
            )
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
