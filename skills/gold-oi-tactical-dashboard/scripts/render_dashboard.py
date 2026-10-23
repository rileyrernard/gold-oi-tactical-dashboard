#!/usr/bin/env python3
"""Render a validated Gold OI snapshot as one offline HTML report."""
import argparse
import csv
import json
import logging
import math
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from plotly.offline import get_plotlyjs
from validate_extracted_csv import validate

LOG = logging.getLogger(__name__)
BIASES = {"Bullish", "Bullish-to-Range", "Range / Neutral", "Bearish-to-Range", "Bearish"}
CONFIDENCE = {"high", "medium", "low"}
COLUMNS = {"oi": ("call_oi", "put_oi"), "change": ("call_oi_change", "put_oi_change"),
           "volume": ("call_volume", "put_volume")}
FILES = {"oi": "raw_oi.csv", "change": "raw_oi_change.csv", "volume": "raw_volume.csv"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, label, *, count=False, positive=False):
    parsed = Decimal(str(value).replace(",", ""))
    require(parsed.is_finite() and abs(parsed) <= 2**53 - 1, f"{label}: invalid/unsafe number")
    require(not count or parsed == parsed.to_integral_value(), f"{label}: count must be an integer")
    require(not positive or parsed > 0, f"{label}: must be positive")
    return int(parsed) if count else float(parsed)


def timestamp(value, label):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.utcoffset() is not None, f"{label}: timezone required")


def text_fields(obj, fields, label):
    for key in fields:
        require(isinstance(obj.get(key), str) and obj[key].strip(), f"{label}.{key}: text required")


def ratio(put, call):
    return put / call if call else None


def build_top_changes(analysis, rows, oi_snapshots, limit=15):
    """Rank each side by absolute daily change without assigning trade direction."""
    as_of = analysis["as_of_date"]
    declared = analysis.get("oi_change_comparison_date")
    if declared is not None:
        require(isinstance(declared, str) and date.fromisoformat(declared).isoformat() == declared,
                "oi_change_comparison_date: use ISO date")
        require(declared < as_of, "oi_change_comparison_date: must precede as_of_date")
    exclusions = analysis.get("history_exclusions", {}).get("change", {})
    require(isinstance(exclusions, dict), "history_exclusions.change: date/reason mapping required")
    available = as_of not in exclusions
    result = {"as_of_date": as_of, "comparison_date": None, "limit": limit,
              "ranking": "absolute_oi_change", "status": "available" if available else "unavailable",
              "unavailable_reason": None if available else str(exclusions[as_of]) or "Daily OI change excluded for this date"}

    previous = None
    if available:
        strikes = {row["strike"] for row in rows}
        prior_dates = [day for day in oi_snapshots if day < as_of]
        candidate = declared if declared is not None else max(prior_dates, default=None)
        observed = oi_snapshots.get(candidate)
        complete = observed is not None and set(observed) == strikes
        matches = complete and all(
            row[f"{side}_oi"] - observed[row["strike"]][f"{side}_oi"] == row[f"{side}_oi_change"]
            for row in rows for side in ("call", "put"))
        if declared is not None and observed is not None:
            require(complete, "Declared comparison OI strike coverage differs from latest snapshot")
            require(matches, "Declared comparison OI does not reconcile with latest OI Change")
        if matches:
            previous = observed
            result["comparison_date"] = candidate
        elif declared is not None:
            # The caller may know the comparison date from the source header,
            # even when raw_oi.csv intentionally stores only the latest day.
            result["comparison_date"] = declared

    for side in ("call", "put"):
        oi_key, change_key, volume_key = f"{side}_oi", f"{side}_oi_change", f"{side}_volume"
        summary = {"total_oi": sum(row[oi_key] for row in rows),
                   "total_volume": sum(row[volume_key] for row in rows),
                   "net_change": sum(row[change_key] for row in rows) if available else None,
                   "increased_strikes": sum(row[change_key] > 0 for row in rows) if available else None,
                   "decreased_strikes": sum(row[change_key] < 0 for row in rows) if available else None,
                   "unchanged_strikes": sum(row[change_key] == 0 for row in rows) if available else None}
        # Deterministic renderer ties: more Volume first, then lower strike.
        # This ordering is not a claim about the source website's algorithm.
        ranked = sorted((row for row in rows if row[change_key] != 0),
                        key=lambda row: (-abs(row[change_key]), -row[volume_key], row["strike"]))[:limit] if available else []
        output_rows = []
        for rank, row in enumerate(ranked, start=1):
            if previous is not None:
                previous_oi, source = previous[row["strike"]][oi_key], "observed"
            else:
                previous_oi = row[oi_key] - row[change_key]
                source = "derived" if previous_oi >= 0 else "unavailable"
                if source == "unavailable":
                    previous_oi = None
            output_rows.append({"rank": rank, "strike": row["strike"], "oi": row[oi_key],
                                "previous_oi": previous_oi, "change": row[change_key],
                                "volume": row[volume_key], "previous_oi_source": source})
        result[side] = {"summary": summary, "rows": output_rows}
    return result


