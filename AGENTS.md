# AGENTS.md — แนวทางสำหรับ AI Agent ที่ทำงานใน repo นี้

โปรเจกต์: Flask Web App คำนวณ BJT DC Bias 3 โหมด (Lab 02–03, ENG29 2121)

## สภาพแวดล้อมเครื่องนี้

- Windows + PowerShell
- **ใช้ `py` launcher** เสมอ (`python` ถูก Microsoft Store alias ดักอยู่)
- รัน tests: `py -m unittest discover -s tests -v` จาก root ของ repo
  (หรือ `.venv\Scripts\python.exe -m unittest ...` ถ้าไม่ activate venv)
- venv อยู่ที่ `.venv/` — **ห้าม commit** (มี .gitignore ครอบแล้ว)

## สถาปัตยกรรม (รักษาไว้เสมอ)

- `dc_bias.py` = engineering module บริสุทธิ์ — **ห้าม import Flask/Jinja
  หรือรู้จัก HTML/HTTP** ใด ๆ
- `app.py` = Flask routes + การแปลงหน่วย (ฟอร์ม kΩ → Ω ก่อนเรียก dc_bias)
- `templates/index.html` = แสดงผลอย่างเดียว — ไม่มีสมการหรือตัวเลขผลลัพธ์
  ฝังอยู่ใน HTML
- ผลลัพธ์ทุกตัวต้องมาจากการคำนวณของ Python Backend — **ห้ามฮาร์ดโค้ด**
- `app.py` เป็นที่เลือกโหมด (`divider`/`fixed`/`emitter`), ตรวจเฉพาะฟิลด์
  ของโหมด และแปลงหน่วย kΩ→Ω; `dc_bias.py` มี 3 ฟังก์ชันแยกตามวงจร
- **ห้าม**ย้ายเงื่อนไขโหมดหรือ HTML ลงใน `dc_bias.py`

## แนวทางการแก้ไขโค้ด

- **TDD**: เขียน test ก่อน ดูมัน fail แล้วค่อยแก้ implementation
  — ยกเว้น Lab 03 ที่ใบงานห้ามเพิ่ม unittest/Playwright script:
  ใช้ tests เดิมเป็น regression guard + ตรวจรับผ่าน browser
  แล้วบันทึกผลใน `docs/validation.md`
- เมื่อแก้สมการใน `dc_bias.py` — ไม่ต้องแก้ HTML (ผลเชื่อมผ่าน Jinja)
- ข้อความ UI เป็นภาษาไทย + ศัพท์เทคนิคอังกฤษ (VB, VE, IC ฯลฯ)
- ค่าอ้างอิงตรวจรับ (VCC=12, R1=100k, R2=22k, RC=2.2k, RE=1k, β=100,
  VBE=0.7 → VCE=8.052 V, IC=1.230 mA) อยู่ใน `tests/test_dc_bias.py`
  — แก้แบบจำลองแล้วต้องอัปเดตค่าอ้างอิงด้วยการคำนวณอิสระ

## Git workflow

- นักศึกษาเป็นผู้ commit ผ่าน **GitHub Desktop** (agent เตรียม stage
  ไฟล์ + ตรวจสอบผลลัพธ์แทน)
- ห้าม commit `.venv/`, `__pycache__/`, `.env`, API keys
