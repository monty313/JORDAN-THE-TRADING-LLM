"""Rewrite L4u runner from L4t template. Mentor stop gate must stay."""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch18_l4t.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch19_l4u.py")
text = src.read_text(encoding="utf-8")
# Do NOT strip block_if_mentor_says_stop — prior emitter removed it and let L4u open ungated.
GATE_IMPORT = "from mentor_preflight import block_if_mentor_says_stop, log_plan_vs_board\n"
GATE_CALL = "    if block_if_mentor_says_stop(SCRIPT):\n        return 0\n"
if GATE_IMPORT not in text:
    text = text.replace(
        "from mentor_preflight import log_plan_vs_board\n",
        GATE_IMPORT,
    )
if GATE_IMPORT not in text:
    raise SystemExit("mentor gate import missing in source template")
if GATE_CALL not in text:
    raise SystemExit("block_if_mentor_says_stop call missing in source template")
repls = [
    ("batch18 L4t", "batch19 L4u"),
    ("L4t m771249", "L4u m771249"),
    ("L4t close", "L4u close"),
    ('"L4t"', '"L4u"'),
    ("our_L4t_left", "our_L4u_left"),
    ("Batch18 Level4 L4t", "Batch19 Level4 L4u"),
    ("Level4 batch18", "Level4 batch19"),
    ("batch18_complete", "batch19_complete"),
    ("## Batch18", "## Batch19"),
    ("comment L4t", "comment L4u"),
    ("_picks18.json", "_picks19.json"),
    ("batch18_signals.json", "batch19_signals.json"),
    ("batch18_jobs.json", "batch19_jobs.json"),
    ("batch18_results.json", "batch19_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"AUDUSD\", \"SELL\"),
    (\"EURGBP\", \"BUY\"),
    (\"EURAUD\", \"BUY\"),
    (\"EURJPY\", \"BUY\"),
    (\"CADJPY\", \"BUY\"),
}"""
new_forbid = """FORBID = {
    (\"USDCAD\", \"BUY\"),
    (\"EURUSD\", \"SELL\"),
    (\"EURCHF\", \"BUY\"),
    (\"EURCAD\", \"BUY\"),
    (\"GBPCHF\", \"BUY\"),
}"""
if old_forbid not in text:
    raise SystemExit("forbid block not found")
text = text.replace(old_forbid, new_forbid)
if GATE_IMPORT not in text or GATE_CALL not in text:
    raise SystemExit("mentor gate must remain after rewrite")
if "mt5.initialize" in text:
    gate_pos = text.find(GATE_CALL)
    init_pos = text.find("mt5.initialize")
    if gate_pos < 0 or init_pos < 0 or gate_pos > init_pos:
        raise SystemExit("block_if_mentor_says_stop must appear before mt5.initialize")
out.write_text(text, encoding="utf-8")
print(
    "ok",
    "L4u m771249" in text,
    "USDCAD" in text and ('"USDCAD", "BUY"' in text or '("USDCAD", "BUY")' in text),
    "block_if_mentor_says_stop" in text,
)
