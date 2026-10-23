# Release verification

2026-10-23 · Armriley · Public package 1.0.0

## Verified locally on Windows

- Python project interpreter with Plotly 5.24.1: import and `pip check` pass.
- Skill Creator frontmatter validation passes.
- Ten Top15 regression tests pass, covering signs, side isolation, deterministic ties, limits, all-zero rows, observed/derived/unavailable prior OI, comparison dates and baseline exclusions.
- Renderer smoke check passes totals, zero denominators, safe JSON embedding, date/contract/numeric checks and missing-strike rejection.
- Three distribution test groups pass: whole-folder install/hash/idempotency/no-overwrite for all three agent path layouts including simulated user scopes; contract/date/strike coverage; blank/nonfinite/unsafe/fractional counts and normalized duplicate strikes.
- Synthetic DEMO generates a standalone HTML. DEMO is not market evidence and does not write Google Sheets.

## Verified on GitHub Actions

- [Run 39905809982](https://github.com/rileyrernard/gold-oi-tactical-dashboard/actions/runs/39905809982) passed all six combinations of Ubuntu, Windows and macOS with Python 3.11 and 3.13 at commit `9c18198`.
- CI checks dependency installation, `pip check`, renderer regressions/smoke and distribution tests. This confirms the Python package tests on those runners, not a live agent or browser/Sheets workflow.
- [Run 39906065804](https://github.com/rileyrernard/gold-oi-tactical-dashboard/actions/runs/39906065804) also passed all six jobs at commit `a1813bb`, after updating to Node 24-compatible action versions.

## Canva publication

- Approved draft edits on pages 3, 5, 9, 10, 22, 23 and 28 were committed and their rendered previews inspected.
- [Public view link](https://canva.link/aa12h38et04fwko) created on 2026-10-23. Canva reports Live and anyone with the link can view without signing in; the public viewer opens 28 slides. The owner original remains separate from view-only access.

## Not established by these tests

- Actual agent invocation in Claude Code or Antigravity.
- Their Chrome/Sheets connectors, accounts, browser permissions or live market data.
- macOS/Linux live workflows; Python CI results do not establish agent integrations.
- Strategy profitability, trade execution, causal positioning labels or dealer gamma.

The user-local installed skill was not overwritten. Release changes are confined to this repository copy. No instructor credentials, Sheet identifiers, browser state or live market snapshots are included.
