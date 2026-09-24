# The Method

Written for Jarvis and Jordan. Read this after `doctrine/007_JARVIS_Momentum_Conservation_Trading_Mentor_Baseline.md` and `mentorship/JARVIS_MENTOR.md`.

Those two files are the contract. They name the sets, the sensors, and the acts. This file is the reason the contract is shaped the way it is. If this file and the baseline ever disagree on a period, a shift, a timeframe set, or an act, the baseline wins. The baseline is read-only. This file does not create a new official strategy and it does not authorize a live order.

Every strategy in the `strategy` folder was read for this rewrite: the gravity sections, the four multi-timeframe entries, the RSI-band variant, the eleven portfolio audits, the gold factory units, the fourteen-strategy trend and reversion guide, the Venice notes, and the student results sheet. They are not fourteen methods. They are one method, plus a pile of single-chart recipes that become legal only when they are forced to obey it.

---

## 1. The method in one relation

Momentum is not a number on one chart. It is a heavier clock and a lighter clock read together.

The heavier clock is force. It is the higher timeframe, and inside one timeframe it is the slower sensor. It moves rarely. It is the mass. Price and every faster sensor orbit it. They can leave it. They come back to it unless a real new force has replaced it.

The lighter clock is velocity. It is the anchor timeframe, and inside one timeframe it is the faster sensor. It tells you whether the immediate swing is breathing against the mass or leaving with the mass.

A trade exists only when both clocks are named and they tell one story.

The sequence, said the way a mentor says it to someone about to click:

1. Both higher timeframes of the official set are on one side. If they disagree, the side is flat. The anchor is not allowed to pick a side.
2. The slow sensor on the anchor is still on that same side. The background has not given up.
3. The fast sensor shows which story this closed bar is. Against the slow sensor, the market is breathing. Back with the slow sensor, the market is leaving.
4. The anchor bar has closed. The forming bar is telemetry. It cannot create a fire, a kill, a cross, or a regime.
5. The relation that would prove the idea wrong is named before any size is discussed.
6. Heat, the daily floor, and whether this symbol is already an expression of the same signal are known. A blank floor is a wait.

Default is no trade. A setup earns permission.

There are exactly two trades inside that sequence.

**Breath.** The heavier clock is already on a side. The slow sensor is still on that side. The fast sensor, or price on the tight band, has moved the other way and has not come back. That state is loaded. It is not an entry. The entry is the release: the fast sensor crosses back to the slow side while the slow sensor and both higher timeframes are still there. The good trade feels hard, because at the moment of the dip the short-term chart still looks like it is going the other way.

**Launch.** Both clocks are already on the same side, and the fast sensor is with the slow sensor. Price is leaving with them. There is no breath to buy. There is a move already underway, and the candle body has cleared its structure while energy is still expanding. A stretched fast oscillator in that state is the launch itself. Fading it is the mistake.

One chart cannot tell those two apart. On one chart a dip and a breakout look like the same excitement. That is why every strategy in this desk is multi-timeframe. The second clock is not confirmation pasted on for confidence. The second clock is the instrument that classifies the bar.

---

## 2. Why it works

### Mass outranks the fast reading

Every trend sensor is a mass. Its mass is its timeframe first, then its period. A higher timeframe is heavier than a lower one even when the period is the same. On one timeframe, the longer period is heavier. H1 SMA(200) outweighs M15 SMA(200). H1 SMA(200) outweighs H1 SMA(20). The order is fixed when the sensors are chosen. Recent win rate does not promote a light sensor into the heavy seat.

The heavy mass sets the field. The light mass reports where price is inside that field, and when. A light mass never overpowers a heavy one. When they disagree, the heavy one keeps the side and the light one is demoted to timing. Disagreement blocks the entry. It does not flip the side.

That is why a beautiful one-minute short inside a one-hour uptrend is refused. The one-minute sensor is reporting a position inside the field. It is not a new field.

### A stretch is two different objects

An oscillator does not track price. It measures distance from a fixed middle built into its formula. RSI and Stochastic sit on 50. CCI sits on 0. Distance from that middle, by itself, is a measurement. It is not an instruction.

The same extreme has two mechanical meanings:

- The extreme has no heavy mass and no energy behind it. Price stretched away from its orbit with nothing pushing. The expected resolution is a snap back toward the heavier mass. Trading the extreme's direction is refused. This is the only place a fade is even a candidate, and only inside a range the heavier clock has already called a range.
- The extreme has the heavy mass on the same side, and energy is still building. The stretch is being driven. It extends. Trading against it is refused. This is the launch.

"Overbought" is not a side. It is a distance. The heavier clock decides whether that distance is a breath inside a trend, a launch, or a snap-back in a range.

### Breath compounds, counter-force decays

A fast orbit moving with the slow mass spends less energy per unit of travel. The light body is being pulled and pushed the same way, so the move goes farther. A fast orbit moving against the slow mass spends energy fighting the field. The move dies at the first fade in energy. That is the mechanical reason counter-gravity entries are forbidden no matter how extreme the fast sensor reads.

The forward shift is how you see that without guessing. Put a short average of the sensor forward under the current closed bar. If the raw value is on the trend side of where that average sat a few bars ago, the baseline itself is still climbing. The orbit is above the line and the line is rising. Momentum is being conserved. If the raw value has crossed back through its own shifted baseline, the push has interrupted. New entries stop on that bar.

The same test runs on energy. ADX and ATR above their own forward-shifted baselines means the move still has fuel. A directional cross while those baselines are falling is a trap wearing the costume of an early entry. Direction and energy are separate questions. A cross answers direction. It answers nothing about fuel. When fuel is absent, there is no smaller size and no wider stop. There is no entry.

