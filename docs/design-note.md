# Design Note — BJT DC Bias Web App (Lab 02)

Course: ENG29 2121 Computer Programming for Electrical Engineers · 2/2569
Date: 2026-11-10 · Status: **อนุมัติแล้ว (Approved)**

## 1. Intent / เหตุผล

Web Application แรกของรายวิชา — Flask app คำนวณ DC Operating Point ของวงจรขยาย
BJT Common-Emitter แบบ **Voltage-Divider Bias** เพื่อ (1) ผ่านเกณฑ์ตรวจรับ A1–A7
และเก็บ 10 คะแนนของ Lab 02 ภายในคาบ และ (2) เป็นฐานโค้ดที่ Lab ถัดไป (W3+) ต่อยอด
เป็น Virtual Transistor Laboratory เรื่อย ๆ ทุกสัปดาห์ต้องจบด้วยระบบที่รันได้ + Tests + GitHub commit

## 2. Goals

- ฟอร์มบนเว็บรับ `VCC [V]`, `R1, R2, RC, RE [kΩ]`, `β`, `VBE [V]` → กดปุ่ม
  **Calculate DC Bias** → **Python Backend** คำนวณและ render ผลกลับมาใน HTML
- แสดงผลพร้อมหน่วย: `VB, VE, VC, VCE [V]`, `IC [mA]`, และ `IB [µA]`, `IE [mA]`
- Validation: ค่าไม่ใช่ตัวเลข / ขาด / `R ≤ 0`, `β ≤ 0`, `VCC ≤ 0` → ข้อความ Error
  อ่านได้ หน้าเว็บไม่ล้ม (HTTP 200 + error แสดงบนฟอร์ม)
- Region Warning: `VTH ≤ VBE` → คำเตือน Cutoff; `VCE < 0.3 V` → คำเตือน
  Saturation พร้อมข้อความว่าแบบจำลอง Forward-Active ใช้ไม่ได้/ไม่น่าเชื่อถือ
- Tests: ≥3 unit tests ตรวจคณิตศาสตร์วิศวกรรม (รวมชุดข้อมูลอ้างอิงใน §6) + ≥1 test
  ผ่าน Flask test client (GET / ได้ 200, POST ถูก/ผิดทำงานตามสเปก) — รันด้วย
  `py -m unittest discover -s tests -v`
- README สั่งรันได้จริง: venv → pip install → flask run → เปิด
  `http://127.0.0.1:5000/` → รัน tests (ตามเกณฑ์ A7)
- Git repo: **repo ที่นักศึกษาสร้างแล้วด้วย GitHub Desktop** — local =
  `Documents\GitHub\BJT DC Bias Web App` · remote =
  `https://github.com/gamewatcharin53-cyber/BJT-DC-Bias-Web-App.git`
  — คุณ (นักศึกษา) commit/push ผ่าน GitHub Desktop

## 3. Non-goals (Week 2 — ตัดออกให้หมด)

- AC / small-signal / gain / Bode plot / transient / signal generator
- Bias แบบอื่น (Fixed, Emitter), ngspice/SPICE solver, DC load line
- FET, interactive schematic, overlay animation, การตกแต่ง UI เกินหน้าที่
- ภาษา/UI framework อื่นนอกจาก Flask + Jinja + CSS ธรรมดา

## 4. Anti-goals (ทำแล้วถือว่าล้มเหลวแม้โปรแกรมรันได้)

- คำนวณผลใน JavaScript ฝั่ง Browser (Lab กำหนดให้ Python Backend คำนวณ)
- ฮาร์ดโค้ดค่าผลลัพธ์ไว้ใน HTML/Template
- เปิดใช้งานด้วย `file://` แทน Flask server
- Commit `.venv/`, `.env`, API keys หรือ credentials ขึ้น GitHub

## 5. Constraints

- เครื่อง: Windows + PowerShell · **Python 3.15.2 ใช้ผ่าน `py` launcher**
  (`python` ถูก Microsoft Store alias ดักอยู่ — คำสั่งทุกอย่างใช้ `py -m ...`)
- Timebox สร้าง ~75 นาที — scope ต้องเล็กที่สุด
- โครงสร้างไฟล์ตามเอกสาร Lab §04 — อยู่ที่ **root ของ repo** โดยตรง
  (clone แล้วรันได้ทันที ตามเกณฑ์ A7):
  `app.py`, `dc_bias.py`, `templates/index.html`, `static/style.css`,
  `tests/test_dc_bias.py`, `tests/test_web.py`, `requirements.txt`,
  `README.md`, `AGENTS.md`, `docs/{design-note,validation,reflection}.md`
- **ที่อยู่ repo จริง (แก้ไขแล้ว):** local =
  `C:\Users\b6828974\Documents\GitHub\BJT DC Bias Web App` · remote =
  `https://github.com/gamewatcharin53-cyber/BJT-DC-Bias-Web-App.git`
  (branch `main` · initial commit `f7db9cd` สร้างโดย GitHub Desktop พร้อม
  `.gitattributes` มาตรฐาน)
- Flask dev server เฉพาะ localhost เท่านั้น
- แบบจำลอง: Forward-Active Approximation (β คงที่, VBE คงที่)

## 6. Design

### 6.1 สถาปัตยกรรม (ทางเลือกที่เลือกไปแล้ว)

