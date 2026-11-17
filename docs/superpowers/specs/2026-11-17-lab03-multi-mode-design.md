# Lab 03 — Multi-Mode BJT Bias Design

สถานะ: อนุมัติแล้ว (17 พ.ย. 2026) · แผน: `docs/superpowers/plans/2026-11-17-lab03-multi-mode.md`
อ้างอิง: ใบงาน `ENG29_2121_Lab03_BJT_Bias_Web_App.html` + โค้ด Lab 02 (HEAD `45b7824`)

## 1. Intent และเหตุผล

ต่อยอดเว็บ Flask จาก Lab 02 (Voltage Divider Bias อย่างเดียว) ให้เลือกวงจร
ไบอัสได้ **สามโหมดในหน้าเดียว** — Voltage Divider (เดิม), Fixed Bias และ
Emitter Bias แบบแหล่งจ่ายเดียว — ตามใบงาน Lab 03 โดยไม่ทำเว็บใหม่ ไม่เพิ่ม
dependency และไม่กระทบผล/การ์ดวงจรของ Divider เดิม

เหตุผล: ใบงานต้องการให้เว็บเดิมรองรับหลายวงจร แยกสมการไว้ใน Python เลือก
ฟังก์ชันตามโหมด ตรวจเฉพาะช่องที่โหมดใช้ และตรวจรับผ่าน browser ด้วยตาราง
A1–A5 ของนักศึกษา

## 2. Goals

- Divider เดิม: ผลลัพธ์ทุกค่าต้องเหมือน Lab 02 เมื่อกรอกค่าเดิม (A1) และ
  การ์ด SVG ยังแสดงเฉพาะโหมด Divider
- เพิ่ม **Fixed Bias**: ใช้ `RB` ต่อ VCC→Base, Emitter ลงกราวด์ตรง ๆ
  (`VE = 0`)
- เพิ่ม **Emitter Bias (single supply)**: ใช้ `RB` และ `RE`
- ฟอร์มเลือกโหมดแล้วโหลดหน้าใหม่ แสดงเฉพาะช่องที่โหมดนั้นใช้
  (server-rendered, ไม่เพิ่ม JavaScript)
- Validation เฉพาะช่องของโหมด; ช่องที่ไม่ใช้ต้องไม่ถูกบังคับ
- โหมดที่ไม่รู้จักต้องแจ้ง error — ไม่เดาเป็น Divider
- ผลลัพธ์ใช้ dict กลาง/หน่วยเดิมของ Lab 02: `v_b`, `v_e`, `v_c`, `v_ce`,
  `ic`, `ib`, `ie` (Divider เพิ่ม `v_th`, `r_th`)
- Warning ตามเกณฑ์ใบงาน: `IB ≤ 0` หรือ `VCE ≤ 0.2 V` → เตือนว่าแบบจำลอง
  Forward-Active อาจใช้ไม่ได้ (ไม่ต้องแก้ไปหา Cutoff/Saturation ที่ถูกต้อง)
- คง tests เดิม **25 ตัว** ให้ผ่าน; ไม่เพิ่ม unittest/Playwright script
  ตามใบงาน
- อัปเดต README + `docs/validation.md` (ตาราง A1–A5, ค่าอ้างอิงอิสระ,
  วิธีตรวจจริง)

## 3. Non-goals

- ไม่ทำ DC Load Line, AC/Transient, ตัวเก็บประจุ Bypass หรือ SPICE
- ไม่เพิ่ม dependency ใหม่ (requirements.txt เท่าเดิม)
- ไม่ทำเว็บใหม่/SPA/JavaScript framework
- ไม่เพิ่ม unittest ใหม่ หรือสคริปต์ Playwright (ใบงานระบุ)
- ไม่คำนวณ Q-Point ที่ถูกต้องใน Cutoff/Saturation — แค่เตือน
- ไม่เปลี่ยนสมการหรือผลของ Divider เดิม
- ไม่แตะการ์ด SVG ของ Divider (ยกเว้นเงื่อนไขการแสดงผล)

## 4. Anti-goals (ถ้าเกิดถือว่างานล้มเหลว)