### Agreement across speeds is one force, not a vote

Three periods of one family, each with its own smoothing line, all on the same side of equilibrium and of their own line, are one force seen at three masses. The slow period is the mass. It licenses. The fast period is the orbit. It times. That is compounding. CCI(14), CCI(100), and CCI(900) agreeing is stronger than any one of them because they are the same measurement at different weights.

Two of three is not a weak version of that. Two of three is the fast and the middle rallying against the slow mass. That is a counter-trend bounce. The output is no signal. There is no 2-of-3 grade, no size scaled to how many agreed, and no repair that swaps in an RSI because the slow CCI failed. An unrelated indicator agreeing is a coincidence of two measurements. It is not the same force.

Shifted copies of one average work the same way. Five SMA(4) lines at shifts 0 through 4, stacked in order and all on the trend side of SMA(50), are a unanimity family. A fan that has crossed itself is disagreement. The fresh bar where the fan finishes straightening is the event. The straight fan persisting afterward is a state. States license. Events enter.

### A state licenses. An event enters. A license is not used up.

Authorization lives in the heavier state. Entries live in a fresh event on the lighter clock. While the heavier state holds, each new release is its own trade. The last trade's loss, its win, and how long it was held are not inputs. The edge is the heavier state that licensed all of them, not the clock time of any one ticket.

A fast exit closes a trade. It does not close the permission to trade. If the heavier license is still true on the exit bar, the next fresh trigger in that direction is mandatory, subject to a new window, a reset decay clock, and one position per signal. Skipping it because the last one hurt is a rule break.

License failure and exit failure are different gates. When the license turns false, new entries stop on that bar. Open trades leave under their own exit rule. License failure does not flatten a position that still has a valid exit clock, and an exit rule does not reopen admission.

### Entry rights expire

A trigger is one closed bar: the bar the cross completed. A state can stay true for a long time after that. The state does not keep the entry right alive. Each signal type has a window counted in closed bars from that event. Outside the window the entry is refused even though the indicators still "look right." Price already sitting on the outer band, with no fresh event inside the window, has migrated from an entry location to an exit location.

Size decays on the same clock. Full risk near the event, less a few bars later, zero when the window is done. How convincing the picture still looks does not restore size.

### The two clocks also split the exit

Breath trades harvest the return leg. The same speed that timed the entry times the exit. Fast in, fast out. A pullback long that waits for the slow mass to flip has overstayed the bounce it bought.

Launch trades harvest the escape. The fast sensor got you in. A slower sensor gets you out. Fast in, mid out. Exiting a launch on the first fast-oscillator wiggle abandons the leg you came for and turns a launch into an unlicensed scalp.

Mixing those exits is an unlicensed trade even when every individual reading was correct. Every order carries one label, breath or launch, and the exit engine reads only the exit bound to that label.

### What "multi-timeframe" means on this desk

Official sets, from the baseline. The first timeframe is the anchor. It times. It never chooses a side against the two supports.

| Set | Anchor | Support 1 | Support 2 | Use |
|---|---|---|---|---|
| 1 | 1m | 15m | 30m | Fast scalp |
| 2 | 5m | 30m | 1h | Standard scalp |
| 3 | 15m | 1h | 4h | Intraday context |
| 4 | 30m | 4h | 1d | Position context |

Scalping lives on sets 1 and 2. Sets 3 and 4 are context. The older four-timeframe "extra confidence" stacks are reference. They are not a fifth official set.

A regime is agreement between at least two clocks computed on their own closed bars. One timeframe reading bullish is a local state. It has no authority to name the tide.

---

## 3. How a closed bar is read

Jarvis already speaks in this order. The physics underneath each step:

1. **Tide.** Both supports, independently, on one side. That is the heavy mass. `long_only`, `short_only`, or `flat`. Flat cannot be overridden by the anchor.
2. **Regime.** Trend, expansion, range, chop, or undefined. Chop is a census failure: price is not stacked on one side of the heavy reference. Chop produces more crosses and less trend. Event frequency is evidence against a trend, not for one. Range is its own book and is not secretly turned into a momentum trade.
3. **Breath or launch.** Slow sensor intact and fast sensor against it: loaded breath. Fast sensor back with it, body clearing structure, energy expanding: launch. Fast sensor extreme while the heavy mass is driving: still a launch. Do not rename it overbought and fade it.
4. **Act.** `FIRE` only when tide, regime, topology, and a fresh trigger are all true and risk is known. `WAIT_LOADED` when the heavier story is intact and the release has not printed. `WAIT_NO_TRADE` when there is no story. `KILL` when a required relation has broken. Name the broken relation.
5. **Finish.** On the next closed bars, the same predicate that licensed the entry is re-read. The first failure closes. A good entry that is no longer true is not defended by the memory of why it was taken.

The spoken block stays the one in the baseline: market, set, tide, regime, state, role map, topology, act, why, invalidation, risk. This file does not replace that block. It tells you what the words mean.

Role law, because a strategy that uses one sensor for two jobs is counting one measurement twice:

| Role | Question it answers | What it is allowed to produce |
|---|---|---|
| Force / gravity | Which side has permission? | A state. Never an entry. |
| Inertia | Is the background push still the same side? | A state. The slow sensor. |
| Velocity | Is this bar breathing or leaving? | The trigger event. |
| Equilibrium | Where is fair? | The line the breath returns to, or the line a launch must clear. |
| Energy / expansion | Is there fuel? | A state on its own axis: nothing, tradable, or great movement. Never a direction. |
| Exit | When is this ticket done? | An exit event. Never an entry. |

