# Gold OI Tactical Dashboard

**Armriley** · Agent skill + Python/Plotly · ภาษาไทย · Version 1.0.0

[![Python renderer and installer](https://github.com/rileyrernard/gold-oi-tactical-dashboard/actions/workflows/test.yml/badge.svg)](https://github.com/rileyrernard/gold-oi-tactical-dashboard/actions/workflows/test.yml)

[สไลด์ Canva 28 หน้า — เปิดดูสาธารณะ](https://canva.link/aa12h38et04fwko) · [บทผู้สอน 60 นาที](teaching/TEACHER-GUIDE-TH.md)

อ่าน Gold **options** OI, OI Change และ Volume ร่วมกับกราฟราคา แล้วสร้าง `dashboard.html` ที่ฝังข้อมูลและ Plotly ในไฟล์เดียว มี Top 15 Call/Put, strike explorer, Level Map, Positioning และ Swing scenarios

## เริ่มที่นี่

1. ดาวน์โหลด repository ด้วย **Code → Download ZIP** แล้วแตกไฟล์ หรือ `git clone https://github.com/rileyrernard/gold-oi-tactical-dashboard.git`
2. เปิดโฟลเดอร์นี้ในโปรแกรมที่ใช้ แล้วทำตาม [คู่มือติดตั้ง](docs/INSTALL.md)
3. ทดลอง [DEMO](docs/QUICKSTART.md) ก่อนใช้ CSV ของตนเอง DEMO ใช้ฝึกเท่านั้น
4. อ่าน [วิธีอ่าน OI](docs/OI-READING-TH.md) และ [สไลด์/คู่มือสอน 60 นาที](teaching/README.md)

```powershell
# Windows: ใช้ PowerShell ในโฟลเดอร์ที่แตกไฟล์
py -3 -m venv .venv
.\.venv\Scripts\python.exe -X utf8 -m pip install -r skills/gold-oi-tactical-dashboard/requirements.txt
.\.venv\Scripts\python.exe -X utf8 tools/install_skill.py --agent codex --project .
.\.venv\Scripts\python.exe -X utf8 skills/gold-oi-tactical-dashboard/scripts/test_render_dashboard.py
```

เปลี่ยน `--agent codex` เป็น `claude` หรือ `antigravity` ตามโปรแกรมที่ใช้ ตัวติดตั้งคัดลอก skill ทั้งโฟลเดอร์ ไม่แก้ config และไม่เขียนทับ skill เดิม

## รองรับอะไร

| เส้นทาง | ขอบเขต |
| --- | --- |
| CSV + Python | ทางหลัก ใช้ไฟล์ตาม schema เดียวกันใน Codex, Claude Code และ Antigravity ที่มี local shell/filesystem |
| Chrome + Google Sheets | เสริมตามเครื่องมือที่แต่ละแอป/บัญชีให้ใช้ ต้อง preflight แยกก่อนทุกครั้ง |
| Claude เว็บ/มือถือ | แชททั่วไปไม่ได้เข้าถึงไฟล์เครื่องโดยอัตโนมัติ ดูข้อจำกัดใน INSTALL |
| HTML ที่สร้างแล้ว | ส่งไฟล์เดียวไปเปิดอ่านและคลิกกรองบนเครื่องอื่นได้ ไม่ดึงข้อมูลสด |

ทดสอบ Python/renderer และ installer ในสภาพแวดล้อม Windows ของผู้จัดทำ การรันทดสอบผ่านไม่เท่ากับยืนยัน integration ทุกแอป ดู [สถานะการทดสอบ](docs/COMPATIBILITY.md)

## การตีความที่สำคัญ

Price/OI matrix 4 ช่องเป็น heuristic ของ **futures สัญญาเดียวกันและช่วงเดียวกัน** ส่วนข้อมูลใน Dashboard เป็น **options แยก Call/Put/strike/expiry** อย่านำสองอย่างนี้มาแทนกัน Call OI เพิ่มยังมีทั้งผู้ซื้อและผู้ขาย ไม่พิสูจน์ขาขึ้นหรือ dealer gamma

โค้ดคำนวณตัวเลขและแสดงผล ส่วนเหตุผล/ระดับ/สถานการณ์มาจาก agent และผู้ใช้ จึงต้องตรวจหลักฐานและจุดยกเลิกเสมอ คะแนนกิจกรรมไม่ใช่โมเดลพยากรณ์ที่ผ่านการทดสอบผลตอบแทน

## สิทธิ์และข้อมูล

- โค้ด, skill และ HTML template: [MIT](LICENSE) โดย Armriley
- คู่มือและเนื้อหาการสอนที่สร้างสำหรับโครงการ: [CC BY 4.0](LICENSE-CONTENT.md)
- ใช้และดัดแปลงเชิงพาณิชย์ได้ตามเงื่อนไขสิทธิ์ การให้เครดิตไม่ทำให้เกิดการรับรองจากผู้จัดทำ
- ไม่รวมข้อมูลตลาดจริง, ภาพ CME/TradingView, credentials, Sheet ID หรือบัญชีผู้สอน สิทธิ์โค้ดไม่ครอบคลุมข้อมูลจากผู้ให้บริการ
- [Third-party notices](THIRD_PARTY_NOTICES.md) และ [แหล่งอ้างอิง](docs/SOURCES.md)

ข้อมูลนี้เป็น tactical market view เพื่อการศึกษา ไม่ใช่คำแนะนำการลงทุน และ OI/Volume ไม่ได้บอกทิศทางของผู้ถือสถานะอย่างแน่นอน
