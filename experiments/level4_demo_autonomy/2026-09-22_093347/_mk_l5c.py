"""Build L5c from L5b; KEEP mentor_preflight stop check before mt5.initialize.

Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
Stale MENTOR_INBOX "send nothing" still blocks. Forbid L4z+L5a+L5b pairs; skip CHFJPY.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch26_l5b.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch27_l5c.py")
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
    ("batch26 L5b", "batch27 L5c"),
    ("L5b m771249", "L5c m771249"),
    ("L5b close", "L5c close"),
    ('"L5b"', '"L5c"'),
    ("our_L5b_left", "our_L5c_left"),
    ("Batch26 Level4 L5b", "Batch27 Level4 L5c"),
    ("Level4 batch26", "Level4 batch27"),
    ("batch26_complete", "batch27_complete"),
    ("## Batch26", "## Batch27"),
    ("comment L5b", "comment L5c"),
    ("_picks26.json", "_picks27.json"),
    ("batch26_signals.json", "batch27_signals.json"),
    ("batch26_jobs.json", "batch27_jobs.json"),
    ("batch26_results.json", "batch27_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"EURUSD\", \"SELL\"),
    (\"EURGBP\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"CHFJPY\", \"BUY\"),
    (\"GBPJPY\", \"BUY\"),
    (\"EURCHF\", \"SELL\"),
    (\"GBPCHF\", \"SELL\"),
    (\"EURCNH\", \"BUY\"),
    (\"AUDUSD\", \"SELL\"),
    (\"GBPUSD\", \"SELL\"),
}"""
new_forbid = """FORBID = {
    (\"EURUSD\", \"SELL\"),
    (\"EURGBP\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"CHFJPY\", \"BUY\"),
    (\"GBPJPY\", \"BUY\"),
    (\"EURCHF\", \"SELL\"),
    (\"GBPCHF\", \"SELL\"),
    (\"EURCNH\", \"BUY\"),
    (\"AUDUSD\", \"SELL\"),
    (\"GBPUSD\", \"SELL\"),
    (\"NZDUSD\", \"SELL\"),
    (\"CHFJPY\", \"SELL\"),
    (\"EURAUD\", \"BUY\"),
    (\"EURCAD\", \"BUY\"),
    (\"CADJPY\", \"BUY\"),
}"""
if old_forbid not in text:
    raise SystemExit("forbid block not found")
text = text.replace(old_forbid, new_forbid)

old_skip = 'SKIP_SYMBOLS = {"CADCHF", "USDSEK"}'
new_skip = 'SKIP_SYMBOLS = {"CADCHF", "USDSEK", "CHFJPY"}'
if old_skip not in text:
    raise SystemExit("skip symbols not found")
text = text.replace(old_skip, new_skip)

text = text.replace('and "L5b" in (p.comment or "")', 'and "L5c" in (p.comment or "")')
text = text.replace('"L5b" in (p.get("comment") or "")', '"L5c" in (p.get("comment") or "")')

if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor stop stripped — abort write")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    raise SystemExit("mentor stop call missing — abort write")
if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate leaked — abort write")
if "L5c m771249" not in text:
    raise SystemExit("L5c comment missing")
if "CHFJPY" not in text:
    raise SystemExit("CHFJPY skip missing")

out.write_text(text, encoding="utf-8")
print(
    "ok",
    "L5c m771249" in text,
    "block_if_mentor_says_stop" in text,
    "if block_if_mentor_says_stop(SCRIPT)" in text,
    "block_if_fresh_stop_token" not in text,
)