- ผล Divider เปลี่ยน หรือการ์ดวงจร Divider หาย
- โหมดใหม่ใช้สมการผิด หรือลืมแปลง kΩ→Ω
- ฟอร์มโหมดใหม่บังคับช่องที่ไม่ใช้ (เช่น Fixed บังคับ `RE`)
- ผลรอบก่อนค้างแสดงเป็นผลของรอบที่กรอกผิด
- `mode` ที่ไม่รู้จักถูกตีเป็น Divider เงียบ ๆ
- แสดง `nan`/`inf` จาก overflow (ต้องคงการป้องกันของ Lab 02)
- tests เดิม 25 ตัวแตก

## 5. Constraints

- Flask + Jinja2 + unittest ที่มีอยู่; Python ใน `.venv`; Windows/PowerShell
- `AGENTS.md`: `dc_bias.py` เป็น engineering module บริสุทธิ์ (ไม่รู้จัก
  HTML/HTTP), `app.py` เป็นที่แปลงหน่วยและ dispatch, templates แสดงผลอย่างเดียว
  ห้ามฮาร์ดโค้ดตัวเลขผลลัพธ์
- หน่วยฟอร์ม: ตัวต้านทานเป็น **kΩ**, VCC/VBE เป็น V, β ไม่มีหน่วย
- นักศึกษา commit ผ่าน GitHub Desktop เท่านั้น
- เกณฑ์ตรวจรับใช้ร่วมกัน: `VCC=12 V`, `RC=2.2 kΩ`, `β=100`, `VBE=0.70 V`
  — tolerance `IC ±0.01 mA`, `VCE ±0.02 V` เทียบค่าอ้างอิงที่ยังไม่ปัดเศษ
- ใบงานห้ามเพิ่ม unittest/Playwright script — เป็นข้อยกเว้นที่ได้รับอนุญาต
  จาก TDD ใน `AGENTS.md`; การตรวจรับใช้ browser + tests เดิม

## 6. Approaches

1. **ขยายของเดิม (เลือก)** — เพิ่ม `solve_fixed_bias()` และ
   `solve_emitter_bias()` แยกกันใน `dc_bias.py`, คง `solve_dc_bias()` เดิม;
   `app.py` เก็บ field list ตามโหมดและ dispatch ด้วย `if/elif`; ฟอร์มเลือก
   โหมดเป็น GET reload (server-rendered); การ์ด SVG แสดงเฉพาะ Divider
   — ตรงโครงเดิม ตรงใบงาน และความเสี่ยงต่ำสุด
2. รวมทุกโหมดในฟังก์ชันเดียว (`solve_dc_bias(mode=...)`) — ใบงานระบุให้แยก
   ฟังก์ชัน Fixed/Emitter และจะทำให้ validation/warning ปนกัน · ไม่เลือก
3. ทำฟอร์ม dynamic ด้วย JavaScript หรือหน้าใหม่ — ใบงานบอกไม่จำเป็นต้องเพิ่ม
   JS และเสี่ยงทำ Lab 02 เสีย · ไม่เลือก

## 7. Design (the how)

### 7.1 ค่า `mode`

- ค่าที่รองรับ: `divider` (ค่าเริ่มต้น), `fixed`, `emitter`
- `GET /` ใช้ `?mode=...`; ไม่มีค่า → `divider`
- `POST /calculate` อ่าน `mode` จากฟอร์ม
  - ไม่มี/ว่าง → `divider` เพื่อความเข้ากันได้กับฟอร์ม Lab 02 และ tests เดิม
  - ค่าที่ไม่รู้จัก (ไม่ว่าง) → error `ไม่รู้จักโหมดวงจร: <mode>` และไม่แสดงผล
- `GET /?mode=<ไม่รู้จัก>` → หน้า error แบบเดียวกัน (ไม่เดาเป็น Divider)

### 7.2 ฟิลด์ต่อโหมด

| โหมด | ฟิลด์ |
|---|---|
| `divider` | `vcc`, `r1`, `r2`, `rc`, `re`, `beta`, `vbe` (เหมือน Lab 02) |
| `fixed` | `vcc`, `rb`, `rc`, `beta`, `vbe` |
| `emitter` | `vcc`, `rb`, `rc`, `re`, `beta`, `vbe` |

