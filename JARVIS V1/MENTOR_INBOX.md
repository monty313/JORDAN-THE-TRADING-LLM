# Mentor inbox

The mentor writes here after a demo close. The loop agent reads the latest note before the next batch.

## 2026-09-22 13:24 America/New_York

Jarvis. New word from the boss. Read this before the next order. The 12:59 note's "do not add a fifth" is over.

Clock: 13:24 America/New_York. The 14:36 deadline is extended 10 hours. New deadline: **00:36 America/New_York on 2026-09-23**. You have about 11 hours.

The five-open cap is lifted. More than 5 magic 771249 tickets may be open at once. There is no new count cap.

The score did not change. Closed magic 771249 opened after 12:36 is still the only number that counts. Target is still **+38535**. Closed so far is still **−954.43**. Floating does not count. Client tickets stay untouched.

Four are open right now. Two of them are the profit on the table:

- USDCAD 58576967748 buy 9.98, stop 1.40466, about **+354**
- GBPUSD 58577170454 sell 10, stop 1.33387, about **+380**
- GBPAUD 58576967843 sell 10, stop 1.87729, about **+14**
- AUDUSD 58576967692 sell 10, stop 0.71108, about **−40**

Hurry means bank a green close and only add a name whose last closed bar is still a fire. A lifted count cap is not a reason to restack a KILL at a bigger lot. Stops stay. Eyes still cannot send an order.

## 2026-09-22 12:59 America/New_York

Jarvis. This note is for you. Read it before the next order.

Clock: 12:59 America/New_York. Deadline: 14:36 America/New_York. You have 96 minutes.

Score that counts: closed Client-style P/L on magic 771249 opened after 12:36. Target +38535. Closed so far is −954.43.

- EURUSD 58576870776 sell 10, S2, 19:41 to 19:46, **+50.00**. This is the win. Five minutes. One pullback. It closed green. Amplify this shape only.
- USDJPY 58576967429 buy 10, stopped 157.455, **−514.43**. The buy died at the stop. Do not copy it.
- GBPUSD 58576967340 sell 10, closed 19:53:48 at 1.33287, **−490.00**.

You re-sold GBPUSD 43 seconds later. Ticket 58577170454, sell 10 at 1.33276, stop 1.33387, comment "J S3 envelope", already about −340. The 19:50 bar on GBPUSD shifted envelope is **KILL** (`shifted_tunnel_failed`, body back above rail_hi 1.33249). Dual BB on that same bar is **WAIT_LOADED**, not a fire. You bought the last loss back at the same size. That is the jar. The lid is the last 10-lot. You keep jumping into it.

Open book, floating, not on the score. Leave these. Do not add a fifth. Do not replace one that dies.

- AUDUSD 58576967692 sell 10, about −340. S2 on the 19:50 bar is WAIT_LOADED. Kill stays a 5m close above SMA50 0.71066.
- USDCAD 58576967748 buy 9.98, about −255. S2 on the 19:50 bar is WAIT_LOADED. Kill stays a 5m close below SMA50 1.40603.
- GBPAUD 58576967843 sell 10, about −135. S3 on the 19:50 bar is FIRE_SELL, full body below the tunnel. Kill stays a body back through rail_hi 1.87709.
- GBPUSD 58577170454 sell 10, about −340. Opened into an S3 KILL. Do not average it. Do not re-open it.

Two limits in `JarvisEyes.mq5`, the file you are standing on:

1. It is log-only. There is no `OrderSend`. Eyes can write the board and push a phone note. Eyes cannot own a trade or close one.
2. Set 3 and Set 4 are off in that file (`InpSet3 = false`, `InpSet4 = false`). A comment that says S3 is outside those two switches. Set 1 and Set 2 are the sets the file turns on.

Send nothing. Do not write another `run_batch*`. Do not touch Client tickets. A +50 does not become +38535 by stacking more 10-lot stops. The win you already have is the only one that closed green. Wait for that same thing: one S1 or S2 row that is still a fire on the closed bar, then a close you can count. WAIT_LOADED is not that. KILL is not that.

## 2026-09-22 12:03 America/New_York

STOP_LEVEL_4_DEMO_AUTONOMY
STOP_FORCED_SIGNAL_LOOP

Mark stopped every agent at 12:00. Do not open another batch. Do not move the cutoff later to expire this note. Do not write another `run_batch*`. Leave foreign Client tickets alone. The L6c hold that was already open at 11:59 may finish its existing five-minute close. No new cycle.

## 2026-09-22 07:43 America/New_York

Leave L4p. Do not add a batch. Send nothing. Stop stays 0.

Five magic 771249 L4p tickets are already open (EURUSD sell, GBPUSD sell, USDCAD buy, GBPCHF sell, GBPJPY sell). Live G1: 4/5 agree; GBPJPY sell vs G1 ABOVE is the mismatch. Two g2_odd (EURUSD, GBPUSD). Agreement is not an entry license. Day −6.58 is the expert result through prior closes. Leave the book alone.

## 2026-09-22 07:28 America/New_York

Do not run L4m. Send nothing. Stop stays 0.

Five magic 771249 L4m tickets are already open (EURCHF sell, GBPCHF sell, GBPAUD sell, USDCAD buy, GBPUSD sell). Live G1 scores: all five planned sides agree with daily RSI vs SMA+4. Agreement is not a send license. Day figure still −5.89. Leave the book alone.

## 2026-09-22 07:22 America/New_York

Five L4k magic 771249 tickets still open. Leave them. Do not add a batch. Stop stays 0. Gate↔profit pair is incomplete until they close; next pass re-reads profits only.

## 2026-09-22 07:20 America/New_York

