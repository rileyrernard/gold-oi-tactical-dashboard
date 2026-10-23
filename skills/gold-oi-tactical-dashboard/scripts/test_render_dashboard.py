#!/usr/bin/env python3
"""Renderer regression checks and explicitly synthetic report fixtures."""
import argparse
import csv
import json
import logging
import math
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from render_dashboard import build_payload, build_top_changes, render, ratio

LOG = logging.getLogger(__name__)


def activity_row(strike, call_change=0, put_change=0, call_oi=100, put_oi=200,
                 call_volume=10, put_volume=20):
    """Small synthetic records make ranking and provenance expectations explicit."""
    return {"strike": strike, "call_oi": call_oi, "put_oi": put_oi,
            "call_oi_change": call_change, "put_oi_change": put_change,
            "call_volume": call_volume, "put_volume": put_volume}


class TopChangesTests(unittest.TestCase):
    def setUp(self):
        self.analysis = {"as_of_date": "2026-09-10"}

    def build(self, rows, snapshots=None):
        return build_top_changes(self.analysis, rows, snapshots or {})

    def test_absolute_changes_independent_sides_and_deterministic_ties(self):
        rows = [activity_row(3040, 10, 2, call_volume=99),
                activity_row(3030, -10, 25, call_volume=7),
                activity_row(3020, 10, -30, call_volume=7),
                activity_row(3010, -50, 0),
                activity_row(3000, 0, 0)]
        result = self.build(rows)
        self.assertEqual([r["strike"] for r in result["call"]["rows"]], [3010, 3040, 3020, 3030])
        self.assertEqual([r["change"] for r in result["call"]["rows"]], [-50, 10, 10, -10])
        self.assertEqual([r["strike"] for r in result["put"]["rows"]], [3020, 3030, 3040])
        self.assertEqual([r["rank"] for r in result["call"]["rows"]], [1, 2, 3, 4])
        self.assertEqual(result, self.build(list(reversed(rows))))
        self.assertEqual(result["ranking"], "absolute_oi_change")

    def test_synthetic_reference_rows_preserve_values_and_sign(self):
        # Original synthetic values, not market data or provider screenshot rows.
        rows = [activity_row(3100, -40, call_oi=160, put_oi=0,
                             call_volume=55, put_volume=0),
                activity_row(3050, 25, call_oi=125, put_oi=0,
                             call_volume=35, put_volume=0),
                activity_row(2900, put_change=12, call_oi=0, put_oi=62,
                             call_volume=0, put_volume=18)]
        result = self.build(rows)
        self.assertEqual(result["call"]["rows"], [
            {"rank": 1, "strike": 3100, "oi": 160, "previous_oi": 200,
             "change": -40, "volume": 55, "previous_oi_source": "derived"},
            {"rank": 2, "strike": 3050, "oi": 125, "previous_oi": 100,
             "change": 25, "volume": 35, "previous_oi_source": "derived"}])
        self.assertEqual(result["put"]["rows"], [
            {"rank": 1, "strike": 2900, "oi": 62, "previous_oi": 50,
             "change": 12, "volume": 18, "previous_oi_source": "derived"}])
        self.assertIsNone(result["comparison_date"])

    def test_limit_does_not_truncate_summary_or_pad_short_sides(self):
        rows = [activity_row(3000 + i * 5, i + 1, -1 if i == 0 else 0,
                             call_oi=100 + i, call_volume=10 + i) for i in range(18)]
        result = self.build(rows)
        self.assertEqual(result["limit"], 15)
        self.assertEqual(len(result["call"]["rows"]), 15)
        self.assertEqual(result["call"]["rows"][-1]["change"], 4)
        self.assertEqual(len(result["put"]["rows"]), 1)
        self.assertEqual(result["call"]["summary"], {"total_oi": 1953, "total_volume": 333,
                         "net_change": 171, "increased_strikes": 18,
                         "decreased_strikes": 0, "unchanged_strikes": 0})
        self.assertEqual(result["put"]["summary"]["unchanged_strikes"], 17)
        self.assertEqual(result["put"]["summary"]["decreased_strikes"], 1)

    def test_all_zero_changes_are_available_with_empty_rankings(self):
        result = self.build([activity_row(3000), activity_row(3025)])
        self.assertEqual(result["status"], "available")
        self.assertIsNone(result["unavailable_reason"])
        for side in ("call", "put"):
            self.assertEqual(result[side]["rows"], [])
            self.assertEqual(result[side]["summary"]["net_change"], 0)
            self.assertEqual(result[side]["summary"]["unchanged_strikes"], 2)

    def test_explicit_previous_observations_are_verified_and_preferred(self):
        self.analysis["oi_change_comparison_date"] = "2026-09-08"
        rows = [activity_row(3000, 7, -5), activity_row(3025, -4, 2)]
        earlier = {3000: {"call_oi": 93, "put_oi": 205}, 3025: {"call_oi": 104, "put_oi": 198}}
        result = self.build(rows, {"2026-09-08": earlier, "2026-09-09": {3000: {"call_oi": 1, "put_oi": 1}}})
        self.assertEqual(result["comparison_date"], "2026-09-08")
        self.assertEqual(result["call"]["rows"][0]["previous_oi"], 93)
        self.assertEqual(result["put"]["rows"][0]["previous_oi"], 205)
        self.assertTrue(all(row["previous_oi_source"] == "observed" for side in ("call", "put") for row in result[side]["rows"]))
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.build(rows, {"2026-09-08": {3000: earlier[3000]}})
        earlier[3025]["put_oi"] = 199
        with self.assertRaisesRegex(ValueError, "reconcile"):
            self.build(rows, {"2026-09-08": earlier})

    def test_auto_date_requires_immediately_prior_complete_exact_snapshot(self):
        rows = [activity_row(3000, 7, -5)]
        exact = {3000: {"call_oi": 93, "put_oi": 205}}
        matched = self.build(rows, {"2026-09-09": exact})
        self.assertEqual(matched["comparison_date"], "2026-09-09")
        self.assertEqual(matched["call"]["rows"][0]["previous_oi_source"], "observed")
        for prior in ({3000: {"call_oi": 93, "put_oi": 204}},
                      {3000: exact[3000], 3025: exact[3000]}):
            unmatched = self.build(rows, {"2026-09-08": exact, "2026-09-09": prior})
            self.assertIsNone(unmatched["comparison_date"])
            self.assertEqual(unmatched["call"]["rows"][0]["previous_oi_source"], "derived")
            self.assertEqual(unmatched["call"]["rows"][0]["previous_oi"], 93)

    def test_derived_previous_oi_keeps_unknown_date_null(self):
        rows = [activity_row(3000, 7, -5)]
        result = self.build(rows)
        self.assertIsNone(result["comparison_date"])
        self.assertEqual(result["call"]["rows"][0]["previous_oi"], 93)
        self.assertEqual(result["put"]["rows"][0]["previous_oi"], 205)
        self.assertEqual(result["put"]["rows"][0]["previous_oi_source"], "derived")
        self.analysis["oi_change_comparison_date"] = "2026-09-09"
        declared = self.build(rows)
        self.assertEqual(declared["comparison_date"], "2026-09-09")
        self.assertEqual(declared["put"]["rows"][0]["previous_oi_source"], "derived")

    def test_impossible_derived_previous_oi_is_unavailable(self):
        result = self.build([activity_row(3000, 3, -2, call_oi=2)])
        call = result["call"]["rows"][0]
        self.assertIsNone(call["previous_oi"])
        self.assertEqual(call["previous_oi_source"], "unavailable")
        self.assertEqual(result["put"]["rows"][0]["previous_oi_source"], "derived")

    def test_latest_excluded_baseline_does_not_become_daily_flow(self):
        self.analysis["history_exclusions"] = {"change": {"2026-09-10": "Initial baseline"}}
        result = self.build([activity_row(3000, 100, 200)])
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["unavailable_reason"], "Initial baseline")
        self.assertIsNone(result["comparison_date"])
        for side in ("call", "put"):
            self.assertEqual(result[side]["rows"], [])
            for key in ("net_change", "increased_strikes", "decreased_strikes", "unchanged_strikes"):
                self.assertIsNone(result[side]["summary"][key])
        self.assertEqual(result["call"]["summary"]["total_oi"], 100)
        self.assertEqual(result["put"]["summary"]["total_volume"], 20)
        self.analysis["history_exclusions"] = {"change": {"2026-09-09": "Initial baseline"}}
        self.assertEqual(self.build([activity_row(3000, 1)])["status"], "available")

    def test_comparison_date_is_canonical_and_strictly_earlier(self):
        for bad in ("2026-09-10", "2026-09-11", "20260909", "09/09/2026", "2026-02-30", 20260909):
            with self.subTest(value=bad):
                self.analysis["oi_change_comparison_date"] = bad
                with self.assertRaises((ValueError, TypeError)):
                    self.build([activity_row(3000, 1)])


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def demo(run):
    run.mkdir(parents=True, exist_ok=True)
    contract, expiry = "DEMO-GC", "2026-11-24"
    fields = {"raw_oi.csv": ["call_oi", "put_oi", "underlying_price"],
              "raw_oi_change.csv": ["call_oi_change", "put_oi_change"],
              "raw_volume.csv": ["call_volume", "put_volume"]}
    for filename, columns in fields.items():
        with (run / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=["as_of_date", "contract", "expiry", "strike"] + columns)
            writer.writeheader()
            for day in range(1, 11):
                for strike in range(3000, 3801, 25):
                    call = math.exp(-((strike - 3450) / 155) ** 2)
                    put = math.exp(-((strike - 3300) / 145) ** 2)
                    values = {"call_oi": round(9500 * call + day * 23), "put_oi": round(6800 * put + day * 17),
                              "underlying_price": 3406.25, "call_oi_change": round((day - 4) * 65 * call - 55),
                              "put_oi_change": round((6 - day) * 55 * put + 15),
                              "call_volume": round((700 + day * 90) * call + 30),
                              "put_volume": round((1000 - day * 35) * put + 25)}
                    writer.writerow({"as_of_date": f"2026-09-{day:02}", "contract": contract, "expiry": expiry,
                                     "strike": strike, **{c: values[c] for c in columns}})
    price = {"as_of_date": "2026-09-10", "contract": contract, "symbol": "DEMO GOLD", "timeframe": "H1",
             "observed_at": "2026-09-10T14:30:00+07:00", "current_price": 3406.25, "price_decimals": 2,
             "visible_swing_high": 3460, "visible_swing_low": 3340, "trend_state": "range",
             "supports": [3350, 3300], "resistances": [3450, 3500], "confidence": "medium",
             "notes": "ตัวอย่างสมมติ: ราคาเคลื่อนไหวในกรอบ 3,350–3,450 รอหลักฐานยืนยันการออกจากกรอบ"}
    levels = [{"strike": strike, "role": role, "evidence": evidence,
               "interpretation": interpretation, "confidence": "medium"}
              for strike, role, evidence, interpretation in [
                  (3550, "จุดติดตามด้านบน", "ระดับประกอบ scenario จำลอง", "ติดตามเมื่อราคาผ่านระดับ 3,500 ได้ตามเงื่อนไข"),
                  (3500, "ระดับยืนยันต่อเนื่อง", "Call OI + Volume ในข้อมูลจำลอง", "ใช้ดูว่าการเคลื่อนขึ้นมีแรงต่อเนื่องหรือไม่"),
                  (3450, "Reclaim level", "Call ΔOI และ Volume เด่นในชุดจำลอง", "รอราคายืนเหนือและกลับทดสอบโดยไม่หลุด"),
                  (3400, "Pivot", "ใกล้ราคากราฟสมมติ", "บริเวณตัดสินใจกลางกรอบ ไม่ใช้ทำนายทิศทางล่วงหน้า"),
                  (3350, "Support candidate", "โครงสร้างราคาสมมติ + Put activity", "เฝ้าดูการตอบสนอง หากรับไม่อยู่ให้ประเมิน scenario ใหม่"),
                  (3300, "จุดติดตามด้านล่าง", "Put OI กระจุกตัวในชุดจำลอง", "เป็นบริเวณที่ต้องดูการตอบสนอง ไม่ใช่เป้าหมายที่รับประกัน")]]
    analysis = {"as_of_date": "2026-09-10", "contract": contract, "expiry": expiry,
                "source_site": "Synthetic demo data", "extracted_at": "2026-09-10T14:35:00+07:00",
                "demo": True, "sheet_write_status": "not_updated", "bias": "Range / Neutral", "confidence": "medium",
                "quick_read": ["ราคาสมมติอยู่ใกล้ pivot 3,400 ภายในกรอบ 3,350–3,450",
                               "Call OI ในชุดจำลองกระจุกบริเวณ 3,450 ส่วน Put OI อยู่แถว 3,300",
                               "ΔOI ล่าสุดของ Call และ Put เคลื่อนไหวต่างกัน ต้องดูคู่กับราคา",
                               "ติดตาม 3,450 ด้านบน และ 3,350 ด้านล่างก่อนเปลี่ยนมุมมอง"],
                "evidence": [{"label": "Price structure", "detail": "กรอบสมมติ 3,350–3,450 · ราคายังไม่ยืนยันการออกจากกรอบ"},
                             {"label": "OI / OI Change / Volume", "detail": "ตัวเลขทั้งหมดสร้างขึ้นเพื่อทดสอบ UI; คลิก strike เพื่อเปรียบเทียบ Call และ Put"},
                             {"label": "Tactical bias", "detail": "Range / Neutral · ความเชื่อมั่นปานกลางสำหรับตัวอย่างนี้เท่านั้น"}],
                "levels": levels,
                "positioning": {"condition": "ข้อมูลจำลองแสดงกิจกรรมคนละด้านของราคา ยังต้องรอ price confirmation",
                                "upside": "ติดตามการ reclaim บริเวณ 3,450", "downside": "ติดตามการหลุด 3,350",
                                "concentration": "Call ใกล้ 3,450 / Put ใกล้ 3,300", "invalidation": "เปลี่ยนมุมมองเมื่อราคายืนยันนอกกรอบและมีข้อมูล options รอบใหม่สนับสนุน"},
                "scenarios": [
                    {"id": "base", "title": "Base · อยู่ในกรอบ", "levels": [3350, 3400, 3450],
                     "trigger": "ราคาสมมติยังอยู่ระหว่าง 3,350–3,450", "confirmation": "การกลับทดสอบขอบกรอบยังไม่ผ่าน และราคาไม่ยอมรับนอกกรอบ",
                     "invalidation": "H1 ยืนยันเหนือ 3,450 หรือใต้ 3,350 พร้อมการกลับทดสอบ"},
                    {"id": "reclaim", "title": "Reclaim · ผ่านด้านบน", "levels": [3450, 3500, 3550],
                     "trigger": "H1 ปิดเหนือ 3,450 แล้วกลับทดสอบโดยไม่หลุด", "confirmation": "โครงสร้างทำ higher low และติดตามกิจกรรมรอบใหม่ที่ 3,450",
                     "invalidation": "ราคากลับมายอมรับใต้ 3,450"},
                    {"id": "breakdown", "title": "Breakdown · หลุดด้านล่าง", "levels": [3350, 3300],
                     "trigger": "H1 ปิดใต้ 3,350 แล้วกลับขึ้นทดสอบไม่ผ่าน", "confirmation": "โครงสร้างทำ lower high และเฝ้าดูการตอบสนองใกล้ 3,300",
                     "invalidation": "ราคากลับยืนเหนือ 3,350"}],
                "warnings": ["ข้อมูลจำลองสำหรับตรวจการแสดงผลเท่านั้น ไม่ได้เชื่อมต่อแหล่งข้อมูลสดหรือเขียน Google Sheets"]}
    write_json(run / "price_context.json", price)
    write_json(run / "analysis.json", analysis)
    return analysis


