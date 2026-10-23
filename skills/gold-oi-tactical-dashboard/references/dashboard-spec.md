# Interactive HTML dashboard

## Deliverable

Generate `dashboard.html`: one responsive, self-contained HTML file with embedded data, CSS, JavaScript, and one Plotly bundle. It must open locally without a server, CDN, network connection, login, or React build.
Reuse `assets/dashboard-template.html` via `scripts/render_dashboard.py`; do not rebuild the layout for each run.
Data represents a dated snapshot. Controls do not fetch live quotes, refresh Sheets, or generate a new market bias.
PNG is no longer a required deliverable; provide an optional screenshot only if requested.

## Render command

Use a Python interpreter with Plotly installed; all other renderer dependencies use the standard library.
Run from the skill directory, passing the existing validated run folder:

```bash
python3 scripts/render_dashboard.py --run-dir /absolute/path/to/run
```

The renderer reads the three CSVs, `price_context.json`, and `analysis.json`, then writes `dashboard.html` atomically and logs the result.
It checks finite numbers, integer counts, normalized duplicate keys, latest dates, contract/expiry, matching latest strike coverage, and the content contract below.
It computes KPI totals directly from CSVs. If supplied known `analysis.totals` differ, rendering fails. Undefined ratios display `N/A`, never huge epsilon-derived values.
It cannot verify source headers, timestamps against the source, Sheet writes, price basis, or reasoning. Complete those workflow checks before rendering.
Missing observations are not zero. Resolve different latest strike coverage before rendering; preserve missing historical dates as gaps.
Do not overwrite raw numbers or use test fixtures in a real run.

## Content contract

Continue to use the `price_context.json` schema in `browser-and-sheets.md`.
Add `observed_at` as an ISO timestamp with timezone, `price_decimals` matching source precision (0–6), and `approximate` as a boolean when applicable.
Record the chart's actual symbol and timeframe. Its observation time may differ from the options as-of date; show both and explain material timing/basis differences in warnings.
Keep all existing chart-context fields for analysis, even when the template does not display them directly.

`analysis.json` contains the following fields in addition to any existing analytical output:

| Field | Type / content |
| --- | --- |
| `as_of_date` | ISO date matching the latest observation in all three CSVs |
| `contract`, `expiry` | Same active options contract and ISO expiry as the CSVs |
| `source_site` | Actual data source name |
| `extracted_at` | ISO timestamp with timezone |
| `bias`, `confidence` | Existing five bias labels; `high`, `medium`, or `low` |
| `demo` | Optional boolean, default false; true only for explicitly synthetic previews |
| `preview_note` | Optional visible banner for a layout preview using a dated existing snapshot; identify it as a preview, not a fresh run |
| `sheet_write_status` | `updated` only after verified write-back; otherwise `not_updated` |
| `quick_read` | 4–6 strings covering structure, OI, ΔOI, Volume, nearby levels, and what changes the bias |
| `evidence` | Objects with `label` and `detail`; cover price, OI, ΔOI, Volume, important strikes, bias and confidence |
| `levels` | Prefer 5–8 objects with numeric `strike`, `role`, `evidence`, `interpretation`, `confidence` |
| `positioning` | Text fields `condition`, `upside`, `downside`, `concentration`, `invalidation` |
| `scenarios` | Three objects: IDs `base`, `reclaim`, `breakdown`; each has `title`, numeric `levels` array, `trigger`, `confirmation`, `invalidation` |
| `warnings` | List of data-quality notes; empty only when there are none |
| `totals` | Optional scorer-compatible totals; CSV totals remain authoritative |
| `oi_change_comparison_date` | Optional ISO date or null, read from the OI Change source and strictly earlier than `as_of_date`; never infer it from a calendar or the nearest available history row |

Retain full ranked-strike evidence and raw metrics in analysis output; rendering does not replace the scorer or semantic analysis.
Use `scored_strikes.json` for intermediate scorer output, then prepare/enrich `analysis.json` without replacing computed evidence with display copy.
Level descriptions must follow `analysis-methodology.md`; chart-only levels are allowed and display `N/A` for absent option metrics.
Quick Read and scenario text must reflect the actual run. The renderer never invents it or infers bias from Call/Put dominance.

### Top OI Change data contract

The renderer owns the calculation of `D.top_changes` from the validated latest rows for the active contract and expiry. Do not hand-author its ranks in `analysis.json`, replace the tactical activity score, or add Sheet columns/tabs for this display.

