# Circuit Diagram Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** เพิ่มการ์ด "Circuit: Common-Emitter Amplifier" (SVG สไตล์รูปในเอกสาร Lab) ลงหน้าเว็บ โดยกำกับค่า input บนตัววงจรและแรงดันโหนด VB/VE/VC เมื่อคำนวณสำเร็จ

**Architecture:** `app.py` สร้าง label ทั้งหมดเป็น context `circuit` (ตามกฎ AGENTS.md — template แสดงผลอย่างเดียว) → `templates/circuit.html` (ไฟล์ใหม่) render SVG ด้วย Jinja conditional → include ไว้ใน index.html ระหว่างกล่อง warnings กับตารางผล หน้าเว็บคงเลย์เอาต์แถวเดียว

**Tech Stack:** Flask + Jinja2 + unittest (มีอยู่แล้ว — ไม่เพิ่ม dependency)

**Spec:** `docs/superpowers/specs/2026-11-10-circuit-diagram-design.md` (อนุมัติแล้ว ฉบับ v2)

## Global Constraints

- ไม่เพิ่ม dependency ใหม่ (requirements.txt เหมือนเดิม)
- ค่าตัวเลขทุกตัวบนรูปสร้างใน `app.py` — `templates/` ห้ามมีตัวเลขผลลัพธ์ฝังตายตัว
- รัน tests จาก root ของ repo (PowerShell): `& .venv\Scripts\python.exe -m unittest discover -s tests -v` (ใช้ `python` ตรง ๆ โดน MS Store alias ดัก)
- นักศึกษา commit ผ่าน GitHub Desktop — agent เตรียม `git add` + ข้อความ commit แล้วรอ
- ลำดับหน้าคงเดิม: ฟอร์ม → errors → warnings → **วงจร (ใหม่)** → ตารางผล
- สไตล์ SVG ตาม design doc: R หยักซิกแซก, เส้นดำ `#1b2733` บนการ์ดขาว, ground symbol แยก 2 จุด (ใต้ R2, ใต้ RE — ไม่มีรางล่าง), label R1/R2 ซ้าย · RC/RE ขวา, ไอคอนหยักสีเขียวหน้าหัวการ์ด
- เรขาคณิต SVG ที่ตรวจแล้ว (XML valid + ตรวจใน browser แล้ว) อยู่ที่ spike: `C:\Users\b6828974\AppData\Local\Temp\opencode\bjt-circuit-spike\templates\circuit.html` — ใช้เป็นต้นฉบับได้ แต่ต้องเขียนใหม่ใน repo (spike เป็นของชั่วคราว)

## Review Focus

สถานะ input ที่แผนไม่ได้ทำ test แยก (ผูกกับ Task 1 ทั้งหมด):

- ค่าไม่ใช่ตัวเลข (`"abc"`) → ห้าม echo ขึ้นวงจร (แสดงแค่ชื่อฟิลด์) → `test_post_invalid_input_not_echoed_on_circuit`
- ค่า non-finite (`"inf"`/`"nan"`) → ห้าม echo → ทดสอบใน test เดียวกัน
- ตัวเลขที่ไม่ผ่าน validation (R ติดลบ `"-1"` → error "ต้องมากกว่า 0") → ห้าม echo ค่าติดลบขึ้นวงจร → ทดสอบใน test เดียวกัน (spike เดิมมี defect จุดนี้ — แก้ด้วย flag `positive`)
- ฟอร์มครึ่ง valid ครึ่ง invalid → ฟิลด์ valid ยังแสดงค่าบนวงจร → ทดสอบใน test เดียวกัน
- Cutoff/Saturation → ค่า input + VB/VE/VC ยังแสดงครบ (วงจรไม่หายเมื่อมี warning) → `test_post_cutoff_shows_input_values`

---

### Task 1: การ์ดวงจร — label builder + template + CSS + tests

**Files:**
- Modify: `app.py` (เพิ่ม 2 ฟังก์ชัน + เดิน context ใน 2 routes)
- Create: `templates/circuit.html`
- Modify: `templates/index.html` (เพิ่ม `{% include 'circuit.html' %}`)
- Modify: `static/style.css` (สไตล์ `.circuit-card`)
- Test: `tests/test_web.py` (+4 tests → suite 23)

**Interfaces:**
- Consumes: `solve_dc_bias(**values)` → `out["results"]` dict มีคีย์ `v_b`, `v_e`, `v_c` (มีอยู่แล้ว) · `FIELDS`, `math.isfinite` (import แล้ว)
- Produces: `build_circuit_labels(form: dict[str, str], results: dict | None) -> dict[str, str | None]` คีย์ `vcc, r1, r2, rc, re, npn, vbe_note, v_b, v_e, v_c` — template เรียกผ่าน context `circuit`

