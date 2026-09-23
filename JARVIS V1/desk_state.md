# JARVIS desk state

| Field | Value |
|---|---|
| Mode | Eyes stay log-only. New orders are SAFE_HOLD. The assistant loop may close magic 771249 for momentum_dying or will_not_rejoin. See `STANDING_ORDERS.md` amendment 21:36 and `assistant/README.md`. |
| Account | demo (unsuffixed Market Watch; no `.sim` required) |
| Doctrine | `doctrine/007_JARVIS_Momentum_Conservation_Trading_Mentor_Baseline.md` (read-only, SHA-256 `ae2d9b8e1f32d52c2557b562969678764e7e1f702f523a2f1a97ab4da8a958d0`). Same bytes may also sit at `C:\Users\C2K\Desktop\Strategies - Copy\007_JARVIS_Momentum_Conservation_Trading_Mentor_Baseline.md` on the original machine. |
| Seat memory | `JARVIS V1/STANDING_ORDERS.md` (read before the board). Lessons: `JARVIS V1/LEARNING_LOG.md`. |
| Today target | Beat closed Client P/L +38535 on demo. Last named deadline: 00:36 America/New_York on 2026-09-23. Do not invent a new one. Score is closed P/L on magic 771249 opened after 12:36. Floating does not count. |
| risk_floor | UNSET. This is the loss boundary, not a name count. The 13:24 ticket list is not a risk floor. Re-read MT5 before any order. |
| liquid_name_quota | 10 liquid names to monitor. A short count does not authorize an anonymous order. |
| Execution authority | Disabled. New orders are SAFE_HOLD. Fable harness file is missing. `risk_floor` is UNSET. Rung is OBSERVATION_ONLY. Amendment 21:54 names 10.0 lots only for a future precious-metal sell (XAGUSD, XAUUSD, XAGEUR) and does not lift SAFE_HOLD. FX 10-lot spray is FORBIDDEN. 100 lots are FORBIDDEN. `anonymous_keep10_fallback` is FORBIDDEN. `book_fill_to_50` is FORBIDDEN. |
| Last agreement | |
| Board | `MQL5/Files/jarvis/board.csv` |
| Tape | `MQL5/Files/jarvis/tape/YYYY-MM-DD.csv` |
| Notify state | `MQL5/Files/jarvis/notify_state.csv` |
| EA source | `JARVIS V1/src/JarvisEyes.mq5` (+ `JarvisEyes.mqh`) |
| Compiled | `MQL5/Experts/JarvisEyes/JarvisEyes.ex5` |
| Schema | `JARVIS V1/SCHEMA.md` |
| Journal | `JARVIS V1/JOURNAL.md` |
| Attach note | New EX5 names may need Navigator refresh (F5) before MCP `chart_add_expert` sees them; first live attach used a known-name host path then restored that host binary. |

Notes:

- The EA never overwrites this file.
- Mentoring stays in Cursor. Phone push is one-way `SendNotification` only.
- RollTide / `rolltide.csv` is legacy board context; doctrine answers cite JarvisEyes `board.csv`.

## State-change ledger

| When | Change |
|---|---|
| 2026-09-22 21:19 ET | Seat memory file created. Lot 1.0. Wide-spread quota fills withdrawn. |
| 2026-09-22 21:25 ET | Continuity bootstrap applied. `risk_floor` left UNSET. `liquid_name_quota` set to 10 as a monitor count. Anonymous keep-10 fills forbidden. New orders require a persisted thesis. Sets 3 and 4 are context. Fable harness file is missing, so execution stays SAFE_HOLD. |
| 2026-09-22 21:27 ET | Folder map written. Live tapes live under `research/`. The 10-lot manage script moved to `halted/`. Experiment batches left in place because their scripts use absolute paths. |
| 2026-09-22 22:03 ET | Learning map corrected. Eyes stay log-only. Assistant loop owns the two exit reasons. `assistant/reader_repl.py` groups tapes by hand and does not promote a split before 20 closes in each reason. |
| 2026-09-22 21:35 ET | Learning phase. Thesis chain is mandatory before any order. Five-minute wake records an observation and does not send. A short name count is not an entry. |
| 2026-09-22 21:38 ET | Charter. Current rung OBSERVATION_ONLY. New entries wait on the execution ladder. 21:36 closes remain the management rule. risk_floor still UNSET. |
| 2026-09-22 21:54 ET | Meter rebuilt. Closed score +298.86 on 183 tickets, not beaten. Paid pattern is the metal sell. Lot tag 10.0 does not lift SAFE_HOLD. |
| 2026-09-22 22:20 ET | GitHub seal. Doctrine copied into `doctrine/` at the same hash. Terminal read: 20 magic 771249 positions at 10.0 lots, comment `J 10lot`, float about +4192.77 of which gold sell 58581979625 was about +4360. That float is not the score. Loop `AGENT_LOOP_TICK_jarvis_20x10` stopped. Next chat reads `FOR_THE_NEXT_LLM.md` and `HOW_JARVIS_IS_DOING.md`. |