One instance, one role. If the same formula is needed twice, declare two instances.

Energy, so the words stay stable:

| Lighter clock | Heavier clock | Volatility state |
|---|---|---|
| Energy fails | anything | Nothing happening. No entry. |
| Energy passes | both energy sensors below their baselines | Nothing happening. |
| Energy passes | one of the two still above | Tradable. Breath is eligible. Launch is not. |
| Energy passes | both above, and the floor holds | Great movement. Breath and launch are both eligible. |

A bigger oscillator number is not energy. CCI above +100 is a stronger displacement. It does not answer whether ADX and ATR are still climbing their own baselines. Super, or launch-grade, is issued by the energy state, not by a louder oscillator.

Risk is the same for breath and launch. Amount at risk is at most 1% of equity. No order against the tide. A scale-in is allowed only while the original license still reads true on this closed bar. Instruments that move together, or two tickers from the same signal, are one bet. One signal source gets one position's worth of risk.

The stop sits where the topology becomes false. It does not sit at a round number, a Fibonacci percentage, or a fixed pip distance invented to look tidy.

---

## 4. The four official trades

These are the live library. Longs are written below. Shorts invert every comparison. Applied prices matter: the CCI slingshot uses typical price `(high + low + close) / 3`. The band strategies and the 50-period average use the close.

### S1 — Dual CCI shifted-SMA slingshot

This is the cleanest breath.

CCI 30 is velocity. CCI 100 is inertia. Each has an SMA 2 shifted forward 2 bars as its equilibrium. The shift is the persistence test: the average is placed where it can show whether the oscillator's own baseline is still rising.

On both higher timeframes, CCI 30 and CCI 100 are above their shifted averages. That is force. On the anchor, CCI 100 stays above its shifted average while CCI 30 falls below its own. The slow mass is still pushing. The fast orbit has dipped against it. Tension is loaded. That dip is the hard feeling. It is `WAIT_LOADED`, not a fire.

Fire when CCI 30 rejoins, back toward or through its shifted average, and both higher timeframes are still intact. Kill when CCI 100 loses its side, either higher timeframe loses its side, or the anchor starts crossing its average back and forth. A fast cross back does not rescue a slow CCI that has already failed.

Why it works: you are buying the light body as it stops fighting the heavy field and starts traveling with it. You are not buying "CCI 30 is low." Low without the heavy field is a snap-back the other way, or noise.

The source specifies only that breath. The continuation of the same pair is the other clock. Both higher timeframes are still above their shifted averages, and on the anchor CCI 30 is already with CCI 100, both above their own lines, and price is leaving. The method classifies that aligned state as a launch. The source does not give it a separate entry. Do not fade it because the fast CCI is high, and do not write a second fire and pretend the source did.

### S2 — Dual Bollinger breath

Same story on price instead of CCI. The wide band, period 100, deviation 0.5, shift +2, is inertia: the outer containment of the trend. The tight band, period 10, deviation 0.5, shift +2, is velocity. SMA 50 is the structural line that says the continuation is still the continuation.

Both higher timeframes hold price outside the wide band and the tight band, on the trend side. The anchor stays outside the wide band and closes through the tight band the other way. Broad containment is intact. Local velocity has turned down. That is the breath.

Fire when price reclaims the tight band and the wide containment is still true. Re-enter on a later touch of the tight band only while SMA 50 remains on the trend side of the wide band and the tide has not broken. Kill when the anchor accepts through the wide band, when SMA 50 no longer supports the side, or when the bands tangle into chop.

The legacy name "trend reversion" is a bad name. The source is a breath inside a trend that never left the wide field. You are not fading the trend.

The continuation of the same bands is the other reading. Price is already outside the wide band and the tight band on the anchor and on both supports, and SMA 50 is on that side. The method classifies that as a launch. The S2 source does not fire it. GV-015 does, on these exact bands. Live S2 stays the breath the source wrote. Do not fade the launch because price looks "too far" outside the tight band.

### S3 — Shifted price envelope

This is the launch.

On the higher timeframes, SMA 4 shifted forward 4 bars, once on the high and once on the low, is a forward-displaced tunnel. On the anchor the same average is shifted 2. Price has to be outside both rails on the higher timeframes and outside both rails on the anchor. A wick through the tunnel is not acceptance. The candle body clears it.

If that clearance follows a prior load, it is the release of a breath. If it arrives with expanding width and no prior load, it is a launch. Both are legal S3. Neither is a pullback that was entered late. There is nothing to fade.

Wait while the higher timeframes are aligned and the anchor body has not cleared. Kill when price loses the anchor tunnel, the higher rails lose alignment, or expansion collapses into chop.

Why the shift exists: an unshifted average tells you where price is relative to a line that already includes the current bar's neighbors. A forward shift puts an older baseline under the current bar, so you can see that the tunnel itself has moved. Clearing a tunnel that is still advancing is conserved momentum. Clearing a tunnel that has already flattened is a late poke.

The source specifies only that clearance. That is the launch. The breath of the same tunnel is the other clock. Both higher timeframes stay outside both rails. The anchor body comes back inside the tunnel, then clears it again on a later closed bar. The method classifies that second clearance as the release of a breath. The source does not write "buy the dip inside the tunnel." A wick is still not acceptance. Fading the first clearance because the fast price looks stretched is still refused.

### S4 — RSI tension snap