| Payload field | Content |
| --- | --- |
| `as_of_date` | Latest options observation date, identical to the snapshot |
| `comparison_date` | Source-read `analysis.oi_change_comparison_date`, or the immediately prior complete OI snapshot date only after every Call/Put delta reconciles; otherwise null |
| `limit`, `ranking` | `15`, `absolute_oi_change` |
| `status`, `unavailable_reason` | `available` or `unavailable`; null or a concise explanation |
| `call`, `put` | Independently computed objects, each with `summary` and `rows` |
| `summary.total_oi`, `summary.total_volume` | Sums over all latest strikes on that side |
| `summary.net_change` | Sum of signed changes over all latest strikes on that side |
| `summary.increased_strikes`, `summary.decreased_strikes`, `summary.unchanged_strikes` | Counts of positive, negative, and zero changes across all latest strikes on that side |
| `rows[]` | Up to 15 objects with `rank`, `strike`, `oi`, `previous_oi`, `change`, `volume`, `previous_oi_source` |

Rank each side separately by descending `abs(change)`, then descending same-side Volume, then ascending numeric strike. This is the dashboard's deterministic tie rule, not a claim that the official source comparator has been verified. Exclude zero changes and never pad a short list. `rank` starts at 1; preserve the signed `change`. The summaries include all latest strikes, including zero-change rows and strikes outside the Top 15 or proximity range.

`oi` and `volume` are the latest exact side-specific values. Use prior OI from a matching observed comparison-date row when available and consistent with the signed change. Otherwise, `oi - change` can be displayed as derived prior OI only when the change represents a valid comparison and the result is a nonnegative integer; label it clearly as a calculation, not an independently observed value. Use `previous_oi_source` values `observed`, `derived`, or `unavailable` and show provenance in hover/detail/table. Use null / `N/A` when prior OI is unavailable, inconsistent, or based on a source baseline. A null comparison date remains visibly unknown even when prior OI can be derived; never assign an invented date.

A source initial-baseline column is not daily flow: do not rank it as daily Top 15, derive a daily prior OI from it, or present its increase/decrease counts as daily activity. An explicit latest-date baseline exclusion produces `status: unavailable`, a reason, empty rankings, and null daily net-change/count summaries, while retaining raw values and valid OI/Volume totals. For a valid all-zero change snapshot, keep `status: available`, zero net change and increased/decreased counts, an unchanged count equal to all strikes, and a clear empty ranking instead of a baseline warning.

## Layout and style

Use a modern institutional research layout: light slate background, white cards, navy typography, restrained gold accents, green Call and red Put series, thin borders, generous readable spacing. In the Top OI Change section, use sign colors instead: green means increased OI and red means decreased OI on both option sides.
Use the bundled HTML template for the fixed layout. The public package excludes provider screenshots; synthetic regression fixtures are only test inputs and never current market data.
Use Thai by default, Thonburi/Tahoma/system font fallbacks, tabular numerals, native labeled controls, visible keyboard focus, and responsive grids.
No external font downloads. Respect reduced-motion preferences; use short CSS transitions for UI changes and Plotly updates rather than rebuilding the page.
Keep data-bearing text deterministic and legible. Never generate report text or charts as raster images.

Required sections:

1. Header: contract, expiry, source, chart symbol/timeframe, options as-of, extraction time, Sheet status.
2. KPI row: observed chart price/time, total Call/Put OI, Put/Call OI ratio, Put/Call Volume ratio.
3. Quick Read: 4–6 bullets; bias and confidence remain prominent.
4. Strike explorer: grouped Call/Put OI bars, current-price marker, selected-strike detail.
5. Top 15 by Open Interest Change: distinct Call and Put panels, each with its all-strike summary, diverging horizontal bars, accessible ranked table, and local selected-row detail.
6. Daily Call/Put OI Change chart.
7. Daily Call/Put Volume chart.
8. Vertical Level Map, ordered high to low with current price between levels.
9. Action Plan with trigger, confirmation, relevant levels, and invalidation.
10. Separate Positioning and Swing views; base/reclaim/breakdown scenario controls.
11. Evidence table, accessible numeric strike table, and Beginner Corner.
12. Data-quality warnings and tactical-view disclaimer.

For Top 15, put the highest absolute change first. Bars extend right for positive change and left for negative change from a visible zero line. Default to an independent symmetric axis around zero for each side; state that bar widths across panels are not comparable in this mode. A labeled independent/shared scale selector may switch to a shared symmetric axis where widths are comparable, without changing ranks or snapshot KPIs. Keep Call/Put identities in panel titles and text, independent of sign color. Green/red means increase/decrease, never bullish/bearish. Stack panels on mobile without clipping labels, signs, dates, or summary values.

Show latest and comparison dates, active contract/expiry, and the absolute-change ranking rule. Hover, accessible tables, and the local detail must expose strike, Volume, prior OI, latest OI, signed change, the relevant dates, and prior-OI provenance. Unknown values display `N/A` with a concise explanation; missing dates/values are never silently zero-filled.