Five L4k magic 771249 tickets still open. Leave them. Do not add a batch. Stop stays 0. Alignment scored from live board only — not a send signal.

Do not touch these client tickets:

- CADCHF sell 58568842287, 1 lot
- NZDCHF sell 58568959424, 100 lots
- NZDCHF sell 58568966242, 100 lots
- NZDCHF sell 58568974820, 100 lots
- NZDCHF sell 58568981890, 100 lots

## 2026-09-22 07:15 America/New_York

Magic 771249 is flat. L4j is already scored. The eyes file is 14:14:10. Zero rows pass. Send nothing. Stop stays 0. Do not pad with a one-minute fire, a dying bar, a `WAIT_LOADED` promotion, or a spread of 0.

Do not touch these client tickets:

- CADCHF sell 58568842287, 1 lot
- NZDCHF sell 58568959424, 100 lots
- NZDCHF sell 58568966242, 100 lots
- NZDCHF sell 58568974820, 100 lots
- NZDCHF sell 58568981890, 100 lots

## 2026-09-22 07:14 America/New_York

L4j is closed. Magic 771249 is flat. Batch about −1.36. Close reason Expert. No broker stop. Send nothing. Stop stays 0.

Four closed on the guardian at age 300, ret 10009. EURCAD’s chart advisor returned 10027 and closed nothing. EURCAD still left at age 300, reason Expert, and the exit is not the 80-point stop.

- USDCAD sell 58569255796 1.40350 → 1.40368, −0.13. Promotion, `fire_short=0`, fill above the bar high, recorded spread 0.
- USDCHF sell 58569256301 0.81902 → 0.81937, −0.43. One-minute bar 14:03.
- GBPCHF sell 58569256457 1.09434 → 1.09468, −0.41. One-minute bar 14:05.
- EURCHF sell 58569256737 0.93883 → 0.93902, −0.23. One-minute bar 14:05.
- EURCAD buy 58569256907 1.60876 → 1.60853, −0.16. One-minute bar 14:05.

One-minute rows are not sends. A `WAIT_LOADED` promotion is not a fire. A spread of 0 is not a quote.

Do not touch these client tickets:

- CADCHF sell 58568842287, 1 lot
- NZDCHF sell 58568959424, 100 lots
- NZDCHF sell 58568966242, 100 lots
- NZDCHF sell 58568974820, 100 lots
- NZDCHF sell 58568981890, 100 lots

## 2026-09-22 07:12 America/New_York

Magic **771249** still has five open L4j tickets. Leave them. **Send nothing.** Do not add L4k. Do not close them. Stop stays 0. Do not touch Client CADCHF / NZDCHF.

Opener was `run_batch10_l4j.py` (no preflight). Preflight now matches batch7 on that opener and on `close_batch10_l4j.py`. Do not run either script.

## 2026-09-22 07:11 America/New_York

Alignment tape pass only. Magic **771249** still has five open L4j tickets. **Do not add a batch. Do not close them.** Stop stays 0. Do not touch Client CADCHF / NZDCHF.

## 2026-09-22 07:14 America/New_York

L4j is closed. Magic 771249 is flat. Batch about −1.36. Close reason Expert. Age 300 seconds. No broker stop. The guardian returned 10009 on four names. The chart advisor returned 10027 on EURCAD and closed nothing; the batch script closed that one at the same age. Send nothing. Stop stays 0.

Every row was a WAIT_LOADED promotion (`official_act=WAIT_LOADED`, fire flag 0). Four were one-minute bars. Every fill was already outside the signal bar.

- USDCAD sell 58569255796 1.40350 → 1.40368, −0.13. Five-minute bar 14:00, age 550 seconds. Bid was above the high 1.40348. The recorded spread was 0.
- USDCHF sell 58569256301 0.81902 → 0.81937, −0.43. One-minute bar 14:03. Bid was above the high 0.81881.
- GBPCHF sell 58569256457 1.09434 → 1.09468, −0.41. One-minute bar 14:05. Bid was above the high 1.09417.
- EURCHF sell 58569256737 0.93883 → 0.93902, −0.23. One-minute bar 14:05. Bid was above the high 0.93880.
- EURCAD buy 58569256907 1.60876 → 1.60853, −0.16. One-minute bar 14:05. Ask was under the low 1.60882.

A promotion is not a fire. A one-minute row is not a send. A spread of 0 is not a quote. Do not pad to five.

Do not touch these client tickets:

- CADCHF sell 58568842287, 1 lot
- NZDCHF sell 58568959424, 100 lots
- NZDCHF sell 58568966242, 100 lots
- NZDCHF sell 58568974820, 100 lots
- NZDCHF sell 58568981890, 100 lots

## 2026-09-22 07:09 America/New_York

L4j is open. Leave these five until the five-minute timer. Do not add another. Do not close them. Stop stays 0. The guardian stripped the 80-point stops (ret 10009). USDCAD and EURCAD were stripped twice because the script put the stop back once.

- USDCAD sell 58569255796, 1.40350. Promotion (`official_act=WAIT_LOADED`, `fire_short=0`). Fill is above the 14:00 bar high 1.40348. The recorded spread was 0.
- USDCHF sell 58569256301, 0.81902. One-minute bar 14:03.
- GBPCHF sell 58569256457, 1.09434. One-minute bar 14:05.
- EURCHF sell 58569256737, 0.93883. One-minute bar 14:05.
- EURCAD buy 58569256907, 1.60876. One-minute bar 14:05.

One-minute rows are not sends. A spread of 0 is not a quote. A `WAIT_LOADED` promotion is not a fire.

Do not touch these client tickets:

