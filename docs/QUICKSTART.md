# เริ่มใช้โดยไม่ต้องมี Chrome/Sheets

คำสั่งต่อไปนี้ใช้ `python` เป็นชื่อย่อ ให้แทนด้วย Python ใน `.venv` ของตนตาม INSTALL และรันจาก root ของ repository

## ทดลอง renderer

```sh
python -X utf8 skills/gold-oi-tactical-dashboard/scripts/test_render_dashboard.py --demo-dir runs/demo
```

จะได้ `runs/demo/dashboard.html` พร้อมป้าย DEMO และ CSV/JSON สมมติ ตัวสร้างปฏิเสธโฟลเดอร์ที่มีข้อมูลอยู่แล้ว เปิด HTML ด้วย browser ได้โดยไม่ต้องรัน server รายงานฝังข้อมูลทั้งหมดไว้ ไม่มีการดึงราคาสด

DEMO ใช้เรียนและตรวจการติดตั้งเท่านั้น ห้ามนำไปตอบโจทย์ตลาดจริงหรือเขียนลง Sheet ตลาดจริง

## ใช้ข้อมูลจริงของตน

สร้างโฟลเดอร์ใหม่ เช่น `runs/my-snapshot/` แยกจาก DEMO เตรียม:

- `raw_oi.csv`, `raw_oi_change.csv`, `raw_volume.csv` ตาม [schema](../skills/gold-oi-tactical-dashboard/references/browser-and-sheets.md)
- `price_context.json` ที่มีราคาจริง symbol/timeframe และเวลาที่อ่าน ระบุ approximate สำหรับระดับที่กะจากภาพ
- `source_context.json` จดที่มาและวันเปรียบเทียบตาม [DATA-INPUT](DATA-INPUT.md)

ขอ agent อ่านไฟล์ ตรวจ source context และวิเคราะห์ตาม skill โดยใช้ prompt ใน PROMPTS โค้ดตรวจรูปแบบไม่สามารถยืนยันว่า CSV เป็นข้อมูลตลาดจริง

```sh
python -X utf8 skills/gold-oi-tactical-dashboard/scripts/validate_extracted_csv.py --oi runs/my-snapshot/raw_oi.csv --change runs/my-snapshot/raw_oi_change.csv --volume runs/my-snapshot/raw_volume.csv
python -X utf8 skills/gold-oi-tactical-dashboard/scripts/score_strikes.py --oi runs/my-snapshot/raw_oi.csv --change runs/my-snapshot/raw_oi_change.csv --volume runs/my-snapshot/raw_volume.csv --price PRICE_FROM_YOUR_CHART --out runs/my-snapshot/scored_strikes.json
```

`PRICE_FROM_YOUR_CHART` เป็น placeholder ต้องแทนด้วยราคาที่อ่านจริง Agent สร้าง `analysis.json` ตาม [content contract](../skills/gold-oi-tactical-dashboard/references/dashboard-spec.md) แล้วรัน:

```sh
python -X utf8 skills/gold-oi-tactical-dashboard/scripts/render_dashboard.py --run-dir runs/my-snapshot
```

โหมดนี้ตั้ง `sheet_write_status: not_updated` และรายงานว่าไม่ได้เขียน Sheet ถ้าได้รับอนุญาตภายหลังจึงเรียก connector, ตรวจสูตร/คอลัมน์เดิม, เขียนและอ่านกลับก่อนเปลี่ยนสถานะ

ก่อนส่ง HTML ตรวจยอดรวม signs, comparison date, prior-OI provenance, ทุกตัวกรอง, การคลิก, scenario และ desktop/mobile ดู [QA checklist](../skills/gold-oi-tactical-dashboard/SKILL.md)
