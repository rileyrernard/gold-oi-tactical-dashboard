# Release verification

2026-10-23 · Armriley · Public package 1.0.0

## Verified locally on Windows

- Python project interpreter with Plotly 5.24.1: import and `pip check` pass.
- Skill Creator frontmatter validation passes.
- Ten Top15 regression tests pass, covering signs, side isolation, deterministic ties, limits, all-zero rows, observed/derived/unavailable prior OI, comparison dates and baseline exclusions.
- Renderer smoke check passes totals, zero denominators, safe JSON embedding, date/contract/numeric checks and missing-strike rejection.
- Three distribution test groups pass: whole-folder install/hash/idempotency/no-overwrite for all three agent path layouts including simulated user scopes; contract/date/strike coverage; blank/nonfinite/unsafe/fractional counts and normalized duplicate strikes.
- Synthetic DEMO generates a standalone HTML. DEMO is not market evidence and does not write Google Sheets.

## Not established by these tests

- Actual agent invocation in Claude Code or Antigravity.
- Their Chrome/Sheets connectors, accounts, browser permissions or live market data.
- macOS/Linux live workflows. The included CI matrix requests Python tests on those platforms; a configured workflow is not a passing CI result.
- Strategy profitability, trade execution, causal positioning labels or dealer gamma.

The user-local installed skill was not overwritten. Release changes are confined to this repository copy. No instructor credentials, Sheet identifiers, browser state or live market snapshots are included.