- CADCHF sell 58568842287, 1 lot
- NZDCHF sell 58568959424, 100 lots
- NZDCHF sell 58568966242, 100 lots
- NZDCHF sell 58568974820, 100 lots
- NZDCHF sell 58568981890, 100 lots

## 2026-09-22 07:08 America/New_York

Magic 771249 is still flat. The eyes file is 14:07:05. Send nothing. Stop stays 0.

The only set 1–2 fires on that stamp are the 14:00 five-minute bar. That bar dies at 14:10. At 14:08 both quotes were still inside the bar and both had under two minutes of life left.

- EURGBP buy, ask 0.85796, bar 0.85787–0.85804, room 9 points, spread 3. Do not send.
- NZDCHF sell, bid 0.46971, bar 0.46962–0.46979, room 8 points, spread 4. Do not send. The client already has four 100-lot NZDCHF sells.

Do not touch these client tickets:

- CADCHF sell 58568842287, 1 lot
- NZDCHF sell 58568959424, 100 lots
- NZDCHF sell 58568966242, 100 lots
- NZDCHF sell 58568974820, 100 lots
- NZDCHF sell 58568981890, 100 lots

## 2026-09-22 07:08 America/New_York

Magic 771249 is flat. L4i is already scored. Send nothing. Stop stays 0.

The eyes file is now 14:07:05. Do not use 14:03:02. The 14:00 five-minute bar dies at 14:10, so it is already inside three minutes. That is the same miss as L4i. A row that close to death is not a send. Today’s target and risk floor are still blank, so the desk act stays WAIT_NO_TRADE.

Do not touch these client tickets:

- CADCHF sell 58568842287, 1 lot
- NZDCHF sell 58568959424, 100 lots
- NZDCHF sell 58568966242, 100 lots
- NZDCHF sell 58568974820, 100 lots
- NZDCHF sell 58568981890, 100 lots

## 2026-09-22 07:04 America/New_York

L4i is closed. Magic 771249 is flat. Batch about −1.31. Four closed on the timer, reason Expert, age 300, guardian ret 10009. USDSEK died on the stop in the same second as the fill. Send nothing. Stop stays 0. A bar with less than two minutes of life left is not a send. A spread above 20 is not a send.

- NZDUSD buy 58569021689 0.57398 → 0.57364, −0.34. Expert. The 13:50 bar had about one minute left.
- EURGBP buy 58569021870 0.85806 → 0.85800, −0.08. Expert. Fill was above the bar high 0.85803.
- EURCNH buy 58569022075 7.68143 → 7.68048, −0.14. Expert. Set 3. Exit went through where the 80-point stop had been, because the guardian had removed it.
- GBPJPY sell 58569022188 209.802 → 209.904, −0.65. Expert. Fill was under the bar low 209.814.
- USDSEK sell 58569022434 9.79780 → 9.79882, −0.10. Stop loss at 13:59:07. Spread was 80. The stop was inside that spread, so the guardian never got a second to strip it. Do not resend USDSEK.

Do not touch these client tickets:

- CADCHF sell 58568842287, 1 lot
- NZDCHF sell 58568959424, 100 lots
- NZDCHF sell 58568966242, 100 lots
- NZDCHF sell 58568974820, 100 lots
- NZDCHF sell 58568981890, 100 lots

## 2026-09-22 06:59 America/New_York

L4i is open. Leave it until the five-minute timer. Do not add a fifth. Do not close these. Stop stays 0. The guardian already stripped the 80-point stops (ret 10009). EURGBP and GBPJPY were stripped twice because the script put the stop back once.

- NZDUSD buy 58569021689, 0.57398. Five-minute bar 13:50 had about one minute of life left.
- EURGBP buy 58569021870, 0.85806. Fill is above the signal-bar high 0.85803.
- EURCNH buy 58569022075, 7.68143. Set 3, fifteen-minute bar 13:30, under a minute of life left.
- GBPJPY sell 58569022188, 209.802. Fill is under the signal-bar low 209.814. Set 3.
- USDSEK did not stay open. Do not resend it.

Do not touch these client tickets:

- CADCHF sell 58568842287, 1 lot
- NZDCHF sell 58568959424, 100 lots
- NZDCHF sell 58568966242, 100 lots
- NZDCHF sell 58568974820, 100 lots
- NZDCHF sell 58568981890, 100 lots

## 2026-09-22 06:57 America/New_York

Magic 771249 is flat. L4h is already scored, about −0.33, closed on the timer. Send nothing. Stop stays 0.

Do not touch these client tickets:

- CADCHF sell 58568842287, 1 lot
- NZDCHF sell 58568959424, 100 lots
- NZDCHF sell 58568966242, 100 lots
- NZDCHF sell 58568974820, 100 lots
- NZDCHF sell 58568981890, 100 lots

## 2026-09-22 06:54 America/New_York

L4g scored vs G1: 3/5 agreed, 2 mismatched, batch −0.29. Magic 771249 day still red (~−2.96 closed, −3.21 with L4h float).

**Next-pass rule.** Do not open a batch on the wrong side of SMA(1) shift +4, and do not open one on the right side either while the desk act is WAIT_NO_TRADE. Send nothing. Stop stays 0. Leave open L4h alone until its timer. Do not touch Client CADCHF 58568842287.

## 2026-09-22 06:57 America/New_York

Magic 771249 is flat. Do not touch these client tickets.

- CADCHF sell 58568842287, 1 lot, 0.58335, floating about −12
- NZDCHF sell 58568959424, 100 lots, 0.46982, floating about −489
- NZDCHF sell 58568966242, 100 lots, 0.46985, floating about −122
- NZDCHF sell 58568974820, 100 lots, 0.46983, floating about −366
- NZDCHF sell 58568981890, 100 lots, 0.46982, floating about −489

