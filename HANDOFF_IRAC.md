# JORDAN-THE-TRADING-LLM — IRAC handoff (2026-10-17)

## Issue
'Jarvis' LLM trading desk in Cursor connected to MT5 via native MCP, with standing orders, mentorship gate, RollTide screener EA.
Central question: Can the LLM desk trade profitably under the doctrine on the OANDA prop $10k verification? Unknown.

## Rule
README/WORKING_JARVIS.md: main frozen, branch off tag; JARVIS V1/STANDING_ORDERS.md wins on conflict; mentorship/JARVIS_MENTOR.md required before a market act. Doctrine: scalping-only; 5m CCI 30/100 burst entry; 1R=0.25% equity; max 4 concurrent; daily floor -3R; pyramid winners OK, add-to-losers banned.

## Application
3 commits; 137e03e 2026-09-23 freeze. HANDOFF.md (2026-09-21) records MT5 MCP connected, account OANDA-Prop Trader $10k Verification; rolltide.csv not updating live ('dump is not a live board'). JARVIS V1/HOW_JARVIS_IS_DOING.md sealed 2026-09-22. Open PRs #1 'Strategy part 2', #2 Cloud Agent env. Last push 2026-09-25.

## Conclusion
Status: in progress (frozen at tag jarvis-working-2026-09-23). Blockers: screener CSV feed not live; PRs #1/#2 unmerged; no verified P&L record vs doctrine.
Next: 1) Review/merge PR #1 on a branch off the tag. 2) Fix RollTide live feed. 3) Log closed-trade R vs -3R floor.
