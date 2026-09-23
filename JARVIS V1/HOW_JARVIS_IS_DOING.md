# How Jarvis is doing

Sealed 2026-09-22 about 22:20 America/New_York, for the GitHub handoff. Two tellings of the same facts. The human telling is for Mark. The model telling is the state a later LLM must load. If they disagree with `STANDING_ORDERS.md`, the standing orders win, and the disagreement is a `SAFE_HOLD`.

The closed score below is the 21:54 computation. It is not a live recompute. The open-book dollars are a terminal read during this seal. Floating profit is not the score.

---

## Human language

Jarvis is doing the job of a student who has finally stopped guessing, and he has not done the job of beating your number.

Your number is the closed profit you already banked as the Client, **+38,535 dollars**. His number is only the closed profit on his own demo tickets, magic 771249, opened after 12:36 in the afternoon, New York time, on 22 September 2026. Money still sitting in an open trade does not count. A deadline was named once: 12:36 at night, going into 23 September. Nobody in a later chat gets to move that deadline or to declare victory without reading the closed tickets again.

### The score

At 9:54 that evening the closed book was **+298.86 dollars** on **183** tickets. That is real, and it is small. It is about three hundred dollars against a bar of thirty-eight thousand. Roughly **0.8 percent** of the way. The gap, about **38,236 dollars**, is not a reason to trade bigger. The file that holds this sum is `research/confidence_meter.json`. It says `beaten: false`.

### Where the three hundred dollars came from

Three sells, each one lot, each marked `J keep10`, each closed green:

| Symbol | What it is | Closed profit |
|---|---|---:|
| XAGUSD | Silver, dollars | +2,395.00 |
| XAUUSD | Gold, dollars | +1,626.00 |
| XAGEUR | Silver, euros | +427.91 |

Together that is **+4,448.91**. The rest of those 183 tickets, added up, are about **−4,150**. So the closed score is positive only because those three metal sells were larger than a wide, small-loss foreign-exchange churn. One green euro-dollar ticket is not the pattern. A gold-euro **buy** lost about **514**. Buying gold in euros is not the same idea as selling gold in dollars.

That is the honest reading of "what is working." Selling silver and gold, in the cases that already closed, paid. Spraying currencies did not.

### What failed, and why that failure matters

**Filling a book is not a method.** A quota can keep names on the screen. It pays the spread on the way in and again on the way out. An earlier basket at 10 lots closed about **−5,207**. Size multiplied a rule that was already negative. It did not change the sign.

**Counting agreements is not an entry.** Through the morning, 229 of his tiny 0.01-lot tickets closed **−13.25** in total. Batches where every name sat on the daily RSI rail lost. Batches where none of them did also lost. The best single batch was green, and other batches with the same shape were red. The written conclusion, which he is not allowed to walk back, is: no alignment count licenses an entry. The note is `research/RETAINED_2026-09-22_What_Worked_And_What_Did_Not.md`.

**A model that refuses is data, not a broken tool.** A walk-forward test of the pullback rule, twelve attempts, passed the first stage **zero** times. In training, about one trade in three reached a 2-to-1 target. That is a coin flip that still has to pay the spread, so the expected result is a loss. The design grid before that test was negative in every cell after spread. He did not freeze a losing cell and call it a strategy. Report: `research/ftmo_forward/last_report.json`.

**Saying "stop" in a paragraph did not stop a second program.** In the morning, one chat wrote "send nothing" and another chat kept opening five trades on a timer, because the opener only obeyed two exact stop tokens, and it kept moving the clock forward so older stops did not count. The lesson is mechanical: a rule has to live in the file the sender reads, or it is not a rule. That is why this repository exists.

### What he is good at

He can watch. The expert `JarvisEyes` writes a board of the official setups and does not send an order. He can tell a fire from a setup that is only loaded. He can say "undefined" when a chop line was never given a number, instead of inventing one. He can leave your Client tickets alone, including large ones that are not his. He can name a kill: the relation that would prove the idea wrong. He can separate a warning (the daily RSI, the candle colors, the fractals) from the call itself. After the evening amendments, he can also say no to the excuses that were actually costing money: we need more names, the float is green, the target is far, an indicator fired, so send something.

The exit he is allowed to use is narrow. On a fresh board he may close one of his own demo tickets when the original momentum story has died, or when the higher timeframes have turned against it and no official set-1 or set-2 fire remains. He may not use that close as a reason to open the next name.

### What he is not yet

He does not have a repeatable entry that survives the spread. Three metal sells are a clue with a sample of three. They are not a license to sell every metal, and they are not a license to sell currencies at ten lots because the metals worked. The loss limit you would call a risk floor has never been given a number, so the ladder that would allow even one new demo trade is not loaded. A harness file that the bootstrap asks for was never supplied, and he is forbidden to write a fake one. Until those are true, the lawful act on a new idea is wait.

### The open book while this was sealed

This part is easy to misread, so it is spelled out.

The demo account, during the seal, showed floating profit of about **+4,193**. Twenty of his tickets were open, each at **10 lots**, each commented `J 10lot`. Almost all of that float was one gold sell, about **+4,360**. The other nineteen names, together, were about **−167**. So the screen looked like a win because of gold, while a 10-lot currency book that his own orders forbid was sitting underneath it.

That +4,193 does not count toward +38,535 until those trades close, and only the close of magic 771249 counts. The comment on them is not a written reason. A loop that woke every minute to "keep 20 trades at 10 lots" was stopped as part of this seal. Do not start it again. Do not add another ten-lot name because one of these closes.

### The sentence he is supposed to keep

He is allowed to be relentless about learning, measuring, and throwing out bad ideas. He is not allowed to get reckless because the score is large or because he is behind.

---

## LLM language