- [ ] **Step 1: เขียน 4 failing tests ใน `tests/test_web.py`** (ต่อท้าย class `TestWeb`)

```python
    def test_get_index_shows_circuit(self):
        rv = self.client.get("/")
        self.assertEqual(rv.status_code, 200)
        html = rv.get_data(as_text=True)
        self.assertIn("Circuit: Common-Emitter Amplifier", html)
        self.assertIn("<svg", html)
        self.assertNotIn("VB =", html)
        self.assertNotIn("100 kΩ", html)

    def test_post_valid_circuit_labels(self):
        rv = self.client.post("/calculate", data=VALID)
        self.assertEqual(rv.status_code, 200)
        html = rv.get_data(as_text=True)
        self.assertIn("VCC = 12 V", html)
        self.assertIn("100 kΩ", html)
        self.assertIn("22 kΩ", html)
        self.assertIn("2.2 kΩ", html)
        self.assertIn("1 kΩ", html)
        self.assertIn("NPN (β = 100)", html)
        self.assertIn("VBE = 0.70 V", html)
        self.assertIn("VB = 1.942 V", html)
        self.assertIn("VE = 1.242 V", html)
        self.assertIn("VC = 9.294 V", html)

    def test_post_invalid_input_not_echoed_on_circuit(self):
        rv = self.client.post("/calculate", data={**VALID, "r1": "abc"})
        html = rv.get_data(as_text=True)
        self.assertNotIn("abc kΩ", html)
        self.assertIn("22 kΩ", html)
        rv = self.client.post("/calculate", data={**VALID, "re": "-1"})
        html = rv.get_data(as_text=True)
        self.assertNotIn("-1 kΩ", html)
        rv = self.client.post("/calculate", data={**VALID, "vcc": "inf"})
        html = rv.get_data(as_text=True)
        self.assertNotIn("inf V", html)

    def test_post_cutoff_shows_input_values(self):
        rv = self.client.post("/calculate", data={**VALID, "r2": "1.5"})
        self.assertEqual(rv.status_code, 200)
        html = rv.get_data(as_text=True)
        self.assertIn("Cutoff", html)
        self.assertIn("1.5 kΩ", html)
        self.assertIn("VB =", html)
```

หมายเหตุ: ใช้ `r2="1.5"` (VTH ≈ 0.18 V < VBE → Cutoff) เพราะ "1 kΩ"/"2 kΩ" เป็น substring ของ "100 kΩ"/"22 kΩ"/"2.2 kΩ" — "1.5 kΩ" ไม่กำกวม

- [ ] **Step 2: รันยืนยัน fail (RED)**

Run: `& .venv\Scripts\python.exe -m unittest discover -s tests -v 2>&1 | Select-Object -Last 8`
Expected: **19 pass + 4 FAIL** (4 tests ใหม่ fail เพราะไม่มี "Circuit: Common-Emitter Amplifier" ฯลฯ ในหน้า)

- [ ] **Step 3: Implement ใน `app.py`**

เพิ่ม 2 ฟังก์ชัน (วางก่อน `_form_context`):

```python
def _typed_number(form, name, positive=False):
    """คืนสตริงตัวเลขตามที่ผู้ใช้พิมพ์ ถ้าผ่านเงื่อนไข — None ถ้าว่าง/ขยะ/non-finite/ติดลบ(ถ้าบังคับ)"""


def build_circuit_labels(form, results):
    """สร้าง label ค่าบนแผนผังวงจร — input ตามที่พิมพ์ + แรงดันโหนดเมื่อคำนวณแล้ว"""
```

กติกา (ตัดสินใจแล้ว — ต่างจาก spike ตรง `positive`):
- `_typed_number`: `raw = form.get(name).strip()` → ว่าง = None · `float()` ไม่ได้ = None · `not math.isfinite` = None · `positive and value <= 0` = None · ไม่งั้นคืน `raw` (สตริงเดิม ไม่จัดทศนิยมใหม่)
- ฟิลด์ positive: `vcc, r1, r2, rc, re, beta` (ตาม validation ของ solve_dc_bias) · `vbe` ไม่บังคับ (ลบ/ศูนย์ได้)
- format label: `vcc` → `"12 V"` · R ทั้ง 4 → `"100 kΩ"` (เติม ` kΩ` ต่อท้าย raw) · `npn` → `"NPN (β = 100)"` ถ้ามี β, `"NPN"` ถ้าไม่มี · `vbe_note` → `"VBE = 0.70 V"` ถ้ามี, None ถ้าไม่มี · `v_b/v_e/v_c` → `"VB = %.3f V" % results["v_b"]` ฯลฯ เมื่อ `results is not None`, ไม่งั้น None
- เดิน context: `index()` ส่ง `circuit=build_circuit_labels({}, None)` · `calculate()` เก็บ `results` (จาก `out["results"]`) แล้วส่ง `circuit=build_circuit_labels(raw_form, results)`

