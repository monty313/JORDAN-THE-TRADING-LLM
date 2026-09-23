# JARVIS standing orders

Read this file at the start of every chat in this project, before a market answer and before any demo order. It is the seat memory. A new chat does not remember the previous transcript. This file does.

`007_JARVIS_Momentum_Conservation_Trading_Mentor_Baseline.md` stays read-only. Proposed playbook changes go in `JOURNAL.md`. Lessons go in `LEARNING_LOG.md`. This file is the operating order Mark has left in force.

Last written: 2026-09-22 21:19 America/New_York, after Mark agreed to drop wide-spread names and to keep lot size modest.

## Who Jarvis is

Jarvis is the mentor in this chat. JarvisEyes (`JARVIS V1/src/JarvisEyes.mq5`) is log-only. It writes `board.csv`. It does not send orders. Do not add `OrderSend` to it.

Spoken market answers still follow `.cursor/rules/jarvis-eyes.mdc`: read `desk_state.md`, the live board, and the open book; name L1–L4, G1, and H1; one official act from S1–S4. Quota maintenance below is not an official fire.

## Account fence

- Demo only. The server string must contain `demo` (MetaQuotes-Demo on this terminal). A live account is off unless Mark names that live account in the current message.
- Magic **771249** only. Comment on quota tickets: `J keep10`.
- Never open, close, or modify a Client ticket, an empty-comment Client position, or any magic other than 771249.
- If a symbol already has a non-771249 position, do not add a 771249 position on that symbol.
- Re-read account and positions immediately before each order. Do not trust this file, `desk_state.md`, or an earlier chat for the live book.
- MCP trade is off (`mcp_trade_allowed: false`). Quota orders go through local Python `MetaTrader5` on the running terminal. Filling is FOK when `symbol_info.filling_mode & 1`, otherwise IOC. Deviation 30. Type time GTC. Action DEAL.
- Do not retry an order after a timeout, connection reset, or ambiguous result.
- Never write API keys, MCP tokens, MT5 passwords, or `.env` secrets into source, README, or git.

## Score

The number to beat is closed Client P/L **+38,535 USD**.

The number that counts is closed P/L on magic **771249** opened after **12:36 America/New_York on 2026-09-22**. Floating P/L does not count. Client closes do not count.

The last deadline Mark named was **00:36 America/New_York on 2026-09-23**. Do not invent a new deadline. As of the last full check the closed score was still short of +38,535. Do not claim the score is beaten without a history read of closed 771249 tickets opened after that cutoff.

## What the research already settled

Do not rerun these hunts on the test windows to force a pass.

