"""Log whether a new chat can reconstruct the desk from files."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "debug-e25812.log"
SESSION = "e25812"


def emit(hypothesis_id: str, message: str, data: dict, run_id: str) -> None:
    # #region agent log
    row = {
        "sessionId": SESSION,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": "continuity_check.py",
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    # #endregion


def main() -> None:
    import sys

    run_id = sys.argv[1] if len(sys.argv) > 1 else "pre-fix"
    standing = (ROOT / "JARVIS V1" / "STANDING_ORDERS.md").read_text(encoding="utf-8")
    desk = (ROOT / "JARVIS V1" / "desk_state.md").read_text(encoding="utf-8")
    required_yaml = [
        "account_mode: DEMO_ONLY",
        "magic_number: 771249",
        "client_tickets_policy: LEAVE_UNTOUCHED",
        "floating_counts_toward_score: false",
        "normal_new_ticket_lots: 1.0",
        "fixed_10_lot_chasing: FORBIDDEN",
        "anonymous_keep10_fallback: FORBIDDEN",
        "pre_trade_thesis_required: true",
        "emergence_execution_authority: false",
        "book_fill_to_50: FORBIDDEN",
        "liquid_name_quota",
        "risk_floor",
    ]
    missing_yaml = [key for key in required_yaml if key not in standing]
    emit(
        "A",
        "standing orders yaml coverage",
        {"missing": missing_yaml, "yaml_complete": not missing_yaml},
        run_id,
    )
    emit(
        "B",
        "desk state ledger and floor words",
        {
            "has_ledger": "State-change ledger" in desk,
            "mentions_risk_floor_term": "risk_floor" in desk,
            "mentions_liquid_name_quota": "liquid_name_quota" in desk,
            "stale_ticket_list_present": "58576967692" in desk,
        },
        run_id,
    )
    tapes = {
        "pre_trade_thesis": ROOT / "JARVIS V1" / "research" / "pre_trade_thesis.jsonl",
        "decision_tape": ROOT / "JARVIS V1" / "research" / "decision_tape.jsonl",
        "demo_trade_tape": ROOT / "JARVIS V1" / "research" / "demo_trade_tape.jsonl",
        "experiment_registry_yaml": ROOT / "JARVIS V1" / "research" / "experiment_registry.yaml",
        "account_snapshots": ROOT / "JARVIS V1" / "research" / "account_snapshots",
    }
    emit(
        "C",
        "canonical tape presence",
        {name: path.exists() for name, path in tapes.items()},
        run_id,
    )
    fable_hits = list(ROOT.rglob("*FABLE*"))
    emit(
        "D",
        "fable harness presence",
        {"count": len(fable_hits), "paths": [str(path.relative_to(ROOT)) for path in fable_hits]},
        run_id,
    )
    terminals = Path(r"C:\Users\C2K\.cursor\projects\c-Users-C2K-Desktop-MT5-to-agent\terminals")
    loop_text = ""
    if terminals.exists():
        for path in terminals.glob("*.txt"):
            text = path.read_text(encoding="utf-8", errors="replace")
            parts = text.split("---")
            header = parts[1] if text.startswith("---") and len(parts) > 1 else ""
            if "status: running" not in header:
                continue
            if "AGENT_LOOP_TICK_jarvis_book" not in text:
                continue
            loop_text = text
            break
    emit(
        "E",
        "running loop authorizes anonymous fill",
        {
            "loop_found": bool(loop_text),
            "mentions_add_liquid": "add only liquid names" in loop_text,
            "forbids_send": "Do not send an order" in loop_text,
        },
        run_id,
    )
    from keep10_open import classify

    set3 = classify(
        {
            "run_id": "probe",
            "signal_id": "probe-set3",
            "magic_number": 771249,
            "symbol": "EURUSD",
            "direction": "BUY",
            "strategy_id": "S1",
            "set_id": 3,
            "anchor_tf": "M5",
            "htf1": "M30",
            "htf2": "H4",
            "htf1_side": "long",
            "htf2_side": "long",
            "topology": "PULLBACK",
            "tide": "long_only",
            "regime": "bull_trend",
            "s5_present": True,
            "official_act": "FIRE_BUY",
            "entry_bid": 1.1,
            "entry_ask": 1.10002,
            "spread_points": 2,
            "structural_stop_price": 1.09,
            "structural_kill_relation": "close back through rail",
            "risk_dollars": 10,
            "risk_percent": 0.1,
            "maximum_duration_minutes": 10,
            "doctrine_version": "007-v1.0",
            "config_hash": "probe",
            "timestamp_utc": "2026-09-23T01:25:00Z",
            "release_bar_time": "2026-09-23T01:20:00Z",
            "current_closed_bar_time": "2026-09-23T01:20:00Z",
        }
    )
    emit("F", "keep10 classify set 3", {"reason": set3}, run_id)
    baseline = Path(r"C:\Users\C2K\Desktop\Strategies - Copy\007_JARVIS_Momentum_Conservation_Trading_Mentor_Baseline.md")
    digest = hashlib.sha256(baseline.read_bytes()).hexdigest() if baseline.exists() else None
    emit("G", "007 baseline path", {"exists": baseline.exists(), "sha256": digest}, run_id)


if __name__ == "__main__":
    main()
