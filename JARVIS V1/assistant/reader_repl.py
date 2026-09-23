"""Sandboxed log reader. Groups passes and exits. Does not trade.

Does not import MetaTrader5. Does not send, modify, or close.
The exit loop in mentor_assistant.py is not started or stopped here.
"""

from __future__ import annotations

import json
from pathlib import Path

ASSISTANT_DIR = Path(__file__).resolve().parent
ROOT = ASSISTANT_DIR.parent
PASSES_PATH = ASSISTANT_DIR / "passes.jsonl"
EXITS_PATH = ASSISTANT_DIR / "exits.jsonl"
HYPOTHESIS_PATH = ASSISTANT_DIR / "reader_hypothesis.md"
JOURNAL_PATH = ROOT / "JOURNAL.md"
MIN_SAMPLE = 20
JOURNAL_MARKER = "reader is a log groupby, not a fire rule"

# The groupby runs with only these names. No import, no open, no order_send.
_SAFE_BUILTINS = {
    "len": len,
    "sum": sum,
    "float": float,
    "int": int,
    "str": str,
    "list": list,
    "dict": dict,
    "sorted": sorted,
    "round": round,
    "min": min,
    "max": max,
    "abs": abs,
}

_GROUP_SOURCE = """
pass_counts = {"PROFITABLE": 0, "NOT_PROFITABLE": 0, "UNRESOLVED": 0, "OTHER": 0}
label_counts = {}
alignment_counts = {}
for row in passes:
    status = str(row.get("outcome_status") or "")
    if status in pass_counts:
        pass_counts[status] = pass_counts[status] + 1
    else:
        pass_counts["OTHER"] = pass_counts["OTHER"] + 1
    label = str(row.get("label") or "none")
    label_counts[label] = label_counts.get(label, 0) + 1
    alignment = str(row.get("alignment_side") or "none")
    alignment_counts[alignment] = alignment_counts.get(alignment, 0) + 1

exit_groups = {}
for row in exits:
    if row.get("ok") is not True:
        continue
    reason = str(row.get("reason") or "unknown")
    bucket = exit_groups.get(reason)
    if bucket is None:
        bucket = {"count": 0, "sum_profit": 0.0, "sides": {}}
        exit_groups[reason] = bucket
    profit = float(row.get("profit") or 0)
    bucket["count"] = bucket["count"] + 1
    bucket["sum_profit"] = bucket["sum_profit"] + profit
    side = str(row.get("side") or "none")
    bucket["sides"][side] = bucket["sides"].get(side, 0) + 1

for reason, bucket in exit_groups.items():
    count = bucket["count"]
    bucket["mean_profit"] = (bucket["sum_profit"] / count) if count else 0.0
"""


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def group_in_sandbox(passes: list[dict], exits: list[dict]) -> dict:
    sandbox = {
        "__builtins__": _SAFE_BUILTINS,
        "passes": passes,
        "exits": exits,
    }
    exec(_GROUP_SOURCE, sandbox, sandbox)  # noqa: S102 — fixed source, no imports
    return {
        "pass_counts": sandbox["pass_counts"],
        "label_counts": sandbox["label_counts"],
        "alignment_counts": sandbox["alignment_counts"],
        "exit_groups": sandbox["exit_groups"],
    }


def hypothesis_sentence(exit_groups: dict) -> tuple[str, str, bool]:
    dying = exit_groups.get("momentum_dying")
    rejoin = exit_groups.get("will_not_rejoin")
    dying_n = 0 if dying is None else int(dying["count"])
    rejoin_n = 0 if rejoin is None else int(rejoin["count"])
    falsifier = (
        "After both reasons have 20 closed tickets, the hypothesis fails if the "
        "reason with the higher mean profit is no longer higher on the next 20 "
        "closes of that same reason."
    )
    if dying_n < MIN_SAMPLE or rejoin_n < MIN_SAMPLE:
        text = (
            f"Insufficient sample. momentum_dying has {dying_n}/{MIN_SAMPLE} closed "
            f"tickets and will_not_rejoin has {rejoin_n}/{MIN_SAMPLE}. "
            "The split is not promoted."
        )
        return text, falsifier, False
    dying_mean = float(dying["mean_profit"])
    rejoin_mean = float(rejoin["mean_profit"])
    if dying_mean >= rejoin_mean:
        higher = "momentum_dying"
        lower = "will_not_rejoin"
        high_mean = dying_mean
        low_mean = rejoin_mean
    else:
        higher = "will_not_rejoin"
        lower = "momentum_dying"
        high_mean = rejoin_mean
        low_mean = dying_mean
    text = (
        f"Hypothesis, still a score to keep, not a new exit: {higher} has the higher "
        f"mean profit ({high_mean:.2f}) versus {lower} ({low_mean:.2f}) on closed "
        f"magic 771249 tickets. Keep scoring the split. Minimum sample is "
        f"{MIN_SAMPLE} in each reason, and both groups are already at that count."
    )
    return text, falsifier, True


