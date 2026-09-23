"""Reconcile L5b cycle 20260922T130625Z from MCP history; append ATLAS md for L5a+L5b."""
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
        signal_id="20260922T130625Z_NZDUSD_2_S3_1",
        symbol="NZDUSD",
        direction="SELL",
        ticket=58571904563,
        entry=0.57260,
        sl=0.57340,
        exit=0.57281,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T130625Z_CHFJPY_1_S1_2",
        symbol="CHFJPY",
        direction="SELL",
        ticket=58571904803,
        entry=191.800,
        sl=192.050,
        exit=191.811,
        point=0.001,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T130625Z_EURAUD_3_S4_3",
        symbol="EURAUD",
        direction="BUY",
        ticket=58571904940,
        entry=1.61162,
        sl=1.61082,
        exit=1.61166,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T130625Z_EURCAD_1_S3_4",
        symbol="EURCAD",
        direction="BUY",
        ticket=58571905233,
        entry=1.60944,
        sl=1.60865,
        exit=1.60974,
        point=1e-5,
        close_path="five_minute",
    ),
    dict(
        signal_id="20260922T130625Z_CADJPY_2_S1_5",
        symbol="CADJPY",
        direction="BUY",
        ticket=58571905536,
        entry=111.954,
        sl=111.704,
        exit=111.928,
        point=0.001,
        close_path="five_minute",
    ),
]

L5A_SUMMARY = (
    "EURCHF SELL 58571744778 +10; GBPCHF SELL 58571745050 -14; "
    "EURCNH BUY 58571745192 -47; AUDUSD SELL 58571745330 -11; GBPUSD SELL 58571745465 -48"
)


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
                    "Batch26 L5b; MCP blocked; Python MT5; MCP history Expert timed close ~+5m."
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
            "review": "Level4 batch26 cycle 20260922T130625Z",
            "doctrine": "Locked reasons unchanged. Old Send-nothing inbox lines not stop tokens.",
            "common_sense": bits,
            "hypotheses": "H-20260922-001/002/003 PROPOSED; H-002 not activated. 20260922T090923Z UNRESOLVED.",
        },
    )
    append(
        DECISION,
        {
            "ts_utc": now,
            "cycle_id": "20260922T130625Z",
            "event": "batch26_complete",
            "results": results,
        },
    )
    append(LOG, {"event": "batch26_reconciled", "ts_utc": now, "results": results})
    (EXP / "batch26_results.json").write_text(
        json.dumps({"cycle_id": "20260922T130625Z", "results": results, "reconciled_via": "mcp_history"}, indent=2),
        encoding="utf-8",
    )

    md = ATLAS_MD.read_text(encoding="utf-8")
    if "20260922T125941Z" not in md:
        md += (
            "\n\n## Review 20260922T130525Z — Level 4 batch25 L5a\n\n"
            "Doctrine audit: locked reasons unchanged. Common sense: "
            f"{L5A_SUMMARY}. "
            "One of five green. MCP trade_* blocked; Python MetaTrader5. "
            "H-20260922-001/002/003 stay PROPOSED. H-002 not activated. "
            "20260922T090923Z UNRESOLVED. No new live rule.\n"
        )
    if "20260922T130625Z" not in md:
        md += (
            "\n## Review 20260922T131130Z — Level 4 batch26 L5b\n\n"
            "Doctrine audit: locked reasons unchanged. Common sense: "
            f"{bits}. "
            "MCP trade_* blocked; Python MetaTrader5. "
            "H-20260922-001/002/003 stay PROPOSED. H-002 not activated. "
            "20260922T090923Z UNRESOLVED. No new live rule.\n"
        )
    ATLAS_MD.write_text(md, encoding="utf-8")

    lines = [
        f"# Level 4 demo handoff — {now}",
        "",
        "Account: MetaQuotes-Demo. Our L5a+L5b book: **flat**. Foreign Client CADCHF not touched.",
        "",
        "## Batch25 (cycle 20260922T125941Z) comment L5a — already scored",
        "| Symbol | Dir | Ticket | Entry | Stop | Exit | Net pts | Close path | Flat |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
        "| EURCHF | SELL | 58571744778 | 0.93972 | 0.94051 | 0.93962 | 10.0 | five_minute | yes |",
        "| GBPCHF | SELL | 58571745050 | 1.0955 | 1.0963 | 1.09564 | -14.0 | five_minute | yes |",
        "| EURCNH | BUY | 58571745192 | 7.67535 | 7.67293 | 7.67488 | -47.0 | five_minute | yes |",
        "| AUDUSD | SELL | 58571745330 | 0.71074 | 0.71154 | 0.71085 | -11.0 | five_minute | yes |",
        "| GBPUSD | SELL | 58571745465 | 1.33555 | 1.33634 | 1.33603 | -48.0 | five_minute | yes |",
        "",
        "## Batch26 (cycle 20260922T130625Z) comment L5b",
        "MCP blocked. Python MT5. Magic 771249, 0.01.",
        "SL: majors max(80, stops+spread); JPY/CNH max(250, stops+spread). No SEK.",
        "Expert timed close ~+5m (16:11:25–27 broker).",
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
        "1. Continue until fresh STOP_LEVEL_4_DEMO_AUTONOMY / STOP_FORCED_SIGNAL_LOOP after 08:58 NY.",
        "2. Do not activate H-20260922-002. Do not rescore 20260922T090923Z.",
        "",
    ]
    HANDOFF.write_text("\n".join(lines), encoding="utf-8")
    print("handoff written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
