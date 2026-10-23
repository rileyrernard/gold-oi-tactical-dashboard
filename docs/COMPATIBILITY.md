# Compatibility and verification

ตรวจเอกสารเส้นทางติดตั้งวันที่ 2026-10-23 การรองรับ skill format ไม่เท่ากับ live workflow พร้อมในทุกบัญชี

| ส่วน | หลักฐาน/สถานะ |
| --- | --- |
| Python 3.11+ + Plotly 5.24.1 | source ใช้ standard library และ Plotly ตรึงรุ่น การตรวจ release บันทึกใน GitHub Actions และ TESTING |
| Codex Windows live workflow | เคยทดสอบบนเครื่องผู้จัดทำพร้อม browser/Sheets tools ของเครื่องนั้น ไม่ใช่การรับประกันเครื่องผู้รับ |
| Claude Code CSV workflow | เตรียม installation path และ prompt ตามเอกสาร ไม่ได้รันใน Claude Code จริง |
| Antigravity CSV workflow | เตรียม installation path และ prompt ตามเอกสาร ไม่ได้รันใน Antigravity จริง |
| macOS/Linux | คำสั่งและ path รองรับโดยออกแบบ ต้องดูผล CI และทดลองเครื่องจริงก่อนอ้าง live readiness |
| Chrome/Sheets | optional ขึ้นกับ integration ไม่รวมมาตรการเปิด/เข้าถึง browser แบบข้ามสิทธิ์ |

รายงาน HTML เป็น snapshot ที่มีเวลาข้อมูล ไม่ใช่ตลาดสดและไม่ใช่ผล backtest การผ่าน numeric/UI QA ไม่ได้พิสูจน์กลยุทธ์ทำกำไร