- เพิ่ม metadata ของ `rb`: label `RB (Base Bias)`, unit `kΩ`, placeholder `1000`
- `FIELDS` เดิมของ Divider คงลำดับเดิมเพื่อไม่ให้ UI/tests เปลี่ยน
- `parse_form(form, mode)` ตรวจเฉพาะ field ของโหมดนั้น:
  - ว่าง/ไม่ใช่ตัวเลข/non-finite → `<NAME> ต้องกรอกเป็นตัวเลข`
  - แปลง kΩ→Ω **ก่อน** ตรวจ `math.isfinite` (คง fix overflow ของ Lab 02)
  - ค่า ≤ 0 ของ VCC/RB/RC/RE/β ถูกตรวจใน `dc_bias` → `<NAME> ต้องมากกว่า 0`
  - `VBE` ไม่บังคับเป็นบวก (พฤติกรรมเดิม)

### 7.3 `dc_bias.py`

คง `solve_dc_bias(vcc, r1, r2, rc, re, beta, vbe)` **ไม่แก้**

เพิ่ม:

```python
def solve_fixed_bias(vcc, rb, rc, beta, vbe):
    # validate vcc, rb, rc, beta > 0
    ib = (vcc - vbe) / rb
    ic = beta * ib
    ie = (beta + 1) * ib
    ve = 0.0
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve
    # results: v_b, v_e, v_c, v_ce, ic, ib, ie (ไม่มี v_th/r_th)

def solve_emitter_bias(vcc, rb, rc, re, beta, vbe):
    # validate vcc, rb, rc, re, beta > 0
    ib = (vcc - vbe) / (rb + (beta + 1) * re)
    ic = beta * ib
    ie = (beta + 1) * ib
    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve
```

ข้อความ warning ของโหมดใหม่:
- `IB ≤ 0` → `คำเตือน Cutoff: IB ≤ 0 A ไบอาสอยู่นอก Forward-Active region ผลลัพธ์จากแบบจำลองนี้ใช้อ้างอิงไม่ได้`
- `VCE ≤ 0.2 V` → `คำเตือน Saturation: VCE ≤ 0.2 V ไบอาสเข้าใกล้ Saturation ผลจากแบบจำลอง Forward-Active ใช้อ้างอิงไม่ได้`

**Divider คง warning เดิมทุกข้อความ** (`VTH ≤ VBE` → Cutoff,
`VCE < 0.3 V` → Saturation) เพื่อรักษาพฤติกรรม Lab 02 และ tests เดิม —
ไม่รวมเกณฑ์ 0.2 V เข้ากับ Divider

### 7.4 `app.py`

- เพิ่ม `MODE_LABELS`:
  - `divider` → `Voltage Divider Bias`
  - `fixed` → `Fixed Bias`
  - `emitter` → `Emitter Bias (single supply)`
- เพิ่ม `MODE_FIELDS` (รายชื่อ field ตาม §7.2)
- `fields_for(mode)` คืน list `(name, label, unit, placeholder)` ตามลำดับ
- `parse_form(form, mode)` ตาม §7.2
- `calculate()`:
  1. อ่าน `mode` (default `divider`)
  2. ถ้าไม่รู้จัก → render error (ไม่มี fields/results/circuit)
  3. `parse_form` → ถ้า error ให้ render ฟอร์มเดิมของโหมดนั้น + error (ไม่มีผล)
  4. dispatch:
     - `divider` → `solve_dc_bias(**values)`
     - `fixed` → `solve_fixed_bias(**values)`
     - `emitter` → `solve_emitter_bias(**values)`
  5. `build_rows(results, mode)` — ค่า common ทุกโหมด; Divider เพิ่ม VTH/RTH
- `index()`: อ่าน `mode` จาก query (default `divider`); ตรวจ unknown แบบเดียวกัน;
  ส่ง `fields`, `form`, `mode`, `mode_label`, `circuit` (เฉพาะ divider), errors/warnings/rows
- `build_circuit_labels()` คงเดิม เรียกเฉพาะ `mode == "divider"`

### 7.5 Templates / CSS

`templates/index.html`:
- subtitle อธิบาย 3 โหมด
- **ฟอร์มเลือกโหมดแยก** (GET `/`) เหนือฟอร์มหลัก:
  `<select id="mode" name="mode">` + ปุ่ม `เปลี่ยนโหมด`; selected ตาม `mode`
  (ถ้า `mode` เป็น None ไม่มี selected)