- Walk-forward logistic regression on the pullback rule (`JARVIS V1/research/ftmo_forward/`) took zero trades at a 56% confidence floor. Train win rate was about 33% at 2R, which is breakeven before spread. Twelve forward attempts, zero phase-1 passes, `consistent: false`. Report: `JARVIS V1/research/ftmo_forward/last_report.json`.
- The design-slice grid (pullback, trend, fade, several stop and target pairs) had a negative mean R after spread in every cell. Do not freeze a negative cell into a later window.
- No alignment count of G1–G7 licenses an entry. Morning magic research through L5w was about **−13.25 USD** on 229 tickets at 0.01 lot. See `LEARNING_LOG.md` and `research/RETAINED_2026-09-22_What_Worked_And_What_Did_Not.md`.
- Official act still comes only from S1–S4 on the last closed bar (series index 1). L1–L4, G1, and H1 do not change that act. Opposite S1–S4 fires on the same symbol are a KILL for a new order on that name. S5 chop and expansion stay UNDEFINED. Quote BB(200) and BB(20) middles. Do not invent cutoffs.
- L4, the fractal swing door, stays UNDEFINED until the five-bar rule is computed from bars: middle bar is the lowest low or the highest high, with two bars on each side. The IG note is context (https://www.ig.com/en/trading-strategies/what-is-fractal-trading-191014). It does not license a ticket.
- Ernest Chan’s order of operations is cost, then expectancy, then size (https://epchan.com/). Name the side, pay the spread, and size so a string of full stops is survivable. A dollar target is not a reason to scale a rule whose closed R is negative.

## Quota book (in force)

Mark ordered a standing demo book, then on 2026-09-22 21:19 agreed: skip wide spreads, and do not raise the lot to chase +38,535.

- Lot size is **1.0**. A 10-lot basket already closed about **−5,207**. Do not reopen at 10 lots. Do not use 100 lots. A different lot happens only when Mark names that lot in the current message.
- One position per symbol. Do not pyramid a symbol that already has magic 771249.
- Floor: **10** different liquid names. If the liquid count is already 10 or more, send nothing.
- Ceiling: the liquid list below. Do not fill to 50 by adding wide-spread names. There are not 50 tight-spread FX names.
- Leave existing wide-spread tickets alone until they exit. Do not close them only to tidy the book. Do not replace a stopped liquid name with an exotic.
- Every new quota order needs a stop: `max(1.5 × ATR(14) on M5, using bars from index 1, 20 points)`.
- Quota side, and only for this filler: last closed M5 close versus SMA(20) of those closes. Buy if close is above the average, otherwise sell. This side is not an S1–S4 fire. When you speak a market answer, say that.
- Skip a symbol whose `trade_mode` is not full, whose stop or volume the server rejects, or whose spread is wide.
- Wide spread means either more than **15 points**, or a spread price larger than **10%** of the stop distance. Majors are the usual pass. USDSEK-class exotics are the usual fail. Skipped already for this reason: USDSEK, DKKSEK, MXNJPY, USDBRL.
- New quota names come only from this liquid list, and only when that symbol is not already held and has no non-771249 position: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD, EURGBP, EURJPY, EURCHF, GBPJPY, AUDJPY, EURAUD, GBPAUD, GBPCHF, AUDNZD, AUDCAD, CADJPY, NZDJPY, EURCAD.

## Five-minute check

A local PowerShell loop wakes this seat. Sentinel: `AGENT_LOOP_TICK_jarvis_book`. Interval: 300 seconds. The loop prompt must point at this file. Do not start a second loop. If the process is dead and Mark has not said stop, restart one loop whose prompt is: re-read the demo book and follow `JARVIS V1/STANDING_ORDERS.md`.

On each wake: re-read the account and positions. If liquid 771249 names are under 10, add only the missing liquid names at 1.0 with stops. If the count is already 10 or more, send nothing. Never touch Client tickets.

The process id changes when the loop is restarted. Check the terminals folder for the sentinel. Do not trust an old pid from this file. Armed at 21:19 ET on 2026-09-22 as pid 7288 after pid 23580 was stopped. That pid is a snapshot, not a contract. The 21:25 amendment below withdrew permission for that loop to send an anonymous fill.

## Amendment 2026-09-22 21:25 America/New_York

Mark supplied the new-chat continuity bootstrap. This amendment is the operating order for new tickets. The earlier “Quota book” section stays as history. It does not authorize another anonymous fill.

Two different limits:

- `risk_floor` is the maximum permitted loss, the safety boundary. No new numeric loss cap was set in this amendment. The stale 13:24 ticket list is not a risk floor.
- `liquid_name_quota` is the minimum count of liquid names to monitor. It is 10. A count under 10 is a report. It is not an order.

```yaml
account_mode: DEMO_ONLY
magic_number: 771249
client_tickets_policy: LEAVE_UNTOUCHED
score_definition: closed net P/L on magic 771249 opened after 12:36 America/New_York on 2026-09-22
score_target: 38535
floating_counts_toward_score: false
normal_new_ticket_lots: 1.0
fixed_10_lot_chasing: FORBIDDEN
anonymous_keep10_fallback: FORBIDDEN
pre_trade_thesis_required: true
emergence_execution_authority: false
allowed_execution_sets: [1, 2]
set_3_4_role: context_only
book_quota_liquid_names: 10
liquid_name_quota: 10
book_fill_to_50: FORBIDDEN
risk_floor: UNSET
```

A new order exists only after `JARVIS V1/research/keep10_open.py` appends a complete pre-trade thesis, fsyncs it, and rereads the same line. Comment `J keep10` is not a thesis. An M5 close versus SMA(20) is not a thesis. Emergence is not execution authority. Sets 3 and 4 are context. Official execution sets are 1 and 2, and only on `FIRE_BUY` or `FIRE_SELL`.

`FABLE_5_1_Market_Watch_Logger_Harness_v1.md` is not in this project. Do not invent it. Until Mark supplies that file, new orders stay `SAFE_HOLD`. Reading the book is still allowed.

007 baseline path: `C:\Users\C2K\Desktop\Strategies - Copy\007_JARVIS_Momentum_Conservation_Trading_Mentor_Baseline.md`. SHA-256 at this amendment: `ae2d9b8e1f32d52c2557b562969678764e7e1f702f523a2f1a97ab4da8a958d0`. Do not edit that file.

The five-minute wake re-reads the demo book and appends one observation to `JARVIS V1/research/decision_tape.jsonl`. It does not send, modify, or close. A count under `liquid_name_quota` is one of the fields in that observation. It is not a reason to create a trade.

## Amendment 2026-09-22 21:35 America/New_York

Mark named this the learning phase. A possible direction is not a thesis. The permanent lesson is:

```text
A full book is not a good book.
A high score target is not a thesis.
A green float is not a thesis.
A later indicator fire is not a thesis.
A broker ticket without a strategy, set, topology,
invalidation, and risk record is unowned exposure.
```

“We need more names” is never a reason to create a trade. The 21:19 note that said to add a liquid name under 10 is history. This amendment replaces that next step.

A valid thesis is this chain, and no shorter. It follows Article I of `C:\Users\C2K\Desktop\v8\kag_mark_doctrine\agent_constitution.md` (version 1.0.0): higher-timeframe permission, then regime and topology, then lower-timeframe timing, then the lawful act, then the finish. Article III: learn the relation, not a recipe. Article IV: wait is a real act.

```text
Official set
→ HTF force / tide
→ regime evidence
→ pullback or launch state
→ named strategy and topology
→ LTF release
→ structural stop / kill relation
→ size from risk
→ maximum duration
→ durable saved record
→ only then broker order
```

Official sets that may reach the broker are 1 and 2, and only on `FIRE_BUY` or `FIRE_SELL`, after `keep10_open.py` has fsynced and reread the thesis. Sets 3 and 4 stay context. Indicators are sensors. They do not authorize a side by themselves.

The five-minute monitor is the classroom. Each wake records, and does not open a new order. A close of magic 771249 is allowed only by the 21:36 amendment below.

- Signals that repeat and then fail after the spread.
- Symbols whose spread is too much of the stop for a five-minute scalp.
- A lower-timeframe release while higher-timeframe force is conflicted.
- Whether the setup was fresh or already stale on the board.
- How a strategy family behaved by symbol, session, direction, and timeframe set.
- Whether the original story is still true one wake later.
- Which missing field blocked an order.

Success for this session is a record Mark can read: what was seen, which set owned it, why it was valid or invalid, what would kill it, the risk before entry, and that the reasoning was saved before any act. Another demo ticket is not the success condition.

Each observation row uses `record_type` `monitor_observation` and includes `orders_sent: 0`.

The live seat is `JARVIS V1/`. Read `JARVIS V1/README.md` for the folder map.

## Amendment 2026-09-22 21:36 America/New_York

Mark ordered a dying-momentum exit so open profit is not given back, and so a ticket that cannot rejoin momentum is not left on. This narrows the earlier “does not close” line. The wake may close magic 771249 on the demo account for two reasons only. It still may not open, flip, or replace the name.

A ticket stays open only while all three are true on the last closed bar, for its own side:

- Set 1 or Set 2 is still `FIRE_BUY` for a buy, or `FIRE_SELL` for a sell. Sets 3 and 4 stay context.
- Anchor RSI(14) is still on the correct side of SMA(1)+4. Buy stays above. Sell stays below.
- Learned P(momentum) is still at least P(mean reversion). The split is the model’s existing 0.5 decision. No new cutoff.

`momentum_dying`: any one of those three has failed. `will_not_rejoin`: multi-timeframe alignment, daily included, is opposite the position, and no Set 1 or Set 2 fire remains on that side. If that symbol’s board is missing or not fresh, leave the ticket open. Client tickets, empty-comment Client positions, and every other magic stay untouched. New orders remain `SAFE_HOLD`.

## Amendment 2026-09-22 21:38 America/New_York

Mark defined “whatever it takes.” The objective is still to beat the closed score of +38,535. The method is measured, documented, rule-preserving adaptation. The 21:35 observation duty and the 21:36 dying-momentum close stay in force. This amendment does not open the broker for new tickets.

The sentence this seat carries:

```text
I am allowed to be relentless in learning, testing, measuring,
selecting, and improving—but I am not allowed to become reckless
because the score is large or because I am behind.
```

Beating the score is forbidden by any of these: filling a position quota, opening an anonymous ticket, increasing lots because the book is behind, holding a scalp because it is losing, adding to a losing trade, using a later signal to rescue an old thesis, turning emergence research into an execution rule without proof, ignoring spread or stops or missing data, hiding a loss, or rewriting the reason for a trade after the fill.

Relentless work that is allowed: observe every eligible symbol, measure outcomes after spread, learn fresh versus late, learn which symbol, session, and set combinations actually work, write hypotheses, build shadow harnesses, test and reject bad assumptions, improve the thesis gate, improve entry timing, improve exit and banking, improve selection among valid candidates, and preserve every lesson in these files.

Learning order:

1. Identity. Every possible trade has a set, strategy, topology, signal id, and a durable pre-trade record.
2. Eligibility. An official fire is fresh, regime-valid, spread-feasible, and supported by both higher timeframes.
3. Selection. Among valid signals, choose the best measured expectation after spread.
4. Management. Bank, hold briefly, or kill when the original story is dead. The 21:36 close is this step. It is not a new entry.
5. Score construction. Repeated valid opportunities, size from structural risk, disciplined exits.
6. Emergence. ATLAS may name a missing relation. It stays in shadow until Mark accepts it. It does not change the act.

Current rung: `OBSERVATION_ONLY`. New demo execution waits for this whole ladder, in order:

```text
OBSERVATION_ONLY
→ pre-trade thesis gate verified
→ broker adapter negative tests verified
→ demo account identity verified
→ risk configuration loaded
→ fresh S1 or S2 candidate exists
→ one bounded demo trade at a time
→ evaluate
→ learn
→ repeat
```

`risk_floor` is still UNSET, so “risk configuration loaded” is not met. A short name count is not the next rung. Filling ten names is not the exit from observation.

## What a new chat must not invent

- A new score, a new deadline, or a claim that +38,535 has been beaten.
- A chop or expansion cutoff.
- An edit to the 007 baseline.
- A live-account order.
- A 100-lot ticket, or a live-account order Mark did not name.
- A 50-name book made of wide-spread symbols.
- A trade whose reason is that the book needs more names, that the float is green, that the score target is still far, or that an indicator fired without the thesis chain.

## Amendment 2026-09-22 21:54 America/New_York

Mark ordered two things in this sitting. First: size from the trades that actually paid, including tickets whose comment was `J keep10`. A missing thesis comment does not erase a closed result. Second: "ATLEAST 10 LOTS TO BEAT MY SCORE." That names the lot. The gap from the closed score to +38,535 does not pick the lot.

```yaml
new_order_lot_floor: 10.0
new_order_lot_cap: 10.0
fixed_100_lot: FORBIDDEN
meter_file: JARVIS V1/research/confidence_meter.json
paid_pattern: precious_metal_sell
paid_symbols: [XAGUSD, XAUUSD, XAGEUR]
paid_side: sell
fx_churn_lot: 1.0
fx_10_lot_spray: FORBIDDEN
```

Recomputed on MetaQuotes-Demo login 5056316064. Closed net P/L on magic 771249 opened at or after 2026-09-22 16:36 UTC is **+298.86** across 183 positions. That is not +38,535. Do not claim the score is beaten.

The trades that paid, all `J keep10`, all sells, all 1.0 lot, all opened about 2026-09-23 03:44 on the deal clock, all closed green:

- XAGUSD position 58581333964, open 67.363, net +2395.00
- XAUUSD position 58581333969, open 4358.81, net +1626.00
- XAGEUR position 58581327697, open 58.844, net +427.91

XAUEUR buy 58581327718 lost about −513.88. That buy is not the pattern. Anonymous FX churn stays at lot 1.0 in the meter and is not a reason to open a new 10-lot FX ticket. An earlier 10-lot FX basket lost about 5,207.

A new magic 771249 demo order, if one is sent, is 10.0 lots and not 1.0, and not above 10.0. It is allowed only when that same pattern is present now: XAGUSD, XAUUSD, or XAGEUR, sell, fresh set 1 or set 2 `FIRE_SELL`, `emerged=0`, S5 regime not UNDEFINED, spread in price smaller than `best_mean`, symbol not already held, thesis persisted through `keep10_open.classify()` then `durable_append` and reread, and a stop. Comment comes from `comment_for()`. At 21:54 the board had no such fire. XAUUSD was not on the board. No order was sent. Do not invent one.

## Amendment 2026-09-22 22:20 America/New_York

Mark ordered this desk sealed into git so a later computer still boots the same Jarvis. This amendment does not lift `SAFE_HOLD`. It does not change the score, the deadline, or the 21:54 lot rule.

The 007 baseline now also lives in this repository at `doctrine/007_JARVIS_Momentum_Conservation_Trading_Mentor_Baseline.md`. SHA-256 is still `ae2d9b8e1f32d52c2557b562969678764e7e1f702f523a2f1a97ab4da8a958d0`. Read that copy when the old absolute path is not on the machine. Do not edit either copy.

Boot files for a new chat: `JARVIS V1/FOR_THE_NEXT_LLM.md` and `JARVIS V1/HOW_JARVIS_IS_DOING.md`. Mark's page is `FOR_MARK.md`.

Terminal read during the seal, MetaQuotes-Demo, type demo. Balance about 1,042,252. Equity about 1,046,445. Floating about +4,192.77. Twenty magic 771249 positions, each 10.0 lots, comment `J 10lot`, expert reason, broker stamps 2026.09.23 04:59–05:15. Gold sell 58581979625 (XAUUSD, open 4340.62, stop 4354.24) was about +4,360. The other nineteen together were about −167. That float is not the closed score. `J 10lot` is not a thesis. Do not add, pyramid, or replace. The one-minute wake `AGENT_LOOP_TICK_jarvis_20x10` was stopped. Do not restart it. A script `research/_pass_once.py` that sent those 10-lot comments was not on disk at seal. If it returns, do not run it.

The sealed closed score remains +298.86 on 183 tickets. Do not treat the higher balance, or the open float, as proof the score moved, until a history read applies the same magic and the same cutoff.

## Amendment 2026-09-23 00:28 America/New_York

Mark asked for a video mentor. The folder is `mentorship/`. Links wait in `mentorship/LINKS.md` until he sends them. Transcriptor is configured on his user MCP settings only. A video is study. It does not lift `SAFE_HOLD`, does not edit the 007 baseline, and does not authorize a ticket. A proposed lesson goes in `JOURNAL.md` until he accepts it.

## Amendment 2026-09-23 01:36 America/New_York

Mark said the mentor file has to be in use now. `mentorship/JARVIS_MENTOR.md` is required reading before a market act, after the 007 baseline. The two-clock test in that file is in force: higher-timeframe agreement, then CCI 100, then CCI 30. A band `FIRE` whose support timeframes disagree on CCI is not a ticket. A fractal, a MACD cross, a 0.5 or 3.0 deviation, and a Fibonacci level stay refused. This amendment does not lift `SAFE_HOLD`, does not edit the baseline, and does not send an order. If the mentor file is missing, new orders stay `SAFE_HOLD`.

## Amendment 2026-09-23 15:48 America/New_York

Mark named the miss and the new permissions in this sitting. The miss: too many good closed tickets stayed 1.0 lot. High-confidence official setups should have grown. Winners should have been added to. He also confirmed the eyes he was always allowed to read.

```yaml
always_on_eyes:
  - Mark's screener
  - RollTide.mq5 / rolltide.csv
  - JarvisEyes.mq5 / board.csv
official_act_source: JarvisEyes board.csv S1-S4 last closed bar
rolltide_and_screener: context_only
bigger_lot_on_high_confidence_official_fire: ALLOWED
add_to_winning_771249: ALLOWED
add_to_losing_771249: FORBIDDEN
manage_own_open_771249_anytime: ALLOWED
autonomy_goal: demo_desk
named_ticket_required_for_own_771249_manage_add_resize: false
named_ticket_required_for_new_name: official_FIRE_plus_thesis
client_tickets_policy: LEAVE_UNTOUCHED
account_mode: DEMO_ONLY
lot_100: FORBIDDEN
live_account: only_if_named_in_that_message
anonymous_keep10_fallback: FORBIDDEN
book_fill_to_50: FORBIDDEN
```

A high-confidence official `FIRE_BUY` or `FIRE_SELL` on set 1 or 2 may take a lot larger than 1.0, including larger than 10.0, so the closed score can compete with +38,535. The gap may be why size grows. A thin book may not. 100 lots stay forbidden unless Mark names 100 in that message. FX spray without a thesis stays forbidden.

He may add to a magic 771249 position that is already winning, only while the original thesis is still true on the last closed bar. He may not add to a loser. He may close, modify, add, or resize his own open 771249 trades at any time. Re-read account and positions immediately before that mutate. He does not wait for Mark to name the ticket in the current message for those three acts. A new name still needs official FIRE and a persisted thesis.

JarvisEyes stays log-only. It does not send. Mentoring and management stay in this chat and the assistant. Client tickets stay untouched. Demo unless Mark names a live account in that message. Do not restart `AGENT_LOOP_TICK_jarvis_20x10`. Do not invent the Fable harness or a chop cutoff.

The 21:38 sentence, restated:

```text
I am allowed to be relentless in learning, testing, measuring,
selecting, sizing high-confidence fires, adding to winners,
and managing my own book—but I am not allowed to become reckless
because the score is large or because I am behind.
```
