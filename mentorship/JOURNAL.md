# Mentorship test journal

Source record of tickets. The teaching is `JARVIS_MENTOR.md`.

Demo only. Magic 771249. This file records whether David Paul's pullback idea helps. It does not rewrite the 007 baseline.

## Judgment, before any ticket

The three rules help as a filter. They do not yet help as a new entry engine.

What matches this desk: take the uncomfortable pullback with the higher-timeframe trend, after the easy chase has been refused. That is official S2, Dual BB pullback, on set 1 or 2.

What does not get adopted: the channel's 38.2%, 50%, and 70.5% Fibonacci limits, fair value gaps, and breaker blocks. One video is not a cutoff.

The live book at the read (MetaQuotes-Demo, type demo, board time 2026.09.23 07:37:13) was 12 magic tickets at 10.0 lots, comment `J 10lot`, account floating about **−12,638**. Most of that was XAUUSD sell 58582636689, about **−9,990**. Those tickets are not this test. They are not closed, added to, or replaced.

## Test rule for this folder

One new demo ticket at a time. Lot **0.01**. Mark authorized the demo test and did not name a lot. A 10-lot foreign-exchange ticket is not the test. Symbol must be free of any open position. Stop is structural. No timer flatten. Result lines are appended below after the fill, and again when the ticket closes.

## 2026-09-23 00:36 America/New_York — candidate

GBPCHF, sell, set 1, S2 Dual BB pullback. Anchor M1, higher timeframes M15 and M30. Tide `short_only`. Closed bar 2026.09.23 07:36, open 1.09400, high 1.09403, low 1.09397, close 1.09400. Spread 4 points. Phase `pullback`, and that phase is the one with the better recorded average (72 samples). Daily RSI warning is bear, which agrees, and it does not license the ticket.

S5 chop and expansion are UNDEFINED. BB(200) middle 1.09737, BB(20) middle 1.09460 on the M15 leg. Price is below both middles. That is gravity, not a chop cutoff.

The board act is `FIRE_SELL` because the pullback phase was promoted (`emerged_enter_pullback`). The comparison field still says the pre-promotion act was `WAIT_LOADED`, and `emerged=1`. The ordinary thesis gate would refuse that. This one ticket is the exception Mark named for the mentorship test. If the bid is already above 1.09403, the pullback is dead and nothing is sent.

Kill: a close back above 1.09403. Stop sits beyond that high, at least far enough that the 4-point spread is under 10% of the stop distance.

## 2026-09-23 00:36 America/New_York — result

Orders sent: **0**.

The first send attempt stopped before any order. MetaTrader returned `Terminal: Out of memory` on the symbol select. GBPCHF was re-read after that. No position was open. Bid was **1.09404**, one point above the pullback high **1.09403**. The test rule said that print kills the entry. Nothing was sent, and the attempt was not retried.

What this pass taught: the pullback was real on the 07:36 bar and gone by the time the terminal could take it. Chasing the next tick would have been the easy trade the mentor said to refuse. The 10-lot book was left as it was.

## 2026-09-23 01:07 America/New_York — mentor 2, no ticket

Orders sent: **0**.

Judge: CCI 100 leading and CCI 30 timing helps, because that is already S1. Two timeframes help, because that is how a pullback is told from a continuation. The fractal breakout does not help. The dual-MACD periods and the 0.5 / 3.0 Bollinger deviations stay unadopted. Detail: `mentorship/notes/2026-09-23_mentor_2.md`.