- ฟอร์มหลัก (POST `/calculate`): hidden `mode`; loop `fields`; ปุ่ม Calculate
- แสดงฟอร์มหลักเฉพาะเมื่อ `mode` valid
- errors/warnings ยังเป็นบล็อกเดิม แต่หัวข้อระบุโหมด:
  `พบข้อผิดพลาด ({{ mode_label }}):` และ `คำเตือน — {{ mode_label }}:`
  (รายการข้อความข้างในไม่เปลี่ยน; ผลลัพธ์ก็มี `mode_label` ในหัวตาราง)
- `{% if circuit %}{% include 'circuit.html' %}{% endif %}` — Divider เท่านั้น
- หัวตารางผล: `DC Bias Results (Q-Point) — {{ mode_label }}`
- ไม่มี JavaScript ใหม่

`static/style.css`: เพิ่มสไตล์ขั้นต่ำสำหรับแถบเลือกโหมด (เช่น `.mode-card`,
`.mode-row`) โดยไม่กระทบสไตล์เดิม

### 7.6 เอกสาร

- `README.md`: อัปเดตเป็น Lab 03 (3 โหมด), สมการทั้งสาม, วิธีเลือกโหมด,
  โครงสร้างไฟล์, วิธีรัน, จำนวน tests (คง 25), ตารางค่าอ้างอิง 3 โหมด,
  หมายเหตุการตรวจรับผ่าน browser และเพิ่มหัวข้อ **Lab 03 Submission**:
  repo URL, ช่อง Commit SHA (เติมหลัง commit สุดท้าย), สรุปว่า AI ช่วยส่วนไหน
  และนักศึกษาตรวจอะไร — ส่วนที่เป็นคำรับรองของนักศึกษาให้เว้นเป็น template
  ให้นักศึกษาเติม/ยืนยันเอง
- `docs/validation.md`: เพิ่มส่วน Lab 03
  - **เปลี่ยนชื่อส่วนเดิมเป็น `Lab 02 · เกณฑ์ A1–A7`** เพื่อไม่ให้ชนกับ
    `Lab 03 · กรณีตรวจ A1–A5` (คนละ rubric) และใส่หมายเหตุสั้น ๆ
  - ตาราง A1–A5: อินพุต, ค่าคาดหมาย (ไม่ปัด), ผลที่เห็นจริง, วิธีตรวจ, สถานะ
  - ค่าอ้างอิงอิสระ + สมการ/หน่วย (อย่างน้อยโหมดใหม่ 1 กรณี)
  - ระบุวิธีจริง: **OpenCode Browser**; Playwright MCP = `NOT RUN`
    เพราะเครื่องนี้ไม่มี `node`/`npx` (ตรวจ `node --version`/`npx --version`
    แล้วไม่พบ) — ไม่ได้เพิ่ม `opencode.json` ในงานนี้
- `docs/reflection.md`: ปรับชุดคำถามให้เป็น Lab 03 (multi-mode) แต่ **ไม่เติม
  คำตอบ** — นักศึกษาเขียนคำตอบเอง
- `AGENTS.md`: ปรับชื่อโครงการเป็น Lab 02–03 และเพิ่มหมายเหตุโหมด
  (ไม่เปลี่ยนกฎสถาปัตยกรรม)

### 7.7 ค่าอ้างอิงอิสระ (ยังไม่ปัดเศษ)

ใช้ `VCC=12 V`, `RC=2.2 kΩ`, `β=100`, `VBE=0.70 V`

| กรณี | อินพุต | IB | IC | VCE |
|---|---|---|---|---|
| A1 Divider | R1=100 kΩ, R2=22 kΩ, RE=1 kΩ | 12.298581 µA | 1.229858 mA | 8.052155 V |
| A2 Fixed | RB=1 MΩ | 11.300000 µA | 1.130000 mA | 9.514000 V |
| A3 Emitter | RB=1 MΩ, RE=1 kΩ | 10.263397 µA | 1.026340 mA | 8.705450 V |
| A4 Emitter | RB=1 MΩ, RE=2 kΩ | 9.401000 µA | 0.940100 mA | 8.032779 V |

