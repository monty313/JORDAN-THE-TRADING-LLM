# JarvisEyes board / tape schema

One row per `symbol × set_stack × strategy_id`. Board is replaced each full pass. Tape appends only when `closed_bar_time` or `act`/`active` changes for that key.

## Strategy families

| family | ids | Role |
|---|---|---|
| `OFFICIAL` | `S1` Dual CCI slingshot, `S2` Dual BB pullback, `S3` Shifted envelope, `S4` RSI-BB tension snap | Drive `tide` / `act` / `strategy_direction_conflict` on official sets 1–2 (3–4 optional inputs) |
| `EVIDENCE` | `S5` Regime gate evidence | Raw HTF relations + `UNDEFINED` where doctrine cutoffs are missing. Never fires alone. |
| `LEGACY` | `L1` Shift SMA, `L2` CCI momentum, `L3` Shift SMA tunnel, `L4` Fractals | Own `ACTIVE`/`INACTIVE`/`UNDEFINED` from written rules. **Never** mutates S1–S4 act/tide/conflict. |
| `GATE` | `G1` Daily RSI tide, `G2`–`G7` M1/M5/M15/M30/H1/H4 RSI tide (same RSI(14) vs SMA(1)+4 relation), `H1` Heikin Ashi door, `C1`–`C7` dual CCI extreme on M1/M5/M15/M30/H1/H4/D1 | Warning / momentum-identification sensors. Do not license or override S1–S4 scalp acts. `G1`–`G7`, `H1`, and `C1`–`C7` never drive `act`. |

`reward hacking.txt` is RL reward-shaping philosophy, **not** a chart sensor. No row, no fake ACTIVE flag.

## Columns

| Column | Meaning |
|---|---|
| `ts` | Pass write time `yyyy.MM.dd HH:mm:ss` |
| `symbol` | Exact MT5 symbol |
| `family` | `OFFICIAL` / `EVIDENCE` / `LEGACY` / `GATE` |
| `strategy` | `S1`…`S5`, `L1`…`L4`, `G1`…`G7`, `H1`, `C1`…`C7` |
| `plain_name` | Human label for mentor (e.g. `Dual CCI slingshot`) |
| `set` | Official set `1`…`4`, or `L` / `G` / `H` / `C` for fixed stacks |
| `anchor_tf` / `htf1_tf` / `htf2_tf` | Stack used for this row |
| `spread_points` | Current spread in points |
| `data` | `fresh` / `stale` / `thin` |
| `active` | `ACTIVE` / `INACTIVE` / `UNDEFINED` — setup lit by its own rules (legacy/gate/evidence). Official rows mirror act severity (`ACTIVE` on FIRE/WAIT_LOADED, else often `INACTIVE`) |
| `tide` | `long_only` / `short_only` / `flat` (official + G1); empty/`n/a` elsewhere when unused |
| `regime` | `bull_trend` / `bear_trend` / `UNDEFINED` |
| `state` | Topology state or `UNDEFINED` |
| `topology` | Named topology token |
| `act` | Official path only: `FIRE_BUY` / `FIRE_SELL` / `WAIT_LOADED` / `WAIT_NO_TRADE` / `KILL`. Legacy/gate use `n/a` |
| `reason` | Wait/kill/inactive token |
| `daily_rsi_warn` | `bull` / `bear` / `flat` / `thin` — copied onto official rows; G1 owns the gate |
| `closed_bar_time` | Closed bar time (index 1) on the row's decision TF |
| `open1` / `high1` / `low1` / `close1` | OHLC at closed bar 1 |
| `forming_close0` | Bar 0 telemetry only |
| `cmp` | Closed-bar comparisons that made ACTIVE/INACTIVE (semicolon `key=value` pairs) |
| `chop_token` | Always `UNDEFINED` until doctrine defines cutoffs |
| `expansion_token` | Always `UNDEFINED` until doctrine defines cutoffs |
| `raw_a`…`raw_f` | Strategy-specific numbers (see below) |

### `raw_*` by strategy

- **S1:** cci30, cci100, cci30_sma, cci100_sma, cci30_prev, cci_dist
- **S2:** bb100_mid, bb10_mid, sma50, bb_width, bb10_mid_prev, —
- **S3:** rail_high, rail_low, —, —, —, —
- **S4:** rsi2, rsi20, rsi2_bb_mid, rsi2_bb_lower, rsi20_bb_mid, rsi2_prev
- **S5:** bb200_mid_htf1, bb20_mid_htf1, bb200_mid_htf2, bb20_mid_htf2, —, —
- **L1:** sma_htf1, sma_htf2, sma_anchor, close_htf1_prev, —, —
- **L2:** cci30, cci100, cci30_sma, cci100_sma, price_sma, —
- **L3:** low_rail_htf, high_rail_htf, close_htf_prev, upper_anchor, lower_anchor, —
- **L4:** last_up_frac, last_dn_frac, up_count_hint, dn_count_hint, —, — (`state=UNDEFINED` if fire rule too vague)
- **G1–G7:** rsi14, sma1_shift4, —, —, —, — (identical relation per row TF; G1=D1, G2=M1, G3=M5, G4=M15, G5=M30, G6=H1, G7=H4)
- **C1–C7:** cci30, cci100, sma1_shift4 of CCI30, sma1_shift4 of CCI100, —, — (typical price; C1=M1, C2=M5, C3=M15, C4=M30, C5=H1, C6=H4, C7=D1). Level and SMA confirmation are logged. They do not change S1–S4.
- **H1:** ha_green_m5, ha_green_m15, ha_red_m1, ha_red_m5, ha_red_m15, ha_green_m1

## Conflict roll-up (OFFICIAL only)

If `S1`–`S4` on the same `symbol`+`set` would both `FIRE_BUY` and `FIRE_SELL`, those fire rows become `tide=flat`, `act=KILL`, `reason=strategy_direction_conflict`. Legacy/gate rows are untouched.

## Phone push

`SendNotification` only when an **official** closed-bar act transitions to `FIRE_BUY`, `FIRE_SELL`, `KILL`, or conflict. Not on legacy ACTIVE flicker. State in `jarvis/notify_state.csv`.

## Paths

- Board: `MQL5/Files/jarvis/board.csv`
- Tape: `MQL5/Files/jarvis/tape/YYYY-MM-DD.csv`
- Notify: `MQL5/Files/jarvis/notify_state.csv`