## Interaction contract

- Strike chart defaults to OI; buttons switch to ΔOI or Volume without changing the snapshot.
- Click a bar, Level Map row, scenario-level chip, or numeric-table strike to update its details. Native buttons provide a keyboard alternative to chart clicks.
- Filter strikes to all / within ±2% / within ±1% of chart price. Show the number of displayed strikes; handle empty ranges explicitly.
- KPI totals, evidence, scenarios, and bias always describe all strikes in the original snapshot. State this next to filters; hiding a trace or zooming never recomputes totals.
- Date controls select only dates present in the embedded history and filter only the two historical charts. They do not present the current price or narrative as historical values.
- The Call/Put Top 15 ranks and their all-strike summaries remain fixed to the latest snapshot under history-date, proximity, metric, and view changes. State this next to the section.
- Clicking a Top 15 bar or its native keyboard-accessible strike button updates both that section's local side/strike detail and the existing strike inspector. Keep the selected row's side-specific metrics visible even if its strike is outside the explorer's current proximity filter; do not silently change the fixed ranking or filters.
- If a historical chart has one observation, show a point and an explicit one-day note. Do not invent a time series.
- Preserve gaps for missing observations. Report inconsistent historical strike coverage as a warning before interpreting trend changes.
- Selecting a Swing scenario highlights related Level Map levels; selecting Positioning removes that scenario highlight.
- Show signed ΔOI, whole-number counts, ratios to 2 decimals, and prices at declared source precision. Raw embedded data remains unrounded.
- Table data and all imported narrative are treated as data: use text nodes and safely escaped embedded JSON, never interpolate source strings as executable markup.
- The HTML must not contain browser credentials, tokens, or private browser state.

## Educational wording

- Call concentration: notable Call positioning, not automatically resistance.
- Put concentration: notable Put positioning, not automatically support.
- OI Change + Volume: changes and participation, not proof of the holder's long/short intent.
- Top OI Change: largest absolute changes on each option side; signed increases/decreases are not bullish/bearish labels or an alternative tactical score.
- Snapshot: interaction does not retrieve fresh data or recalculate bias.

Required Thai disclaimer:

`คำเตือน: ข้อมูลนี้เป็น tactical market view จากข้อมูลราคาและ options positioning ไม่ใช่คำแนะนำการลงทุน และ OI/Volume ไม่ได้บอกทิศทางของผู้ถือสถานะอย่างแน่นอน`

## QA and reusable smoke check

Run the small regression check after changing the renderer or template:

```bash
python3 scripts/test_render_dashboard.py
```

For an explicitly synthetic preview, append `--demo-dir /absolute/path/to/new-empty-demo-folder`.
The fixture generator refuses to overwrite a nonempty folder and marks the page `DEMO`. This is a renderer test, not a live-dashboard run or a substitute for missing sources.
Inspect the HTML at desktop and mobile widths, then exercise chart click, metric switch, strike filter/reset, both views, all scenarios, and historical date controls.
Verify unchanged snapshot KPIs under filters, correct detail metrics, `N/A` for zero denominators, one-day history, warnings, Thai text, keyboard focus, and no console errors or external requests when offline.

Focused Top 15 checks:

- Validate separate Call/Put absolute-change ordering with positive and negative values, equal absolute changes with different Volumes, a remaining strike tie, and an excluded zero; confirm Volume-descending then strike-ascending ties and unchanged signs.
- Check more than 15 qualifying strikes, fewer than 15, one qualifying strike, and an all-zero side without padding. Verify summaries against all latest raw strikes rather than the selected 15, including increase/decrease/unchanged counts.
- Confirm older dates and another contract/expiry cannot enter the latest ranking. Keep Top 15 and summaries unchanged after explorer proximity/metric changes and both history-date controls.
- Verify observed prior OI, explicitly labeled derived prior OI, unknown comparison date, unavailable/inconsistent prior OI, and baseline exclusion. A latest source baseline must show an unavailable daily ranking rather than an artificial surge.
- Click both a positive and negative bar on each side, and activate native strike buttons with the keyboard; verify local side-specific detail and the shared inspector, including a strike hidden by the current explorer range.
- At desktop and mobile widths, check symmetric independent axes, the cross-panel width warning, signed labels, readable dates, no clipped content, and visible keyboard focus. If shared scaling is provided, check identical axis ranges and unchanged ranks/KPIs. Ensure sign colors have no bullish/bearish meaning.

Record render/interaction QA in the run log only after it passes; do not equate a successful file write with a completed dashboard.
