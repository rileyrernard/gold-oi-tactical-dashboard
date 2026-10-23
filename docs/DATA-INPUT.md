# ข้อมูลเข้าและที่มา

skill อ่าน **options OI** ของ contract/expiry เดียว ไม่รับ CSV futures OI มาใส่คอลัมน์ Call/Put แทนกัน ใช้ source ที่ผู้ใช้เข้าถึงและมีสิทธิ์ใช้งาน ไม่มี downloader หรือบัญชี CME แถมมากับ repository

แต่ละ CSV ต้องมีวันที่ ISO, contract, expiry, strike, ค่า Call/Put และ header ครบ จำนวนสัญญาเป็นจำนวนเต็ม finite ไม่ติดลบ ยกเว้น ΔOI ที่ติดลบได้ ห้ามเติมช่องหายเป็นศูนย์เอง ถ้า source ยืนยันว่า blank คือศูนย์จึง normalize และเก็บหลักฐานการแปลง

เก็บ historical OI ได้เมื่อมีจริง เพื่อเทียบ `OI_latest - OI_previous == OI_change` ด้วยวันที่ฐานจาก source อย่าคิดว่า OI change วันแรกใน matrix เป็น daily change ถ้าเป็น initial baseline

`source_context.json` เป็นบันทึกที่ agent ต้องอ่าน ประกอบด้วย:

| Field | ความหมาย |
| --- | --- |
| source_site / source_url | ชื่อและหน้าข้อมูลที่อ่าน ไม่ใส่ token/cookies |
| extracted_at | ISO timestamp พร้อม timezone |
| contract / expiry | ตาม header แหล่งข้อมูล |
| underlying_symbol | futures เดือนจริง เช่น symbol ที่ source ระบุ ไม่เดา |
| as_of_date / oi_change_comparison_date | วันข้อมูลและวันฐานที่ source แสดง |
| source_totals | ยอด Call/Put ที่ใช้ตรวจอิสระ หากไม่มีให้ระบุ null พร้อมข้อจำกัด |
| normalization_notes | blank, baseline, missing rows หรือการแก้ไขที่ทำ |
| price_basis_notes | กราฟ broker/continuous contract ตรงกับ futures เดือนหรือไม่ |

source context ไม่ใช่หลักฐานว่าตัวเลขถูกเพียงเพราะกรอกครบ Agent ต้องตรวจกลับกับไฟล์/แหล่งจริง หากวันเปรียบเทียบไม่ทราบ ให้เก็บ null และไม่เดาวัน

Volume และ OI อาจมีการแก้ไข, roll, expiry, exercise หรือ adjustment จึงไม่ใช้ `abs(ΔOI) <= Volume` เป็น invariant สากล หากพบให้ตรวจ source definitions และระบุสาเหตุไม่ทราบเมื่อไม่มีหลักฐาน ถ้าผลต่าง OI ที่เทียบวันตรงกันไม่เท่ากับ ΔOI ต้องหยุดก่อนวิเคราะห์/เขียน Sheet

เก็บข้อมูลของตนใน `runs/` ซึ่ง Git ignore แล้ว อย่า commit raw market data หรือ credential ลง repository สาธารณะโดยไม่มีสิทธิ์
