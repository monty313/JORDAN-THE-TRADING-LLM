# Assistant to Jarvis

- Clock: 2026-09-22 22:29:10
- Board ts: 2026.09.23 05:25:58
- Closed-score gap (from desk_state): Beat closed Client P/L +38535 on demo. Last named deadline: 00:36 America/New_York on 2026-09-23. Do not invent a new one. Score is closed P/L on magic 771249 opened after 12:36. Floating does not count.
- Mode: new orders stay SAFE_HOLD. A close is sent only for momentum_dying or will_not_rejoin on magic 771249. No reentry.

## Official FIRE (up to three)

- **GBPUSD** `FIRE_SELL` (S2 Dual BB pullback) — label **momentum** (above=0 below=7 alignment_side=BELOW htf_agree_count=6 pullback_min_undefined=true). Kill: RSI(14) closes back above SMA(1)+4 on M1, or official row loses FIRE (emerged_enter_pullback) L4 context only: last_up_frac=1.33457000 last_dn_frac=1.33371000 up_count_hint=4.00000000 dn_count_hint=3.00000000 (not a license) Learned P(momentum)=0.256 P(mean reversion)=0.744.
- **NZDCHF** `FIRE_SELL` (S2 Dual BB pullback) — label **momentum** (above=1 below=6 alignment_side=BELOW htf_agree_count=5 pullback_min_undefined=true). Kill: RSI(14) closes back above SMA(1)+4 on M1, or official row loses FIRE (emerged_enter_pullback) L4 context only: last_up_frac=0.47038000 last_dn_frac=0.46774000 up_count_hint=4.00000000 dn_count_hint=4.00000000 (not a license) Learned P(momentum)=0.256 P(mean reversion)=0.744.
- **USDCAD** `FIRE_BUY` (S3 Shifted envelope) — label **momentum** (above=6 below=1 alignment_side=ABOVE htf_agree_count=3 pullback_min_undefined=true). Kill: RSI(14) closes back below SMA(1)+4 on M30, or official row loses FIRE (full_body_above_tunnel) L4 context only: last_up_frac=1.40676000 last_dn_frac=1.40641000 up_count_hint=2.00000000 dn_count_hint=3.00000000 (not a license) Learned P(momentum)=0.271 P(mean reversion)=0.729.

## Exits

- Hold 58581979851 AUDNZD sell profit=11.42. Momentum still intact on the closed bar, or the board was not fresh.
- Hold 58581979863 AUDCAD sell profit=49.72. Momentum still intact on the closed bar, or the board was not fresh.
- Hold 58582036910 NZDJPY sell profit=6.35. Momentum still intact on the closed bar, or the board was not fresh.
- Hold 58582175913 XAUUSD sell profit=-2030.00. Momentum still intact on the closed bar, or the board was not fresh.
- Closed 58582198680 EURUSD buy profit=40.00 reason=will_not_rejoin. No reentry.
- Closed 58582198688 GBPUSD buy profit=70.00 reason=will_not_rejoin. No reentry.
- Closed 58582198700 USDJPY sell profit=82.49 reason=will_not_rejoin. No reentry.
- Closed 58582198713 USDCHF sell profit=182.64 reason=will_not_rejoin. No reentry.
- Closed 58582198718 AUDUSD buy profit=90.00 reason=will_not_rejoin. No reentry.
- Closed 58582198726 USDCAD sell profit=28.41 reason=will_not_rejoin. No reentry.
- Closed 58582198733 NZDUSD buy profit=100.00 reason=will_not_rejoin. No reentry.
- Closed 58582198744 EURGBP sell profit=-26.65 reason=will_not_rejoin. No reentry.
- Closed 58582198774 EURJPY sell profit=25.38 reason=will_not_rejoin. No reentry.
- Closed 58582198780 EURCHF buy profit=-231.35 reason=will_not_rejoin. No reentry.
- Closed 58582198808 GBPJPY sell profit=-19.04 reason=will_not_rejoin. No reentry.
- Closed 58582198822 AUDJPY sell profit=-69.80 reason=momentum_dying. No reentry.
- Closed 58582198864 EURAUD sell profit=78.16 reason=momentum_dying. No reentry.
- Closed 58582198886 GBPAUD sell profit=21.32 reason=momentum_dying. No reentry.
- Closed 58582198899 GBPCHF buy profit=-267.87 reason=will_not_rejoin. No reentry.
- Closed 58582198922 CADJPY sell profit=-12.69 reason=will_not_rejoin. No reentry.

Book (magic 771249): 20 open at the read, closed 16, left 4. Client tickets not touched. No reentry.

Freshness note: 13 symbol(s) not scored (board missing sides or data not fresh).

**Sample / model:** Chan logistic (sklearn-logistic) on Paul multi-TF sides M1-D1, anchor-vs-D1 disagreement, alignment counts, htf agree. y=1 momentum continuation paid; y=0 continuation failed (mean reversion on that bar). train=1682 test=721 holdout_accuracy=0.616. Desk +38535 is not a feature. No lot. No order.