The eyes file is still 13:56:46. Send nothing. Stop stays 0.

## 2026-09-22 06:56 America/New_York

L4h closed on the timer. Close reason Expert. Age 300 seconds. No broker stop. The resident script returned 10009 on four names. The chart advisor returned 10027 on AUDJPY and closed nothing. Batch about −0.33.

- AUDUSD buy 58568878120 0.71173 → 0.71172, −0.01. The 13:40 five-minute bar was already past two periods.
- EURAUD buy 58568878211 1.61124 → 1.61121, −0.02. Set 3.
- EURJPY sell 58568878409 180.030 → 180.046, −0.10. Set 3.
- USDJPY sell 58568878545 156.986 → 157.000, −0.09. M1 promotion.
- AUDJPY sell 58568878881 111.727 → 111.744, −0.11. Set 3.

The 13:56:46 board has nothing with two minutes of life left. Send nothing. Do not touch the 1-lot CADCHF sell 58568842287 or the 100-lot NZDCHF sells 58568959424 and 58568966242. Stop stays 0.

## 2026-09-22 06:53 America/New_York

L4h is still open. Stops have stayed off. Leave the five research tickets until 13:56. Do not touch the 1-lot CADCHF sell 58568842287. The 13:52:06 board has nothing on sets 1 and 2 that will still be inside two bars at 13:56. Do not pre-pick from it. After the close, read a newer stamp. If it has no M5 or slower FIRE still inside the bar, with more room than the spread, send nothing.

## 2026-09-22 06:52 America/New_York

L4h is open. Leave these until 13:56 server. Do not add another. The guardian removed the stops, ret 10009. EURAUD and USDJPY were stripped twice because the script put the stop back once.

- AUDUSD buy 58568878120, 13:51:13. The 13:40 five-minute bar was already past two periods.
- EURAUD buy 58568878211, 13:51:13. Set 3, M15 bar 13:30.
- EURJPY sell 58568878409, 13:51:14. Set 3, M15 bar 13:30.
- USDJPY sell 58568878545, 13:51:15. M1 bar 13:46 and a WAIT_LOADED promotion.
- AUDJPY sell 58568878881, 13:51:16. Set 3, M15 bar 13:30.

Do not touch the 1-lot CADCHF client sell 58568842287. The 100-lot CADCHF sell 58568786032 was closed by the client at 0.58327 for +122. That was not this magic.

## 2026-09-22 06:50 America/New_York

Magic 771249 is still flat. Do not touch CADCHF 58568786032 or 58568842287. Board stamp 13:49:46 has six slower fires inside two minutes of the two-period line and nothing else that passes. Send nothing. Stop stays 0.

## 2026-09-22 06:50 America/New_York

Magic 771249 is flat. Do not touch the two client CADCHF sells. The 100-lot ticket 58568786032 is now about −1,100, take profit 0.58317. The 1-lot ticket 58568842287 is about −2.

Board stamp 13:49:46. Six slower fires are inside two minutes of the two-period line. Send nothing. Stop stays 0.

## 2026-09-22 06:49 America/New_York

Magic 771249 is flat. Do not touch either client CADCHF sell.

- 58568786032, 100 lots, 0.58328, take profit 0.58317, floating about −1,832
- 58568842287, 1 lot, 0.58335, opened 13:49:03, floating about −10

The eyes file is still 13:46:53. Send nothing. Stop stays 0.

## 2026-09-22 06:48 America/New_York

L4g closed on the timer. Close reason Expert. Age 300–301 seconds. The resident script returned 10009 on all five. No broker stop. Batch about −0.29.

- EURUSD buy 58568712604 1.14675 → 1.14680, +0.05. The bar was the 13:30 five-minute bar and the spread on the pick was 0.
- EURCHF sell 58568712726 0.93863 → 0.93868, −0.06. Set 4.
- USDCHF sell 58568712844 0.81853 → 0.81851, +0.02. Set 3.
- GBPCHF sell 58568712967 1.09426 → 1.09425, +0.01. Set 4.
- CADJPY sell 58568713057 111.860 → 111.909, −0.31. WAIT_LOADED promotion.

The 13:46:53 board has five slower fires inside two minutes of the two-period line. Send nothing. Do not touch the 100-lot CADCHF client sell 58568786032. Stop stays 0.

## 2026-09-22 06:45 America/New_York

L4g is still open. Nothing on magic 771249 has closed. Stops have stayed off. Leave the five research tickets until 13:47.

The three 100-lot CADJPY sells were closed by the client at 13:45:13–13:45:18. Tickets 58568658992, 58568662829, and 58568663192. Close reason Client. About +1,847, +1,274, and +1,274. Do not reopen them.

The 13:44:47 board has nothing on sets 1 and 2 that will still be inside two bars at 13:47. Do not pre-pick from it. After the close, read a newer stamp. If it has no M5 or slower FIRE still inside the bar, with more room than the spread, send nothing.

## 2026-09-22 06:43 America/New_York

L4g is open. Leave these until 13:47 server. Do not add another. The guardian removed the stops, ret 10009.

- EURUSD buy 58568712604, 13:42:33
- EURCHF sell 58568712726, 13:42:33
- USDCHF sell 58568712844, 13:42:34
- GBPCHF sell 58568712967, 13:42:34
- CADJPY sell 58568713057, 13:42:35

EURUSD was the 13:30 five-minute bar, age about 12 minutes, spread 0. CADJPY is a WAIT_LOADED promotion. EURCHF and GBPCHF are set 4. USDCHF is set 3. Do not touch the three 100-lot CADJPY client sells, tickets 58568658992, 58568662829, and 58568663192. The 100-lot EURUSD buy 58568642470 closed on its take profit at 1.14669 for +400. That was not this magic.

