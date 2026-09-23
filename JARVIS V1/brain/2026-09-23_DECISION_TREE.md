# Decision tree — one wake, end to end — 2026-09-23

How a market question becomes exactly one spoken act. Every diamond is a real question from the seat files. Every rounded box is a place the wake ends. Source: `STANDING_ORDERS.md` including amendment 2026-09-23 15:48, `mentorship/JARVIS_MENTOR.md` two-clock test, `.cursor/rules/jarvis-eyes.mdc`, `desk_state.md`.

Picture: `2026-09-23_jarvis-decision-tree.png`. Print file: `2026-09-23_jarvis-decision-tree.svg`.

A new **name** still waits on official FIRE plus a thesis. Managing, adding to a winner, or resizing a still-valid 771249 fire does not wait for Mark to name the ticket in that message. He re-reads the book first. `risk_floor` is still UNSET. The Fable harness is still missing. Those facts do not block management of the open 771249 book.

```mermaid
flowchart TD
  wake["Wake: market question, book-check, or a named trade request"] --> seat["Load the seat in order:<br/>FOR_THE_NEXT_LLM → BOOTSTRAP → STANDING_ORDERS → desk_state<br/>newest LEARNING_LOG → HOW_JARVIS_IS_DOING → 007 hash → JARVIS_MENTOR"]
  seat --> files{"Every seat file present?<br/>Baseline hash unchanged?"}
  files -->|no| hold1["SAFE_HOLD<br/>Report the exact gap. No trade. No strategy edit."]
  files -->|yes| check["Print CONTINUITY CHECK"]
  check --> eyes["Read JarvisEyes board.csv on the last closed bar index 1.<br/>Also read RollTide and Mark's screener. They do not vote.<br/>Forming bar is telemetry. Re-read the open book."]
  eyes --> fresh{"Board fresh, quote present,<br/>closed bar time current?"}
  fresh -->|no| stale["WAIT_NO_TRADE<br/>Say the board is stale. Do not hide it."]
  fresh -->|yes| htf{"Both support timeframes<br/>agree on one side?"}
  htf -->|no| flat["Tide flat. No permission.<br/>Say flat even if a band row says long_only."]
  htf -->|yes| cci100{"CCI 100 on the anchor<br/>still on that side?"}
  cci100 -->|no| kill["KILL. Force failed.<br/>A fast cross back is not a rescue."]
  cci100 -->|yes| cci30{"Where is CCI 30<br/>on the closed bar?"}
  cci30 -->|against the side| loaded["WAIT_LOADED<br/>Name the rejoin that would release it."]
  cci30 -->|already with it, price clearing| cont["Continuation. S3 language.<br/>Do not call it a pullback."]
  cci30 -->|just crossed back| still{"That bar itself still passes S1–S4?<br/>No opposite S1–S4 fire on the symbol?"}
  still -->|no| notfire["Not a fire. An older cross does not stay a fire.<br/>An opposite fire kills a new order."]
  still -->|yes| fire["Technical act: FIRE shape<br/>S1 typical · S2 close · S3 rails + body · S4 close"]
  fire --> attack["Attack: spread, bar speed, heat, book.<br/>Regime from S5. UNDEFINED quotes the two middles.<br/>G1, H1, L1–L4 named. They do not vote."]
  attack --> speak["Speak one 007 block:<br/>MARKET SET TIDE REGIME STATE ROLE MAP<br/>TOPOLOGY ACT WHY INVALIDATION RISK"]
  speak --> named{"Did Mark name a symbol or ticket<br/>to trade in this message?"}
  named -->|no| report["Report only. A short name count is not a request."]
  named -->|yes| floor{"Today target and risk_floor both set?"}
  floor -->|no| waitfloor["WAIT_NO_TRADE<br/>Say the technical act beside it.<br/>A blank floor is not a fire."]
  floor -->|yes| harness{"Harness present? Rung above OBSERVATION_ONLY?<br/>Server says demo unless a live account was named?"}
  harness -->|no| hold2["SAFE_HOLD. Reading the book is still allowed."]
  harness -->|yes| thesis{"Set 1 or 2, official FIRE not emerged,<br/>regime defined, release bar fresh,<br/>symbol not held, no Client ticket on it?"}
  thesis -->|no| refused["Refused. Emergence is not execution authority."]
  thesis -->|yes| write["Write the thesis to disk. fsync. Reread."]
  write --> alive{"Live bid still on the right side of the kill?"}
  alive -->|no| dead["Dead bar. Send nothing. No retry.<br/>Do not reuse that bar. GBPCHF 07:36, bid 1.09404."]
  alive -->|yes| send["Send one order. Magic 771249. Lot Mark named.<br/>Timeout or ambiguous: no retry. Reconcile from the book."]
  send --> manage["Hold while tide, regime, and structure hold on the closed bar.<br/>Close only for momentum_dying or will_not_rejoin.<br/>A close is not a reason to open the next name."]
  manage --> learn["Record: decision_tape, LEARNING_LOG, JOURNAL proposals.<br/>Baseline stays read-only. Score is closed 771249 after 12:36."]
  learn -.->|next wake| wake
```

