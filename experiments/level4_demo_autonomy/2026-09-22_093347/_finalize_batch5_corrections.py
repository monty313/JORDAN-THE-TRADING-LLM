"""Append-only corrections for batch5 null exits (MCP history). Do not rewrite locked lines."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
HANDOFF = EXP / "reports" / "handoff.md"
LOG = EXP / "demo_trade_tape.jsonl"

FIXES = [
    dict(
        signal_id="20260922T101810Z_CADCHF_1_S2_1",
        symbol="CADCHF",
        direction="SELL",
        ticket=58568324211,
        entry=0.58373,
        sl=0.58453,
        exit=0.58390,
        point=1e-5,
        reject=False,
    ),
    dict(
        signal_id="20260922T101810Z_USDSEK_2_S3_2",
        symbol="USDSEK",
        direction="SELL",
        ticket=None,
        entry=None,
        sl=None,
        exit=None,
        point=1e-5,
        reject=True,
        reject_text="retcode 10016 Invalid stops (one attempt, no retry)",
    ),
    dict(
        signal_id="20260922T101810Z_EURUSD_4_S2_3",
        symbol="EURUSD",
        direction="SELL",
        ticket=58568324325,
        entry=1.14620,
        sl=1.14700,
        exit=1.14628,
        point=1e-5,
        reject=False,
    ),
    dict(
        signal_id="20260922T101810Z_GBPUSD_2_S4_4",
        symbol="GBPUSD",
        direction="BUY",
        ticket=58568324455,
        entry=1.33677,
        sl=1.33597,
        exit=1.33676,
        point=1e-5,
        reject=False,
    ),
    dict(
        signal_id="20260922T101810Z_USDCAD_2_S4_5",
        symbol="USDCAD",
        direction="SELL",
        ticket=58568324777,
        entry=1.40341,
        sl=1.40421,
        exit=1.40348,
        point=1e-5,
        reject=False,
        already_ok=True,
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
    rows_out = []
    for r in FIXES:
        if r.get("reject"):
            rows_out.append(
                {
                    "symbol": r["symbol"],
                    "direction": r["direction"],
                    "ticket": "REJECT",
                    "entry": "-",
                    "sl": "-",
                    "exit": "-",
                    "net_points": "-",
                    "close_path": "reject",
                    "flat": "yes",
                }
            )
            append(
                FORCED,
                {
                    "record_type": "outcome_correction",
                    "signal_id": r["signal_id"],
                    "scored_utc": now,
                    "outcome_status": "REJECTED_OR_NO_FILL",
                    "commission_status": "NOT_INCLUDED",
                    "outcome_reason": r["reject_text"],
                    "locked_reason_unchanged": True,
                    "flat": True,
                    "close_path": "reject",
                },
            )
            continue
        d = r["direction"]
        net_price = (r["exit"] - r["entry"]) if d == "BUY" else (r["entry"] - r["exit"])
        net_pts = round(net_price / r["point"], 1)
        rows_out.append(
            {
                "symbol": r["symbol"],
                "direction": d,
                "ticket": r["ticket"],
                "entry": r["entry"],
                "sl": r["sl"],
                "exit": r["exit"],
                "net_points": net_pts,
                "close_path": "five_minute",
                "flat": "yes",
            }
        )
        if r.get("already_ok"):
            continue
        status = "PROFITABLE" if net_pts > 0 else "NOT_PROFITABLE"
        append(
            FORCED,
            {
                "record_type": "outcome_correction",
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
                    f"Demo ticket {r['ticket']}: entry {r['entry']}, SL {r['sl']} (80 pts), "
                    f"exit {r['exit']} via five_minute. Net {net_pts} points. "
                    "Correction: prior outcome had null exit; MCP history Expert close."
                ),
                "post_outcome_review": "Batch5 correction via MCP history; locked reason unchanged.",
                "locked_reason_unchanged": True,
                "demo_ticket": r["ticket"],
                "magic": 771249,
                "volume": 0.01,
                "stop": r["sl"],
                "close_path": "five_minute",
                "flat": True,
            },
        )
        print("corrected", r["symbol"], net_pts)

    bits = "; ".join(
        f"{x['symbol']} {x['direction']} {x['close_path']} net={x['net_points']}" for x in rows_out
    )
    append(
        ATLAS,
        {
            "ts_utc": now,
            "review": "Level4 batch5 correction",
            "doctrine": "Locked reasons unchanged.",
            "common_sense": bits + ". USDSEK rejected Invalid stops once.",
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(LOG, {"event": "batch5_corrected", "ts_utc": now, "rows": rows_out})

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Positions re-read: **flat**.",
        "",
        "## Batch5 (cycle 20260922T101810Z)",
        "MCP trade blocked. Python MetaTrader5. Magic 771249, volume 0.01, SL 80 points. Comment L4e.",
        "",
        "| Symbol | Dir | Ticket | Entry | Stop | Exit | Net pts | Close path | Flat |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for x in rows_out:
        lines.append(
            f"| {x['symbol']} | {x['direction']} | {x['ticket']} | {x['entry']} | {x['sl']} | "
            f"{x['exit']} | {x['net_points']} | {x['close_path']} | {x['flat']} |"
        )
    lines += [
        "",
        "No foreign tickets touched. Book empty.",
        "",
        "## Batch4 (cycle 20260922T100907Z) also scored this wake",
        "NZDUSD -59, EURUSD -43, AUDUSD -29, EURCHF -41, GBPCHF -74 — all five_minute.",
        "",
        "## Next wake",
        "1. Continue until STOP_LEVEL_4_DEMO_AUTONOMY / STOP_FORCED_SIGNAL_LOOP.",
        "2. Do not activate H-20260922-002. Do not rescore 20260922T090923Z.",
        "",
    ]
    HANDOFF.write_text("\n".join(lines), encoding="utf-8")
    print("handoff updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
