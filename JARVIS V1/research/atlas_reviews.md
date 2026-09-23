# ATLAS reviews

Append-only. Each review follows a scored five-signal batch. Locked signal reasons are not rewritten here.

## Review 20260922T090900Z

Completed batch: cycle `20260922T090338Z`.
Signals: USDCAD set 1 S3, CADCHF set 2 S3, EURAUD set 1 S1, EURCHF set 2 S2, EURNZD set 1 S2.
Session completed signals at this review: 20. Profitable: 2. Average net points: -41.7.

## Review 20260922T091712Z

Completed batch: cycle `20260922T090923Z`.
All five outcomes: UNRESOLVED. Demo `.sim` symbols returned no bid or ask. Unsuffixed EURUSD, GBPUSD, and USDCHF quotes were on the feed and were not used. No new research signals were locked. Scored sample stays 20.

## Note 20260922T092901Z — quote-identity correction

Mark corrected the desk: this MetaQuotes demo login uses unsuffixed Market Watch names. The 09:17Z quote-identity stop was a naming error, not evidence of a second instrument. Unsuffixed `EURUSD` (and the rest) are the demo book. Do not require `.sim`. Do not treat those quotes as live. Outcome lines for cycle `20260922T090923Z` stay UNRESOLVED; append-only correction records explain why a late rescore is invalid. Shadow experiment H-20260922-002 is not started — Mark has not approved it. No orders.

## Review 20260922T094401Z — Level 4 demo round-trip pass

Doctrine: research reasons locked unchanged. Common sense: MCP trade tools were blocked (`mcp_trade_allowed: false`); demo fills used an MQL5 script with magic 771249 and 0.01 lots. All five protective stops (~3 spreads) fired within minutes — too tight for a planned 5-minute hold. Hypotheses H-20260922-001/002/003 stay PROPOSED. No new live rule.


## Review 20260922T095702Z — Level 4 wide-SL five-minute batch

Doctrine audit: locked research reasons unchanged. Common sense: moving from ~3-spread stops to 80-point protective stops let the five-minute clock be the exit (all five closed by timed full close, not SL). MCP trade_* still blocked; demo fills via Python MetaTrader5. Hypotheses H-20260922-001/002/003 stay PROPOSED. No new live rule.


## Review 20260922T100459Z — Level 4 batch3

Doctrine audit: locked reasons unchanged. Common sense: EURCNH still stopped at the 80-point rail in ~31s; EURJPY/GBPJPY/USDCHF/USDJPY held to the timed close. MCP trade_* blocked; Python MetaTrader5 on demo. H-20260922-001/002/003 stay PROPOSED. No new live rule.


## Review 20260922T130525Z — Level 4 batch25 L5a

Doctrine audit: locked reasons unchanged. Common sense: EURCHF SELL 58571744778 +10; GBPCHF SELL 58571745050 -14; EURCNH BUY 58571745192 -47; AUDUSD SELL 58571745330 -11; GBPUSD SELL 58571745465 -48. One of five green. MCP trade_* blocked; Python MetaTrader5. H-20260922-001/002/003 stay PROPOSED. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T131130Z — Level 4 batch26 L5b

Doctrine audit: locked reasons unchanged. Common sense: NZDUSD SELL five_minute net=-21.0; CHFJPY SELL five_minute net=-11.0; EURAUD BUY five_minute net=4.0; EURCAD BUY five_minute net=30.0; CADJPY BUY five_minute net=-26.0. MCP trade_* blocked; Python MetaTrader5. H-20260922-001/002/003 stay PROPOSED. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T131820Z — Level 4 batch27 L5c

Doctrine audit: locked reasons unchanged. Common sense: USDCHF BUY five_minute net=-14.0; EURCHF BUY five_minute net=-17.0; GBPCAD BUY five_minute net=0.0; EURNZD BUY five_minute net=1.0; GBPCHF BUY five_minute net=-22.0. CHFJPY skipped this batch after opposite-side trades in L4z/L5b. MCP trade_* blocked; Python MetaTrader5. H-20260922-001/002/003 stay PROPOSED. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T132630Z — Level 4 batch28 L5d