def smoke():
    with TemporaryDirectory(prefix="gold-oi-test-") as folder:
        run = Path(folder)
        analysis = demo(run)
        payload = build_payload(run)
        assert len(payload["rows"]) == 33 and len(payload["history"]["change"]) == 10
        assert payload["top_changes"]["as_of_date"] == analysis["as_of_date"]
        assert payload["top_changes"]["call"]["summary"]["total_oi"] == payload["totals"]["call_oi"]
        assert payload["totals"]["call_oi"] == sum(row["call_oi"] for row in payload["rows"])
        assert payload["totals"]["put_call_oi_ratio"] == payload["totals"]["put_oi"] / payload["totals"]["call_oi"]
        assert ratio(2, 0) is None and ratio(0, 0) is None
        analysis["quick_read"][0] = '</script><img src=x onerror="alert(1)">'
        write_json(run / "analysis.json", analysis)
        html = render(run).read_text(encoding="utf-8")
        assert analysis["quick_read"][0] not in html
        assert '\\u003c/script>' in html and '<script src=' not in html
        assert '"demo": true' in html
        volume = run / "raw_volume.csv"
        original = volume.read_text(encoding="utf-8")
        for bad, expected in [(original.replace("2026-09-10", "2026-09-11"), "Latest dates"),
                              (original.replace(",3000,", ",NaN,", 1), "invalid/unsafe"),
                              (original.replace("2026-11-24", "2026-12-24"), "contract/expiry"),
                              (original.replace("DEMO-GC", "DIFFERENT"), "contract/expiry")]:
            volume.write_text(bad, encoding="utf-8")
            try:
                build_payload(run)
            except ValueError as error:
                assert expected in str(error), str(error)
            else:
                raise AssertionError("Invalid input unexpectedly accepted")
        volume.write_text(original, encoding="utf-8")
        lines = original.splitlines()
        volume.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
        try:
            build_payload(run)
        except ValueError as error:
            assert "coverage" in str(error)
        else:
            raise AssertionError("Missing latest strike accepted")
        volume.write_text(original, encoding="utf-8")
        change = run / "raw_oi_change.csv"
        with change.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        rows[-1]["call_oi_change"] = ""
        with change.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        try:
            build_payload(run)
        except ValueError as error:
            assert "blank numeric" in str(error), str(error)
        else:
            raise AssertionError("Missing daily change silently accepted as zero")
    LOG.info("PASS: totals, zero denominator, safe embedding, dates, contract, finite numbers, missing strikes")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-dir", type=Path)
    args = parser.parse_args()
    regression = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TopChangesTests))
    if not regression.wasSuccessful():
        raise SystemExit(1)
    smoke()
    if args.demo_dir:
        require_empty = not args.demo_dir.exists() or not any(args.demo_dir.iterdir())
        if not require_empty:
            raise SystemExit("Use a new/empty demo directory; never overwrite an existing report")
        demo(args.demo_dir)
        render(args.demo_dir)