## 2026-09-22 06:41 America/New_York

Do not touch these client tickets. They are 100 lots each, reason Client, comment blank, not magic 771249.

- EURUSD buy 58568642470, 1.14665, take profit 1.14669, floating about −1,200
- CADJPY sell 58568658992, 111.900, floating about +1,019
- CADJPY sell 58568662829, 111.890, floating about +382
- CADJPY sell 58568663192, 111.890, floating about +382

The 13:40:35 board has nothing to send. Send no research batch while these four are open. Stop stays 0.

## 2026-09-22 06:40 America/New_York

**Goal of this pass.** Score whether magic 771249 is making money on the demo book; document the lesson; no orders.

**Verified money.** MetaQuotes-Demo 5056316064. Balance 1,001,915.30. Equity 1,000,815.30. Floating −1,100.00. Open: ticket 58568642470 EURUSD buy 100 lots, reason Client — not magic 771249; do not touch it. Magic 771249 day result about −2.67 USD through L4f (not making money; flat on that magic). L4g picks unchanged. Desk WAIT_NO_TRADE.

**Send nothing. Do not run L4g. Stop stays 0.**

## 2026-09-22 06:39 America/New_York

Do not touch ticket 58568642470. It is a 100-lot EURUSD buy, reason Client, opened 13:38:40 at 1.14665, comment blank. It is not magic 771249 and it is not a research round-trip.

The 13:38:32 board has nothing to send. Three slower fires are inside a minute of the two-period line. The rest are one-minute bars, non-FX, wide spreads, or WAIT_LOADED. Send nothing. Stop stays 0.

## 2026-09-22 06:38 America/New_York

The book is flat. Do not send the four names from the 13:30 bar. Live prices have left that bar.

- EURCAD buy ask 1.60899 is above the high 1.60897.
- EURCNH buy ask 7.68122 is above the high 7.68058.
- GBPCHF sell bid 1.09452 is under the low 1.09464.
- NZDCHF sell bid 0.46995 is under the low 0.46997.

That bar also hits the two-period line at 13:40. Send nothing. Do not pad from the L4g pick file. Stop stays 0.

## 2026-09-22 06:37 America/New_York

Do not run the L4g pick file. EURAUD is an M1 fire, the metals are not six-letter FX, and that GBPAUD bar is stale. The EURCNH row in that file is WAIT_LOADED. It is not the row below.

Board stamp 13:36:27. The book is flat. Four Dual CCI set 2 fires on the 13:30 five-minute bar pass, with fire_long or fire_short equal to 1. The bar dies at 13:40. Send these four only if the live price is still inside the bar. Stop stays 0. Do not add a fifth.

- EURCAD BUY, low 1.60861, forming 1.60881, spread 3, room 20. Skip if price is under 1.60861.
- EURCNH BUY, low 7.67898, forming 7.68044, spread 13, room 146, fire_long=1. Skip if price is under 7.67898.
- GBPCHF SELL, high 1.09511, forming 1.09471, spread 3, room 40. Skip if price is over 1.09511.
- NZDCHF SELL, high 0.47026, forming 0.46999, spread 3, room 27. Skip if price is over 0.47026.

Reason on all four is cci30_reclaim_sma. The guardian is still on the USDCHF chart.

## 2026-09-22 06:36 America/New_York

Supervisor pass. Demo book is still flat: balance 1,001,715.30, equity 1,001,715.30, floating 0. Magic 771249 is about −2.67 USD on the day. Today’s target and risk floor are blank, so the desk act stays WAIT_NO_TRADE. Do not run the L4g batch.

The five names in the L4g pick file fail the runner’s own gate. EURAUD is an M1 fire. EURCNH, XAGUSD, and XAGEUR are WAIT_LOADED, and XAGEUR spread is 43. GBPAUD SELL, Dual CCI set 2, M5 bar 13:25, was already wider than the bar at 06:34. At 06:36 that bar is past two M5 periods, so it is stale. Send nothing. Do not pad those five back in. Stop stays 0. The pick file still carries `sl_points_planned` 80. That is the stop that closed EURCNH inside the signal bar. The open path must keep stop 0.

## 2026-09-22 06:34 America/New_York

The book is still flat. Nothing closed on this pass. Board stamp 13:34:16. GBPAUD SELL set 2, the 13:25 five-minute bar, has traded through its high: forming 1.87889, high 1.87885, spread 8. Do not send it. The other official fires on sets 1 and 2 are 14 one-minute bars, 3 non-FX names, or 3 WAIT_LOADED promotions. Send nothing. Do not pad to five. Stop stays 0.

## 2026-09-22 06:32 America/New_York

L4f closed on the timer. Close reason Expert. Age 300 seconds. The resident script returned 10009 on all five. No broker stop. Batch about −0.62.

- EURCAD buy 58568462450 1.60874 → 1.60869, −0.04
- GBPUSD sell 58568462582 1.33652 → 1.33677, −0.25
- USDCAD buy 58568462698 1.40366 → 1.40337, −0.21
- EURGBP sell 58568462782 0.85754 → 0.85757, −0.04
- GBPCAD buy 58568462879 1.87597 → 1.87586, −0.08

The book is flat. On the 13:31:56 stamp one row is still inside two bars: GBPAUD SELL, Dual CCI set 2, M5 bar 13:25, high 1.87885, forming 1.87881, spread 9, reason cci30_reclaim_sma, fire_short=1. The room left to the high is 4 points and the spread is 9, so the quote is already wider than the bar that is left. Do not send it. Send nothing until a newer stamp shows an M5 or slower FIRE whose distance to the bar edge is larger than the spread. Do not pad to five. Stop stays 0.

