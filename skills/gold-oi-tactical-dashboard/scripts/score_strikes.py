#!/usr/bin/env python3
import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from validate_extracted_csv import load, validate_datasets

EPS = 1e-9


def fnum(v):
    if v is None or str(v).strip() == "":
        raise ValueError('Blank numeric value; do not substitute zero')
    result = float(str(v).replace(",", ""))
    if not math.isfinite(result):
        raise ValueError('Nonfinite numeric value')
    return result


def load_latest(path, value_cols):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return [], None
    dates = sorted({r["as_of_date"] for r in rows})
    latest = dates[-1]
    out = {}
    for r in rows:
        if r["as_of_date"] != latest:
            continue
        strike = fnum(r["strike"])
        out[strike] = {c: fnum(r.get(c)) for c in value_cols}
    return out, latest


def zscores(values):
    if not values:
        return []
    if len(values) < 2:
        return [0.0] * len(values)
    mu = statistics.mean(values)
    sd = statistics.pstdev(values)
    if sd < EPS:
        return [0.0] * len(values)
    return [(v - mu) / sd for v in values]


def pct_rank(value, values):
    if not values:
        return 0.0
    return sum(1 for v in values if v <= value) / len(values)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--oi", required=True)
    p.add_argument("--change", required=True)
    p.add_argument("--volume", required=True)
    p.add_argument("--price", required=True, type=float)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    if not math.isfinite(args.price) or args.price <= 0:
        p.error('--price must be finite and positive')
    validate_datasets({kind: load(getattr(args, kind)) for kind in ('oi','change','volume')})

    oi, d1 = load_latest(args.oi, ["call_oi", "put_oi"])
    ch, d2 = load_latest(args.change, ["call_oi_change", "put_oi_change"])
    vol, d3 = load_latest(args.volume, ["call_volume", "put_volume"])
    if not oi or not ch or not vol:
        raise SystemExit("All three datasets must contain rows")

    strikes = sorted(set(oi) | set(ch) | set(vol))
    if len(strikes) > 1:
        gaps = [b - a for a, b in zip(strikes[:-1], strikes[1:]) if b > a]
        median_gap = statistics.median(gaps) if gaps else max(args.price * 0.005, 1.0)
    else:
        median_gap = max(args.price * 0.005, 1.0)
    proximity_scale = max(median_gap * 2.0, args.price * 0.005, 1.0)

    call_abs_change = [abs(ch.get(s, {}).get("call_oi_change", 0.0)) for s in strikes]
    put_abs_change = [abs(ch.get(s, {}).get("put_oi_change", 0.0)) for s in strikes]
    call_vols = [vol.get(s, {}).get("call_volume", 0.0) for s in strikes]
    put_vols = [vol.get(s, {}).get("put_volume", 0.0) for s in strikes]
    call_ois = [oi.get(s, {}).get("call_oi", 0.0) for s in strikes]
    put_ois = [oi.get(s, {}).get("put_oi", 0.0) for s in strikes]

    z_cchg = zscores(call_abs_change)
    z_pchg = zscores(put_abs_change)
    z_cvol = zscores(call_vols)
    z_pvol = zscores(put_vols)
    z_coi = zscores(call_ois)
    z_poi = zscores(put_ois)

    ranked = []
    for i, s in enumerate(strikes):
        proximity = 1.0 / (1.0 + abs(s - args.price) / proximity_scale)
        call_score = 0.45*z_cchg[i] + 0.35*z_cvol[i] + 0.10*z_coi[i] + 0.10*proximity
        put_score = 0.45*z_pchg[i] + 0.35*z_pvol[i] + 0.10*z_poi[i] + 0.10*proximity
        side = "call" if call_score >= put_score else "put"
        score = max(call_score, put_score)
        ranked.append({
            "strike": s,
            "distance": s - args.price,
            "proximity": proximity,
            "call_oi": call_ois[i],
            "put_oi": put_ois[i],
            "call_oi_change": ch.get(s, {}).get("call_oi_change", 0.0),
            "put_oi_change": ch.get(s, {}).get("put_oi_change", 0.0),
            "call_volume": call_vols[i],
            "put_volume": put_vols[i],
            "call_score": call_score,
            "put_score": put_score,
            "dominant_activity_side": side,
            "significance_score": score,
            "call_oi_percentile": pct_rank(call_ois[i], call_ois),
            "put_oi_percentile": pct_rank(put_ois[i], put_ois),
            "call_change_percentile": pct_rank(call_abs_change[i], call_abs_change),
            "put_change_percentile": pct_rank(put_abs_change[i], put_abs_change),
            "call_volume_percentile": pct_rank(call_vols[i], call_vols),
            "put_volume_percentile": pct_rank(put_vols[i], put_vols),
        })

    ranked.sort(key=lambda x: x["significance_score"], reverse=True)

    total_call_oi = sum(call_ois)
    total_put_oi = sum(put_ois)
    total_call_change = sum(ch.get(s, {}).get("call_oi_change", 0.0) for s in strikes)
    total_put_change = sum(ch.get(s, {}).get("put_oi_change", 0.0) for s in strikes)
    total_call_volume = sum(call_vols)
    total_put_volume = sum(put_vols)

    result = {
        "latest_dates": {"oi": d1, "oi_change": d2, "volume": d3},
        "price": args.price,
        "totals": {
            "call_oi": total_call_oi,
            "put_oi": total_put_oi,
            "put_call_oi_ratio": total_put_oi / total_call_oi if total_call_oi else None,
            "call_oi_change": total_call_change,
            "put_oi_change": total_put_change,
            "net_call_minus_put_oi_change": total_call_change - total_put_change,
            "call_volume": total_call_volume,
            "put_volume": total_put_volume,
            "put_call_volume_ratio": total_put_volume / total_call_volume if total_call_volume else None,
            "oi_balance": (total_call_oi - total_put_oi) / (total_call_oi + total_put_oi + EPS),
            "oi_change_balance": (total_call_change - total_put_change) / (abs(total_call_change) + abs(total_put_change) + EPS),
            "volume_balance": (total_call_volume - total_put_volume) / (total_call_volume + total_put_volume + EPS),
        },
        "ranked_strikes": ranked,
        "method_note": "Scores rank activity significance only. They do not prove bullish/bearish trade direction or dealer gamma sign. Assign support/resistance/wall labels only after chart confirmation."
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(args.out)


if __name__ == "__main__":
    main()
