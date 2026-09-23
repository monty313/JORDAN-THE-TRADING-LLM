"""Reconcile L4i cycle 20260922T105904Z from MCP history (incl. USDSEK instant SL)."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
HANDOFF = EXP / "reports" / "handoff.md"
LOG = EXP / "demo_trade_tape.jsonl"

ROWS = [
    dict(
        signal_id="20260922T105904Z_NZDUSD_2_S1_1",
        symbol="NZDUSD",
        direction="BUY",
        ticket=58569021689,
        entry=0.57398,
        sl=0.57318,
        exit=0.57364,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T105904Z_EURGBP_2_S3_2",
        symbol="EURGBP",
        direction="BUY",
        ticket=58569021870,
        entry=0.85806,
        sl=0.85726,
        exit=0.85800,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T105904Z_EURCNH_3_S1_3",
        symbol="EURCNH",
        direction="BUY",
        ticket=58569022075,
        entry=7.68143,
        sl=7.68056,
        exit=7.68048,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T105904Z_GBPJPY_3_S4_4",
        symbol="GBPJPY",
        direction="SELL",
        ticket=58569022188,
        entry=209.802,
        sl=209.885,
        exit=209.904,
        point=0.001,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T105904Z_USDSEK_1_S4_5",
        symbol="USDSEK",
        direction="SELL",
        ticket=58569022434,
        entry=9.79780,
        sl=9.79882,
        exit=9.79882,
        point=1e-5,
        close_path="stop",
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")


def main() -> int:
    now = utc_now()
    broker = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y.%m.%d %H:%M:%S")
    results = []
    for r in ROWS:
        d = r["direction"]
        net_price = (r["exit"] - r["entry"]) if d == "BUY" else (r["entry"] - r["exit"])
        net_pts = round(net_price / r["point"], 1)
        row = {**r, "net_points": net_pts, "flat": True}
        results.append(row)
        status = "PROFITABLE" if net_pts > 0 else "NOT_PROFITABLE"
        append(
            FORCED,
            {
                "record_type": "outcome",
                "signal_id": r["signal_id"],
                "scored_utc": now,
                "scored_broker": broker,
                "exit_bid": r["exit"] if d == "BUY" else None,
                "exit_ask": r["exit"] if d == "SELL" else None,
                "exit_executable_price": r["exit"],
                "net_price_after_spread": net_price,
                "net_points_after_spread": net_pts,
                "outcome_status": status,
                "commission_status": "NOT_INCLUDED",
                "outcome_reason": (
                    f"Demo ticket {r['ticket']}: entry {r['entry']}, SL {r['sl']}, "
                    f"exit {r['exit']} via {r['close_path']}. Net {net_pts} points."
                ),
                "post_outcome_review": (
                    "Batch9 L4i; MCP blocked; Python MT5; MCP history reconcile. "
                    + (
                        "USDSEK filled then immediate SL before fill lookup."
                        if r["symbol"] == "USDSEK"
                        else "Expert timed close."
                    )
                ),
                "locked_reason_unchanged": True,
                "demo_ticket": r["ticket"],
                "magic": 771249,
                "volume": 0.01,
                "stop": r["sl"],
                "close_path": r["close_path"],
                "flat": True,
            },
        )
        print(r["symbol"], net_pts, r["close_path"])

    bits = "; ".join(f"{r['symbol']} {r['direction']} {r['close_path']} net={r['net_points']}" for r in results)
    append(
        ATLAS,
        {
            "ts_utc": now,
            "review": "Level4 batch9 cycle 20260922T105904Z",
            "doctrine": "Locked reasons unchanged.",
            "common_sense": bits,
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(LOG, {"event": "batch9_reconciled", "ts_utc": now, "results": results})
    (EXP / "batch9_results.json").write_text(
        json.dumps({"cycle_id": "20260922T105904Z", "results": results, "reconciled_via": "mcp_history"}, indent=2),
        encoding="utf-8",
    )

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Our L4i book: **flat**. Foreign Client CADCHF not touched.",
        "",
        "## Batch9 (cycle 20260922T105904Z) comment L4i",
        "MCP blocked. Python MT5. Magic 771249, 0.01. SL=max(80, stops+spread+2).",
        "USDSEK filled then hit SL immediately (script saw fill-not-found; no retry).",
        "",
        "| Symbol | Dir | Ticket | Entry | Stop | Exit | Net pts | Close path | Flat |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r['symbol']} | {r['direction']} | {r['ticket']} | {r['entry']} | {r['sl']} | "
            f"{r['exit']} | {r['net_points']} | {r['close_path']} | yes |"
        )
    lines += [
        "",
        "## Next wake",
        "1. Continue until STOP_LEVEL_4_DEMO_AUTONOMY / STOP_FORCED_SIGNAL_LOOP.",
        "2. Do not activate H-20260922-002. Do not rescore 20260922T090923Z.",
        "",
    ]
    HANDOFF.write_text("\n".join(lines), encoding="utf-8")
    print("handoff written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