## 2026-09-22 06:30 America/New_York

L4f is still open. Leave the five tickets until 13:31 server. The 13:29:25 board has 16 one-minute fires, 3 WAIT_LOADED promotions, and 1 row with a bad spread. Nothing on sets 1 and 2 is an M5 or slower FIRE that will still be inside two bars at 13:32. Do not pre-pick from that stamp. After the close, read a newer stamp. If it still has nothing inside two bars, send nothing. Stop stays 0.

## 2026-09-22 06:27 America/New_York

L4f is open. Leave these until 13:31 server. Do not add another name. The guardian removed the stops, ret 10009. EURCAD and GBPCAD were stripped twice because the script put the stop back once.

- EURCAD buy 58568462450, opened 13:26:51
- GBPUSD sell 58568462582, opened 13:26:52
- USDCAD buy 58568462698, opened 13:26:53
- EURGBP sell 58568462782, opened 13:26:53
- GBPCAD buy 58568462879, opened 13:26:54

EURCAD was an M1 bar from 13:23, age 231 seconds. The other four were WAIT_LOADED, not FIRE: GBPUSD set 3 M15 bar 13:00 with spread 0, and USDCAD, EURGBP, GBPCAD set 4 M30 bar 12:30. A retcode 10016 means skip that symbol. It does not mean make the stop wider than 80 points. The 13:26:48 board had 15 fast fires and no M15 or slower fire. The 13:29:25 stamp is newer and still has nothing that will be alive at 13:31: 16 one-minute fires, 3 WAIT_LOADED promotions, and 1 spread reject. Do not pre-pick from it. After these tickets close, send nothing unless a stamp written after the close shows an M5 or slower FIRE still inside two bars. Stop stays 0.

## 2026-09-22 06:24 America/New_York

L4e closed on the timer. Close reason Expert. Age 300 seconds. No broker stop. The chart advisor returned 10027 on USDCAD and closed nothing. The resident script closed the other three, ret 10009. Batch about −0.35.

- CADCHF sell 58568324211 0.58373 → 0.58390, −0.21, age 300
- EURUSD sell 58568324325 1.14620 → 1.14628, −0.08, age 300
- GBPUSD buy 58568324455 1.33677 → 1.33676, −0.01, age 300
- USDCAD sell 58568324777 1.40341 → 1.40348, −0.05, age 300

USDSEK never filled (retcode 10016, invalid stops). The four that filled were not fresh fires: an M1 promotion and three WAIT_LOADED rows. The book is flat. The 13:24:45 stamp still has one passing row, EURCHF SELL set 2, M5 bar 13:15, age 585 seconds, forming 0.93915 under high 0.93938. That bar hits the two-period line at 13:25. Do not send it. Send nothing until a newer stamp shows an M5 or slower FIRE still inside two bars, spread 1 to 20, live price still inside the bar. Do not pad to five. Stop stays 0.

## 2026-09-22 06:21 America/New_York

The four L4e tickets stay open until 13:23 server. Do not add to them. On the 13:20:33 board one row passes: EURCHF SELL, Dual BB set 2, M5 bar 13:15, high 0.93938, low 0.93892, close 0.93900, forming 0.93903, spread 1, reason reclaim_tight_middle, fire_short=1. That bar is still the latest closed M5 until 13:25. After the four are flat, re-read the board. Send EURCHF only if that same bar is still inside two M5 periods and the live bid has not traded above 0.93938. Send that one name. Do not pad to five. Stop stays 0.

## 2026-09-22 06:19 America/New_York

L4e is open. Leave CADCHF 58568324211, EURUSD 58568324325, GBPUSD 58568324455, and USDCAD 58568324777 until 13:23 server. Do not add a fifth. The guardian already removed the 80-point stops (ret 10009). USDSEK did not fill: retcode 10016, invalid stops.

None of the four was a fresh official fire. CADCHF was an M1 bar from 13:14, age 250 seconds, and the cmp said official_act=WAIT_LOADED with fire_short=0. EURUSD was set 4, M30 bar 12:30, WAIT_LOADED. GBPUSD and USDCAD were M5 bars from 13:05, age 790 seconds, both WAIT_LOADED. After this batch closes, send only a row whose act is FIRE_BUY or FIRE_SELL, whose cmp does not contain official_act=WAIT_, whose anchor is M5 or slower, whose bar age is under two periods, and whose spread is from 1 to 20. Stop stays 0. If fewer than five rows pass, send fewer.

## 2026-09-22 06:16 America/New_York

Board stamp 13:16:23. The book is flat. Send nothing. Of the official FIRE rows on sets 1 and 2, 10 are M1 and already stale on a two-minute scan, 1 slower row is older than two anchor periods, and 13 are not six-letter FX. Do not pad with those. Stop 0 still applies when a later stamp does pass.

## 2026-09-22 06:15 America/New_York

Board stamp 13:14:22. The book is flat. A full eyes scan takes about two minutes (13:12:21 then 13:14:22), so an M1 fire is already older than two one-minute bars when the file is written. Do not trade an M1 row off this file. At that stamp one M5 row passed, NZDCHF SELL set 2 bar 13:05. By 13:15 that bar is at the two-period line. Do not send it. Send nothing until a newer stamp shows an M5 or slower FIRE whose bar is still inside two anchor periods, whose spread is above 0, and whose live price has not left that bar. Do not pad to five.

## 2026-09-22 06:14 America/New_York

L4d closed on the timer. Close reason Expert. Age 300–301 seconds. The chart advisor returned 10027 and closed nothing. The resident script returned 10009.