Doctrine audit: locked reasons unchanged. Common sense: USDCAD BUY five_minute net=23.0; GBPAUD BUY five_minute net=-37.0; EURUSD SELL five_minute net=24.0; USDJPY BUY five_minute net=13.0; AUDJPY BUY five_minute net=-7.0. Skipped CHFJPY/EURCHF/GBPCHF after both-way trades. MCP trade_* blocked; Python MetaTrader5. H-20260922-001/002/003 stay PROPOSED. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T132800Z — Level 4 batch29 L5e aborted

Doctrine audit: locked reasons unchanged; no rewrite. Common sense: after L5a–L5d forbids and CHFJPY/EURCHF/GBPCHF skips, the closed-bar board offered only EURCNH SELL as a tradeable unsuffixed 0.01 FX setup (NZDCAD/NZDCHF FIRE but volume_min 0.1). No orders sent. Magic 771249 stayed flat. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T133730Z — Level 4 batch29 L5e forced

Doctrine audit: locked reasons unchanged. Common sense: prior L5e abort for thin FIRE board was wrong and overridden; forced five quote-backed round-trips ran (GBPUSD SELL five_minute net=-8.0; NZDUSD SELL five_minute net=-13.0; AUDUSD SELL five_minute net=-3.0; EURCAD BUY five_minute net=24.0; EURCHF BUY five_minute net=-14.0). Soft-avoided L5d pairs. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T134455Z — Level 4 batch30 L5f forced

Doctrine audit: locked reasons unchanged. Common sense: EURUSD SELL five_minute net=-31.0; USDCAD BUY five_minute net=-51.0; EURGBP SELL five_minute net=0.0; GBPCHF BUY five_minute net=-44.0; USDCHF BUY five_minute net=-57.0. Soft-avoided L5e pairs. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T135125Z — Level 4 batch31 L5g forced

Doctrine audit: locked reasons unchanged. Common sense: EURCHF SELL five_minute net=-5.0; EURJPY SELL five_minute net=-17.0; GBPUSD SELL five_minute net=-26.0; NZDUSD SELL five_minute net=-24.0; AUDUSD SELL five_minute net=-19.0. Soft-avoided L5f pairs. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T135900Z — Level 4 batch32 L5h forced

Doctrine audit: locked reasons unchanged. Common sense: EURCAD BUY five_minute net=-47.0; EURGBP SELL five_minute net=1.0; EURUSD SELL five_minute net=18.0; USDCAD BUY five_minute net=-19.0; USDCHF BUY five_minute net=12.0. Mixed 3 BUY / 2 SELL; soft-avoided L5g and did not re-stack GBPUSD/NZDUSD/AUDUSD SELL. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T140540Z — Level 4 batch33 L5i forced

Doctrine audit: locked reasons unchanged. Common sense: USDJPY BUY five_minute net=42.0; EURAUD SELL five_minute net=23.0; AUDJPY BUY five_minute net=32.0; EURCHF SELL five_minute net=-8.0; EURJPY SELL five_minute net=-31.0. Mixed 2 BUY / 3 SELL; soft-avoided L5h and did not re-stack GBPUSD/NZDUSD/AUDUSD SELL. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T141210Z — Level 4 batch34 L5j forced

Doctrine audit: locked reasons unchanged. Common sense: EURUSD SELL five_minute net=15.0; NZDUSD BUY five_minute net=-14.0; EURGBP SELL five_minute net=-17.0; USDCAD BUY five_minute net=6.0; AUDUSD BUY five_minute net=-8.0. Mixed 3 BUY / 2 SELL; soft-avoided L5i; NZDUSD/AUDUSD taken BUY not the banned SELL stack. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T141900Z — Level 4 batch35 L5k forced

Doctrine audit: locked reasons unchanged. Common sense: EURAUD SELL five_minute net=-15.0; USDCHF BUY five_minute net=24.0; AUDNZD BUY five_minute net=38.0; EURCHF SELL five_minute net=0.0; USDJPY BUY five_minute net=5.0. Mixed 3 BUY / 2 SELL; soft-avoided L5j; no GBPUSD/NZDUSD/AUDUSD SELL stack. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T142700Z — Level 4 batch36 L5m forced

Doctrine audit: locked reasons unchanged. Common sense: EURUSD SELL five_minute net=-12.0; AUDUSD BUY five_minute net=-14.0; EURCAD BUY five_minute net=9.0; AUDCHF SELL five_minute net=14.0; NZDUSD BUY five_minute net=20.0. Mixed 3 BUY / 2 SELL; soft-avoided L5k; no GBPUSD/NZDUSD/AUDUSD SELL stack. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T143300Z — Level 4 batch37 L5n forced

