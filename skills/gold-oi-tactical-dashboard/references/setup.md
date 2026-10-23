# Setup

Requires Python 3.11+, pinned Plotly from requirements.txt, local files and shell access. This skill does not install browser or Google Sheets integrations.

Create a project virtual environment with `python -m venv .venv`. Use its interpreter for `python -X utf8 -m pip install -r <skill-dir>/requirements.txt`, `python -X utf8 -m pip check` and `python -X utf8 <skill-dir>/scripts/test_render_dashboard.py`.

Interpreter: `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on macOS/Linux. Resolve paths relative to the user's project. Do not change global Python or disable TLS verification.

Installation for Codex, Claude Code and Antigravity: https://github.com/rileyrernard/gold-oi-tactical-dashboard/blob/main/docs/INSTALL.md

CSV is the portable default: read [csv-workflow.md](csv-workflow.md). For optional live mode, test authorized access to all source tabs and the exact Sheet before extraction. Installed skill files and renderer tests do not establish integration readiness. Missing tools/data cannot be replaced with old or DEMO data.
