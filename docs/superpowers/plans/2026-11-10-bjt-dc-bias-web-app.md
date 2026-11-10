# BJT DC Bias Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Flask web app คำนวณ DC Operating Point ของวงจร BJT Common-Emitter แบบ Voltage-Divider Bias — ฟอร์มบน Browser → Python Backend คำนวณ → แสดงผลพร้อมหน่วย, validation, region warnings และ automated tests ผ่านเกณฑ์ A1–A7 ของ Lab 02

**Architecture:** Server-rendered Flask (ไม่มี JavaScript คำนวณ) — GET `/` แสดงฟอร์ม, POST `/calculate` แปลง kΩ→Ω แล้วเรียก `dc_bias.py` (pure engineering module) แล้ว render ผลกลับ `templates/index.html`

**Tech Stack:** Python 3.15 (ผ่าน `py` launcher), Flask 3.x + Jinja2, unittest

**Spec:** `docs/design-note.md` (สถานะ: อนุมัติแล้ว) — สมการอ้างอิงอยู่ที่ §6.4, ค่าอ้างอิงที่ §6.6

## Global Constraints

- ทุกคำสั่ง Python ใช้ `py` launcher (`python` ถูก MS Store alias ดัก) · คำสั่งรัน tests: `py -m unittest discover -s tests -v` จาก root ของ repo
- การรันใน shell ของ agent (แต่ละครั้งเป็น process ใหม่): ใช้ path เต็ม `.venv\Scripts\python.exe` แทน activate
- `dc_bias.py` ห้าม import Flask/Jinja หรือรู้จัก HTML/HTTP ใด ๆ
- ฟอร์มรับ R1/R2/RC/RE เป็น **kΩ** แปลง ×1000 เป็น Ω เฉพาะใน `app.py` จุดเดียว · `dc_bias` รับ/คืนหน่วย SI เสมอ (V, Ω, A)
- รูปแบบแสดงผล: `"%.3f"` + หน่วย (V / mA / µA)
- ข้อความ error/warning: ภาษาไทย + ชื่อฟิลด์อังกฤษตามที่ pin ในแต่ละ task
- ไม่ commit `.venv/`, `__pycache__/`, `.env` (มี `.gitignore` ครอบตั้งแต่ Task 2)
- ทุก task จบด้วย: agent เตรียมไฟล์ด้วย `git add` → **นักศึกษา commit ผ่าน GitHub Desktop GUI** ด้วยข้อความที่กำหนด → agent ยืนยันด้วย `git log --oneline -1` แล้วค่อยไป task ถัดไป
- ทำงานใน repo โดยตรงที่ `C:\Users\b6828974\Documents\GitHub\BJT DC Bias Web App` (ไม่ใช้ worktree เพราะนักศึกษาใช้ GitHub Desktop ดู diff ระหว่างทำ)
- ไฟล์ทุกไฟล์ encode UTF-8

## Review Focus

1. POST ไม่ครบ 7 ช่อง (ฟิลด์ขาดหาย) → HTTP 200 + error ระบุฟิลด์ที่หาย ไม่ crash → `test_post_missing_fields` (Task 2)
2. ตัวเลขผิดรูปแบบ (`"abc"`, `"2,2"`) → HTTP 200 + error ไม่ใช่ exception → `test_post_non_numeric` + `test_post_bad_decimal` (Task 2)
3. GET `/calculate` (ผิด method) → 405 ไม่ใช่ 500 → `test_get_calculate_405` (Task 2)
4. ค่าสุดขั้ว β=1e12 และ VBE ติดลบ → คำนวณได้ ไม่ overflow/crash → `test_huge_beta_no_crash` + `test_negative_vbe_still_computes` (Task 1)
5. ขอบเขตของ warning: VTH=VBE พอดี → Cutoff (กฎ ≤) และ VCE ต่ำกว่า 0.3 V → Saturation → `test_vth_equals_vbe_cutoff` + `test_saturation_warning` (Task 1)