- A4 คาดการณ์: IC **ลดลง** จาก A3 เพราะ `RE` ใหญ่ขึ้น → ตัวหาร
  `RB + (β+1)RE` ใหญ่ขึ้น; VCE ลดลงเล็กน้อย
- A5 Fixed `RB=0` → error `RB ต้องมากกว่า 0`, ไม่แสดงผล/ตาราง
- A2/A3/A4 ไม่มี warning (IB > 0, VCE > 0.2 V)

### 7.8 แผนตรวจรับผ่าน browser

1. รัน Flask (`flask --app app run --port 5000`)
2. ใช้ **OpenCode Browser**: navigate + snapshot + fill + click + snapshot
3. ตรวจ A1–A5 ตามตาราง §7.7; บันทึกค่าที่เห็นจริง/หน่วย/สถานะ
4. เก็บหลักฐานอย่างน้อย 1 กรณี (ข้อความผลจากหน้าเว็บหรือ screenshot)
5. รัน tests เดิม: `Ran 25 tests — OK`

## 8. Testing / TDD exception

ใบงานระบุชัดว่าไม่ต้องเขียน unittest ใหม่ และให้ตรวจผ่าน Browser ด้วยตาราง
A1–A5 — ดังนั้นงานนี้ **ไม่เพิ่ม test ใหม่** และคง tests เดิม 25 ตัวเป็น
regression guard ของ Divider/ฟอร์มเดิม การทวนสอบโหมดใหม่ทำผ่าน browser
ตาม §7.8; ระหว่างพัฒนาใช้ Python/Flask test client เฉพาะเพื่อ sanity check
ชั่วคราวได้ แต่ไม่ commit test ใหม่

## 9. สิ่งที่เหลือให้ builder ตัดสิน

- ถ้อยคำ/รูปแบบ HTML ของแถบเลือกโหมด (ใช้สไตล์ `.card` เดิมได้)
- ตำแหน่งแสดง `mode_label` ในหน้าผล (หัวตารางตาม §7.5)
- การจัดลำดับ field ในฟอร์มตาม §7.2
- รายละเอียด CSS ของ `.mode-card`/`.mode-row`
- ถ้า `RB` ว่างในโหมด Fixed/Emitter → ข้อความ `RB ต้องกรอกเป็นตัวเลข`
  (ตาม pattern เดิม)

## 10. Builder-check resolutions (17 พ.ย. 2026)

คำถามที่ reviewer ถาม 5 ข้อ — ข้อ 2 ตรวจเครื่องแล้วตัดสินได้ ที่เหลือเป็น
call ของผม (แก้ในเอกสารแล้ว):

1. **เอกสารที่ใบงานให้คะแนน (README URL/SHA/AI-assisted + สิ่งที่นักศึกษา
   ตรวจ)** → เพิ่มหัวข้อ `Lab 03 Submission` ใน README; URL ใส่ได้เลย,
   SHA เป็นช่องว่างให้เติมหลัง commit สุดท้าย; ส่วน "AI ช่วยอะไร/นักศึกษา
   ตรวจอะไร" เป็น template ให้นักศึกษาเติม (agent ไม่เขียนคำรับรองแทน)
2. **Playwright MCP** → เครื่องนี้ไม่มี `node`/`npx` จึงรัน Playwright MCP
   ไม่ได้จริง; ใช้ **OpenCode Browser** และบันทึก Playwright MCP = `NOT RUN`
   พร้อมเหตุผลตามใบงาน — ไม่สร้าง `opencode.json` ในงานนี้
3. **ให้ error/warning ระบุโหมด** → เพิ่ม `mode_label` ในหัวข้อ error และ
   warning (ไม่เปลี่ยนข้อความรายการ) ตาม §7.5
4. **`docs/reflection.md`** → ปรับชุดคำถามเป็น Lab 03 แต่ไม่เติมคำตอบ
5. **A1–A5 ชนกับ A1–A7 เดิม** → เปลี่ยนชื่อส่วน Lab 02 เป็น
   `Lab 02 · เกณฑ์ A1–A7` และเรียกส่วนใหม่ว่า `Lab 03 · กรณีตรวจ A1–A5`
   พร้อมหมายเหตุว่าเป็นคนละ rubric
