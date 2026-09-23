"""Rewrite L4t runner from L4s template. Mentor stop gate must stay."""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch17_l4s.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch18_l4t.py")
text = src.read_text(encoding="utf-8")
# Do NOT strip block_if_mentor_says_stop — prior emitter removed it and let L4t open ungated.
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
    ("batch17 L4s", "batch18 L4t"),
    ("L4s m771249", "L4t m771249"),
    ("L4s close", "L4t close"),
    ('"L4s"', '"L4t"'),
    ("our_L4s_left", "our_L4t_left"),
    ("Batch17 Level4 L4s", "Batch18 Level4 L4t"),
    ("Level4 batch17", "Level4 batch18"),
    ("batch17_complete", "batch18_complete"),
    ("## Batch17", "## Batch18"),
    ("comment L4s", "comment L4t"),
    ("_picks17.json", "_picks18.json"),
    ("batch17_signals.json", "batch18_signals.json"),
    ("batch17_jobs.json", "batch18_jobs.json"),
    ("batch17_results.json", "batch18_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"EURUSD\", \"SELL\"),
    (\"GBPUSD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"GBPCHF\", \"SELL\"),
    (\"EURNZD\", \"BUY\"),
}"""
new_forbid = """FORBID = {
    (\"AUDUSD\", \"SELL\"),
    (\"EURGBP\", \"BUY\"),
    (\"EURAUD\", \"BUY\"),
    (\"EURJPY\", \"BUY\"),
    (\"CADJPY\", \"BUY\"),
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
    "L4t m771249" in text,
    "AUDUSD" in text and ('"AUDUSD", "SELL"' in text or "(\"AUDUSD\", \"SELL\")" in text),
    "block_if_mentor_says_stop" in text,
)
