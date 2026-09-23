# Reader hypothesis

This note does not change S1–S4 act, the hold checks, or the exit.
The reader does not send an order. New orders stay SAFE_HOLD.

## Scored passes

- PROFITABLE: 781
- NOT_PROFITABLE: 1314
- UNRESOLVED: 85
- OTHER: 0

## Pass labels

- mean_reversion: 341
- momentum: 1419
- none: 420

## Alignment side

- ABOVE: 1239
- BELOW: 933
- SPLIT: 8

## Closed exits (ok only)

- momentum_dying: count=7 sum_profit=372.32 mean_profit=53.19 sides (buy=2, sell=5)
- will_not_rejoin: count=2 sum_profit=2834.06 mean_profit=1417.03 sides (sell=2)

## One hypothesis

Insufficient sample. momentum_dying has 7/20 closed tickets and will_not_rejoin has 2/20. The split is not promoted.

Promoted: no.

## Falsifier

After both reasons have 20 closed tickets, the hypothesis fails if the reason with the higher mean profit is no longer higher on the next 20 closes of that same reason.
