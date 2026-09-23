"""Build L4x from current L4w file; KEEP mentor_preflight stop check before mt5.initialize.

Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
Stale MENTOR_INBOX "send nothing" still blocks. Forbid L4w pairs.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch21_l4w.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch22_l4x.py")
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
    ("batch21 L4w", "batch22 L4x"),
    ("L4w m771249", "L4x m771249"),
    ("L4w close", "L4x close"),
    ('"L4w"', '"L4x"'),
    ("our_L4w_left", "our_L4x_left"),
    ("Batch21 Level4 L4w", "Batch22 Level4 L4x"),
    ("Level4 batch21", "Level4 batch22"),
    ("batch21_complete", "batch22_complete"),
    ("## Batch21", "## Batch22"),
    ("comment L4w", "comment L4x"),
    ("_picks21.json", "_picks22.json"),
    ("batch21_signals.json", "batch22_signals.json"),
    ("batch21_jobs.json", "batch22_jobs.json"),
    ("batch21_results.json", "batch22_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"EURUSD\", \"SELL\"),
    (\"GBPUSD\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"EURAUD\", \"BUY\"),
    (\"EURCAD\", \"BUY\"),
}"""
new_forbid = """FORBID = {
    (\"AUDUSD\", \"SELL\"),
    (\"EURCHF\", \"SELL\"),
    (\"GBPCHF\", \"SELL\"),
    (\"GBPCAD\", \"BUY\"),
    (\"EURNZD\", \"BUY\"),
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
    "L4x m771249" in text,
    "block_if_mentor_says_stop" in text,
    "if block_if_mentor_says_stop(SCRIPT)" in text,
    "block_if_fresh_stop_token" not in text,
    '("AUDUSD", "SELL")' in text or '(\"AUDUSD\", \"SELL\")' in text,
)