def build_payload(run):
    analysis = json.loads((run / "analysis.json").read_text(encoding="utf-8"))
    price = json.loads((run / "price_context.json").read_text(encoding="utf-8"))
    text_fields(analysis, ("as_of_date", "contract", "expiry", "source_site", "extracted_at", "bias", "confidence"), "analysis")
    date.fromisoformat(analysis["as_of_date"])
    date.fromisoformat(analysis["expiry"])
    timestamp(analysis["extracted_at"], "analysis.extracted_at")
    require(analysis["bias"] in BIASES, "Unknown bias")
    require(analysis["confidence"] in CONFIDENCE, "Unknown confidence")
    require(isinstance(analysis.get("demo", False), bool), "demo must be boolean")
    require(analysis.get("sheet_write_status") in {"updated", "not_updated"}, "sheet_write_status required")
    text_fields(price, ("contract", "symbol", "timeframe", "observed_at", "confidence", "notes"), "price")
    timestamp(price["observed_at"], "price.observed_at")
    require(price["contract"] == analysis["contract"], "Chart context contract mismatch")
    require(price["confidence"] in CONFIDENCE, "Unknown price confidence")
    price["current_price"] = number(price["current_price"], "current_price", positive=True)
    precision = price.get("price_decimals", 2)
    require(type(precision) is int and 0 <= precision <= 6, "price_decimals must be 0..6")
    price["price_decimals"] = precision
    require(isinstance(price.get("approximate", False), bool), "price.approximate must be boolean")

    tables, latest, history, oi_snapshots = {}, {}, {}, {}
    for kind, filename in FILES.items():
        with (run / filename).open(newline="", encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
        contracts, expiries = validate(rows, kind, filename)
        require(contracts == {analysis["contract"]} and expiries == {analysis["expiry"]}, f"{filename}: contract/expiry mismatch")
        seen, aggregates = set(), {}
        for row in rows:
            day = row["as_of_date"]
            require(date.fromisoformat(day).isoformat() == day, f"{filename}: use ISO date")
            row["strike"] = number(row["strike"], "strike", positive=True)
            key = (day, row["strike"])
            require(key not in seen, f"{filename}: duplicate normalized date/strike")
            seen.add(key)
            for column in COLUMNS[kind]:
                row[column] = number(row[column], column, count=True)
            if kind == "oi":
                row["underlying_price"] = number(row.get("underlying_price"), "underlying_price", positive=True)
                oi_snapshots.setdefault(day, {})[row["strike"]] = row
            pair = aggregates.setdefault(day, [0, 0])
            for i, column in enumerate(COLUMNS[kind]):
                pair[i] += row[column]
                require(abs(pair[i]) <= 2**53 - 1, "Aggregate exceeds safe browser integer range")
        latest[kind] = max(aggregates)
        tables[kind] = {r["strike"]: r for r in rows if r["as_of_date"] == analysis["as_of_date"]}
        history[kind] = [{"date": day, "call": pair[0], "put": pair[1]} for day, pair in sorted(aggregates.items())]
    require(set(latest.values()) == {analysis["as_of_date"]}, "Latest dates must match analysis across all three CSVs")
    strikes = set(tables["oi"])
    require(strikes == set(tables["change"]) == set(tables["volume"]), "Latest strike coverage differs; resolve missing observations, never fill with zero")
    combined = [{"strike": strike, **{column: tables[kind][strike][column] for kind in COLUMNS for column in COLUMNS[kind]}}
                for strike in sorted(strikes)]
    totals = {column: sum(row[column] for row in combined) for columns in COLUMNS.values() for column in columns}
    totals.update(put_call_oi_ratio=ratio(totals["put_oi"], totals["call_oi"]),
                  put_call_volume_ratio=ratio(totals["put_volume"], totals["call_volume"]),
                  net_call_minus_put_oi_change=totals["call_oi_change"] - totals["put_oi_change"],
                  net_call_minus_put_volume=totals["call_volume"] - totals["put_volume"])
    # CSVs own numeric totals; reject stale known totals instead of displaying a second answer.
    for key, value in analysis.get("totals", {}).items():
        if key in totals:
            expected = totals[key]
            require(value is None if expected is None else value is not None and math.isclose(float(value), expected, rel_tol=1e-8, abs_tol=1e-8), f"analysis.totals.{key}: differs from CSV")
    for key in ("quick_read", "warnings"):
        require(isinstance(analysis.get(key), list) and all(isinstance(v, str) for v in analysis[key]), f"{key}: list of text required")
    require(4 <= len(analysis["quick_read"]) <= 6, "quick_read needs 4–6 bullets")
    require(isinstance(analysis.get("evidence"), list) and analysis["evidence"], "evidence required")
    for item in analysis["evidence"]:
        text_fields(item, ("label", "detail"), "evidence")
    require(isinstance(analysis.get("levels"), list) and analysis["levels"], "levels required")
    for level in analysis["levels"]:
        text_fields(level, ("role", "evidence", "interpretation", "confidence"), "level")
        level["strike"] = number(level["strike"], "level.strike", positive=True)
        require(level["confidence"] in CONFIDENCE, "Unknown level confidence")
    text_fields(analysis.get("positioning", {}), ("condition", "upside", "downside", "concentration", "invalidation"), "positioning")
    scenarios = analysis.get("scenarios", [])
    require(len(scenarios) == 3 and {s.get("id") for s in scenarios} == {"base", "reclaim", "breakdown"}, "Three unique scenarios required")
    for scenario in scenarios:
        text_fields(scenario, ("title", "trigger", "confirmation", "invalidation"), "scenario")
        require(isinstance(scenario.get("levels"), list) and scenario["levels"], "scenario.levels required")
        scenario["levels"] = [number(v, "scenario.level", positive=True) for v in scenario["levels"]]
    for kind in ("change", "volume"):
        with (run / FILES[kind]).open(newline="", encoding="utf-8-sig") as stream:
            coverage = {}
            for row in csv.DictReader(stream):
                coverage.setdefault(row["as_of_date"], set()).add(number(row["strike"], "strike", positive=True))
        if any(observed != strikes for observed in coverage.values()):
            analysis["warnings"].append(f"{FILES[kind]}: จำนวนหรือชุด strike ในประวัติต่างจาก snapshot ล่าสุด ยอดรายวันอาจเปรียบเทียบกันไม่ได้โดยตรง")
    top_changes = build_top_changes(analysis, combined, oi_snapshots)
    return {"analysis": analysis, "price": price, "rows": combined, "history": history, "totals": totals,
            "top_changes": top_changes}


def render(run):
    payload = build_payload(run)
    template = (Path(__file__).resolve().parent.parent / "assets/dashboard-template.html").read_text(encoding="utf-8")
    data = json.dumps(payload, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    # Replace the template once: embedded source strings must never become template instructions.
    head, tail = template.split("/*__PLOTLY__*/")
    middle, end = tail.split("/*__DATA__*/")
    html = head + get_plotlyjs() + middle + data + end
    output = run / "dashboard.html"
    temporary = output.with_suffix(".html.tmp")
    temporary.write_text(html, encoding="utf-8")
    temporary.replace(output)
    LOG.info("Rendered %s (%s strikes, as-of %s)", output, len(payload["rows"]), payload["analysis"]["as_of_date"])
    return output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        render(args.run_dir)
    except (ValueError, KeyError, TypeError, OSError, ArithmeticError) as error:
        LOG.error("Cannot render dashboard: %s", error)
        raise SystemExit(1)
