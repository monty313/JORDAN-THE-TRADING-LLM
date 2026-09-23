"""Build L5e from L5d; KEEP mentor_preflight stop check before mt5.initialize.

Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
Stale MENTOR_INBOX "send nothing" still blocks. Forbid L5a+L5b+L5c+L5d pairs;
skip CHFJPY/EURCHF/GBPCHF.
"""
from __future__ import annotations

import re
from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch28_l5d.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch29_l5e.py")
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
    ("batch28 L5d", "batch29 L5e"),
    ("L5d m771249", "L5e m771249"),
    ("L5d close", "L5e close"),
    ('"L5d"', '"L5e"'),
    ("our_L5d_left", "our_L5e_left"),
    ("Batch28 Level4 L5d", "Batch29 Level4 L5e"),
    ("Level4 batch28", "Level4 batch29"),
    ("batch28_complete", "batch29_complete"),
    ("## Batch28", "## Batch29"),
    ("comment L5d", "comment L5e"),
    ("_picks28.json", "_picks29.json"),
    ("batch28_signals.json", "batch29_signals.json"),
    ("batch28_jobs.json", "batch29_jobs.json"),
    ("batch28_results.json", "batch29_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

new_forbid = """FORBID = {
    # L5a
    (\"EURCHF\", \"SELL\"),
    (\"GBPCHF\", \"SELL\"),
    (\"EURCNH\", \"BUY\"),
    (\"AUDUSD\", \"SELL\"),
    (\"GBPUSD\", \"SELL\"),
    # L5b
    (\"NZDUSD\", \"SELL\"),
    (\"CHFJPY\", \"SELL\"),
    (\"EURAUD\", \"BUY\"),
    (\"EURCAD\", \"BUY\"),
    (\"CADJPY\", \"BUY\"),
    # L5c
    (\"USDCHF\", \"BUY\"),
    (\"EURCHF\", \"BUY\"),
    (\"GBPCAD\", \"BUY\"),
    (\"EURNZD\", \"BUY\"),
    (\"GBPCHF\", \"BUY\"),
    # L5d
    (\"USDCAD\", \"BUY\"),
    (\"GBPAUD\", \"BUY\"),
    (\"EURUSD\", \"SELL\"),
    (\"USDJPY\", \"BUY\"),
    (\"AUDJPY\", \"BUY\"),
}"""

text2, n = re.subn(r"FORBID = \{.*?\}", new_forbid, text, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f"forbid replace failed n={n}")
text = text2

skip_targets = [
    'SKIP_SYMBOLS = {"CADCHF", "USDSEK", "CHFJPY", "EURCHF", "GBPCHF"}',
    'SKIP_SYMBOLS = {"CADCHF", "USDSEK", "CHFJPY"}',
    'SKIP_SYMBOLS = {"CADCHF", "USDSEK"}',
]
new_skip = 'SKIP_SYMBOLS = {"CADCHF", "USDSEK", "CHFJPY", "EURCHF", "GBPCHF"}'
replaced = False
for old in skip_targets:
    if old in text:
        text = text.replace(old, new_skip)
        replaced = True
        break
if not replaced:
    raise SystemExit("skip symbols not found")

text = text.replace('and "L5d" in (p.comment or "")', 'and "L5e" in (p.comment or "")')
text = text.replace('"L5d" in (p.get("comment") or "")', '"L5e" in (p.get("comment") or "")')

if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor stop stripped — abort write")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    raise SystemExit("mentor stop call missing — abort write")
if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate leaked — abort write")
if "L5e m771249" not in text:
    raise SystemExit("L5e comment missing")

out.write_text(text, encoding="utf-8")
print(
    "ok",
    "L5e m771249" in text,
    "block_if_mentor_says_stop" in text,
    "if block_if_mentor_says_stop(SCRIPT)" in text,
    "block_if_fresh_stop_token" not in text,
)