RSI 2 is velocity. RSI 20 is inertia. Each carries Bollinger bands of period 20, deviation 0.5, shifted forward 2. Both higher timeframes need both RSIs on the trend side of those bands. On the anchor, RSI 20 stays above its middle while RSI 2 drops through its lower band. That is a fast stretch inside a slow trend that is still allowed.

Fire when RSI 2 turns back out of that extreme and the higher timeframes are still there. Kill when RSI 20 loses its middle, either higher timeframe loses RSI force, or price structure contradicts the side.

This is a breath with a very fast velocity sensor. The source specifies only that breath: the fast RSI in the extreme, the slow RSI still on the side, both higher timeframes still there. The fire is the turn back out, not the print of the extreme.

The continuation of the same pair is both RSI 2 and RSI 20 already on the trend side of their bands on the anchor as well as on both supports. The method classifies that as a launch. The source does not fire an already-stretched RSI 2. RSI 2 prints extremes constantly. When RSI 20 and both higher timeframes are still driving, the extreme is the trend. Selling it is the mistake.

### The one-line test

Read the higher timeframe first. Then the slow sensor. Then the fast sensor.

| Higher timeframes | Slow sensor | Fast sensor | What it is | Act |
|---|---|---|---|---|
| Agree on a side | Still on that side | Against that side | Breath, loaded | Wait. Name the rejoin. |
| Agree on a side | Still on that side | Just crossed back | Breath, released | Fire shape, if regime, spread, heat, and the thesis also pass. |
| Agree on a side | Still on that side | Already with it, and price is clearing structure | Launch | S3 language. Do not call it a pullback. |
| Agree on a side | Lost that side | Either way | Force failed | Kill. |
| The two supports disagree | Anything | Anything | No permission | Flat. |

A fractal, a MACD cross, or a lone band touch does not fill a cell of that table.

### Sibling sensor, not a second library

`rsi + bb strategy.txt` tells the same story with different numbers: RSI 14, bands of period 10, deviation 1, shift 5, on three timeframes. The source writes both sides, unlike S4. The momentum buy is the continuation: RSI above its upper band on all three timeframes. The pullback buy is the breath: the two higher timeframes stay above the upper band, and the anchor RSI crosses back up through the middle. Sells invert both. The sets written in that file are 1m/15m/30m, 5m/1h/4h, and 15m/4h/1d. The first matches official set 1. The other two do not match sets 2 and 3. Live acts still use S4's sensors (RSI 2 and RSI 20, bands of period 20, deviation 0.5, shift +2) and the official sets. This file is the same principle in another costume. It does not add a set, and it does not replace RSI 2 / RSI 20.

---

## 5. The same method in the research portfolio

Sections 1 through 6 and section 8 of this folder are the audit language for that method. There is no section 7 in the folder. The eleven named strategies below are not extra edges. Each one is a host, a gate, or a broken host. A host is tradable only as a bundle: directional story, plus the energy gate, plus the 1% and one-signal risk map, plus the dual-timeframe gate on every grade, not only on the "super" grade.

The recurring repair is always the same. Most of these specs knew direction and forgot fuel. Oscillator magnitude was being asked to do the energy job. And several of them required the second timeframe only when they wanted to call the trade super. The second timeframe is the tide. It is required for every grade, or the grade is not a trade.

Sections 1 through 6 of the folder are the physics those audits sit on, not extra strategies. Gravity is mass and orbit: timeframe first, then period. A stretch without the heavy mass is a snap-back. A stretch with the heavy mass and with fuel is an extension. The five finding failures are vetoes: one timeframe is not a regime, chop is a failed census, a cross without fuel is not early momentum, two of three is not a weak yes, and one sensor cannot hold two roles. The five utilization failures are execution vetoes: a stale state is not an entry, the license is re-read every closed bar, size decays from the event, a fast exit does not spend the license, and two tickers on one signal are one bet. Pullback and super are the breath and the launch, and they do not share an exit. A higher-timeframe state that still holds is a standing license for the next fresh lighter-clock event. Nested periods of one family, all on the same side of equilibrium and of their own line, are one force. There is no section 7 in the folder.

### STRAT-001 — Regime pulse

Price versus the Bollinger middle is a mass. BB(200) middle is heavier than BB(20) middle. Higher-timeframe price above both middles is the tide. The source specifies both trades. The breath is a pullback to the BB(20) middle or lower band that closes back on the trend side. The launch is a close through the BB(20) upper band on the higher timeframe and on the anchor, as two separate reads. The higher-timeframe pierce is permission. The anchor pierce is the event. Do not enter the launch on the touch of the band, and do not enter the breath on the dip before the close back. Exit is the fast oscillator completing its round trip, or the middle band flipping. "Full neutral chop" means the census failed. It is not an energy reading. This host still needs the energy gate before it is a trade.

### STRAT-002 — CCI surge

H1 CCI(30) and CCI(100), and the same pair on M15, all on one side of zero. That is S1's family with the zero line as equilibrium instead of a shifted SMA. The source specifies the continuation: both clocks already agree, both periods already on the same side of zero. Mixed signs on either timeframe are flat. Both anchor CCIs beyond +100 is a louder displacement, not a super grade. Super still waits on great movement from the energy gate. The breath of the same pair would be the fast CCI dipping through zero while the slow CCI and both clocks stay on the side, with the fire on the rejoin. The source does not write that dip as an entry. It fires the aligned state and the fresh cross that completes it, and it re-enters while both clocks stay on the side. The fast exit is M15 RSI(7) crossing 50 against the position. The trail is the slower CCI crossing zero against.

### STRAT-003 — CCI trinity