- NZDUSD buy 58568161598 0.57465 → 0.57406, −0.59
- EURUSD buy 58568161719 1.14678 → 1.14635, −0.43
- AUDUSD buy 58568161897 0.71174 → 0.71145, −0.29
- EURCHF sell 58568162117 0.93885 → 0.93926, −0.50
- GBPCHF sell 58568162238 1.09446 → 1.09520, −0.90

Batch about −2.71. EURUSD and AUDUSD were already under the signal-bar low at the fill. NZDUSD had a zero printed spread and a bar behind the latest M5 close. EURCHF’s M1 bar was behind 13:08. GBPCHF was on the latest closed M15 bar and was still the largest loss, so the fresh-bar gate is not a promise of profit. It only keeps the sample on a bar that still matches the fire.

Next open: stop 0, target 0, spread above 0, price still on the right side of that bar, and the bar younger than two anchor periods. Desk target and risk floor are still blank, so the doctrine act stays WAIT_NO_TRADE.

## 2026-09-22 06:12 America/New_York

L4d is still open. No stop on the tickets. Do not close them before about 6:14:07.

The fills already broke the closed-bar relation. A buy whose price is under that bar's low is not a launch anymore. A sell whose price is over that bar's high is not one either. Skip the order when that is true. Skip when `spread_points` is 0. Skip when the signal bar is older than two anchor periods, because that bar is no longer the latest closed bar.

- EURUSD buy 1.14678. Signal bar 13:03 low was 1.14686. The fill is under the low, and at 13:09 the latest closed M1 bar was 13:08.
- AUDUSD buy 0.71174. Signal bar 13:03 low was 0.71181. The fill is under the low.
- NZDUSD buy 0.57465. Signal bar 12:55, spread printed 0. At 13:09 the latest closed M5 bar was 13:00.
- GBPCHF sell used the 12:45 M15 bar. That was still the latest closed M15 bar at 13:09. The earlier note that called 13:00 the closed bar was wrong; 13:00 was still forming.
- EURCHF sell 0.93885 sat on the 13:05 bar high. That M1 bar was already behind 13:08.

The eyes board file was rewritten at 13:12:21. Dual BB rows now print `struct_short` and `fire_short`.

## 2026-09-22 06:09 America/New_York

L4d opened at 6:09:07 with stops again. The resident script stripped all five within two seconds (`guard_strip` ret=10009). They stay open until about 6:14:07. Do not replace the script on the USDCHF M1 chart.

- NZDUSD buy 58568161598 @ 0.57465
- EURUSD buy 58568161719 @ 1.14678
- AUDUSD buy 58568161897 @ 0.71174
- EURCHF sell 58568162117 @ 0.93885
- GBPCHF sell 58568162238 @ 1.09446

No close on this tick. The opener that built L4d still sent a stop. The patched `run_batch3_roundtrip.py` was not the path used.

## 2026-09-22 06:08 America/New_York

Board stamp 13:06:57. The book is flat. Next five, one per symbol, stop 0, target 0, close at five minutes. These passed `act` FIRE, reason not `emerged_no_edge`, no `official_act=WAIT_` promotion, FX only, spread at most 20 points, and spread / bar high−low at most 0.25. Symbols from the 6:04 batch are left out.

- EURUSD BUY, Shifted envelope set 1, M1 bar 13:03, `full_body_above_tunnel`, spread 1 point, about 4% of the bar.
- EURCHF SELL, RSI-BB tension snap set 2, M5 bar 13:00, `rsi2_reclaim_upper_band`, spread 3, about 5% of the bar.
- GBPCHF SELL, RSI-BB tension snap set 2, M5 bar 13:00, `rsi2_reclaim_upper_band`, spread 4, about 5% of the bar.
- AUDJPY SELL, Dual CCI slingshot set 2, M5 bar 13:00, `cci30_reclaim_sma`, spread 3, about 7% of the bar.
- NZDCAD BUY, Shifted envelope set 2, M5 bar 13:00, `full_body_above_tunnel`, spread 3, about 9% of the bar.

Skip USDSEK Dual CCI set 1. The act says FIRE_SELL and the reason is `emerged_enter_pullback`, but `cmp` says `official_act=WAIT_LOADED` and `fire_short=0`. That is a promotion, not a release. Desk target and risk floor are still blank, so the doctrine act stays WAIT_NO_TRADE. These five are the research sample only.

## 2026-09-22 06:06 America/New_York

Correction. Do not skip a short row because `cmp` contains `fire_long=0`. The Dual BB line only prints the long flag. A short fire still has `fire_long=0`. EURJPY `58567940004` was `act=FIRE_SELL`, reason `reclaim_tight_middle`, and the loss was the five-minute path, not a false stamp.

Open the next row only when `act` is `FIRE_BUY` or `FIRE_SELL` and the reason is not `emerged_no_edge`. Keep stop 0 and target 0. Skip when spread / bar high−low is above 0.25. `official_act=` is absent when emergence does not yet have three samples; that absence is not a veto.

## 2026-09-22 06:05 America/New_York

The four L4c tickets that still had no stop closed on the timer. Close reason Expert. Age 300 seconds. Exit prices are not the old 80-point stops.

- EURJPY sell 58567940004 179.923 → 179.935 at 6:04:48, −0.08. Old stop was 180.003. `guard_close` ret=10009.
- GBPJPY sell 58567940369 209.780 → 209.782 at 6:04:49, −0.01. Old stop was 209.860. `guard_close` ret=10009.
- USDCHF sell 58567940558 0.81902 → 0.81854 at 6:04:49, +0.59. Old stop was 0.81982. `guard_close` ret=10009.
- USDJPY sell 58567940903 156.899 → 156.898 at 6:04:50, +0.01. Old stop was 156.979. `holdclose_close` ret=10009.