## How to read it

The path runs down seven bands.

| Band | Job |
|---|---|
| A Boot | Load the seat. If a required file is missing, or the 007 hash is not `ae2d9b8e…`, stop. |
| B Eyes | Last closed bar only. Also read RollTide and the screener. Forming bar cannot create a fire. |
| C Two clocks | Higher timeframes first, then CCI 100, then CCI 30. The first failed clock ends the story. |
| D Attack | Spread, speed, heat, book. Context is named and does not vote. |
| E Speak | One block. Then stop talking about a second act. |
| F Desk gates | Permission. Today the floor, the harness, and the rung stop every new order. |
| G Manage and learn | Narrow exits on his own tickets. Then write what the wake taught. |

## Two-clock table

| Higher timeframes | CCI 100 | CCI 30 | What it is | Act |
|---|---|---|---|---|
| Agree on a side | Still on that side | Against that side | Pullback, loaded | Wait. Name the rejoin. |
| Agree on a side | Still on that side | Just crossed back | Pullback, released | Fire shape, if the gates pass. |
| Agree on a side | Still on that side | Already with it, price clearing | Continuation | S3 language. Not a pullback. |
| Agree on a side | Lost that side | Either way | Force failed | Kill. |
| The two supports disagree | Anything | Anything | No permission | Flat. No trade. |

A fractal, a MACD cross, a 0.5 or 3.0 deviation, or a Fibonacci level does not fill any cell.

## What can set the act, and what cannot

**These four can set the technical act:** S1 Dual CCI slingshot. S2 Dual BB pullback. S3 Shifted envelope. S4 RSI-BB tension snap.

**These may be named. They do not vote:** S5 regime gate. L1–L3 legacy doors. L4 fractal swing. G1 daily RSI. H1 Heikin Ashi.

## Levers that would change this tree

| Lever | Owner | Gate it opens | Today |
|---|---|---|---|
| Set `risk_floor` as a number | Mark, in `STANDING_ORDERS.md` | Target and floor both set | UNSET |
| Supply the Fable harness file | Mark | Harness present | Missing. Do not write a fake one. |
| Raise the rung above `OBSERVATION_ONLY` | Mark | Rung check | OBSERVATION_ONLY |
| An entry that survives the spread | Research on closed bars | Makes the FIRE shape worth taking | 0 of 12 forward passes. Mean R negative in every grid cell. |
| Numbers for S5 chop and expansion | Mark, proposal in `JOURNAL.md` | Regime stops saying UNDEFINED | UNDEFINED |
| Faster board and symbol read | Engineering | Fewer dead bars between close and send | GBPCHF 07:36 died at bid 1.09404 |
| Compute the L4 five-bar rule | Engineering | L4 becomes real context. Still no vote. | UNDEFINED |

## What stays fixed

- Only S1–S4 on the closed bar set the technical act.
- Context does not vote. 229 tickets at 0.01 lot, −13.25, proved no alignment count licenses an entry.
- A blank floor is `WAIT_NO_TRADE`. A 10-lot FX basket closed about −5,207. Size multiplied the sign.
- No retry after an ambiguous send.
- The 007 baseline is read-only. Proposals go in `JOURNAL.md`.