CCI(14), CCI(100), CCI(900), each with its own SMA(20). All three on the same side of equilibrium and of their own average is one compounded force. The source specifies that continuation, and it specifies the refusal of the breath that would break it. Any one off-side is no signal, including a clean 2-of-3. The method can see the shape of a breath — the fastest member dips against the two slower members, then rejoins — but the source classifies that dip as unanimity failure, not as a loaded entry. Do not promote it. The fastest member times the entry only while all three still agree. The slower members license. For a launch-grade hold, the exit clock is the mid member, not the fastest, or the trade is reclassified as a scalp. The higher-timeframe trinity belongs on every entry, not only the super branch.

### STRAT-004 — SMA stack

Price above SMA(50), above SMA(4), and above SMA(4) shifted forward. The source specifies the continuation: the stack is already aligned, and the fresh event is the stack completing, not a dip. The shifted copy is the persistence test on a mass. SMA(50) dominates if they disagree. The breath of the same stack would be price dipping through SMA(4) while SMA(50), the shifted copy, and the higher-timeframe stack still hold, with the fire on the recross. The source does not write that dip as an entry. It writes the cross back through SMA(4) as the exit, the mirror of the entry. The higher-timeframe stack is the tide for every grade. A stop "1% beyond the extreme" places a price. It does not size the account. Those are different units.

### STRAT-005 — SMA reversion rally

The source specifies the breath. SMA(30) above SMA(50) is the slow field. The entry event is price crossing back above SMA(30) after the dip, or RSI(5) crossing back above 50. The fire is the rejoin, not the dip. The continuation of the same relation is price already above SMA(30) and SMA(50) on the anchor and on the higher timeframe, with no fresh cross. The method classifies that as a launch. The source does not fire it. The same SMA relation on the higher timeframe is the source's heavier license, not a second recipe. Exit when RSI(5) completes the round trip through 40, or when price closes through SMA(50). Two trigger paths under one license are one signal source. They share one risk budget. They never open two positions.

### STRAT-006 — Energy gate

This is not a strategy. It is the fuel question, and it is the piece the other hosts were missing.

On each timeframe, ADX(14) above its own SMA(1) shifted forward 5, and ATR(14) above its own SMA(1) shifted forward 5, and ADX above a floor near 20. The lighter clock failing is nothing happening. The lighter clock passing while the heavier clock is dead is still nothing happening. Partial heavier-clock fuel is tradable, which licenses a breath and refuses a launch. Both clocks passing is great movement, which licenses the breath and the launch. ADX and ATR never receive a directional job, so they have no pullback entry and no continuation entry of their own. Import this gate into a directional host. Do not trade it alone, and do not let a directional host trade without it.

### STRAT-007 — SMA fan

Five shifted SMA(4) copies, parallel and all on one side of SMA(50). That is unanimity by shift instead of by period. The source specifies the continuation: entry is the bar the fan finishes aligning, not the twentieth bar it stays pretty. A fan that crosses itself is no signal. The breath of the same fan would be price touching back toward a fan that is still straight, with the fire on the bounce. The source does not write that touch as an entry. Re-straightening after a break is a new alignment event under the same license, if the license is still true. That is another launch of the fan, not a pullback into it.

### STRAT-008 — CCI band outbreak

Bollinger bands drawn on CCI(30), CCI(100), and CCI(300). The source specifies the continuation: all three closing outside their own upper band is a launch on an oscillator instead of on price. All three inside their bands is compression: nothing happening, entries masked. The breath would be the fast CCI back inside its band while the two slower members stay outside, then rejoining. The source classifies two of three as no signal, so that dip is not an entry it wrote. Do not trade it as a breath of this host. Exit is any member crossing its own middle band against the position. The pierce algebra does not care whether the band was computed on price or on CCI.

### STRAT-009 — Opening-bell breakout

The cash open is a known energy injection. It can stand in for the measured energy gate. It stands in for nothing else. The source specifies the continuation: the first confirmed anchor close beyond the prior range, inside a short window after the open. A later extended state is stale. The breath of the same range would be a retest of the broken level, still inside the window, while the heavier clock stays on that side, with the fire on the bounce. The source does not write that retest. Direction still needs a heavier-clock mass, a mirrored exit back inside the range, and a license that dies when the window dies. A clock is not a strategy.

### STRAT-010 — Red-folder news with a weekly bias

Weekly positioning is a very heavy, very slow mass. A red-folder release is another known energy spike. The source specifies only the breath: after the first spike, inside a short window, pull back to the heavy average in the direction of the weekly mass, and only if the actual-versus-forecast agrees with that mass. The fire is that pullback, not the spike. The continuation is the spike itself, price leaving with the news. The method classifies that first burst as a launch. The source refuses to trade it, and it refuses any entry against the weekly mass. Several instruments keyed to the same weekly extreme are one signal.

### STRAT-011 — Shifted CCI aligner

This is the persistence test written without decoration. H1 CCI(140) above zero and above its own SMA(1) shifted forward 4 bars is uninterrupted momentum. One closed bar back through that shifted line interrupts it. New entries stop. The source's event is an M5 CCI(14) zero-cross in the license direction. That cross is the breath: the fast CCI was on the other side of zero and has rejoined, while the heavy CCI is still persistent. The continuation of the same pair is M5 CCI already above zero and extending, with no fresh cross, while H1 is still persistent. The method classifies that extended state as a launch. The source does not fire it. It fires the cross, and the cross back is the mirror exit. While the H1 license holds, the next fresh M5 cross is a new trade. ATR here sizes the stop. It does not, by itself, classify energy. The energy gate is still imported.