- [ ] **Step 4: สร้าง `templates/circuit.html` + include + CSS**

- `circuit.html` = การ์ด `.circuit-card` ตามเรขาคณิต spike (ต้นฉบับตรวจแล้ว) โดย label ทุกตัวใช้ pattern: `<text ...>R1</text>` ตามด้วย `{% if circuit.r1 %}<text ...>{{ circuit.r1 }}</text>{% endif %}` และ VCC ใช้ `VCC{% if circuit.vcc %} = {{ circuit.vcc }}{% endif %}` · node voltage 3 ตัว + `vbe_note` เป็น conditional ทั้งก้อน
- `index.html`: แทรก `{% include 'circuit.html' %}` หลังบล็อก `{% if warnings %}...{% endif %}` ก่อน `{% if rows %}`
- `style.css`: เพิ่ม `.circuit-card h2` (flex + gap สำหรับไอคอน), `.circuit-card .icon-zig`, `.circuit-card .circuit-wrap` (flex จัดกลาง), `svg.circuit` (max-width 100%, height auto)

- [ ] **Step 5: รันยืนยันผ่าน (GREEN)**

Run: `& .venv\Scripts\python.exe -m unittest discover -s tests -v 2>&1 | Select-Object -Last 4`
Expected: **Ran 23 tests — OK**

- [ ] **Step 6: Stage ไฟล์ให้นักศึกษา commit ผ่าน GitHub Desktop**

```bash
git add app.py templates/circuit.html templates/index.html static/style.css tests/test_web.py
```

ข้อความ commit: `feat: add circuit diagram with input values and node voltages`

---

### Task 2: Docs + End-to-End Verification

**Files:**
- Modify: `README.md` (โครงสร้างไฟล์ + บรรยายฟีเจอร์วงจร)
- Modify: `docs/validation.md` (จำนวน tests 23 + ผลตรวจวงจรผ่าน HTTP จริง)

**Interfaces:**
- Consumes: ผลจาก Task 1 (การ์ดวงจร + 23 tests)
- Produces: เอกสารตรงความจริงสำหรับส่งงาน

- [ ] **Step 1: อัปเดต README.md**

- โครงสร้างไฟล์: เพิ่ม `templates/circuit.html # แผนผังวงจร SVG + ค่า input/node voltage`
- เพิ่มย่อหน้าบรรยาย: การ์ดวงจรแสดงค่า input ตามตำแหน่งจริง + VB/VE/VC เมื่อคำนวณสำเร็จ (ค่า invalid ไม่ถูก echo)
- อัปเดตจำนวน test: 23 (9 engineering + 14 web)

- [ ] **Step 2: อัปเดต docs/validation.md**

- ส่วน Automated Tests: **Ran 23 tests — OK** + เพิ่มบรรยาย 4 tests วงจร
- เพิ่มแถวในตาราง HTTP: ตรวจ label วงจร (GET / ไม่มีค่า · POST valid มี "100 kΩ"/"VB = 1.942 V" · POST r1=abc ไม่มี "abc kΩ")

- [ ] **Step 3: ตรวจ HTTP จริงผ่าน Flask server**

รัน background: `& .venv\Scripts\python.exe -m flask --app app run --port 5001` แล้วตรวจด้วย `Invoke-WebRequest`:
- GET `/` → 200 + "Circuit: Common-Emitter Amplifier" + **ไม่มี** "VB =" / "100 kΩ"
- POST `/calculate` ชุดอ้างอิง → 200 + "VCC = 12 V", "100 kΩ", "VB = 1.942 V", "VC = 9.294 V", "VE = 1.242 V"
- POST r1="abc" → 200 + **ไม่มี** "abc kΩ" แต่มี "22 kΩ"
ตรวจแล้วหยุด server (`Get-Process python | Stop-Process`)

- [ ] **Step 4: รัน suite สุดท้าย + Stage**

Run: `& .venv\Scripts\python.exe -m unittest discover -s tests -v 2>&1 | Select-Object -Last 4`
Expected: **Ran 23 tests — OK**

```bash
git add README.md docs/validation.md
```

ข้อความ commit: `docs: update README and validation for circuit diagram`
