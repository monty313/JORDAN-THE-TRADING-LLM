"""Rewrite L4v runner from L4u; KEEP mentor_preflight stop check."""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch19_l4u.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch20_l4v.py")
text = src.read_text(encoding="utf-8")

# Ensure mentor gate is present (do not strip)
if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor_preflight missing in source — abort")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    # restore call after main() starts if somehow missing
    needle = "def main() -> int:\n"
    insert = (
        "def main() -> int:\n"
        "    if block_if_mentor_says_stop(SCRIPT):\n"
        "        return 0\n\n"
    )
    if needle not in text:
        raise SystemExit("main() not found")
    text = text.replace(needle, insert, 1)

repls = [
    ("batch19 L4u", "batch20 L4v"),
    ("L4u m771249", "L4v m771249"),
    ("L4u close", "L4v close"),
    ('"L4u"', '"L4v"'),
    ("our_L4u_left", "our_L4v_left"),
    ("Batch19 Level4 L4u", "Batch20 Level4 L4v"),
    ("Level4 batch19", "Level4 batch20"),
    ("batch19_complete", "batch20_complete"),
    ("## Batch19", "## Batch20"),
    ("comment L4u", "comment L4v"),
    ("_picks19.json", "_picks20.json"),
    ("batch19_signals.json", "batch20_signals.json"),
    ("batch19_jobs.json", "batch20_jobs.json"),
    ("batch19_results.json", "batch20_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"USDCAD\", \"BUY\"),
    (\"EURUSD\", \"SELL\"),
    (\"EURCHF\", \"BUY\"),
    (\"EURCAD\", \"BUY\"),
    (\"GBPCHF\", \"BUY\"),
}"""
# L4u currently forbids L4t pairs; replace with L4u pairs for this pass
old_forbid = """FORBID = {
    (\"AUDUSD\", \"SELL\"),
    (\"EURGBP\", \"BUY\"),
    (\"USDCHF\", \"SELL\"),
    (\"EURCHF\", \"SELL\"),
    (\"GBPCHF\", \"SELL\"),
}"""
# Wait - check what's actually in L4u source
# L4u forbids L4t: USDCAD BUY, EURUSD SELL, EURCHF BUY, EURCAD BUY, GBPCHF BUY
old_forbid = """FORBID = {
    (\"USDCAD\", \"BUY\"),
    (\"EURUSD\", \"SELL\"),
    (\"EURCHF\", \"BUY\"),
    (\"EURCAD\", \"BUY\"),
    (\"GBPCHF\", \"BUY\"),
}"""
new_forbid = """FORBID = {
    (\"AUDUSD\", \"SELL\"),
    (\"EURGBP\", \"BUY\"),
    (\"USDCHF\", \"SELL\"),
    (\"EURCHF\", \"SELL\"),
    (\"GBPCHF\", \"SELL\"),
}"""
if old_forbid not in text:
    raise SystemExit("forbid block not found")
text = text.replace(old_forbid, new_forbid)
out.write_text(text, encoding="utf-8")
print(
    "ok",
    "L4v m771249" in text,
    "block_if_mentor_says_stop" in text,
    'if block_if_mentor_says_stop(SCRIPT)' in text,
)