### GV-014 and GV-015 — the factory, gold

These are tested instances of the same relation, not a new religion. They were walked forward on gold. They are pool units. They are not a claim of a smooth daily income.

GV-014 is a breath on set 2's clocks: anchor 5m, supports 30m and 1h. The source specifies only that breath. The tide is gold outside both a wide tunnel and a tight tunnel on 30m and on 1h (SMA 200 plus one standard deviation, and SMA 20 plus one standard deviation). The event is the first 5m close back inside the tight upper band while that tide holds. The fire is the snap back in, not the fact that price is outside. The continuation of the same tunnels is the 5m close already outside both bands while 30m and 1h are outside both. The method classifies that as a launch. The source does not fire it. It waits for the return inside the tight band. The exit is a 30m close through SMA(4) shifted one bar. The heavier clock exits. The lighter clock enters. Shorts mirror. One position. No pyramid.

GV-015 is S2's exact bands — period 100 and period 10, deviation 0.5, shift +2 — on set 3's clocks: 15m anchor, 1h and 4h support, gold by default. The source specifies both trades. The first entry is the continuation: the anchor closes outside both the wide band and the tight band and beyond SMA 50, and both gravity timeframes are already outside both bands. The re-entry is the breath: a later touch of the tight band while SMA 50 still supports the wide band and price is still beyond SMA 50. Exit is a close through SMA 50. Shorts mirror. The machine-learning file on top of GV-015 scores an already-legal signal. It does not create permission, and it does not override a failed tide. The Python harness around both units measures them. It is not a third strategy. The reinforcement layer in that same audit prices the gates. It does not create a side, a breath, or a launch.

---

## 6. The fourteen textbook strategies, passed through the method

`Strategies to replicate in Algo Trading` is a general guide: seven trend systems and seven reversion systems, mostly on one chart, mostly daily. They are useful as raw material. They are not the desk. Each one below is rewritten as what Jarvis is allowed to hear in it.

The guide's own last page already knows the split. Strong, rising fuel favors riding. Dead fuel favors fading toward a mean. A new extreme in a strong trend is a candidate to join, not to fade. Price riding an outer band is the launch. An extreme in a range is the only place a fade is even a candidate. News is not a side. That page is the method in ordinary language. The fourteen recipes violate it whenever they are run on one timeframe.

### Trend recipes — they are launches, and they are late on purpose

A trend system enters after the move has begun and exits after it has turned. That lateness is the price of confirmation. It matches the launch, not the breath. On this desk the confirmation has to include the heavier clock. A daily 50/200 cross, by itself, is one clock. The guide writes these seven as launches. The breath of each one is stated below as the method's reading of the same sensors, unless the guide itself already wrote the pullback.

**1. Fifty and two hundred.** The source specifies a launch on one daily chart: the 50-period average crosses above the 200, both sloping up, entered on the next open. The death cross is the exit. Whipsaw in chop is the census failure. EMA and SMA are not interchangeable; pick one and keep the role. On this desk that cross is legal as a tide on a heavy clock. It is illegal as a scalp trigger. The breath of the same pair is the lighter clock dipping against a 50 that is still above a rising 200, with the fire on the rejoin. The guide does not write that dip. It writes the cross.

**2. Range breakout.** The source specifies the launch: a body that closes beyond a range tested on both sides, with volume above its recent average. A wick is not a break. A close back inside is the mirror exit. The guide also writes the breath: wait for price to pull back and retest the broken level as support, and enter on the bounce. That retest is legal only after the launch has already been proven and the heavier clock is on the same side. Volume confirms. It never sets the side. This is S3's shape.

**3. Donchian turtle.** The source specifies the launch: a close beyond the 20-bar high, or below the 20-bar low. The 10-bar channel is the exit, slower than a scalp clock and faster than the entry channel, so the trade can breathe without giving the whole move back. Do not exit on the same line that got you in. Skip-after-a-winner and ATR size are risk hygiene. They do not replace the heavier clock. The breath of the same channel would be a pullback that stays beyond the broken extreme and then leaves again. The guide does not write that retest. It writes the new N-bar extreme. Fading the new high because it is "extended" is the mistake.

**4. ADX and DI.** ADX is fuel. DI is direction. The source specifies a continuation only when fuel is alive: +DI crosses above −DI while ADX is above a floor near 25 and still rising. Fuel below the floor means do not take directional trades. ADX falling is not a short. Very high and falling is exhaustion, not a fresh entry. This is STRAT-006 said with DI as the direction sensor. The breath of the same pair is price dipping while +DI is still above −DI and ADX is still climbing, with the fire on the turn back with DI. The guide's entry is the DI cross itself, which is the launch of direction once fuel agrees. It does not write a separate dip entry. A heavier clock still has to name the tide. ADX on one chart cannot.

**5. Rate of change.** The source specifies a momentum flip through zero, with a same-chart filter that price is already on the trend side of a 50-period average. Without that filter the flip is noise. Against a heavier trend it is usually a snap-back, not a new tide. The method keeps ROC only as a velocity event inside an already-legal tide. If the heavier clock is on the side and ROC crosses back through zero with it, that cross is the breath's rejoin. If ROC is already through zero and still accelerating while both clocks agree, the method classifies that as a launch. The guide writes the cross, not the already-extended print. Do not fade a ROC that is stretched in the direction of the tide.