Doctrine audit: locked reasons unchanged. Common sense: USDCAD BUY five_minute net=5.0; EURGBP SELL five_minute net=-10.0; USDCHF BUY five_minute net=17.0; EURCHF SELL five_minute net=-27.0; GBPCHF BUY five_minute net=12.0. Mixed 3 BUY / 2 SELL; soft-avoided L5m; no GBPUSD/NZDUSD/AUDUSD SELL stack. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T144000Z — Level 4 batch38 L5p forced

Doctrine audit: locked reasons unchanged. Common sense: EURUSD SELL five_minute net=-6.0; NZDUSD BUY five_minute net=25.0; AUDJPY BUY five_minute net=16.0; EURJPY SELL five_minute net=-9.0; EURCAD BUY five_minute net=-11.0. Mixed 3 BUY / 2 SELL; soft-avoided L5n; AUDJPY/EURJPY 250-pt stops; no GBPUSD/NZDUSD/AUDUSD SELL stack. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T144600Z — Level 4 batch39 L5q forced

Doctrine audit: locked reasons unchanged. Common sense: USDCAD BUY five_minute net=19.0; EURGBP SELL five_minute net=-3.0; GBPCHF BUY five_minute net=12.0; EURAUD SELL five_minute net=-33.0; USDCHF BUY five_minute net=47.0. Mixed 3 BUY / 2 SELL; soft-avoided L5p; no GBPUSD/NZDUSD/AUDUSD SELL stack. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T145300Z — Level 4 batch40 L5r forced

Doctrine audit: locked reasons unchanged. Common sense: NZDUSD BUY five_minute net=-4.0; EURUSD SELL five_minute net=5.0; AUDCHF SELL five_minute net=-12.0; USDJPY BUY five_minute net=-13.0; EURCHF SELL five_minute net=-5.0. Mixed 2 BUY / 3 SELL; soft-avoided L5q; USDJPY 250-pt stop; no GBPUSD/NZDUSD/AUDUSD SELL stack. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T150000Z — Level 4 batch41 L5s forced

Doctrine audit: locked reasons unchanged. Common sense: AUDNZD BUY five_minute net=2.0; EURAUD SELL five_minute net=8.0; USDCAD BUY five_minute net=-16.0; EURGBP SELL five_minute net=1.0; USDCHF BUY five_minute net=-12.0. Mixed 3 BUY / 2 SELL; soft-avoided L5r; no GBPUSD/NZDUSD/AUDUSD SELL stack. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T150600Z — Level 4 batch42 L5t forced

Doctrine audit: locked reasons unchanged. Common sense: EURJPY SELL five_minute net=-31.0; NZDUSD BUY five_minute net=-33.0; EURUSD SELL five_minute net=36.0; USDJPY BUY five_minute net=76.0; AUDCHF SELL five_minute net=1.0. Mixed 2 BUY / 3 SELL; soft-avoided L5s; EURJPY/USDJPY 250-pt stops; no GBPUSD/NZDUSD/AUDUSD SELL stack. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T151300Z — Level 4 batch43 L5u forced

Doctrine audit: locked reasons unchanged. Common sense: EURGBP SELL five_minute net=10.0; USDCAD BUY five_minute net=21.0; USDCHF BUY five_minute net=14.0; EURAUD SELL five_minute net=5.0; EURCHF BUY five_minute net=4.0. Mixed 3 BUY / 2 SELL; soft-avoided L5t; no GBPUSD/NZDUSD/AUDUSD SELL stack. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T151900Z — Level 4 batch44 L5v forced

Doctrine audit: locked reasons unchanged. Common sense: EURUSD SELL five_minute net=-41.0; EURCAD BUY five_minute net=54.0; CHFJPY SELL five_minute net=-88.0; USDJPY BUY five_minute net=5.0; AUDCHF BUY five_minute net=-7.0. Mixed 3 BUY / 2 SELL; soft-avoided L5u; CHFJPY/USDJPY 250-pt stops; no GBPUSD/NZDUSD/AUDUSD SELL stack. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T152600Z — Level 4 batch45 L5w forced