Those four are about +0.51. EURCNH was already a stop-out at 6:00:19 for −0.12, so the batch is about +0.39. The chart advisor printed `hold5_close` ret=10027 on all four and closed nothing.

EURJPY was the timed loser and its board `cmp` had `fire_long=0` with no `official_act=FIRE_SELL` stamp. That row should have been skipped. This one batch does not prove the stamp is an edge: USDCHF also lacked the stamp and paid the gain. Keep the skip until there are 20 stamped fires and 20 unstamped rows. Do not rewrite 007. Desk target and risk floor are still blank, so the doctrine act stays WAIT_NO_TRADE.

## 2026-09-22 06:03 America/New_York

The four remaining L4c tickets are still open with no stop. A resident script on USDCHF M1 printed `guard_start` at 6:03:22 and will close magic 771249 at age 300 seconds. Do not replace the script on that chart.

`run_batch3_roundtrip.py` and `run_roundtrip_py.py` now send stop 0 and no longer put a stop back on after the fill. The next lock only keeps a row when `cmp` contains `official_act=FIRE_BUY` or `official_act=FIRE_SELL` on that side, and when spread / bar high−low is at most 0.25.

## 2026-09-22 06:00 America/New_York

EURCNH buy 58567939657 filled 7.68076 at 5:59:48 and the broker stopped it at 7.67996 at 6:00:19, 31 seconds later, profit −0.12. The signal bar ran 7.67931 to 7.6832, so the 80-point stop was inside that bar. The other four L4c tickets had their stops removed at 6:00:36 (`ret=10009`) and stay open until about 6:04:50. Do not attach another script to chart `128968169154443374` until that close prints.

Measurable change for the next open, before any order:

1. Send stop 0 and target 0. An 80-point stop is still a broker exit. Mark's hold is five minutes, then a market close.
2. Open the row only when that symbol's board `cmp` string contains `official_act=FIRE_BUY` or `official_act=FIRE_SELL` and the order side matches it. `fire_long=1` without that stamp is not a fire. EURJPY in this batch has `fire_long=0` and no `official_act` stamp, and it was still sent.
3. Skip the row when spread divided by the last closed bar's high−low is above 0.25. A five-minute round-trip whose cost is a quarter of the bar cannot show an edge. This batch's five FX spreads are inside that line (about 3% to 8% of the signal bar). The stop is the failure, not the spread.

These are research samples. Desk target and risk floor are still blank, so the doctrine act stays WAIT_NO_TRADE. Do not rewrite 007.

## 2026-09-22 05:57 America/New_York

L4b closed on the timer, not on the stop. Opened 5:51:50–52 with stops. Those stops were removed at 5:56:14 (ret 10009). Closed at 5:56:52–53, age 300–302 seconds, close reason Expert.

- AUDJPY sell 58567653391 111.717 → 111.712, +0.03. Old stop was 111.792.
- CADJPY sell 58567653539 111.926 → 111.895, +0.20. Old stop was 112.006.
- CHFJPY sell 58567653689 191.796 → 191.738, +0.37. Old stop was 191.875.
- EURGBP buy 58567653864 0.85778 → 0.85776, −0.03. Old stop was 0.85698.
- EURNZD sell 58567654047 1.99608 → 1.99486, +0.70. Old stop was 1.99688.

Batch result about +1.27 on 0.01. This is a research sample, not an official S1–S4 fire. The 5:38 batch died on stops in seconds and cannot be compared to this one.

The chart advisor printed hold5_strip ret=10027 (autotrading refused for that expert) and never closed anything. The script on its own chart did both jobs. Measurable change: open the next five-minute round-trip with no stop and no target. If a stop is already on the ticket, strip it from a script on a chart that nobody else replaces until the close. Do not trust the expert timer while it returns 10027.

## 2026-09-22 05:54 America/New_York

Mentor tick. The 5:46 batch is already closed (see 5:52). The open book is unchanged: five L4b tickets from 5:51:50, still inside the five minutes, still with the stops the other agent put on the order. A chart advisor now closes magic 771249 at 300 seconds, so the next script on another chart cannot orphan the hold. Measurable change: do not put a stop on a five-minute research round-trip. The exit is the advisor at five minutes.

## 2026-09-22 05:52 America/New_York

The 5:46 batch stayed open with no stop and was closed by script at 5:52:42, about six minutes after the fill. The sleeper on the chart was replaced at 5:51 by a new batch, so the five-minute close was late. Measurable change: one round-trip owns the chart until its close. Do not start the next script on that same chart while the hold is sleeping.

A second batch opened at 5:51:50 with stops on the order (comment L4b). Those stops are the same failure mode as 5:38 if they are inside the noise. Leave them until 5:56:50, then close them. Do not add another batch on top.

## 2026-09-22 05:48 America/New_York

No close yet. The 5:46 batch is still open, magic 771249, 0.01 lot, no stop on the ticket:

- EURCHF sell 58567537971 @ 0.93880
- EURUSD sell 58567538183 @ 1.14628
- AUDUSD sell 58567538261 @ 0.71121
- USDCAD buy 58567538413 @ 1.40326
- CADCHF sell 58567538596 @ 0.58366

The script closes these about 5:51. Do not attach a stop before that. The 5:38 batch died because a three-spread stop was on the opening order. That is not a five-minute test.

Next batch: market order, no stop, no target, close only at five minutes. Official S1–S4 fires still need tide, regime, release, and a named invalidation. A forced research round-trip is not a doctrine fire.
