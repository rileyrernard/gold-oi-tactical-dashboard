# ติดตั้ง skill

ใช้ Python 3.11 ขึ้นไป มี shell และเข้าถึงโฟลเดอร์โปรเจกต์ได้ ตรวจว่าเรียก interpreter ตัวไหนก่อนติดตั้ง

## Python

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -X utf8 -m pip install -r skills/gold-oi-tactical-dashboard/requirements.txt
.\.venv\Scripts\python.exe -X utf8 -m pip check
```

macOS/Linux:

```sh
python3 -m venv .venv
.venv/bin/python -X utf8 -m pip install -r skills/gold-oi-tactical-dashboard/requirements.txt
.venv/bin/python -X utf8 -m pip check
```

ไม่จำเป็นต้อง activate venv ให้ใช้ path ของ interpreter โดยตรง ไม่ต้องปิด TLS หรือเปลี่ยน ExecutionPolicy

## ติดตั้งในโปรเจกต์

จากโฟลเดอร์ repository รันหนึ่งคำสั่งตามแอป Windows ใช้ `.venv\Scripts\python.exe` แทน `python` ในตัวอย่าง ส่วน macOS/Linux ใช้ `.venv/bin/python`

```sh
python -X utf8 tools/install_skill.py --agent codex --project /path/to/my-project
python -X utf8 tools/install_skill.py --agent claude --project /path/to/my-project
python -X utf8 tools/install_skill.py --agent antigravity --project /path/to/my-project
```

| แอป | โฟลเดอร์ที่ได้ | วิธีเรียก |
| --- | --- | --- |
| Codex | `.agents/skills/gold-oi-tactical-dashboard` | `$gold-oi-tactical-dashboard` |
| Claude Code | `.claude/skills/gold-oi-tactical-dashboard` | `/gold-oi-tactical-dashboard` |
| Google Antigravity | `.agents/skills/gold-oi-tactical-dashboard` | ขอให้ใช้ skill `gold-oi-tactical-dashboard` |

เปิดโปรเจกต์ปลายทางในแอป ตรวจว่าเห็น skill หากยังไม่เห็นให้เริ่ม session ใหม่ ไม่ต้องติดตั้งซ้ำทั้งระดับ user และ project

ตัวติดตั้งคัดลอกทั้งโฟลเดอร์ ตรวจ hash และหยุดถ้ามีปลายทางชื่อเดียวกันอยู่แล้ว ถ้าเหมือนกันทุกไฟล์จะบอกว่า installed already โดยไม่เขียน การอัปเดตให้สำรองเวอร์ชันเดิมแล้วจัดการปลายทางเอง ไม่มี `--force` ลบทับ

โหมดระดับผู้ใช้: เปลี่ยน `--project ...` เป็น `--user` ใช้ `~/.agents/skills` สำหรับ Codex, `~/.claude/skills` สำหรับ Claude Code และ `~/.gemini/config/skills` สำหรับ Antigravity App/IDE ส่วน Antigravity CLI ใช้ project scope ตามตัวอย่างข้างต้น

## ความพร้อมแยกสามส่วน

1. **Skill:** แอปค้นพบคำสั่งและอ่าน supporting files ได้
2. **Python:** import Plotly, `pip check` และ renderer smoke test ผ่าน
3. **Integration:** อ่าน Chrome ที่ผู้ใช้ล็อกอินได้จริงและเขียน Sheet ที่ระบุได้จริงเมื่ออนุญาต

ข้อ 1–2 ผ่านยังไม่แปลว่าข้อ 3 พร้อม ไม่แจก cookies, token, service-account key หรือบัญชีผู้สอน และไม่เปิด remote debugging ให้ทุกคนในเครือข่าย

Claude ในเว็บ/มือถือกับ Claude Code เป็นคนละสภาพแวดล้อม การอัปโหลด skill เข้าเว็บไม่ทำให้เข้าถึง Chrome หรือไฟล์เครื่องได้เอง ดูความสามารถและข้อจำกัดของบัญชีตามเอกสารผู้ให้บริการ

ติดตั้งเสร็จไป [QUICKSTART](QUICKSTART.md) และ [PROMPTS](PROMPTS.md) แหล่งอ้างอิง path ที่ตรวจวันที่ 23 ต.ค. 2026 อยู่ใน [SOURCES](SOURCES.md)
