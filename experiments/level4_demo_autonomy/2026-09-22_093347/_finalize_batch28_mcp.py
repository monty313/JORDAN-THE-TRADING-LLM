"""Reconcile L5d cycle 20260922T132125Z from MCP history exits."""
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
        signal_id="20260922T132125Z_USDCAD_1_S4_1",
        symbol="USDCAD",
        direction="BUY",
        ticket=58572295619,
        entry=1.40477,
        sl=1.40397,
        exit=1.40500,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T132125Z_GBPAUD_3_S4_2",
        symbol="GBPAUD",
        direction="BUY",
        ticket=58572295733,
        entry=1.87926,
        sl=1.87846,
        exit=1.87889,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T132125Z_EURUSD_4_S2_3",
        symbol="EURUSD",
        direction="SELL",
        ticket=58572295976,
        entry=1.14573,
        sl=1.14653,
        exit=1.14549,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T132125Z_USDJPY_1_S3_4",
        symbol="USDJPY",
        direction="BUY",
        ticket=58572296142,
        entry=157.294,
        sl=157.045,
        exit=157.307,
        point=0.001,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T132125Z_AUDJPY_1_S3_5",
        symbol="AUDJPY",
        direction="BUY",
        ticket=58572296278,
        entry=111.836,
        sl=111.586,
        exit=111.829,
        point=0.001,
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
                    "Batch28 L5d; MCP blocked; Python MT5; MCP history Expert timed close ~+5m."
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
            "review": "Level4 batch28 cycle 20260922T132125Z",
            "doctrine": "Locked reasons unchanged. Old Send-nothing inbox lines not stop tokens.",
            "common_sense": bits,
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(
        DECISION,
        {"ts_utc": now, "cycle_id": "20260922T132125Z", "event": "batch28_complete", "results": results},
    )
    append(LOG, {"event": "batch28_reconciled", "ts_utc": now, "results": results})
    (EXP / "batch28_results.json").write_text(
        json.dumps({"cycle_id": "20260922T132125Z", "results": results, "reconciled_via": "mcp_history"}, indent=2),
        encoding="utf-8",
    )

    md = ATLAS_MD.read_text(encoding="utf-8")
    if "20260922T132125Z" not in md:
        md += (
            "\n## Review 20260922T132630Z — Level 4 batch28 L5d\n\n"
            "Doctrine audit: locked reasons unchanged. Common sense: "
            f"{bits}. "
            "Skipped CHFJPY/EURCHF/GBPCHF after both-way trades. "
            "MCP trade_* blocked; Python MetaTrader5. "
            "H-20260922-001/002/003 stay PROPOSED. H-002 not activated. "
            "20260922T090923Z UNRESOLVED. No new live rule.\n"
        )
        ATLAS_MD.write_text(md, encoding="utf-8")

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Our L5d book: **flat**. Foreign Client CADCHF not touched.",
        "",
        "## Batch28 (cycle 20260922T132125Z) comment L5d",
        "MCP blocked. Python MT5. Magic 771249, 0.01.",
        "SL: majors max(80, stops+spread); JPY/CNH max(250, stops+spread). No SEK.",
        "Skipped CHFJPY/EURCHF/GBPCHF. Expert timed close ~+5m (16:26:25–27 broker).",
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
        "1. Continue until fresh STOP_LEVEL_4_DEMO_AUTONOMY / STOP_FORCED_SIGNAL_LOOP after 09:19 NY.",
        "2. Do not activate H-20260922-002. Do not rescore 20260922T090923Z.",
        "",
    ]
    HANDOFF.write_text("\n".join(lines), encoding="utf-8")
    print("handoff written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
