"""Level 4 demo round-trip via MetaTrader5 Python API. Demo only. Magic 771249."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import MetaTrader5 as mt5

from mentor_preflight import block_if_mentor_says_stop

MAGIC = 771249
VOLUME = 0.01
SL_POINTS = 0
HOLD_SEC = 300
COMMENT = "L4b m771249"
EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
LOG = EXP / "demo_trade_tape.jsonl"
SCRIPT = Path(__file__).name
MT5_LOG = Path(
    r"C:\Users\C2K\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files\jarvis\level4_roundtrip.jsonl"
)

JOBS = [
    {"signal_id": "20260922T094840Z_AUDJPY_2_S3_1", "symbol": "AUDJPY", "direction": "SELL"},
    {"signal_id": "20260922T094840Z_CADJPY_1_S3_2", "symbol": "CADJPY", "direction": "SELL"},
    {"signal_id": "20260922T094840Z_CHFJPY_1_S3_3", "symbol": "CHFJPY", "direction": "SELL"},
    {"signal_id": "20260922T094840Z_EURGBP_2_S3_4", "symbol": "EURGBP", "direction": "BUY"},
    {"signal_id": "20260922T094840Z_EURNZD_1_S2_5", "symbol": "EURNZD", "direction": "SELL"},
]




def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(obj):
    line = json.dumps(obj, separators=(",", ":"))
    for path in (LOG, MT5_LOG):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")
    print(line)


def main():
    if block_if_mentor_says_stop(SCRIPT):
        return 0

    if not mt5.initialize():
        log({"event": "init_fail", "error": str(mt5.last_error())})
        return 1
    ai = mt5.account_info()
    if ai is None or ai.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
        log({"event": "refuse_not_demo", "trade_mode": getattr(ai, "trade_mode", None)})
        mt5.shutdown()
        return 2

    # snapshot foreign tickets
    foreign = []
    for p in mt5.positions_get() or []:
        foreign.append({"ticket": p.ticket, "symbol": p.symbol, "magic": p.magic, "comment": p.comment})
    log({"event": "pre_positions", "ts_utc": utc_now(), "positions": foreign})

    fills = []
    for job in JOBS:
        symbol = job["symbol"]
        direction = job["direction"]
        if not mt5.symbol_select(symbol, True):
            log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "symbol_select failed"})
            continue
        info = mt5.symbol_info(symbol)
        tick = mt5.symbol_info_tick(symbol)
        if info is None or tick is None:
            log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": "no quote"})
            continue
        point = info.point
        digits = info.digits
        order_type = mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL
        price = tick.ask if direction == "BUY" else tick.bid
        sl = 0.0
        filling = mt5.ORDER_FILLING_FOK
        if info.filling_mode & 2:
            filling = mt5.ORDER_FILLING_IOC
        elif info.filling_mode & 1:
            filling = mt5.ORDER_FILLING_FOK
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": VOLUME,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": 0.0,
            "deviation": 30,
            "magic": MAGIC,
            "comment": COMMENT,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling,
        }
        # before tickets on symbol
        before = {p.ticket for p in (mt5.positions_get(symbol=symbol) or [])}
        result = mt5.order_send(request)
        if result is None:
            log({"event": "reject", "signal_id": job["signal_id"], "symbol": symbol, "text": str(mt5.last_error())})
            continue
        if result.retcode not in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_DONE_PARTIAL):
            log(
                {
                    "event": "reject",
                    "signal_id": job["signal_id"],
                    "symbol": symbol,
                    "direction": direction,
                    "retcode": result.retcode,
                    "text": result.comment,
                }
            )
            continue
        time.sleep(0.4)
        after = list(mt5.positions_get(symbol=symbol) or [])
        pos = None
        for p in after:
            if p.ticket not in before and p.magic == MAGIC:
                pos = p
                break
        if pos is None:
            # fallback by deal
            for p in after:
                if p.magic == MAGIC and COMMENT[:3] in (p.comment or ""):
                    pos = p
                    break
        if pos is None:
            log(
                {
                    "event": "reject",
                    "signal_id": job["signal_id"],
                    "symbol": symbol,
                    "text": "filled but position not found",
                    "order": result.order,
                    "deal": result.deal,
                    "price": result.price,
                }
            )
            continue
        fill = {
            "event": "fill",
            "ts_utc": utc_now(),
            "signal_id": job["signal_id"],
            "symbol": symbol,
            "direction": direction,
            "ticket": pos.ticket,
            "entry": pos.price_open,
            "sl": pos.sl or sl,
            "volume": pos.volume,
            "magic": pos.magic,
            "retcode": result.retcode,
        }
        fills.append(fill)
        log(fill)

    log({"event": "hold_start", "ts_utc": utc_now(), "seconds": HOLD_SEC, "n_fills": len(fills)})
    time.sleep(HOLD_SEC)
    log({"event": "hold_end", "ts_utc": utc_now()})

    results = []
    for fill in fills:
        ticket = fill["ticket"]
        symbol = fill["symbol"]
        direction = fill["direction"]
        entry = fill["entry"]
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            # already closed by SL — get from history
            from_ts = int(time.time()) - 900
            deals = mt5.history_deals_get(from_ts, int(time.time()) + 10) or []
            exit_px = None
            for d in deals:
                if d.position_id == ticket and d.entry == mt5.DEAL_ENTRY_OUT:
                    exit_px = d.price
                    break
            info = mt5.symbol_info(symbol)
            point = info.point if info else 0.00001
            net = None
            if exit_px is not None:
                net = (exit_px - entry) / point if direction == "BUY" else (entry - exit_px) / point
            rec = {
                "event": "close",
                "ts_utc": utc_now(),
                "signal_id": fill["signal_id"],
                "symbol": symbol,
                "direction": direction,
                "ticket": ticket,
                "entry": entry,
                "sl": fill["sl"],
                "exit": exit_px,
                "net_points": round(net, 1) if net is not None else None,
                "close_path": "stop",
                "flat": True,
            }
            results.append(rec)
            log(rec)
            continue

        pos = positions[0]
        tick = mt5.symbol_info_tick(symbol)
        info = mt5.symbol_info(symbol)
        point = info.point if info else 0.00001
        price = tick.bid if direction == "BUY" else tick.ask
        close_type = mt5.ORDER_TYPE_SELL if direction == "BUY" else mt5.ORDER_TYPE_BUY
        filling = mt5.ORDER_FILLING_IOC if (info.filling_mode & 2) else mt5.ORDER_FILLING_FOK
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": pos.volume,
            "type": close_type,
            "position": ticket,
            "price": price,
            "deviation": 30,
            "magic": MAGIC,
            "comment": "L4b close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling,
        }
        result = mt5.order_send(req)
        ok = result is not None and result.retcode in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_DONE_PARTIAL)
        if not ok:
            log(
                {
                    "event": "close_fail",
                    "ticket": ticket,
                    "retcode": getattr(result, "retcode", None),
                    "text": getattr(result, "comment", str(mt5.last_error())),
                }
            )
            # one retry if still open
            if mt5.positions_get(ticket=ticket):
                result = mt5.order_send(req)
                ok = result is not None and result.retcode in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_DONE_PARTIAL)
                log({"event": "close_retry", "ticket": ticket, "ok": ok, "retcode": getattr(result, "retcode", None)})
        exit_px = result.price if result and result.price else price
        still = bool(mt5.positions_get(ticket=ticket))
        net = (exit_px - entry) / point if direction == "BUY" else (entry - exit_px) / point
        rec = {
            "event": "close",
            "ts_utc": utc_now(),
            "signal_id": fill["signal_id"],
            "symbol": symbol,
            "direction": direction,
            "ticket": ticket,
            "entry": entry,
            "sl": fill["sl"],
            "exit": exit_px,
            "net_points": round(net, 1),
            "close_path": "five_minute",
            "flat": not still,
        }
        results.append(rec)
        log(rec)

    # final book
    left = []
    for p in mt5.positions_get() or []:
        left.append({"ticket": p.ticket, "symbol": p.symbol, "magic": p.magic, "comment": p.comment})
    ours_left = [p for p in left if p["magic"] == MAGIC and "L4b" in (p.get("comment") or "")]
    log({"event": "batch_done", "ts_utc": utc_now(), "positions": left, "our_L4b_left": ours_left})
    (EXP / "batch2_results.json").write_text(json.dumps({"fills": fills, "results": results, "left": left}, indent=2), encoding="utf-8")
    mt5.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
