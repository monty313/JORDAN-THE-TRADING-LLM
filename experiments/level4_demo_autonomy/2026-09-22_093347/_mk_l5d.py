"""Build L5d from L5c; KEEP mentor_preflight stop check before mt5.initialize.

Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
Stale MENTOR_INBOX "send nothing" still blocks. Forbid L5a+L5b+L5c pairs;
skip CHFJPY/EURCHF/GBPCHF.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch27_l5c.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch28_l5d.py")
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
    ("batch27 L5c", "batch28 L5d"),
    ("L5c m771249", "L5d m771249"),
    ("L5c close", "L5d close"),
    ('"L5c"', '"L5d"'),
    ("our_L5c_left", "our_L5d_left"),
    ("Batch27 Level4 L5c", "Batch28 Level4 L5d"),
    ("Level4 batch27", "Level4 batch28"),
    ("batch27_complete", "batch28_complete"),
    ("## Batch27", "## Batch28"),
    ("comment L5c", "comment L5d"),
    ("_picks27.json", "_picks28.json"),
    ("batch27_signals.json", "batch28_signals.json"),
    ("batch27_jobs.json", "batch28_jobs.json"),
    ("batch27_results.json", "batch28_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

# Replace whatever FORBID block is present with Mark's L5d list (L5a+L5b+L5c only)
import re

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
}"""

text2, n = re.subn(
    r"FORBID = \{.*?\}",
    new_forbid,
    text,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f"forbid replace failed n={n}")
text = text2

if 'SKIP_SYMBOLS = {"CADCHF", "USDSEK", "CHFJPY"}' in text:
    text = text.replace(
        'SKIP_SYMBOLS = {"CADCHF", "USDSEK", "CHFJPY"}',
        'SKIP_SYMBOLS = {"CADCHF", "USDSEK", "CHFJPY", "EURCHF", "GBPCHF"}',
    )
elif 'SKIP_SYMBOLS = {"CADCHF", "USDSEK"}' in text:
    text = text.replace(
        'SKIP_SYMBOLS = {"CADCHF", "USDSEK"}',
        'SKIP_SYMBOLS = {"CADCHF", "USDSEK", "CHFJPY", "EURCHF", "GBPCHF"}',
    )
else:
    raise SystemExit("skip symbols not found")

text = text.replace('and "L5c" in (p.comment or "")', 'and "L5d" in (p.comment or "")')
text = text.replace('"L5c" in (p.get("comment") or "")', '"L5d" in (p.get("comment") or "")')

if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor stop stripped — abort write")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    raise SystemExit("mentor stop call missing — abort write")
if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate leaked — abort write")
if "L5d m771249" not in text:
    raise SystemExit("L5d comment missing")

out.write_text(text, encoding="utf-8")
print(
    "ok",
    "L5d m771249" in text,
    "block_if_mentor_says_stop" in text,
    "if block_if_mentor_says_stop(SCRIPT)" in text,
    "block_if_fresh_stop_token" not in text,
)
