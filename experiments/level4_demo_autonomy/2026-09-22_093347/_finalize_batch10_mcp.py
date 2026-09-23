"""Reconcile L4j cycle 20260922T110910Z from MCP history exits."""
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
        signal_id="20260922T110910Z_USDCAD_2_S4_1",
        symbol="USDCAD",
        direction="SELL",
        ticket=58569255796,
        entry=1.40350,
        sl=1.40430,
        exit=1.40368,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T110910Z_USDCHF_1_S2_2",
        symbol="USDCHF",
        direction="SELL",
        ticket=58569256301,
        entry=0.81902,
        sl=0.81982,
        exit=0.81937,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T110910Z_GBPCHF_1_S2_3",
        symbol="GBPCHF",
        direction="SELL",
        ticket=58569256457,
        entry=1.09434,
        sl=1.09514,
        exit=1.09468,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T110910Z_EURCHF_1_S2_4",
        symbol="EURCHF",
        direction="SELL",
        ticket=58569256737,
        entry=0.93883,
        sl=0.93963,
        exit=0.93902,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T110910Z_EURCAD_1_S2_5",
        symbol="EURCAD",
        direction="BUY",
        ticket=58569256907,
        entry=1.60876,
        sl=1.60796,
        exit=1.60853,
        point=1e-5,
        close_path="five_minute",
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(path: Path, obj: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, separators=(",", ":")) + "\n")


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
                    "Batch10 L4j; MCP blocked; Python MT5; MCP history Expert timed close ~+5m."
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
        print(r["symbol"], net_pts)

    bits = "; ".join(
        f"{r['symbol']} {r['direction']} {r['close_path']} net={r['net_points']}" for r in results
    )
    append(
        ATLAS,
        {
            "ts_utc": now,
            "review": "Level4 batch10 cycle 20260922T110910Z",
            "doctrine": "Locked reasons unchanged.",
            "common_sense": bits,
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(LOG, {"event": "batch10_reconciled", "ts_utc": now, "results": results})
    (EXP / "batch10_results.json").write_text(
        json.dumps({"cycle_id": "20260922T110910Z", "results": results, "reconciled_via": "mcp_history"}, indent=2),
        encoding="utf-8",
    )

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Our L4j book: **flat**. Foreign Client CADCHF not touched.",
        "",
        "## Batch10 (cycle 20260922T110910Z) comment L4j",
        "MCP blocked. Python MT5. Magic 771249, 0.01.",
        "SL: majors max(80, stops+spread); exotics max(250, stops+spread). No USDSEK.",
        "Expert timed close ~+5m (14:14:09–14:14:12 broker).",
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