## ก่อน Task 1 — Commit เอกสาร

นักศึกษา commit ไฟล์ที่มีอยู่แล้วผ่าน GitHub Desktop:
ข้อความ: `docs: add design note and implementation plan`
ไฟล์: `docs/design-note.md`, `docs/superpowers/plans/2026-11-10-bjt-dc-bias-web-app.md`

---

### Task 1: Engineering Module `dc_bias.py`

**Files:**
- Create: `dc_bias.py`
- Test: `tests/test_dc_bias.py`

**Interfaces:**
- Consumes: ไม่มี (task แรก)
- Produces: `solve_dc_bias(vcc: float, r1: float, r2: float, rc: float, re: float, beta: float, vbe: float) -> dict` — Task 2 เรียกด้วยชื่อนี้เท่านั้น
- รีเทิร์น:
  ```python
  {
    "errors": list[str],    # [] เมื่อ valid; เช่น "R1 ต้องมากกว่า 0"
    "warnings": list[str],  # [] เมื่อ Active region
    "results": None | {
        "v_th": float, "r_th": float,          # V, Ω
        "ib": float, "ic": float, "ie": float, # A
        "v_b": float, "v_e": float, "v_c": float, "v_ce": float,  # V
    },
  }
  ```
- เงื่อนไข: ตรวจ `vcc>0, r1>0, r2>0, rc>0, re>0, beta>0` (VBE ค่าใด ๆ ก็ได้) — ผิดข้อใดข้อหนึ่ง → เก็บ error ทุกข้อที่ผิดตามลำดับฟิลด์ (VCC, R1, R2, RC, RE, β) และ `results=None` · ถ้า valid คำนวณผลเสมอ (แม้ออกนอก region) แล้วเก็บ warnings
- ข้อความ pin:
  - error: `f"{NAME} ต้องมากกว่า 0"` เช่น `"β ต้องมากกว่า 0"`
  - warning Cutoff: `"คำเตือน Cutoff: VTH ≤ VBE ไบอาสอยู่นอก Forward-Active region ผลลัพธ์จากแบบจำลองนี้ใช้อ้างอิงไม่ได้"`
  - warning Saturation: `"คำเตือน Saturation: VCE < 0.3 V ไบอาสเข้าใกล้ Saturation ผลจากแบบจำลอง Forward-Active ใช้อ้างอิงไม่ได้"`

- [ ] **Step 1: เขียน failing tests ใน `tests/test_dc_bias.py`**

