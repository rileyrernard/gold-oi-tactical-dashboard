# Portable CSV mode

Requires local file access and a Python interpreter with Plotly. Host-specific browser or Google connectors are not required. The data contract is the same across compatible hosts; host integration behavior must be tested separately.

1. Read only the supplied run folder. Require `raw_oi.csv`, `raw_oi_change.csv`, `raw_volume.csv`, `price_context.json`, `source_context.json`.
2. Ground contract, expiry, source as-of/comparison dates, extraction timestamp, underlying month and source totals. Verify against supplied evidence; metadata alone is not proof. Unknown comparison date stays null.
3. Run `scripts/validate_extracted_csv.py`. Check source headers/units/totals independently, preserve signs and require latest strike coverage. Never zero-fill missing data. Historical OI differences must reconcile where observed snapshots exist.
4. Read actual chart price, symbol, timeframe and observation time. Do not infer broker/futures basis equality. Mark approximate levels and confidence.
5. Run `scripts/score_strikes.py` with actual chart price. Scoring ranks activity, not direction. Read methodology and create `analysis.json` with the dashboard content contract, data limitations and three conditional scenarios.
6. Set Sheet status `not_updated`. Only use a connector if the user authorizes a particular Sheet, and mark updated only after exact readback.
7. Render `scripts/render_dashboard.py --run-dir <folder>`, inspect numbers and exercise controls at desktop/mobile widths. Report what was and was not tested. HTML embeds a snapshot and does not update automatically.

Use the chosen interpreter with `-X utf8`: `.venv/Scripts/python.exe -X utf8` on Windows or `.venv/bin/python -X utf8` on macOS/Linux. Resolve scripts relative to the skill directory, never the publisher's home directory.

Synthetic examples are only for explicitly requested education or renderer tests and remain visibly DEMO. They cannot substitute for missing real data.