**6. Parabolic SAR.** The source specifies a flip of the dot from one side of price to the other, and it wants the system always in. In a range it flips every other bar. On this desk the dot is an exit manager inside a tide another sensor already set. It does not choose a side against the heavier clock. The initial dot can be far; size comes from that distance, not from confidence. The continuation is a dot already on the trend side of price while the heavier clock agrees and fuel is expanding. That is a launch you trail, not a fade. The breath is price tagging back toward the dot while the heavier clock and the dot's side still hold, with the fire only if price rejects the dot and leaves again. The guide writes the flip as a reversal into the new side. The method refuses that reversal when it fights the heavier clock.

**7. EMA ribbon.** Periods 8, 13, 21, 34, 55. Fanned and stacked in order is one force. Bunched is no signal. The guide writes both clocks of the same ribbon. The breath is the one that matches this desk: price pulls back onto the fast edge, the 8 or the 13, while the stack is still ordered, and the fire is the bounce. A touch of the fastest average is the breath, not the stop. The continuation is the aggressive entry the guide also writes: the first bar the ribbon fans out and stacks after being bunched. That is a launch. A close through the slowest average, the 55, is the structural kill. The heavier timeframe still has to agree before either entry is a fire. A pretty fan on the anchor against a heavier clock is a local state.

### Reversion recipes — they are breaths, and they are illegal against the tide

Mean reversion is the snap-back of a stretch that has no heavy mass behind it. Inside a real trend, the same stretch is the launch or the breath, and fading it fights the field. The guide says this. The individual recipes then forget it unless a filter is bolted on. On this desk the filter is not optional and it is not a 200-period average on the same chart. It is the other timeframe.

The entry detail the guide gets right, and that this desk already uses: touching an extreme is not the entry. The entry is the turn back — the close back inside the band, the cross back through 30, the cross back through +2. The extreme is the load. The exit from the extreme is the release. Entering on the touch is buying the loaded state.

These seven are breaths only when the heavier clock has already called a range. Inside a tide they are illegal as fades. The continuation of each one is what the same extreme means when the heavier clock is driving.

**8. Bollinger fade.** The source specifies the breath inside a range: price tags the outer band, and the next candle closes back inside. The target is the middle. Riding the band is not that trade. The method classifies a close that stays outside the band, with the heavier clock on the same side and fuel expanding, as a launch. Do not fade it. A squeeze, bands at their narrowest, is stored energy about to choose a side. Wait for the break and trade that side. If the heavier clock is trending, this setup is S2's breath — a dip that never left the wide field — or it is nothing.

**9. RSI 30/70.** The source specifies the breath: RSI enters the zone, then crosses back out. The cross back is the fire. Divergence is weakening velocity. It is a warning. It is not a side. Against a confirmed tide, skip the fade. The continuation is RSI pinned in the extreme while the heavier clock and the slow sensor are still driving. The method classifies that pin as a launch. RSI(2) extremes are S4's velocity sensor, not a standalone fade. The guide's two-period variant, oversold below 10 and overbought above 90, is the same rule with a faster orbit.

**10. VWAP fade.** Session fair price. The source specifies an intraday breath: price stretches beyond a deviation band, a rejection candle prints, volume is present, and the target is VWAP. It resets daily, so it is not a swing tide. The continuation is the trend day the guide already names: price accepts beyond the outer band and does not come back. The method classifies that day as a launch. Stop fading and join, which on this desk is S3 language, and only with the higher intraday clock. Volume confirms a rejection. It does not set the side. The first minutes of the session are not a reading. VWAP has not accumulated.

**11. Keltner fade.** Same pierce-and-return algebra as Bollinger, with ATR width so a spike does not instantly widen the band and hide the extreme. The source specifies the breath: a close back inside the channel, target the middle EMA. The continuation is the squeeze the guide writes into the same chapter: when Bollinger width sits inside the Keltner width, that is compression. Wait for the break and trade that side. The method classifies the break, with the heavier clock agreeing, as a launch. Do not fade it. A Keltner extreme while the heavier clock is trending is the same illegal fade as the Bollinger ride.

**12. Z-score.** Distance from a rolling mean in standard deviations. The source specifies the breath: Z goes beyond +2 or −2, then crosses back inside. The target is zero. A print beyond 3 is a momentum event. The guide says stand aside. The method classifies a Z that stays beyond 2, with the heavier clock on that side and fuel still expanding, as a launch. A number of standard deviations is still just distance. The heavier clock decides whether the cross back inside is a legal breath in a range, or a trap against a tide.

**13. Stochastic.** The source specifies the breath: both %K and %D inside the extreme zone, then %K crosses %D back out of it. The cross is the fire. The touch of 80 or 20 is the load. It stays pinned in a trend and looks like a setup the whole way. That pin, with the heavier clock driving, is the continuation. The method classifies it as a launch. Do not fade it. A higher-timeframe stochastic can be context. It cannot outvote the tide. Fast settings add noise, not a new principle.

**14. Williams %R.** The same extreme-exit idea on a scale that runs backward from RSI. Above −20 is the hot zone. Below −80 is the cold zone. Read the zone before you name the side. The source specifies the breath: %R enters the zone, then exits it, and the next candle confirms. The source also specifies the continuation, in one clause: a very fast travel from one extreme to the other in a handful of bars is a momentum burst. Trade the burst, not the fade. The method classifies that burst, when the heavier clock agrees, as a launch. Honor it. A slow extreme against the tide is still an illegal fade.

---

## 7. What else is in the folder, and what Jarvis does with it

