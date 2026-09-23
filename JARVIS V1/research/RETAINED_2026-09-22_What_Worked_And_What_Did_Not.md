# Retained — 2026-09-22, about 6:24 AM to 12:03 PM America/New_York

Halt record. Demo only. This file does not change `007`. It does not place, modify, or close trades. It keeps what the last five hours actually showed, so the next session does not start from zero and does not repeat the forced loop.

Sources: `LEARNING_LOG.md`, `research/SCORED_BATCHES.md`, `research/KNOWLEDGE_HARNESS_Momentum_Mean_Reversion.md`, `Strategies - Copy/Daily_RSI_Tide_Gate.md`, experiment handoff `2026-09-22_093347`.

## Goal this record is held against

Jarvis learns from success and failure, with a time and a goal on every pass, and becomes an expert advisor that can trade. The orientation Mark named: quantify momentum and mean reversion on multiple timeframes; a buy stays alive only while the tide measure is above SMA(1) shift +4; a sell stays alive only while it is below; more timeframe agreement should be better; a lower timeframe at odds with many higher ones is the pullback question.

What is computable today is narrower than that sentence. The only defined SMA(1)+4 rule is daily RSI(14) versus SMA(1) shift +4 on the RSI, gate G1. It is a permission stamp. It does not fire a scalp. `pullback_call` stayed undefined all morning. Desk act stays `WAIT_NO_TRADE` while today's target and today's risk floor are blank.

## What worked, and why

**Writing the closed result next to the gate stamp.** Thirty-seven batches (185 tickets, magic 771249, 0.01 lot) were scored only after they closed, against the G1 side from when they were opened. That is why the morning can say something definite. The sheet's own line holds: **no alignment count licenses an entry.** One batch is not a cutoff.

**The five-minute expert close, as an exit, not as an entry.** Batches that finished did so on a timed close (about five minutes, reason Expert), not because an 80-point broker stop was the plan. L4j had already shown a chart advisor failing to close one name while the others closed on the timer. The timer is what made the book flat so the score could be written. It is not a reason to open the next five.

**Small size, and not touching the other book.** Jarvis tickets stayed 0.01. A later request for $1000 per 15 minutes did not raise the lot. Client tickets (including 100-lot USDCAD and earlier NZDCHF) were left alone and were not counted as Jarvis profit or loss. That is why the magic day figure is interpretable at all.

**The harness kept the rule honest.** Mark's multi-timeframe sentence was saved as the learning target. The agents did not invent a price SMA(1)+4, a chop cutoff, or a second tide sensor per timeframe. G1 stayed a warning column. S1–S4 act was not rewritten from this experiment. `007` was not edited.

**The best closed batch still does not prove the rail.** L4r was the best scored batch: **+0.74**, all five tickets green, 4 on the daily rail and 1 mismatch. The mismatch was not the worst ticket. Four agrees netted +0.65 inside that one batch. That is a green batch. It is not a license, because batches with the same 4-agree shape also lost hard (L4y **−1.58**, L5g **−0.86**, L4s **−0.72**).

Other green scored batches, same caution: L5q +0.59, L5u +0.54, L5k +0.43, L5t +0.32, L4t +0.33, L5i +0.33, L4w +0.26, L5d +0.18, L5m +0.17, L5p +0.15, L4k +0.07, L4q +0.02. In several of those, a G1 mismatch was the best ticket (L5q USDCHF, L5u USDCHF, L5k USDCHF, L5p NZDUSD). Agreement was not what paid.

## What did not work, and why

**Forcing five trades every cycle.** The opener's handoff kept saying to continue with a forced five whenever quotes existed, and to mix directions. That is the opposite of the harness. The book was built by the clock, not by a relation that was still true on the closed bar. Day sum on the scored sheet, magic 771249 only, through the L5w close: **−13.25 USD across 229 closed tickets.** Later batches (through L6b) were opened after that sum and are not in it. L6b's handoff shows four of five names green in points and one red; those are points, not dollars, the batch was forced, and it was not scored against G1. Do not promote L6b into a method.

**Treating "how many timeframes agree" as an entry.** Full agreement lost: L4u was 5 of 5 on the daily rail and **−0.53**. L4m was 5 of 5 and **−0.26**. Full disagreement also lost: L4h was 0 of 5 on the rail and **−0.33**, every ticket red. Inside mixed batches the worst ticket was often a name that agreed with G1 (L5w USDCAD −0.31, L5a GBPUSD −0.48, L4y USDCHF −0.44, L5f's agrees were both red). A lower timeframe at odds with higher ones (`g2_odd`) was logged and was not a fire. The pullback call was never defined, so it never selected a trade.

**Saying "send nothing" in prose.** `MENTOR_INBOX.md` was full of "Send nothing" and "Stop stays 0" from 7:11 AM onward. The opener's gate was rewritten so those words do not count. It blocks only if the exact tokens `STOP_LEVEL_4_DEMO_AUTONOMY` or `STOP_FORCED_SIGNAL_LOOP` appear in a section **later than a cutoff the opener keeps moving forward.** At 12:00 that cutoff sat at 11:58 AM. That is why "STOP EVERYTHING" at 11:45 did not stop the machine. At 11:59 AM `run_batch51_l6c_forced.py` was already running and had opened five magic tickets (USDCAD buy, EURCHF sell, EURGBP buy, EURJPY sell, AUDCHF sell, comment `L6c m771249`). The supervisor log at 11:41 AM had already named this failure: recording a lesson did not change the next order. Two chats were split. One wrote "send nothing." The other wrote "continue with forced five."

**A learning log that cannot refuse.** Learning a better entry is possible only when a killed rule is refused by the thing that sends the order. The scorer and the sender were not the same process. Restoring `block_if_mentor_says_stop` on an old runner did not bind the next runner, which called only `block_if_fresh_stop_token`.

## What to keep using

- Student test before any act: which timeframe, which indicator, the SMA(1) shift +4 value, the live measure, above or below, and what kill closes back through that same line. If those cannot be read, the gate did not fire.
- Score a ticket only after it is closed, against the gate stamp from entry. Do not let the forming bar change the score.
- Demo only. Magic 771249 is the Jarvis book. Client tickets are not Jarvis.
- Lot stays 0.01 until Mark names a different size in the message that is allowed to send.
- `007` stays read-only. Doctrine changes wait in `JOURNAL.md` for Mark.

## Halt

At 12:03 America/New_York the inbox carries both stop tokens in a section after the 11:58 cutoff. The experiment folder contains `STOP_FORCED_SIGNAL_LOOP`. The gate returns block when that file exists, including if a later edit moves the cutoff past 12:03. The L6c process that was already inside its five-minute hold was left to close those five tickets. No successor batch is authorized.
