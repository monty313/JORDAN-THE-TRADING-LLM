"""Reconcile L5e forced cycle 20260922T133223Z from MCP history."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

EXP = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347")
FORCED = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\forced_signals.jsonl")
ATLAS = EXP / "atlas_reviews.jsonl"
ATLAS_MD = Path(r"C:\Users\C2K\Desktop\MT5 to agent\JARVIS V1\research\atlas_reviews.md")
HANDOFF = EXP / "reports" / "handoff.md"
LOG = EXP / "demo_trade_tape.jsonl"
DECISION = EXP / "decision_tape.jsonl"

ROWS = [
    dict(
        signal_id="20260922T133223Z_GBPUSD_4_S2_1",
        symbol="GBPUSD",
        direction="SELL",
        ticket=58572570625,
        entry=1.33599,
        sl=1.33679,
        exit=1.33607,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T133223Z_NZDUSD_1_S3_2",
        symbol="NZDUSD",
        direction="SELL",
        ticket=58572570880,
        entry=0.57264,
        sl=0.57344,
        exit=0.57277,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T133223Z_AUDUSD_4_S3_3",
        symbol="AUDUSD",
        direction="SELL",
        ticket=58572571328,
        entry=0.71096,
        sl=0.71176,
        exit=0.71099,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T133223Z_EURCAD_3_S2_4",
        symbol="EURCAD",
        direction="BUY",
        ticket=58572571585,
        entry=1.60936,
        sl=1.60857,
        exit=1.60960,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T133223Z_EURCHF_2_S1_5",
        symbol="EURCHF",
        direction="BUY",
        ticket=58572571847,
        entry=0.93945,
        sl=0.93864,
        exit=0.93931,
        point=1e-5,
        close_path="five_minute",
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")


def outcome_status(net_pts: float) -> str:
    if net_pts > 0:
        return "PROFITABLE"
    if net_pts == 0:
        return "FLAT"
    return "NOT_PROFITABLE"


def main() -> int:
    existing = FORCED.read_text(encoding="utf-8-sig")
    now = utc_now()
    broker = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y.%m.%d %H:%M:%S")
    results = []
    for r in ROWS:
        d = r["direction"]
        net_price = (r["exit"] - r["entry"]) if d == "BUY" else (r["entry"] - r["exit"])
        net_pts = round(net_price / r["point"], 1)
        row = {**r, "net_points": net_pts, "flat": True}
        results.append(row)

        has_good = False
        for line in existing.splitlines():
            if not line.strip():
                continue
            o = json.loads(line)
            if (
                o.get("record_type") == "outcome"
                and o.get("signal_id") == r["signal_id"]
                and o.get("exit_executable_price") is not None
            ):
                has_good = True
                break
        if has_good:
            print("skip", r["symbol"])
            continue

        status = outcome_status(net_pts)
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
                    "Batch29 L5e FORCED after abort override: thin FIRE board must not skip five. "
                    "MCP blocked; Python MT5; Expert timed close ~+5m."
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
        print(r["symbol"], net_pts, status)

    bits = "; ".join(
        f"{r['symbol']} {r['direction']} {r['close_path']} net={r['net_points']}" for r in results
    )
    append(
        ATLAS,
        {
            "ts_utc": now,
            "review": "Level4 batch29 cycle 20260922T133223Z L5e forced",
            "doctrine": "Locked reasons unchanged. Prior thin-FIRE abort overridden — forced five required.",
            "common_sense": bits,
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(
        DECISION,
        {
            "ts_utc": now,
            "cycle_id": "20260922T133223Z",
            "event": "batch29_complete_forced",
            "abort_overridden": True,
            "results": results,
        },
    )
    append(LOG, {"event": "batch29_reconciled", "ts_utc": now, "results": results, "abort_overridden": True})
    (EXP / "batch29_results.json").write_text(
        json.dumps(
            {
                "cycle_id": "20260922T133223Z",
                "results": results,
                "reconciled_via": "mcp_history",
                "abort_overridden": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    md = ATLAS_MD.read_text(encoding="utf-8")
    if "20260922T133223Z" not in md:
        md += (
            "\n## Review 20260922T133730Z — Level 4 batch29 L5e forced\n\n"
            "Doctrine audit: locked reasons unchanged. Common sense: prior L5e abort for thin FIRE "
            "board was wrong and overridden; forced five quote-backed round-trips ran "
            f"({bits}). Soft-avoided L5d pairs. "
            "MCP trade_* blocked; Python MetaTrader5. H-002 not activated. "
            "20260922T090923Z UNRESOLVED. No new live rule.\n"
        )
        ATLAS_MD.write_text(md, encoding="utf-8")

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Our L5e book: **flat**. Foreign Client CADCHF not touched.",
        "",
        "## Batch29 (cycle 20260922T133223Z) comment L5e — FORCED after abort override",
        "Prior thin-FIRE abort overridden. Soft-avoided L5d pairs. EURCHF used to fill five.",
        "MCP blocked. Python MT5. Magic 771249, 0.01.",
        "Expert timed close ~+5m (16:37:23–26 broker).",
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
        "1. Continue with forced five every cycle when quotes exist; thin FIRE is not a skip.",
        "2. Do not activate H-20260922-002. Do not rescore 20260922T090923Z.",
        "",
    ]
    HANDOFF.write_text("\n".join(lines), encoding="utf-8")
    print("handoff written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