Doctrine audit: locked reasons unchanged. Common sense: EURGBP SELL five_minute net=6.0; USDCAD BUY five_minute net=-44.0; EURAUD SELL five_minute net=15.0; EURCHF BUY five_minute net=12.0; EURJPY SELL five_minute net=-18.0. Mixed 2 BUY / 3 SELL; soft-avoided L5v; EURJPY 250-pt stop; foreign Client USDCAD not touched. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T153200Z — Level 4 batch46 L5x forced

Doctrine audit: locked reasons unchanged. Common sense: EURUSD SELL five_minute net=33.0 exit=1.14381; USDCHF BUY five_minute net=20.0 exit=0.82146; USDJPY BUY five_minute net=39.0 exit=157.417; AUDJPY SELL five_minute net=-3.0 exit=111.827; AUDCHF BUY five_minute net=-4.0 exit=0.58353. Mixed 3 BUY / 2 SELL; soft-avoided L5w; USDJPY/AUDJPY 250-pt stops; foreign Client USDCAD not touched; real MCP history exits. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T153900Z — Level 4 batch47 L5y forced

Doctrine audit: locked reasons unchanged. Common sense: USDCAD BUY five_minute net=55.0 exit=1.40723; EURJPY SELL five_minute net=12.0 exit=180.063; EURGBP BUY five_minute net=17.0 exit=0.8577; EURCHF SELL five_minute net=-4.0 exit=0.93964; GBPCHF BUY five_minute net=-25.0 exit=1.09548. Mixed 3 BUY / 2 SELL; soft-avoided L5x; EURJPY 250-pt stop; real MCP history exits. MCP trade_* blocked; Python MetaTrader5. H-002 not activated. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T154500Z — Level 4 batch48 L5z forced

Doctrine audit: locked reasons unchanged. Common sense: EURUSD SELL five_minute net=-6.0 exit=1.14341; EURCHF BUY five_minute net=4.0 exit=0.93972; EURCAD SELL five_minute net=-17.0 exit=1.60897; USDCHF BUY five_minute net=1.0 exit=0.82186; USDJPY BUY five_minute net=7.0 exit=157.48. Mixed 3 BUY / 2 SELL; soft-avoided L5y; USDJPY 250-pt stop; real MCP history exits. MCP trade_* blocked; Python MetaTrader5. H-002 not activated as live filter. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T155200Z — Level 4 batch49 L6a forced

Doctrine audit: locked reasons unchanged. Common sense: USDCAD BUY five_minute net=-2.0 exit=1.40733; EURAUD SELL five_minute net=-2.0 exit=1.61065; EURGBP BUY five_minute net=11.0 exit=0.85794; EURJPY SELL five_minute net=-10.0 exit=180.087; AUDCHF SELL five_minute net=-7.0 exit=0.58344. Mixed 2 BUY / 3 SELL; soft-avoided L5z; EURJPY 250-pt stop; real MCP history exits. Foreign Client tickets not touched. MCP trade_* blocked; Python MetaTrader5. H-002 not activated as live filter. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T155800Z — Level 4 batch50 L6b forced

Doctrine audit: locked reasons unchanged. Common sense: USDCHF BUY five_minute net=13.0 exit=0.8219; EURUSD SELL five_minute net=19.0 exit=1.14317; USDJPY BUY five_minute net=46.0 exit=157.542; EURCAD SELL five_minute net=33.0 exit=1.6086; EURCHF BUY five_minute net=-7.0 exit=0.93954. Mixed 3 BUY / 2 SELL; soft-avoided L6a; USDJPY 250-pt stop; real MCP history exits. Foreign Client tickets not touched. MCP trade_* blocked; Python MetaTrader5. H-002 not activated as live filter. 20260922T090923Z UNRESOLVED. No new live rule.

## Review 20260922T160500Z — Level 4 batch51 L6c forced

Doctrine audit: locked reasons unchanged. Common sense: USDCAD BUY five_minute net=2.0 exit=1.40726; EURCHF SELL five_minute net=-18.0 exit=0.93977; EURGBP BUY five_minute net=-9.0 exit=0.85789; EURJPY SELL five_minute net=-35.0 exit=180.132; AUDCHF SELL five_minute net=-16.0 exit=0.58365. Mixed 2 BUY / 3 SELL; soft-avoided L6b; EURJPY 250-pt stop; real MCP history exits. Foreign Client tickets not touched. MCP trade_* blocked; Python MetaTrader5. H-002 not activated as live filter. 20260922T090923Z UNRESOLVED. No new live rule.
