# Prompt พร้อมใช้

## Preflight อ่านอย่างเดียว

```text
ใช้ skill gold-oi-tactical-dashboard ตรวจความพร้อมของโปรเจกต์นี้
ตรวจ Python ใน .venv, Plotly, template และ renderer smoke test
บอกว่าแอปนี้เข้าถึง local files, Chrome และ Google Sheets ได้จริงแค่ไหน
ขั้นนี้ยังไม่วิเคราะห์ตลาด ไม่เขียน Sheet และไม่เปลี่ยนกราฟ
หาก integration ขาด ให้ใช้ CSV เมื่อฉันให้ข้อมูลจริง ห้ามใช้ DEMO หรือ snapshot เก่าทดแทน
```

## CSV workflow

```text
ใช้ skill gold-oi-tactical-dashboard กับข้อมูลจริงใน runs/my-snapshot
อ่าน source_context.json, raw_oi.csv, raw_oi_change.csv, raw_volume.csv และ price_context.json
ตรวจ contract/expiry/date, comparison date, strike coverage, source totals, units และ price basis ก่อนวิเคราะห์
ข้อมูลหายหรือไม่สอดคล้องให้หยุด ระบุจุดที่แก้ได้ ห้ามแต่งตัวเลขหรือเติมศูนย์แทนช่องที่ไม่รู้
ใช้ Python ใน .venv พร้อม -X utf8 รัน validator และ scorer แล้วสร้าง analysis.json
วิเคราะห์ไทย เน้น ΔOI และ Volume ประกอบโครงสร้างราคา พร้อม Positioning และ base/reclaim/breakdown ที่มี trigger, confirmation, invalidation
โหมดนี้ยังไม่อนุญาตเขียน Google Sheet ให้บันทึก not_updated
สร้าง dashboard.html ทดสอบตัวเลข Top15, clicks, keyboard, filters, history, desktop/mobile และ KPI คงเดิม
รายงานข้อจำกัดอย่างตรงไปตรงมา ไม่อ้างว่า Call/Put หรือ OI บอก long/short intent
```

แทน path ให้ตรงกับโฟลเดอร์จริง Codex เริ่มด้วย `$gold-oi-tactical-dashboard` ส่วน Claude Code เริ่มด้วย `/gold-oi-tactical-dashboard` ได้ สำหรับ Antigravity บอกชื่อ skill ตามข้อความข้างต้น

## Live workflow เมื่อ integration พร้อม

```text
ใช้ skill gold-oi-tactical-dashboard จากแท็บ Chrome ที่เปิดและฉันมีสิทธิ์เข้าถึง
ตรวจการเข้าถึง Chrome และ Google Sheet ก่อน ถ้ามีหลาย Sheet ให้ถามเป้าหมายก่อนเขียน
อนุญาตอ่านเฉพาะแท็บ OI, OI Change, Volume, กราฟราคาทอง และ Sheet เป้าหมาย
อนุญาตอัปเดตเฉพาะ managed ranges ตาม skill รักษาข้อมูลเก่า สูตรและคอลัมน์อื่น ตรวจ metadata/สูตรก่อนเขียนและอ่านกลับหลังเขียน
อ่าน contract, expiry, as-of และ comparison date จากหน้าปัจจุบัน ไม่เปลี่ยนกราฟหรือ indicators
ถ้าขาด tool/data หรือข้อมูลไม่สอดคล้อง ให้หยุด ห้ามไปใช้ข้อมูล DEMO หรือวันเก่า
ใช้ Python .venv -X utf8 วิเคราะห์ไทยและสร้าง Dashboard พร้อม Top15, Positioning, Swing scenarios และ QA desktop/mobile
เปิด Dashboard พร้อมสรุปวันที่ข้อมูล ราคา bias ระดับสำคัญ ข้อจำกัด และสถานะ Sheet ตามที่ตรวจได้จริง
```

การอนุญาตใน prompt นี้ใช้กับ Sheet เป้าหมายของรอบนั้นเท่านั้น ไม่มีการส่ง Telegram, วาด MT4/MT5 หรือส่งคำสั่งซื้อขาย
