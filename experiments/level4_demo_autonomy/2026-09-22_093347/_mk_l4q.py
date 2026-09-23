"""Rewrite L4q runner from L4p template. Mentor stop gate must stay."""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch14_l4p.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch15_l4q.py")
text = src.read_text(encoding="utf-8")
# Do NOT strip block_if_mentor_says_stop — previous emitters did; that let L4q open ungated.
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
    ("batch14 L4p", "batch15 L4q"),
    ("L4p m771249", "L4q m771249"),
    ("L4p close", "L4q close"),
    ('"L4p"', '"L4q"'),
    ("our_L4p_left", "our_L4q_left"),
    ("Batch14 Level4 L4p", "Batch15 Level4 L4q"),
    ("Level4 batch14", "Level4 batch15"),
    ("batch14_complete", "batch15_complete"),
    ("## Batch14", "## Batch15"),
    ("comment L4p", "comment L4q"),
    ("_picks14.json", "_picks15.json"),
    ("batch14_signals.json", "batch15_signals.json"),
    ("batch14_jobs.json", "batch15_jobs.json"),
    ("batch14_results.json", "batch15_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"AUDUSD\", \"SELL\"),
    (\"EURGBP\", \"BUY\"),
    (\"USDJPY\", \"SELL\"),
    (\"GBPCAD\", \"BUY\"),
    (\"EURCNH\", \"SELL\"),
}"""
new_forbid = """FORBID = {
    (\"EURUSD\", \"SELL\"),
    (\"GBPUSD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"GBPCHF\", \"SELL\"),
    (\"GBPJPY\", \"SELL\"),
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
    "L4q m771249" in text,
    "EURUSD" in text and ('"EURUSD", "SELL"' in text or "(\"EURUSD\", \"SELL\")" in text),
    "block_if_mentor_says_stop" in text,
)
