"""Build L4y from L4x; KEEP mentor_preflight stop check before mt5.initialize.

Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
Stale MENTOR_INBOX "send nothing" still blocks. Forbid L4x pairs.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch22_l4x.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch23_l4y.py")
text = src.read_text(encoding="utf-8")

if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor_preflight missing in source — abort")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    needle = "def main() -> int:\n"
    insert = (
        "def main() -> int:\n"
        "    if block_if_mentor_says_stop(SCRIPT):\n"
        "        return 0\n\n"
    )
    if needle not in text:
        raise SystemExit("main() not found")
    text = text.replace(needle, insert, 1)

# Refuse any rewrite that strips the mentor gate or swaps in token-only gate
if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate not allowed — keep mentor stop")

repls = [
    ("batch22 L4x", "batch23 L4y"),
    ("L4x m771249", "L4y m771249"),
    ("L4x close", "L4y close"),
    ('"L4x"', '"L4y"'),
    ("our_L4x_left", "our_L4y_left"),
    ("Batch22 Level4 L4x", "Batch23 Level4 L4y"),
    ("Level4 batch22", "Level4 batch23"),
    ("batch22_complete", "batch23_complete"),
    ("## Batch22", "## Batch23"),
    ("comment L4x", "comment L4y"),
    ("_picks22.json", "_picks23.json"),
    ("batch22_signals.json", "batch23_signals.json"),
    ("batch22_jobs.json", "batch23_jobs.json"),
    ("batch22_results.json", "batch23_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"AUDUSD\", \"SELL\"),
    (\"EURCHF\", \"SELL\"),
    (\"GBPCHF\", \"SELL\"),
    (\"GBPCAD\", \"BUY\"),
    (\"EURNZD\", \"BUY\"),
}"""
new_forbid = """FORBID = {
    (\"EURUSD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"EURGBP\", \"SELL\"),
    (\"EURJPY\", \"BUY\"),
    (\"EURCAD\", \"BUY\"),
}"""
if old_forbid not in text:
    raise SystemExit("forbid block not found")
text = text.replace(old_forbid, new_forbid)

if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor stop stripped — abort write")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    raise SystemExit("mentor stop call missing — abort write")

out.write_text(text, encoding="utf-8")
print(
    "ok",
    "L4y m771249" in text,
    "block_if_mentor_says_stop" in text,
    "if block_if_mentor_says_stop(SCRIPT)" in text,
    "block_if_fresh_stop_token" not in text,
    '("EURUSD", "SELL")' in text or '(\"EURUSD\", \"SELL\")' in text,
)
