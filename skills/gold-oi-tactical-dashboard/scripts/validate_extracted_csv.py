#!/usr/bin/env python3
import argparse
import csv
import math
import sys
from datetime import date
from pathlib import Path

SCHEMAS = {
    "oi": ["as_of_date", "contract", "expiry", "strike", "call_oi", "put_oi"],
    "change": ["as_of_date", "contract", "expiry", "strike", "call_oi_change", "put_oi_change"],
    "volume": ["as_of_date", "contract", "expiry", "strike", "call_volume", "put_volume"],
}


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def require_columns(rows, required, label):
    if not rows:
        raise ValueError(f"{label}: no rows")
    cols = set(rows[0].keys())
    missing = [c for c in required if c not in cols]
    if missing:
        raise ValueError(f"{label}: missing columns {missing}")


def numeric(v, label):
    if v is None or str(v).strip() == "":
        raise ValueError(f"blank numeric value in {label}")
    try:
        result = float(str(v).replace(",", ""))
        if not math.isfinite(result) or abs(result) > 2**53 - 1:
            raise ValueError('nonfinite or unsafe number')
        return result
    except Exception as e:
        raise ValueError(f"invalid/unsafe numeric value {v!r} in {label}") from e


def validate(rows, kind, label):
    require_columns(rows, SCHEMAS[kind], label)
    seen = set()
    contracts = set()
    expiries = set()
    for i, r in enumerate(rows, start=2):
        for field in ('as_of_date', 'expiry'):
            if date.fromisoformat(r[field]).isoformat() != r[field]:
                raise ValueError(f'{label}: invalid ISO {field} at row {i}')
        if not r['contract'].strip():
            raise ValueError(f'{label}: missing contract at row {i}')
        strike = numeric(r['strike'], f'{label} row {i} strike')
        if strike <= 0:
            raise ValueError(f'{label}: strike must be positive')
        key = (r["as_of_date"], r["contract"], r["expiry"], strike)
        if key in seen:
            raise ValueError(f"{label}: duplicate key at CSV row {i}: {key}")
        seen.add(key)
        contracts.add(r["contract"])
        expiries.add(r["expiry"])
        numeric(r["strike"], f"{label} row {i} strike")
        for field in SCHEMAS[kind][4:]:
            value = numeric(r[field], f'{label} row {i} {field}')
            if value != int(value):
                raise ValueError(f'{label}: contract count must be an integer at row {i}')
        if kind == "oi":
            if numeric(r["call_oi"], f"{label} row {i} call_oi") < 0:
                raise ValueError(f"{label}: negative call_oi at row {i}")
            if numeric(r["put_oi"], f"{label} row {i} put_oi") < 0:
                raise ValueError(f"{label}: negative put_oi at row {i}")
        elif kind == "change":
            numeric(r["call_oi_change"], f"{label} row {i} call_oi_change")
            numeric(r["put_oi_change"], f"{label} row {i} put_oi_change")
        else:
            if numeric(r["call_volume"], f"{label} row {i} call_volume") < 0:
                raise ValueError(f"{label}: negative call_volume at row {i}")
            if numeric(r["put_volume"], f"{label} row {i} put_volume") < 0:
                raise ValueError(f"{label}: negative put_volume at row {i}")
    return contracts, expiries


def validate_datasets(datasets):
    meta = {kind: validate(rows, kind, kind) for kind, rows in datasets.items()}
    if any(len(v[0]) != 1 or len(v[1]) != 1 for v in meta.values()):
        raise ValueError('Each dataset must contain exactly one contract and expiry')
    if len({next(iter(v[0])) for v in meta.values()}) != 1 or len({next(iter(v[1])) for v in meta.values()}) != 1:
        raise ValueError('Contract/expiry mismatch across datasets')
    latest = {kind: max(r['as_of_date'] for r in rows) for kind, rows in datasets.items()}
    if len(set(latest.values())) != 1:
        raise ValueError('Latest dates differ across datasets')
    coverage = [{numeric(r['strike'], 'strike') for r in rows if r['as_of_date'] == latest[kind]}
                for kind, rows in datasets.items()]
    if any(c != coverage[0] for c in coverage):
        raise ValueError('Latest strike coverage differs; missing data cannot be zero-filled')
    return latest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--oi", required=True)
    p.add_argument("--change", required=True)
    p.add_argument("--volume", required=True)
    args = p.parse_args()

    datasets = {
        "oi": load(args.oi),
        "change": load(args.change),
        "volume": load(args.volume),
    }
    validate_datasets(datasets)
    meta = {}
    for kind, rows in datasets.items():
        meta[kind] = validate(rows, kind, Path(getattr(args, kind)).name)

    contract_sets = [m[0] for m in meta.values()]
    expiry_sets = [m[1] for m in meta.values()]
    if any(len(s) != 1 for s in contract_sets):
        raise ValueError(f"multiple contracts detected: {contract_sets}")
    if any(len(s) != 1 for s in expiry_sets):
        raise ValueError(f"multiple expiries detected: {expiry_sets}")
    if len({next(iter(s)) for s in contract_sets}) != 1:
        raise ValueError(f"contract mismatch across datasets: {contract_sets}")
    if len({next(iter(s)) for s in expiry_sets}) != 1:
        raise ValueError(f"expiry mismatch across datasets: {expiry_sets}")

    print("VALIDATION_OK")
    print(f"rows_oi={len(datasets['oi'])}")
    print(f"rows_change={len(datasets['change'])}")
    print(f"rows_volume={len(datasets['volume'])}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"VALIDATION_ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