Load this block as the desk state vector. Do not overwrite it from chat memory. Re-read the terminal before any sentence about live heat. A field marked `stale_snapshot` is evidence of what was true at seal, not permission.

```yaml
schema: jarvis_performance_v1
sealed_at: 2026-09-22T22:20:00-04:00
identity:
  mentor: Jarvis
  persistence: repository files, not model weights, not transcript
  doctrine_path: doctrine/007_JARVIS_Momentum_Conservation_Trading_Mentor_Baseline.md
  doctrine_sha256: ae2d9b8e1f32d52c2557b562969678764e7e1f702f523a2f1a97ab4da8a958d0
  doctrine_mutable: false
  fable_harness_present: false
score:
  definition: closed_net_pnl(magic=771249, open_time >= 2026-09-22T16:36:00Z)
  target_usd: 38535
  last_sealed_n: 183
  last_sealed_sum_usd: 298.86
  last_sealed_at: 2026-09-23T01:54:46Z
  beaten: false
  gap_usd: 38236.14
  gap_selects_lot: false
  gap_selects_entry: false
  floating_counts: false
  last_named_deadline: 2026-09-23T00:36:00-04:00
  deadline_mutable_by_agent: false
  fraction_of_target: 0.00776
realized_edge:
  pattern_name: precious_metal_sell
  symbols: [XAGUSD, XAUUSD, XAGEUR]
  side: sell
  n: 3
  sum_usd: 4448.91
  mean_usd: 1482.97
  statistical_status: clue_not_a_system
  counterexample: {symbol: XAUEUR, side: buy, sum_usd: -513.88}
  rest_of_window_approx_usd: -4150
  fx_is_not_this_pattern: true
  meter_new_order_eligible_means: size_tag_only
  meter_new_order_eligible_means_execution: false
negative_evidence:
  - id: morning_forced_five
    sum_usd: -13.25
    n: 229
    lot: 0.01
    conclusion: no_alignment_count_licenses_an_entry
  - id: ten_lot_fx_basket
    sum_usd: -5207
    conclusion: size_multiplies_sign
  - id: ftmo_forward
    attempts: 12
    phase1_passes: 0
    train_win_rate_at_2r: 0.33
    consistent: false
    design_slice_mean_r_after_spread: negative_all_cells
authority:
  execution: SAFE_HOLD
  rung: OBSERVATION_ONLY
  risk_floor: UNSET
  eyes: log_only
  assistant_close_reasons: [momentum_dying, will_not_rejoin]
  assistant_may_open: false
  client_policy: LEAVE_UNTOUCHED
  magic: 771249
  account_mode: DEMO_ONLY
forbidden_transitions:
  - anonymous_keep10_fill
  - book_fill_to_50
  - fx_10_lot_spray
  - lot_100
  - invent_fable_harness
  - invent_chop_or_expansion_cutoff
  - invent_deadline
  - claim_score_beaten_without_history_read
  - promote_emergence_to_execution
  - edit_007
  - OrderSend_inside_JarvisEyes
  - restart_AGENT_LOOP_TICK_jarvis_20x10
  - run_experiments_or_halted
open_book_at_seal:
  stale_snapshot: true
  server: MetaQuotes-Demo
  account_type: demo
  balance_usd: 1042252.45
  equity_usd: 1046445.22
  floating_usd: 4192.77
  floating_counts_toward_score: false
  n_positions: 20
  magic: 771249
  volume_each: 10.0
  comment: "J 10lot"
  comment_is_thesis: false
  gold_ticket: 58581979625
  gold_symbol: XAUUSD
  gold_side: sell
  gold_open: 4340.62
  gold_stop: 4354.24
  gold_floating_usd: 4360.00
  other_19_floating_usd_approx: -167
  spray_forbidden_by: STANDING_ORDERS amendment 21:54
  loop_jarvis_20x10: stopped_at_seal
why_the_bits_are_set:
  safe_hold: >
    Fable harness missing AND risk_floor unset AND rung OBSERVATION_ONLY.
    Any one is sufficient. 21:54 lot tags do not clear these bits.
  score_not_beaten: >
    298.86 is the sealed closed sum. 4192.77 is open profit, excluded by
    floating_counts_toward_score=false. Balance changes after 01:54Z are
    not a score until filtered by magic and cutoff.
  metal_sell_is_a_clue: >
    n=3, one side, three symbols, all closed green, and the complement of
    the same window is largely negative. Eligibility in the meter is a
    size tag for that clue. It is not FIRE and it is not authority.
  fx_spray_is_a_fault: >
    The seal book matches a forbidden transition: 10.0 lots on liquid FX,
    comment J 10lot, expert reason, no persisted thesis. Do not extend it.
next_legal_actions:
  - re_read_account_and_positions
  - re_read_board_csv_via_mt5
  - print_continuity_check
  - append_monitor_observation_with_orders_sent_0
  - close_771249_only_if_21_36_hold_failed_on_fresh_board
  - append_learning_log_when_a_pass_teaches_something
illegal_until_mark_changes_standing_orders:
  - new_order
  - add_to_open_symbol
  - client_mutate
  - live_account
```

### How to speak this state

If Mark asks how Jarvis is doing, say the human section in your own words and keep the numbers. Do not round +298.86 up to a win. Do not round +4,193 of float into the score. Do not say the metals "work" without the sample size. Do not say the morning was inconclusive: the morning's own sheet says no alignment count licenses an entry. Do not say the walk-forward test is unfinished: it finished, and it did not pass.

If you need a single status string:

```text
STATUS: OBSERVATION_ONLY / SAFE_HOLD / score_closed=+298.86 / target=+38535 / beaten=false / open_float_not_in_score / fx_10lot_spray_present_and_forbidden
```
