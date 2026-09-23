"""Shared mentor gate for every order_send / trading-connect script in this folder.

Returns True when the script must NOT connect or send. Does not touch MT5.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

EXP = Path(__file__).resolve().parent
MENTOR_INBOX = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\MENTOR_INBOX.md")
TAPE = EXP / "demo_trade_tape.jsonl"
TIDE_TAPE = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\tide_alignment_tape.jsonl")
BOARD = Path(
    r"C:\Users\C2K\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files\jarvis\board.csv"
)

_GATE_IDS = ("G1", "G2", "G3", "G4", "G5", "G6", "G7")
_PEER_KEYS = ("g1", "g3", "g4", "g5", "g6", "g7")

_BLOCK_PHRASES = (
    "Send nothing",
    "Do not run",
    "Do not add a batch",
    "do not add a batch",
)


def _newest_section(text: str) -> str:
    """First ## section (newest notes are written at the top)."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## "):
            start = i
            break
    if start is None:
        return ""
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end])


def _log_block(script_name: str, reason: str) -> None:
    line = json.dumps(
        {"event": "preflight_block", "reason": reason, "script": script_name},
        separators=(",", ":"),
    )
    with TAPE.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
    print(line, flush=True)


def block_if_mentor_says_stop(script_name: str) -> bool:
    """Return True (BLOCK) when mentor inbox says stop or is missing. Fail closed."""
    if not MENTOR_INBOX.is_file():
        _log_block(script_name, "mentor_inbox_missing")
        return True
    try:
        text = MENTOR_INBOX.read_text(encoding="utf-8")
    except OSError:
        _log_block(script_name, "mentor_inbox_missing")
        return True
    section = _newest_section(text)
    if any(p in section for p in _BLOCK_PHRASES):
        _log_block(script_name, "mentor_send_nothing")
        return True
    return False


def _gate_side(row: dict) -> str:
    """ABOVE/BELOW/FLAT from rsi14 vs sma1_shift4 (raw_a / raw_b). Never invent RSI."""
    raw_a, raw_b = row.get("raw_a"), row.get("raw_b")
    if raw_a in (None, "") or raw_b in (None, ""):
        return "UNDEFINED"
    try:
        rsi = float(raw_a)
        sma = float(raw_b)
    except (TypeError, ValueError):
        return "UNDEFINED"
    if rsi > sma:
        return "ABOVE"
    if rsi < sma:
        return "BELOW"
    return "FLAT"


def _modal_side(sides: list[str]) -> str | None:
    counted = [s for s in sides if s in ("ABOVE", "BELOW")]
    if not counted:
        return None
    return Counter(counted).most_common(1)[0][0]


def _g2_odd(gate_sides: dict[str, str]) -> bool | str:
    """True when G2 is not FLAT and differs from modal of G1+G3–G7. Missing gate → UNDEFINED."""
    if any(gate_sides.get(k) == "UNDEFINED" for k in ("g1", "g2", "g3", "g4", "g5", "g6", "g7")):
        return "UNDEFINED"
    g2 = gate_sides["g2"]
    if g2 == "FLAT":
        return False
    modal = _modal_side([gate_sides[k] for k in _PEER_KEYS])
    if modal is None:
        return "UNDEFINED"
    return g2 != modal


def _latest_gate_sides(symbols: set[str]) -> tuple[str, dict[str, dict[str, str]]]:
    """Read board.csv GATE G1–G7 for symbols only. Returns (board_ts, {sym: {g1..g7}})."""
    rows = list(csv.DictReader(BOARD.open(encoding="utf-8", errors="replace")))
    if not rows:
        return "", {s: {f"g{i}": "UNDEFINED" for i in range(1, 8)} for s in symbols}
    board_ts = max(r["ts"] for r in rows)
    cur = [r for r in rows if r["ts"] == board_ts and r.get("family") == "GATE"]
    out: dict[str, dict[str, str]] = {
        s: {f"g{i}": "UNDEFINED" for i in range(1, 8)} for s in symbols
    }
    for r in cur:
        sym = (r.get("symbol") or "").replace(".sim", "")
        if sym not in symbols:
            continue
        gid = r.get("strategy") or ""
        if gid not in _GATE_IDS:
            continue
        out[sym][gid.lower()] = _gate_side(r)
    return board_ts, out


def log_plan_vs_board(script: str, plans: list[dict]) -> list[dict]:
    """Append one tide-alignment tape row per planned {symbol, side}. No MetaTrader5. No orders."""
    wanted = {(p.get("symbol") or "").replace(".sim", "") for p in plans if p.get("symbol")}
    board_ts, by_sym = _latest_gate_sides(wanted)
    ts_local = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%dT%H:%M:%S%z")
    ts_local = ts_local[:-2] + ":" + ts_local[-2:]
    written: list[dict] = []
    TIDE_TAPE.parent.mkdir(parents=True, exist_ok=True)
    with TIDE_TAPE.open("a", encoding="utf-8", newline="\n") as f:
        for p in plans:
            sym = (p.get("symbol") or "").replace(".sim", "")
            side = p.get("side") or p.get("direction") or ""
            gates = by_sym.get(sym) or {f"g{i}": "UNDEFINED" for i in range(1, 8)}
            vals = [gates[f"g{i}"] for i in range(1, 8)]
            above_n = sum(1 for v in vals if v == "ABOVE")
            below_n = sum(1 for v in vals if v == "BELOW")
            row = {
                "script": script,
                "symbol": sym,
                "side": side,
                "g1": gates["g1"],
                "g2": gates["g2"],
                "g3": gates["g3"],
                "g4": gates["g4"],
                "g5": gates["g5"],
                "g6": gates["g6"],
                "g7": gates["g7"],
                "above_n": above_n,
                "below_n": below_n,
                "g2_odd": _g2_odd(gates),
                "pullback_call": "UNDEFINED",
                "board_ts": board_ts,
                "ts_local": ts_local,
            }
            f.write(json.dumps(row, separators=(",", ":")) + "\n")
            written.append(row)
    return written