def render(grouped: dict) -> str:
    passes = grouped["pass_counts"]
    labels = grouped["label_counts"]
    alignments = grouped["alignment_counts"]
    exits = grouped["exit_groups"]
    claim, falsifier, promoted = hypothesis_sentence(exits)
    lines = [
        "# Reader hypothesis",
        "",
        "This note does not change S1–S4 act, the hold checks, or the exit.",
        "The reader does not send an order. New orders stay SAFE_HOLD.",
        "",
        "## Scored passes",
        "",
        f"- PROFITABLE: {passes.get('PROFITABLE', 0)}",
        f"- NOT_PROFITABLE: {passes.get('NOT_PROFITABLE', 0)}",
        f"- UNRESOLVED: {passes.get('UNRESOLVED', 0)}",
        f"- OTHER: {passes.get('OTHER', 0)}",
        "",
        "## Pass labels",
        "",
    ]
    for key in sorted(labels):
        lines.append(f"- {key}: {labels[key]}")
    lines.extend(["", "## Alignment side", ""])
    for key in sorted(alignments):
        lines.append(f"- {key}: {alignments[key]}")
    lines.extend(["", "## Closed exits (ok only)", ""])
    if not exits:
        lines.append("- No successful exits on the tape.")
    else:
        for reason in sorted(exits):
            bucket = exits[reason]
            sides = ", ".join(
                f"{side}={bucket['sides'][side]}" for side in sorted(bucket["sides"])
            )
            lines.append(
                f"- {reason}: count={bucket['count']} "
                f"sum_profit={bucket['sum_profit']:.2f} "
                f"mean_profit={bucket['mean_profit']:.2f} sides ({sides})"
            )
    lines.extend(
        [
            "",
            "## One hypothesis",
            "",
            claim,
            "",
            f"Promoted: {'yes' if promoted else 'no'}.",
            "",
            "## Falsifier",
            "",
            falsifier,
            "",
        ]
    )
    return "\n".join(lines)


def ensure_journal_row() -> None:
    row = (
        "| 2026-09-22 | Sandbox tape reader. `JARVIS V1/assistant/reader_repl.py` "
        "groups `passes.jsonl` and `exits.jsonl` and rewrites "
        "`reader_hypothesis.md`. The reader is a log groupby, not a fire rule "
        "and not an exit rule. It does not import MetaTrader5 and does not send. "
        "The dying-momentum hold checks stay. | Proposed |\n"
    )
    if JOURNAL_PATH.exists():
        text = JOURNAL_PATH.read_text(encoding="utf-8")
        if JOURNAL_MARKER in text:
            return
    else:
        text = (
            "# JARVIS journal\n\n"
            "Proposed doctrine changes only. Mark accepts or rejects. "
            "Do not edit `007_*.md` from the agent.\n\n"
            "| Date | Proposal | Status |\n|---|---|---|\n"
        )
    if "\n---\n" in text:
        text = text.replace("\n---\n", "\n" + row + "\n---\n", 1)
    else:
        text = text.rstrip() + "\n" + row
    JOURNAL_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    grouped = group_in_sandbox(load_jsonl(PASSES_PATH), load_jsonl(EXITS_PATH))
    HYPOTHESIS_PATH.write_text(render(grouped), encoding="utf-8")
    ensure_journal_row()
    print(
        json.dumps(
            {
                "hypothesis": str(HYPOTHESIS_PATH),
                "exit_reasons": sorted(grouped["exit_groups"]),
                "promoted": "Insufficient sample" not in HYPOTHESIS_PATH.read_text(encoding="utf-8"),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
