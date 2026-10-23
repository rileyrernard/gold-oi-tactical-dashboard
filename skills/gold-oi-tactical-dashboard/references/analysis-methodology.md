# Analysis methodology

## Purpose

Use this reference when converting raw OI, OI Change, Volume, and chart context into tactical levels and sentiment.

## 1. Evidence hierarchy

For tactical relevance, prioritize:

1. OI Change
2. Volume
3. OI
4. Proximity to current price
5. Price confirmation

Large OI far from price may be structurally important but tactically weak. Smaller OI with unusually large fresh change and volume near price may be tactically important.

## 2. Significant-strike score

Use the provided script as a first-pass ranking. Conceptually, score each option side by:

`activity_score = 0.45 * z(abs(OI Change)) + 0.35 * z(Volume) + 0.10 * z(OI) + 0.10 * proximity`

Where proximity increases as strike distance to current price decreases.

Do not use the score alone to assign support/resistance semantics.

### Top 15 by Open Interest Change

Keep this descriptive ranking separate from the weighted tactical score. For the latest contract/expiry/date, rank Call and Put independently by descending absolute signed OI Change, breaking ties by descending same-side Volume and then ascending strike. This deterministic tie rule belongs to the dashboard; it is not a verified official source comparator. Exclude zero changes and show up to 15 without padding. This answers which strikes changed most; Volume breaks ties only, while total OI, distance from price, and directional conviction do not determine rank.

Accompany each side with all-strike totals for OI, Volume, and signed net change, plus counts of increased, decreased, and unchanged strikes. A top-ranked strike can still be tactically weak if far from price or unsupported by price structure. Use Volume and chart evidence to interpret it, rather than changing this fixed ranking to favor nearby strikes.

Read the change's comparison date from the source when available. Prior OI calculated as latest OI minus signed change is derived evidence and must be labeled; it is not a second independent observation. If the date is unknown, leave it unknown. Missing/inconsistent prior OI displays `N/A`. A source initial-baseline column cannot establish daily change and must be excluded from daily-flow ranking and interpretation.

Positive change means OI increased and negative change means OI decreased, for both Calls and Puts. Neither sign reveals buyer/seller intent, dealer positioning, or a bullish/bearish price forecast. See `dashboard-spec.md` for the renderer payload, provenance labels, fixed filters, and interaction requirements.

## 3. Structural vs active concentrations

Use these distinctions:

- Structural concentration: high total OI, but current OI Change/Volume is not exceptional.
- Active concentration: fresh OI Change and/or Volume is high, especially near price.
- Confirmed wall: active or structural concentration plus repeated price rejection/support behavior visible on the chart.

Avoid claiming dealer gamma sign, long/short direction, or hedging flows unless a separate source explicitly provides that information.

## 4. Ratios

Compute:

- Put/Call OI Ratio = total Put OI / total Call OI
- Put/Call Volume Ratio = total Put Volume / total Call Volume

Use ratios descriptively. Do not treat a ratio above 1 as automatically bearish or below 1 as automatically bullish.

## 5. Flow balance

Use signed balances for descriptive comparison:

- OI Change balance = `(Call OI Change - Put OI Change) / (abs(Call OI Change) + abs(Put OI Change) + eps)`
- Volume balance = `(Call Volume - Put Volume) / (Call Volume + Put Volume + eps)`
- OI balance = `(Call OI - Put OI) / (Call OI + Put OI + eps)`

These describe which option side dominates measured activity. They are not a direct mapping to spot direction.

## 6. Price structure

Classify the chart:

- Bullish: higher highs/higher lows and price holding above reclaimed key levels
- Bullish-to-Range: constructive recovery but still below major resistance
- Range / Neutral: overlapping swings and no clear directional acceptance
- Bearish-to-Range: major selloff or lower highs, but price stabilizing near support
- Bearish: lower highs/lower lows and acceptance below important support

If H1 and D1 disagree, state the conflict and lower confidence.

## 7. Final tactical bias

Anchor the final bias on price structure. Use options activity as confirmation, contradiction, or a map of important levels.

Examples:

- Bearish price + put-side activity near/below price + failure to reclaim nearby active call concentration -> Bearish / Bearish-to-Range.
- Bearish price + strong fresh call-side activity at nearby strikes + successful price reclaim -> reduce bearish conviction; possibly Range / Bullish-to-Range.
- Range price + strong activity on both sides -> Range / Neutral with well-defined breakout levels.

## 8. Level semantics

### Reclaim level

A nearby level above price that must be regained and held to weaken a bearish thesis.

### Pivot

A level around which both option activity and price behavior change meaningfully.

### Magnet / high-activity node

A strike with unusually high active participation. Use neutral language unless price behavior supports directional semantics.

### Support candidate

A strike below/near price with high relevant activity and visible price stabilization/reaction.

### Resistance candidate

A strike above/near price with high relevant activity and visible price rejection/reaction.

### Call wall / Put wall

Use sparingly. Require both options concentration and chart confirmation. Prefer `call concentration` or `put concentration` when evidence is incomplete.

## 9. Action-plan structure

For each scenario, state:

- condition
- trigger level
- confirming evidence
- target area / next level to monitor (not a guaranteed target)
- invalidation

Do not express certainty. Use language such as `if accepted above`, `if rejected below`, `watch for`, and `evidence would strengthen/weaken`.