**Venice VWAP note.** The note writes a one-chart fade: tag a deviation band around VWAP, with volume above its average and a rejection candle, target VWAP. The only sentences that belong to this method: know the one-hour tide before you scalp, and if price accepts beyond the outer band, stop fading and join. That acceptance is the continuation. The method classifies it as a launch. The fade is the breath, and it is legal only when the higher clock is not already leaving. Volume confirms a rejection. It does not set the side. The same note's EMA alternative is a breath the source does write: price pulls back to the 9 EMA while the 9 is with the 21 and ADX is above 25, and the fire is the close back through the 9. The continuation of that pair is price already leaving with both averages stacked and ADX still rising. The method classifies that as a launch. The note does not fire it. It fires the pullback to the 9. The advertised win rates, the session table, and the offer to code an EA are not doctrine.

**Venice "real edges" note.** Order-flow reading, market making, latency arbitrage, statistical pairs, news-speed scalping, microstructure patterns, and opening-auction imbalances are other businesses. The note's retail leftovers — support and resistance bounces, and a volatility-compression breakout — are the same breath and launch this file already has, without a sensor spec precise enough to fire. They need data and infrastructure this desk does not trade with, or they are names without a kill. They do not change tide, breath, or launch. Leave them. Do not treat a latency race or a queue jump as a strategy to learn here.

**Student results sheet.** Other people's named studies: order blocks, supply and demand, a reversal method, Fibonacci, a DXY study, an SID method, and, under those same headings, head and shoulders and M-and-W patterns. The sheet is a list of students and claimed win rates. It does not specify a sensor, a set, or a kill condition. A win rate without the relation is not a principle. Jarvis does not fire from a name on that sheet. There is no pullback rule and no continuation rule to classify, because the source never wrote either one.

**Factory backtest code.** `prep.py`, `sweep.py`, `wf.py`, `engine.py`, and the rest are how GV-014 and GV-015 were measured. They are not rules of trading. A passing walk-forward says the relation showed up in that sample. It does not relax the tide, the closed-bar rule, or the risk gate.

---

## 8. Given a sensor you have never seen

Do this before it is allowed near a fire.

1. Look at the output. If it is in price units and has no fixed middle, it is a mass. Hierarchy and orbit apply. If it has a fixed middle, it is an oscillator. Distance from that middle is not a side.
2. Give it exactly one role: force, inertia, velocity, equilibrium, energy, or exit.
3. Place it on a clock. A heavier timeframe, or a longer period on the same timeframe, can set or confirm the tide. The anchor copy can only time.
4. Decide which trade it serves. If the slow reading stays and the fast reading dips, it is a breath, and the fire is the rejoin. If everything is already on the same side and price is clearing structure with fuel, it is a launch, and you do not fade it.
5. Write the kill as the negation of the license. If you cannot name the closed-bar relation that makes the idea false, the sensor is not ready.
6. Require the energy gate and the 1% / one-signal rule. A new indicator does not arrive with its own risk law.
7. Run it on an official set. Do not invent a timeframe pair because the picture looks cleaner there.

If you can only say that a condition "is true right now" and you cannot point to the closed bar where the cross completed, you have a state. States wait. They do not fire.

---

## 9. What this file refuses

- A scalp against a confirmed higher-timeframe tide.
- Any one indicator, on any one timeframe, as a fire.
- Calling every anchor dip a reversal.
- Fading a launch because a fast oscillator is extreme.
- Folding direction and fuel into one number.
- A grade, a vote, or a smaller size when unanimity fails.
- Trading chop, mixed supports, or an undefined regime.
- A new timeframe set that was not written into the baseline.
- Holding because the entry used to be valid.
- Adding size to get back a loss.
- Treating a loaded, unreleased breath as indecision. That wait is the skill.

---

## Coverage

`strategy - Copy` is a duplicate of this folder. It is not a second strategy set.

| Source | Where it is |
|---|---|
| `section-1.md` gravity, mass, orbit, snap-back versus extension | Sections 2 and 5 |
| `section-2.md` five finding failures | Sections 2 and 3, and the opening of section 5 |
| `section-3.md` five utilization failures | Sections 2 and 3, and the opening of section 5 |
| `section-4.md` pullback versus super | Sections 2 and 5 |
| `section-5.md` higher-timeframe persistence and re-entry | Sections 2 and 5 |
| `section-6.md` multi-period unanimity | Sections 2 and 5 |
| `section-8.md` STRAT-001 through STRAT-011, including STRAT-0009 and STRAT-0010 | Section 5. There is no section 7 in the folder. |
| `new_trading_strategies.md` and `new_trading_strategies (1).md` (the same four) | Section 4. Extra-confidence four-timeframe stacks stay reference, not a fifth official set. |
| `rsi + bb strategy.txt` | Section 4, sibling sensor |
| `factory_full\GV-014-XAU-L1.md` and `GV014_gravity_snap.pine` | Section 5 |
| `factory_full\GV015_tunnel_rider.pine` | Section 5 |
| `factory_full\ml15.py` | Section 5. It scores GV-015. It is not a strategy. |
| `factory_full\README_FACTORY.txt` and the Python harness | Section 7. Measurement, not a rule. |
| `Strategies to replicate in Algo Trading.docx.html` (the fourteen) | Section 6 |
| `venice strate.txt` | Section 7 |
| `venice strat 2.txt` | Section 7. Named and refused. |
| `Student Strategy Tests.xlsx - Student Results.csv` | Section 7. Names only. Refused as fires. |

---

## 10. The operating sentence

See force on the heavier clock. Name the regime, including when it has no cutoff and must be called undefined. Tell a breath from a launch. Then say one act: fire, wait loaded, wait with no trade, or kill.

The specialty is not predicting the next bar. The specialty is recognizing when a pullback is still inside real force, and when the market has given no permission to act.