```python
import unittest

from dc_bias import solve_dc_bias

DATASET = dict(vcc=12.0, r1=100e3, r2=22e3, rc=2.2e3, re=1e3, beta=100.0, vbe=0.70)


class TestReferenceValues(unittest.TestCase):
    def test_lab_dataset(self):
        out = solve_dc_bias(**DATASET)
        self.assertEqual(out["errors"], [])
        self.assertEqual(out["warnings"], [])
        r = out["results"]
        self.assertAlmostEqual(r["v_th"], 2.163934, places=5)
        self.assertAlmostEqual(r["r_th"], 18032.786885, places=3)
        self.assertAlmostEqual(r["ib"] * 1e6, 12.298581, places=4)
        self.assertAlmostEqual(r["ic"] * 1e3, 1.229858, places=4)
        self.assertAlmostEqual(r["ie"] * 1e3, 1.242157, places=4)
        self.assertAlmostEqual(r["v_e"], 1.242157, places=5)
        self.assertAlmostEqual(r["v_b"], 1.942157, places=5)
        self.assertAlmostEqual(r["v_c"], 9.294312, places=5)
        self.assertAlmostEqual(r["v_ce"], 8.052155, places=5)


class TestValidation(unittest.TestCase):
    def test_zero_resistor(self):
        out = solve_dc_bias(12, 0, 22e3, 2.2e3, 1e3, 100, 0.7)
        self.assertIn("R1 ต้องมากกว่า 0", out["errors"])
        self.assertIsNone(out["results"])

    def test_zero_beta(self):
        out = solve_dc_bias(**{**DATASET, "beta": 0})
        self.assertIn("β ต้องมากกว่า 0", out["errors"])
        self.assertIsNone(out["results"])

    def test_negative_vcc(self):
        out = solve_dc_bias(**{**DATASET, "vcc": -5})
        self.assertIn("VCC ต้องมากกว่า 0", out["errors"])
        self.assertIsNone(out["results"])


class TestRegionWarnings(unittest.TestCase):
    def test_cutoff_warning(self):
        # VTH = 0.1188 V <= VBE = 0.70 V
        out = solve_dc_bias(12, 100e3, 1e3, 2.2e3, 1e3, 100, 0.7)
        self.assertEqual(out["errors"], [])
        self.assertTrue(any("Cutoff" in w for w in out["warnings"]))
        self.assertIsNotNone(out["results"])

    def test_saturation_warning(self):
        # VCE = 0.0028 V < 0.3 V และ VTH = 1.0 V > VBE
        out = solve_dc_bias(2, 10e3, 10e3, 390, 10, 100, 0.7)
        self.assertEqual(out["errors"], [])
        self.assertTrue(any("Saturation" in w.lower() for w in out["warnings"]))
        self.assertFalse(any("Cutoff" in w for w in out["warnings"]))
        self.assertAlmostEqual(out["results"]["v_ce"], 0.002829, places=5)

    def test_vth_equals_vbe_cutoff(self):
        # VTH = 0.7 V == VBE = 0.7 V -> กฎ <= ต้องเตือน Cutoff
        out = solve_dc_bias(1.4, 10e3, 10e3, 390, 10, 100, 0.7)
        self.assertTrue(any("Cutoff" in w for w in out["warnings"]))


class TestExtremeInputs(unittest.TestCase):
    def test_huge_beta_no_crash(self):
        out = solve_dc_bias(**{**DATASET, "beta": 1e12})
        self.assertEqual(out["errors"], [])
        self.assertIsNotNone(out["results"])

    def test_negative_vbe_still_computes(self):
        out = solve_dc_bias(**{**DATASET, "vbe": -0.7})
        self.assertEqual(out["errors"], [])
        self.assertIsNotNone(out["results"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: รันเพื่อยืนยันว่า fail**

Run: `py -m unittest discover -s tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'dc_bias'`

- [ ] **Step 3: Implement `solve_dc_bias` ใน `dc_bias.py`**

- ตรวจเงื่อนไข 6 ตัวตาม Interfaces (เก็บ error ทุกข้อที่ผิด, ถ้ามี error คืน `{"errors": [...], "warnings": [], "results": None}`)
- ถ้า valid คำนวณตามสมการใน spec §6.4: `VTH`, `RTH`, `IB`, `IC`, `IE`, `VE`, `VB`, `VC`, `VCE`
- ต่อท้าย warnings: `VTH <= VBE` → Cutoff · `VCE < 0.3` → Saturation (สองอย่างเป็นไปได้พร้อมกัน)
- ไม่มี import อื่นนอกจาก typing ถ้าจำเป็น

- [ ] **Step 4: รันเพื่อยืนยันว่าผ่าน**

Run: `py -m unittest discover -s tests -v`
Expected: 9 tests OK

- [ ] **Step 5: Commit**

Run: `git add dc_bias.py tests/test_dc_bias.py` → นักศึกษา commit ใน GitHub Desktop ด้วยข้อความ `feat: add dc_bias engineering module with unit tests` → ยืนยัน `git log --oneline -1`

---

### Task 2: Flask App + Template + CSS + Web Tests

**Files:**
- Create: `app.py`, `templates/index.html`, `static/style.css`, `tests/test_web.py`, `requirements.txt`, `.gitignore`
- Create (ไม่ commit): `.venv/`

**Interfaces:**
- Consumes: `solve_dc_bias(vcc, r1, r2, rc, re, beta, vbe)` จาก Task 1
- Produces: Flask `app` (สำหรับ `app.test_client()` ใน Task 2 เองและการรันจริง) พร้อม:
  - `FIELDS` — list คู่ `(name, label, unit, placeholder)` ตายตัว 7 ช่อง: `(vcc, "VCC (Supply Voltage)", "V", "12")`, `(r1, "R1 (Upper Bias)", "kΩ", "100")`, `(r2, "R2 (Lower Bias)", "kΩ", "22")`, `(rc, "RC (Collector)", "kΩ", "2.2")`, `(re, "RE (Emitter)", "kΩ", "1")`, `(beta, "β (Current Gain)", "—", "100")`, `(vbe, "VBE (Base-Emitter)", "V", "0.70")`
  - `parse_form(form: Mapping[str, str]) -> tuple[dict[str, float], list[str]]` — คืน values (key `vcc,r1,r2,rc,re,beta,vbe`, R เป็น Ω แล้ว) และ errors (`f"{LABEL} ต้องกรอกเป็นตัวเลข"` เมื่อขาด/ว่าง/`float()` ไม่ได้)
  - `build_rows(results: dict) -> list[dict]` — แถวผลลัพธ์ `{"label": ..., "value": ...}` ลำดับ: VB, VE, VC, VCE, IC, IB, IE, VTH, RTH · V/VCE ใช้ `"%.3f V"`, IC/IE `"%.3f mA"`, IB `"%.3f µA"`, VTH `"%.3f V"`, RTH `"%.3f kΩ"` (หาร 1000)
  - Routes: `GET /` → `render_template("index.html", form=<dict 7 คีย์ค่าว่าง>, errors=[], warnings=[], rows=[])` · `POST /calculate` → parse → ถ้า parse errors แสดง error; ไม่งั้นเรียก `solve_dc_bias(**values)` → ถ้า `out["errors"]` แสดง error; ไม่งั้น `rows=build_rows(out["results"])`, ส่ง `warnings=out["warnings"]` · ทุกกรณี refilled form จาก `request.form` (raw string) และคืน HTTP 200
  - Template context: `form` (dict[str,str] 7 คีย์), `errors: list[str]`, `warnings: list[str]`, `rows: list[dict]`

- [ ] **Step 1: สร้าง venv + ติดตั้ง Flask ใน venv + เขียน `requirements.txt` และ `.gitignore`**

Run: `py -m venv .venv` แล้ว `.venv\Scripts\python.exe -m pip install flask` (ลงใน venv ไม่ใช่ global)
`requirements.txt`: `flask>=3.1,<4` → ตรวจว่าทำงาน: `.venv\Scripts\python.exe -m pip install -r requirements.txt`
`.gitignore`: `.venv/`, `__pycache__/`, `*.pyc`, `.env`

- [ ] **Step 2: เขียน failing tests ใน `tests/test_web.py`**

```python
import unittest