**Server-rendered**: GET `/` แสดงฟอร์ม · POST `/calculate` รับฟอร์ม → เรียก
`dc_bias.py` → render `index.html` กลับพร้อมผล (ไม่ใช้ AJAX)
ทางเลือกที่ตัดทิ้ง: JSON API + fetch (เพิ่ม JS โดยไม่มีเกณฑ์ Lab ต้องการ) และ
คำนวณใน JS (ผิดเงื่อนไข Backend) — เหตุผล: ตรงแผนภาพ §04 ของเอกสาร Lab
และเล็กที่สุด

### 6.2 การแบ่งความรับผิดชอบ

- `dc_bias.py` — ฟังก์ชันคำนวณบริสุทธิ์ **ไม่รู้จัก HTML/HTTP**: รับค่า SI
  (V, Ω, กระแสเป็น A) คืน dict ผลลัพธ์ + validation errors + region warnings
- `app.py` — parse/validate ฟอร์ม (kΩ → Ω ×1000), เรียก `dc_bias`, render template
- `templates/index.html` — ฟอร์ม + ตารางผล + error/warning blocks (Jinja)
- `static/style.css` — หน้าตาอ่านง่าย ธีมสะอาด

### 6.3 หน่วยข้อมูล (ตัดสินร่วมกันแล้ว)

ฟอร์มกรอกตัวต้านทานเป็น **kΩ** (ป้ายกำกับทุกช่อง) — ตรงกับ dataset ของ Lab
(VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V)
แปลงเป็น Ω จุดเดียวใน `app.py` ก่อนเรียก `dc_bias` · แสดงผล: V, mA, µA
ทางเลือกที่ตัดทิ้ง: กรอก Ω ล้วน (พิมพ์ผิดง่าย), suffix parser เช่น `2.2k`
(โค้ด+tests เกินจำเป็น)

### 6.4 สมการและเงื่อนไข (ตามเอกสาร Lab §06)

`VTH = VCC·R2/(R1+R2)` · `RTH = R1·R2/(R1+R2)` ·
`IB = (VTH−VBE)/(RTH+(β+1)·RE)` · `IC = β·IB` · `IE = (β+1)·IB` ·
`VE = IE·RE` · `VB = VE+VBE` · `VC = VCC−IC·RC` · `VCE = VC−VE`

Validation: ทุกช่องต้องเป็นตัวเลข และ `VCC>0, R1,R2,RC,RE>0, β>0`
(VBE ยอมรับ 0 ได้ · `VTH ≤ VBE` ไม่ error แต่แจ้ง Cutoff warning)

### 6.5 Git workflow, การทำงานร่วมกัน และเอกสาร docs

- **ผู้สร้าง:** Agent (OpenCode) สร้างโค้ด/tests/README ทั้งหมดใน session นี้
  ทันที · **นักศึกษา:** ตรวจ diff, รันเว็บ/tests เอง, พิมพ์ commit message
  และกด Publish/Commit/Push ผ่าน GitHub Desktop GUI (ตามที่ตกลงกันไว้)
  — ชื่อ repo บน GitHub: **"BJT DC Bias Web App"** (สร้างและ publish เสร็จแล้ว
  ด้วย GitHub Desktop · slug = `BJT-DC-Bias-Web-App`) ไฟล์โปรเจกต์ทั้งหมด
  วางที่ root ของ repo นี้โดยตรง
- `docs/validation.md` — agent เขียนจากผล verification จริง (เทียบ §6.6,
  ผล tests, ผลลัพธ์ใน Browser)
- `docs/reflection.md` — **มีผลต่อคะแนน** (แถว Rubric "README และ Reflection" =
  2 คะแนน) → agent สร้างเป็นแบบฟอร์มคำถาม/หัวข้อ ให้นักศึกษาเขียน
  เนื้อหาด้วยคำพูดของตนเอง
- ที่มาของค่าในเอกสารนี้: สมการ §6.4 และโครงสร้างไฟล์ §5 คัดมาจาก
  เอกสาร Lab ตรง ๆ · เกณฑ์ `VCE < 0.3 V` เป็น **การเลือกเชิงวิศวกรรมของ
  agent** (เอกสาร Lab ระบุแค่ "VCE ต่ำใกล้ saturation") อิงค่า VCE(sat)
  ทั่วไปของ BJT ≈ 0.2–0.3 V — ตรวจสอบได้ถ้าอาจารย์กำหนดตัวเลขอื่น

### 6.6 ค่าอ้างอิงตรวจรับ A3 (คำนวณอิสระจากสมการ §6.4)

| ปริมาณ | ค่า |
|---|---|
| VTH | 2.163934 V |
| RTH | 18.032787 kΩ |
| IB | 12.298581 µA |
| IC | 1.229858 mA |
| IE | 1.242157 mA |
| VE | 1.242157 V |
| VB | 1.942157 V |
| VC | 9.294312 V |
| VCE | 8.052155 V → Active region ✓ |

## 7. What's left to the builder (ผู้สร้างเลือกได้)

- รายละเอียด HTML/CSS (โทนสี, layout) ตราบใดยังอ่านง่ายและมีครบตาม Goals
- ข้อความ error/warning เป็นภาษาไทยหรืออังกฤษ (จริง ๆ ตามใจ — ผมเลือกไทย+ศัพท์อังกฤษ)
- จำนวน test cases เพิ่มเติมเหนือขั้นต่ำ A6
- รูปแบบการแสดงตัวเลข (ทศนิยม 3–4 ตำแหน่ง)
