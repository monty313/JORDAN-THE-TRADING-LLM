"""Build L5b from L5a; KEEP mentor_preflight stop check before mt5.initialize.

Do not replace block_if_mentor_says_stop with a fresh-token-only gate.
Stale MENTOR_INBOX "send nothing" still blocks. Forbid L4z + L5a pairs.
"""
from __future__ import annotations

from pathlib import Path

src = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch25_l5a.py")
out = Path(r"C:\Users\C2K\Desktop\MT5 to agent\experiments\level4_demo_autonomy\2026-09-22_093347\run_batch26_l5b.py")
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
    ("batch25 L5a", "batch26 L5b"),
    ("L5a m771249", "L5b m771249"),
    ("L5a close", "L5b close"),
    ('"L5a"', '"L5b"'),
    ("our_L5a_left", "our_L5b_left"),
    ("Batch25 Level4 L5a", "Batch26 Level4 L5b"),
    ("Level4 batch25", "Level4 batch26"),
    ("batch25_complete", "batch26_complete"),
    ("## Batch25", "## Batch26"),
    ("comment L5a", "comment L5b"),
    ("_picks25.json", "_picks26.json"),
    ("batch25_signals.json", "batch26_signals.json"),
    ("batch25_jobs.json", "batch26_jobs.json"),
    ("batch25_results.json", "batch26_results.json"),
]
for a, b in repls:
    text = text.replace(a, b)

old_forbid = """FORBID = {
    (\"EURUSD\", \"SELL\"),
    (\"EURGBP\", \"SELL\"),
    (\"USDCAD\", \"BUY\"),
    (\"CHFJPY\", \"BUY\"),
    (\"GBPJPY\", \"BUY\"),
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
}"""
if old_forbid not in text:
    raise SystemExit("forbid block not found")
text = text.replace(old_forbid, new_forbid)

text = text.replace('and "L5a" in (p.comment or "")', 'and "L5b" in (p.comment or "")')
text = text.replace('"L5a" in (p.get("comment") or "")', '"L5b" in (p.get("comment") or "")')

if "block_if_mentor_says_stop" not in text:
    raise SystemExit("mentor stop stripped — abort write")
if "if block_if_mentor_says_stop(SCRIPT):" not in text:
    raise SystemExit("mentor stop call missing — abort write")
if "block_if_fresh_stop_token" in text or "stop_token_gate" in text:
    raise SystemExit("token-only gate leaked — abort write")

out.write_text(text, encoding="utf-8")
print(
    "ok",
    "L5b m771249" in text,
    "block_if_mentor_says_stop" in text,
    "if block_if_mentor_says_stop(SCRIPT)" in text,
    "block_if_fresh_stop_token" not in text,
    '("EURCNH", "BUY")' in text or '(\"EURCNH\", \"BUY\")' in text,
)