from app import app

VALID = {"vcc": "12", "r1": "100", "r2": "22", "rc": "2.2", "re": "1",
         "beta": "100", "vbe": "0.70"}


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_index(self):
        rv = self.client.get("/")
        self.assertEqual(rv.status_code, 200)
        html = rv.get_data(as_text=True)
        self.assertIn("Calculate DC Bias", html)
        self.assertIn('name="vcc"', html)
        self.assertIn('name="beta"', html)

    def test_post_valid_reference(self):
        rv = self.client.post("/calculate", data=VALID)
        self.assertEqual(rv.status_code, 200)
        html = rv.get_data(as_text=True)
        self.assertIn("8.052 V", html)
        self.assertIn("1.230 mA", html)
        self.assertIn("12.299 µA", html)
        self.assertNotIn("Cutoff", html)
        self.assertNotIn("Saturation", html)

    def test_post_non_numeric(self):
        rv = self.client.post("/calculate", data={**VALID, "r1": "abc"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("R1 ต้องกรอกเป็นตัวเลข", rv.get_data(as_text=True))

    def test_post_bad_decimal(self):
        rv = self.client.post("/calculate", data={**VALID, "r2": "2,2"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("R2 ต้องกรอกเป็นตัวเลข", rv.get_data(as_text=True))

    def test_post_missing_fields(self):
        rv = self.client.post("/calculate", data={"vcc": "12"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("R1 ต้องกรอกเป็นตัวเลข", rv.get_data(as_text=True))

    def test_post_negative_resistor(self):
        rv = self.client.post("/calculate", data={**VALID, "re": "-1"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("RE ต้องมากกว่า 0", rv.get_data(as_text=True))

    def test_post_cutoff_warning_shown(self):
        rv = self.client.post("/calculate", data={**VALID, "r2": "1"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("Cutoff", rv.get_data(as_text=True))

    def test_post_saturation_warning_shown(self):
        rv = self.client.post("/calculate",
                             data={"vcc": "2", "r1": "10", "r2": "10",
                                   "rc": "0.39", "re": "0.01",
                                   "beta": "100", "vbe": "0.7"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("Saturation", rv.get_data(as_text=True))

    def test_get_calculate_405(self):
        rv = self.client.get("/calculate")
        self.assertEqual(rv.status_code, 405)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: รันเพื่อยืนยันว่า fail**

Run: `.venv\Scripts\python.exe -m unittest discover -s tests -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app'` (test_dc_bias ยังผ่านอยู่)

- [ ] **Step 4: Implement `app.py`, `templates/index.html`, `static/style.css`**

- `app.py`: ตาม Interfaces (FIELDS + parse_form + build_rows + 2 routes) — parse ครบทุกช่องแล้วค่อยเรียก solve (ถ้ามี parse error ไม่เรียก)
- `templates/index.html`: หน้าเดียว — `<!doctype html>` + `lang="th"` + `<meta charset="utf-8">` · h1 "BJT DC Bias Calculator" + คำอธิบาย "วงจรขยาย Common-Emitter แบบ Voltage-Divider Bias" · form POST `/calculate` วน `FIELDS` (Jinja for-loop ได้) แสดง label + unit + `value="{{ form[name] }}"` + placeholder · ปุ่ม submit ข้อความ **Calculate DC Bias** · `{% if errors %}` กล่อง `.errors` แจ้งทุกข้อ · `{% if warnings %}` กล่อง `.warnings` · `{% if rows %}` ตาราง `.results` (คอลัมน์ Quantity / Value) · CSS ผูกด้วย `<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">`
- `static/style.css`: ~50 บรรทัด พื้นหลังอ่อน + การ์ดขาว + ฟอร์ม grid 2 คอลัมน์ + กล่อง `.errors` (แดง) + `.warnings` (ส้ม) + ตารางมีเส้น (รายละเอียดตกแต่งเป็นของ builder ตาม spec §7)

- [ ] **Step 5: รันเพื่อยืนยันว่าผ่าน**

Run: `.venv\Scripts\python.exe -m unittest discover -s tests -v`
Expected: 18 tests OK (9 ของ Task 1 + 9 ของ Task 2)

- [ ] **Step 6: Commit**

Run: `git add app.py templates/index.html static/style.css tests/test_web.py requirements.txt .gitignore` → นักศึกษา commit ด้วยข้อความ `feat: add Flask web app with form, validation and web tests` → ยืนยัน `git log --oneline -1`

---

### Task 3: Project Docs + End-to-End Verification

**Files:**
- Create: `README.md`, `AGENTS.md`, `docs/validation.md`, `docs/reflection.md`

**Interfaces:**
- Consumes: ทุกอย่างจาก Task 1–2 (รันจริงเพื่อเก็บผล)
- Produces: เอกสารครบตาม file tree ของ spec §5 · `docs/validation.md` เก็บผลจริงจากการรันใน task นี้

- [ ] **Step 1: เขียน `README.md`**

โครง (ภาษาไทย): ชื่อโปรเจกต์ + คำอธิบาย 1 ย่อหน้า · แบบจำลองและสมการ §6.4 ของ spec · โครงสร้างไฟล์ · การติดตั้ง: `py -m venv .venv` → activate (PowerShell: `.venv\Scripts\Activate.ps1` / cmd: `.venv\Scripts\activate`) → `pip install -r requirements.txt` · การรัน: `flask --app app run --debug` → เปิด `http://127.0.0.1:5000/` · การรัน tests: `python -m unittest discover -s tests -v` · ชุดข้อมูลทดลอง (VCC=12, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V) + ผลที่ควรเห็นตาม spec §6.6

- [ ] **Step 2: เขียน `AGENTS.md`**

หลักสำหรับ AI agent ที่ทำงานใน repo นี้: ใช้ `py` launcher · รัน tests ด้วย unittest discover จาก root · `dc_bias.py` ไม่รู้จัก HTTP/HTML · UI ภาษาไทย + ศัพท์อังกฤษ · ผลต้องมาจากการคำนวณจริง ห้ามฮาร์ดโค้ด · นักศึกษาเป็นคน commit ผ่าน GitHub Desktop

- [ ] **Step 3: ตรวจสอบ reproducibility จากไฟล์ว่าง (เกณฑ์ A7)**

ลบ `.venv` แล้วสร้างใหม่: `py -m venv .venv` → `py -m pip install -r requirements.txt` → รัน tests: `.venv\Scripts\python.exe -m unittest discover -s tests -v` → Expected: 18 tests OK

- [ ] **Step 4: ตรวจ HTTP จริง (เกณฑ์ A1, A2, A5)**

รัน server แบบ background: `.venv\Scripts\python.exe -m flask --app app run --port 5001` → รอจนพร้อม → ตรวจ:
- `Invoke-WebRequest http://127.0.0.1:5001/` → StatusCode 200 + เจอ "Calculate DC Bias"
- POST ชุดข้อมูลอ้างอิง → เจอ "8.052 V" และ "1.230 mA"
- POST `r1=abc` → 200 + เจอ "R1 ต้องกรอกเป็นตัวเลข"
→ หยุด server

- [ ] **Step 5: เขียน `docs/validation.md` จากผลจริงของ Step 3–4**

บันทึก: ตารางเทียบผลเว็บกับค่าอ้างอิง spec §6.6 · จำนวน tests ที่ผ่าน (18) · ผล HTTP checks · ข้อจำกัดของแบบจำลอง (Forward-Active approximation, ไม่ใช่ SPICE)

- [ ] **Step 6: เขียน `docs/reflection.md` (scaffold ให้นักศึกษาเติม)**

หัวข้อคำถาม: (1) การเปิด `templates/index.html` ตรง ๆ ต่างจากการรัน Flask อย่างไร (2) ฟอร์มส่งข้อมูลไป Python อย่างไร (3) แก้สมการใน `dc_bias.py` แล้วต้องแก้ HTML ไหม เพราะอะไร (4) ทำไมผลนอก Active Region ต้องมี Warning — ทิ้งช่องว่างให้นักศึกษาเขียนเอง

- [ ] **Step 7: Commit + Push**

Run: `git add README.md AGENTS.md docs/validation.md docs/reflection.md` → นักศึกษา commit ด้วยข้อความ `docs: add README, AGENTS, validation and reflection notes` → กด **Push origin** ใน GitHub Desktop → ส่ง repo URL + commit SHA บน Moodle ตามหัวข้อ 10 ของเอกสาร Lab
