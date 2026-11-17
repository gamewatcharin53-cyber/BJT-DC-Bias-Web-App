# Lab 03 Multi-Mode BJT Bias Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** เพิ่มโหมด Fixed Bias และ Emitter Bias (single supply) ในเว็บ Flask เดิม โดยคงผลลัพธ์ Divider และ tests เดิม 25 ตัวไว้ครบ

**Architecture:** `dc_bias.py` เพิ่มฟังก์ชันคำนวณบริสุทธิ์สองตัวแยกจาก `solve_dc_bias()` เดิม; `app.py` เก็บ field list/metadata ต่อโหมด, validate เฉพาะช่องที่โหมดใช้, แปลง kΩ→Ω แล้ว dispatch ไปฟังก์ชันตามโหมด; template ใช้ select แบบ GET reload (ไม่มี JS ใหม่) และ include การ์ด SVG เฉพาะ Divider

**Tech Stack:** Python 3, Flask, Jinja2, unittest ที่มีอยู่, CSS ธรรมดา

**Spec:** `docs/superpowers/specs/2026-11-17-lab03-multi-mode-design.md`

## Global Constraints

- หน่วยฟอร์ม: ตัวต้านทานทุกตัว (รวม `RB`) เป็น **kΩ**; VCC/VBE เป็น V; β ไม่มีหน่วย — แปลง kΩ→Ω ก่อนเรียก `dc_bias`
- tests เดิม **25 ตัวต้องผ่านทั้งหมด** และ **ห้ามเพิ่ม unittest หรือสคริปต์ Playwright** (ใบงานระบุ)
- ห้ามเพิ่ม dependency, JavaScript framework หรือ `opencode.json`
- `dc_bias.py` ต้องไม่ import Flask/Jinja และไม่รู้จัก HTML/HTTP
- `solve_dc_bias()` และพฤติกรรม/warning ของ Divider **ห้ามเปลี่ยน** (Cutoff: `VTH ≤ VBE`, Saturation: `VCE < 0.3 V`)
- POST ที่ไม่มี/ว่าง `mode` ถือเป็น `divider`; `mode` ที่ไม่รู้จักต้อง error ไม่ fallback
- UI เป็นภาษาไทย + ศัพท์เทคนิคอังกฤษ; ตัวเลขผลลัพธ์ทั้งหมดมาจาก Python
- นักศึกษา commit ผ่าน GitHub Desktop — agent **ห้าม** `git commit`/`git push`; ทำได้แค่ `git add` + เสนอข้อความ commit
- Playwright MCP ใช้ไม่ได้บนเครื่องนี้ (ไม่มี `node`/`npx`) — ใช้ OpenCode Browser และบันทึก `NOT RUN`

## Review Focus

รายการที่ spec กำหนดแต่ tests เดิมไม่ครอบ — ทุกข้อมีขั้นตรวจใน task ที่เป็นเจ้าของโค้ด:

1. `mode=fixed` ที่ไม่ส่ง `r1/r2/re` ต้องไม่ขึ้น error ของช่องเหล่านั้น (validate เฉพาะช่องที่ใช้)
2. `mode` แปลก ๆ (เช่น `class-a`) ทั้ง GET และ POST ต้องขึ้น `ไม่รู้จักโหมดวงจร: class-a` และไม่มีตารางผล — ไม่เงียบ ๆ เป็น Divider
3. `RB=0` (fixed/emitter) ต้องได้ `RB ต้องมากกว่า 0` และไม่มีตาราง/การ์ดวงจร
4. Fixed bias ที่ `VBE > VCC` (เช่น VCC=0.5, VBE=0.7) ต้องได้ warning Cutoff จาก `IB ≤ 0` ไม่ใช่ `nan`
5. สลับโหมดแล้วฟอร์ม/ผลของโหมดก่อนต้องไม่ค้าง: Fixed ต้องไม่มีช่อง `R1/R2/RE` และไม่มีผลลัพธ์ Divider

---

### Task 1: ฟังก์ชัน Fixed Bias และ Emitter Bias ใน `dc_bias.py`

**Files:**
- Modify: `dc_bias.py` (ต่อท้ายไฟล์หลัง `solve_dc_bias`)
- Test: ใช้ tests เดิม `tests/test_dc_bias.py` (ไม่เพิ่ม test ใหม่) + sanity check ชั่วคราวด้วย `python -c`

**Interfaces:**
- Consumes: ไม่มี (โมดูลบริสุทธิ์)
- Produces:
  - `solve_fixed_bias(vcc, rb, rc, beta, vbe) -> dict` — คีย์ `{"errors": list[str], "warnings": list[str], "results": dict|None}`; `results` มี `ib, ic, ie, v_b, v_e, v_c, v_ce` (หน่วย SI: V, A, Ω)
  - `solve_emitter_bias(vcc, rb, rc, re, beta, vbe) -> dict` — คีย์เดียวกัน
- ค่าอ้างอิง SI: `vcc=12`, `rb=1e6`, `rc=2.2e3`, `re=1e3`, `beta=100`, `vbe=0.70`

- [ ] **Step 1: เขียน `solve_fixed_bias` ใน `dc_bias.py`**

Signature ตาม Interfaces; ตรวจ `("VCC", vcc), ("RB", rb), ("RC", rc), ("β", beta)` ด้วย `value <= 0` → `f"{name} ต้องมากกว่า 0"` และคืน `{"errors": errors, "warnings": [], "results": None}` เมื่อมี error (รูปแบบเดียวกับ `solve_dc_bias`)

สมการ: `ib = (vcc - vbe) / rb`; `ic = beta * ib`; `ie = (beta + 1) * ib`; `v_e = 0.0`; `v_b = v_e + vbe`; `v_c = vcc - ic * rc`; `v_ce = v_c - v_e`

Warnings (เรียง Cutoff ก่อน Saturation):
- `ib <= 0` → `"คำเตือน Cutoff: IB ≤ 0 A ไบอาสอยู่นอก Forward-Active region ผลลัพธ์จากแบบจำลองนี้ใช้อ้างอิงไม่ได้"`
- `v_ce <= 0.2` → `"คำเตือน Saturation: VCE ≤ 0.2 V ไบอาสเข้าใกล้ Saturation ผลจากแบบจำลอง Forward-Active ใช้อ้างอิงไม่ได้"`

- [ ] **Step 2: เขียน `solve_emitter_bias` ใน `dc_bias.py`**

ตรวจ `("VCC", vcc), ("RB", rb), ("RC", rc), ("RE", re), ("β", beta)` แบบเดียวกัน

สมการ: `ib = (vcc - vbe) / (rb + (beta + 1) * re)`; `ic`, `ie`, `v_e = ie * re`, `v_b`, `v_c`, `v_ce` เหมือน Task 1 Step 1; warnings เงื่อนไข/ข้อความเดียวกัน

- [ ] **Step 3: Sanity check ค่าอ้างอิงด้วย Python ชั่วคราว (ไม่สร้างไฟล์ commit)**

Run:
```powershell
.venv\Scripts\python.exe -c "from dc_bias import solve_fixed_bias, solve_emitter_bias; f=solve_fixed_bias(12,1e6,2.2e3,100,0.70)['results']; e=solve_emitter_bias(12,1e6,2.2e3,1e3,100,0.70)['results']; e2=solve_emitter_bias(12,1e6,2.2e3,2e3,100,0.70)['results']; print(round(f['ic']*1e3,6), round(f['v_ce'],6)); print(round(e['ic']*1e3,6), round(e['v_ce'],6)); print(round(e2['ic']*1e3,6), round(e2['v_ce'],6))"
```
Expected: `1.13 9.514` / `1.02634 8.70545` / `0.9401 8.032779`

- [ ] **Step 4: ตรวจ warning และ validation ด้วย Python ชั่วคราว**

Run:
```powershell
.venv\Scripts\python.exe -c "from dc_bias import solve_fixed_bias, solve_emitter_bias; print(solve_fixed_bias(0.5,1e6,2.2e3,100,0.7)['warnings'][0][:20]); print(solve_fixed_bias(12,0,2.2e3,100,0.7)['errors']); print(solve_emitter_bias(5,1e6,20e3,1e3,100,0.7)['warnings'][0][:20])"
```
Expected: `คำเตือน Cutoff:` / `['RB ต้องมากกว่า 0']` / `คำเตือน Saturation:`

- [ ] **Step 5: รัน tests เดิมทั้งชุด**

Run: `.venv\Scripts\python.exe -m unittest discover -s tests -v`
Expected: `Ran 25 tests` และ `OK` (Divider ต้องไม่เปลี่ยน)

- [ ] **Step 6: Stage งานของ task นี้**

```powershell
git add dc_bias.py
```
ข้อความ commit ที่เสนอ: `feat: add fixed-bias and emitter-bias solvers`

---

### Task 2: Mode plumbing ใน `app.py` + ฟอร์มเลือกโหมด + CSS

**Files:**
- Modify: `app.py`
- Modify: `templates/index.html`
- Modify: `static/style.css`
- Test: tests เดิม `tests/test_dc_bias.py`, `tests/test_web.py` + sanity check ด้วย Flask test client

**Interfaces:**
- Consumes: `solve_fixed_bias`, `solve_emitter_bias` จาก Task 1; `solve_dc_bias` เดิม
- Produces (ใช้ภายใน `app.py`/template):
  - `MODE_LABELS: dict[str, str]` — `{"divider": "Voltage Divider Bias", "fixed": "Fixed Bias", "emitter": "Emitter Bias (single supply)"}` (เรียงตามนี้)
  - `MODE_FIELDS: dict[str, list[str]]` — divider `["vcc","r1","r2","rc","re","beta","vbe"]`, fixed `["vcc","rb","rc","beta","vbe"]`, emitter `["vcc","rb","rc","re","beta","vbe"]`
  - `fields_for(mode: str) -> list[tuple[str, str, str, str]]` — คืน `(name, label, unit, placeholder)`
  - `parse_form(form, mode: str) -> tuple[dict, list[str]]`
  - `build_rows(results) -> list[tuple[str, str]]`
  - template context เพิ่ม: `mode`, `mode_label`, `mode_valid`, `mode_options` (list ของ `(value, label)`), `fields`, `form`, `circuit`

- [ ] **Step 1: เพิ่ม metadata และ mode tables ใน `app.py`**

- คง `FIELDS` เดิม (Divider) ตามลำดับเดิมทุกตัว
- เพิ่ม `RB_FIELD = ("rb", "RB (Base Bias)", "kΩ", "1000")` และ `FIELD_LOOKUP = {f[0]: f for f in FIELDS + [RB_FIELD]}`
- เพิ่ม `KOHM_FIELDS = {"r1", "r2", "rc", "re", "rb"}`
- เพิ่ม `MODE_LABELS`, `MODE_FIELDS` ตาม Interfaces; `fields_for(mode)` คืน `[FIELD_LOOKUP[name] for name in MODE_FIELDS[mode]]`
- import `solve_fixed_bias`, `solve_emitter_bias` เพิ่มจาก `dc_bias`
- อัปเดต docstring หัวไฟล์เป็น Lab 03 (3 โหมด)

- [ ] **Step 2: ปรับ `parse_form(form, mode)` และ `build_rows`**

- `parse_form` วน `fields_for(mode)` แทน `FIELDS`; ตรรกะเดิมทุกอย่าง: ว่าง/`ValueError`/non-finite → `f"{label.split(' ')[0]} ต้องกรอกเป็นตัวเลข"`; คูณ 1000 ถ้าอยู่ใน `KOHM_FIELDS` **ก่อน** `math.isfinite`
- `build_rows` สร้าง 7 แถวร่วมตามลำดับเดิม (VB, VE, VC, VCE, IC, IB, IE) แล้วต่อท้าย VTH/RTH **เฉพาะเมื่อ** `"v_th" in results` — Divider ต้องได้ลำดับ 9 แถวเหมือนเดิม

- [ ] **Step 3: ปรับ `_typed_number`, `build_circuit_labels`, `_form_context`**

- `_typed_number`: ไม่ต้องแก้ (KOHM_FIELDS ครอบ `rb` แล้ว แต่ Divider ไม่มี field นี้)
- `build_circuit_labels`: คงเดิมทั้งหมด
- `_form_context(fields, form=None)`: รับ field list เป็นพารามิเตอร์แรก; คืน `{name: "" ...}` หรือ `{name: form.get(name, "") ...}` ตาม field ที่ส่งมา (แทนการใช้ `FIELDS` ตายตัว)

- [ ] **Step 4: ปรับ route `/` และ `/calculate`**

`index()`:
- `mode = (request.args.get("mode") or "").strip() or "divider"`
- `mode_valid = mode in MODE_LABELS`; `fields = fields_for(mode) if mode_valid else []`
- `mode_label = MODE_LABELS.get(mode, mode)`
- ถ้าไม่ valid → `errors=[f"ไม่รู้จักโหมดวงจร: {mode}"]`, `circuit=None`, `form=_form_context([], None)`
- ถ้า valid → `circuit=build_circuit_labels({}, None)` เฉพาะ `mode == "divider"`; ไม่ใช่ Divider → `None`
- ส่ง `mode`, `mode_label`, `mode_valid`, `mode_options=list(MODE_LABELS.items())` เข้า template

`calculate()`:
- `mode = (request.form.get("mode") or "").strip() or "divider"`
- ถ้า `mode not in MODE_LABELS` → render ด้วย `fields=[]`, `form=_form_context([], raw_form)`, `circuit=None`, `errors=[f"ไม่รู้จักโหมดวงจร: {mode}"]`, warnings/rows ว่าง, `mode_valid=False`
- ไม่งั้น `values, parse_errors = parse_form(raw_form, mode)`; ถ้าไม่มี error → dispatch:
  `SOLVERS = {"divider": solve_dc_bias, "fixed": solve_fixed_bias, "emitter": solve_emitter_bias}` แล้ว `out = SOLVERS[mode](**values)`
- `circuit = build_circuit_labels(raw_form, results) if mode == "divider" else None`
- ส่ง context ครบเหมือน `index()`

- [ ] **Step 5: ปรับ `templates/index.html`**

- subtitle: อธิบาย 3 โหมด (Voltage Divider เดิม, Fixed Bias, Emitter Bias single supply) + แบบจำลอง Forward-Active
- เพิ่มการ์ดเลือกโหมด **ก่อน** บล็อก error:
```html
<form method="get" action="/" class="card mode-card">
    <h2>เลือกโหมดวงจร</h2>
    <div class="mode-row">
        <label for="mode">โหมดไบอัส</label>
        <select id="mode" name="mode">
            {% for value, label in mode_options %}
            <option value="{{ value }}"{% if value == mode %} selected{% endif %}>{{ label }}</option>
            {% endfor %}
        </select>
        <button type="submit" class="btn-mode">เปลี่ยนโหมด</button>
    </div>
</form>
```
- ย้าย/คงบล็อก error ไว้ **นอก** form หลัก (เพื่อให้แสดงได้ตอน mode ไม่รู้จัก) และเปลี่ยนหัวเป็น `พบข้อผิดพลาด{% if mode_label %} ({{ mode_label }}){% endif %}:` — รายการ `<li>` คงเดิม
- ครอบฟอร์มหลักด้วย `{% if mode_valid %}` … `{% endif %}`; ในฟอร์มเพิ่ม `<input type="hidden" name="mode" value="{{ mode }}">`; loop `fields` เหมือนเดิม; ปุ่ม Calculate คงข้อความเดิม
- warning heading: `คำเตือน — {{ mode_label }}:` (รายการคงเดิม)
- เปลี่ยน `{% include 'circuit.html' %}` เป็น `{% if circuit %}{% include 'circuit.html' %}{% endif %}`
- results heading: `DC Bias Results (Q-Point) — {{ mode_label }}`; ภายในตารางไม่เปลี่ยน
- ไม่เพิ่ม `<script>`

- [ ] **Step 6: เพิ่ม CSS ขั้นต่ำใน `static/style.css`**

ต่อท้ายส่วนก่อน media query หรือท้ายไฟล์: `.mode-card h2` ใช้สี/ขนาดเดียวกับ `.form-card h2`; `.mode-row` เป็น flex + gap + wrap + align-items center; `.mode-row select` padding/border/font ตาม `.input-row input`; `.btn-mode` ใช้สีพื้น `var(--blue)`, ตัวอักษรขาว, border-radius 6px, padding 8px 16px, cursor pointer และ hover เป็น `var(--navy)`; ใต้ `@media (max-width: 560px)` ให้ `.mode-row` เป็น `flex-direction: column; align-items: stretch;`

- [ ] **Step 7: Sanity check ผ่าน Flask test client (ไม่สร้างไฟล์ commit)**

Run:
```powershell
.venv\Scripts\python.exe -c "from app import app; c=app.test_client(); v={'vcc':'12','rc':'2.2','rb':'1000','re':'1','beta':'100','vbe':'0.70','mode':'fixed'}; h=c.post('/calculate',data=v).get_data(as_text=True); print('9.514 V' in h, '1.130 mA' in h, 'name=\"r1\"' in h); u=c.post('/calculate',data={**v,'mode':'class-a'}).get_data(as_text=True); print('ไม่รู้จักโหมดวงจร: class-a' in u, 'DC Bias Results' in u); z=c.post('/calculate',data={**v,'rb':'0'}).get_data(as_text=True); print('RB ต้องมากกว่า 0' in z, 'DC Bias Results' in z)"
```
Expected: `True True False` / `True False` / `True False`

- [ ] **Step 8: รัน tests เดิมทั้งชุด**

Run: `.venv\Scripts\python.exe -m unittest discover -s tests -v`
Expected: `Ran 25 tests` + `OK`

- [ ] **Step 9: Stage งานของ task นี้**

```powershell
git add app.py templates/index.html static/style.css
```
ข้อความ commit ที่เสนอ: `feat: add mode selector for divider, fixed, and emitter bias`

---

### Task 3: ตรวจรับผ่าน browser A1–A5 และเก็บหลักฐาน

**Files:**
- ไม่แก้ไฟล์โค้ด; เก็บผลไว้ใส่ `docs/validation.md` ใน Task 4

**Interfaces:**
- Consumes: เว็บจาก Task 2 (`/`, `/calculate`)
- Produces: ค่าที่เห็นจริงบนหน้าเว็บต่อกรณี A1–A5 + หลักฐานอย่างน้อย 1 ชิ้น

- [ ] **Step 1: รัน Flask server (background)**

Run: `.venv\Scripts\python.exe -m flask --app app run --port 5000`
ถ้าพอร์ต 5000 ถูกใช้อยู่ ให้ใช้พอร์ต 5001 และบันทึกพอร์ตที่ใช้จริง

- [ ] **Step 2: ตรวจ A1 — Divider เดิม**

เปิด `http://127.0.0.1:5000/` (ไม่ระบุ mode) กรอก VCC=12, R1=100, R2=22, RC=2.2, RE=1, β=100, VBE=0.70 → Calculate
Expected: มีการ์ด `Circuit: Common-Emitter Amplifier`, หัวตารางลงท้าย `— Voltage Divider Bias`, IC `1.230 mA`, VCE `8.052 V`, IB `12.299 µA`, ไม่มี Cutoff/Saturation

- [ ] **Step 3: ตรวจ A2 — Fixed Bias**

เลือกโหมด `Fixed Bias` → เปลี่ยนโหมด; ตรวจว่ามีเฉพาะ VCC, RB, RC, β, VBE (ไม่มี R1/R2/RE) และไม่มีการ์ดวงจร
กรอก VCC=12, RB=1000, RC=2.2, β=100, VBE=0.70 → Calculate
Expected: IC `1.130 mA`, VCE `9.514 V`, IB `11.300 µA`; ไม่มี warning

- [ ] **Step 4: ตรวจ A3/A4 — Emitter Bias**

เลือก `Emitter Bias (single supply)`; กรอก VCC=12, RB=1000, RC=2.2, RE=1, β=100, VBE=0.70 → Calculate
Expected A3: IC `1.026 mA`, VCE `8.705 V`, IB `10.263 µA`; ไม่มี warning
เปลี่ยน RE=2 → Calculate
Expected A4: IC `0.940 mA`, VCE `8.033 V` และ IC **ลดลง** จาก A3; ไม่มี warning

- [ ] **Step 5: ตรวจ A5 — Validation `RB=0`**

โหมด Fixed Bias, RB=0, ค่าอื่นตาม A2 → Calculate
Expected: HTTP 200, ข้อความ `RB ต้องมากกว่า 0`, ไม่มีตารางผล, ไม่มี `nan`

- [ ] **Step 6: ตรวจกรณีเสริมตาม Review Focus**

- Fixed bias ไม่กรอก R1/R2/RE → ไม่มี error ของช่องเหล่านั้น
- เปิด `/?mode=class-a` → `ไม่รู้จักโหมดวงจร: class-a`, ไม่มีฟอร์มหลัก/ตารางผล
- Fixed bias VCC=0.5, VBE=0.70 → warning `Cutoff` (IB ≤ 0) และไม่มี `nan`

- [ ] **Step 7: เก็บหลักฐาน**

จดค่าที่เห็นจริงทุกกรณี (ข้อความในตาราง) และเก็บ screenshot อย่างน้อย 1 รูป (A2 หรือ A3) ไว้ใน `docs/` หรือ `%TEMP%` ตามความเหมาะสม — ห้าม commit ไฟล์ screenshot ถ้าไม่จำเป็น

- [ ] **Step 8: ปิด server และบันทึกว่ากรณีใดใช้ OpenCode Browser**

ระบุในบันทึกผลว่า Playwright MCP = `NOT RUN` เพราะเครื่องไม่มี `node`/`npx`

---

### Task 4: เอกสาร (README, validation, reflection, AGENTS) + stage

**Files:**
- Modify: `README.md`
- Modify: `docs/validation.md`
- Modify: `docs/reflection.md`
- Modify: `AGENTS.md`
- Modify: `docs/superpowers/specs/2026-11-17-lab03-multi-mode-design.md` (สถานะ → อนุมัติแล้ว)

**Interfaces:**
- Consumes: ผลตรวจ A1–A5 จาก Task 3 + ตัวเลขจาก Task 1
- Produces: เอกสาร Lab 03 ที่ grader อ่านได้, ไฟล์ทั้งหมด staged

- [ ] **Step 1: อัปเดต `README.md`**

- หัวเรื่อง/คำอธิบาย: Lab 02–03, รองรับ 3 โหมด
- เพิ่มสมการ Fixed และ Emitter; คงสมการ Divider เดิม; ระบุว่า `VE = 0` สำหรับ Fixed
- เพิ่มหัวข้อ "การเลือกโหมด": select + ปุ่มเปลี่ยนโหมด (GET reload), ช่องที่แสดงเปลี่ยนตามโหมด, การ์ด SVG เฉพาะ Divider
- เพิ่ม `RB` ใน単位 kΩ และตารางค่าอ้างอิง A1–A5 (§7.7 ของ spec): A1 IC 1.229858→`1.230 mA`/VCE `8.052 V`; A2 `1.130 mA`/`9.514 V`; A3 `1.026 mA`/`8.705 V`; A4 `0.940 mA`/`8.033 V`; A5 error `RB ต้องมากกว่า 0`
- โครงสร้างไฟล์: `dc_bias.py` มี 3 ฟังก์ชัน; tests ยัง 9 + 16 = 25
- คงจำนวน tests `25 tests OK`
- เพิ่มหัวข้อ **Lab 03 Submission** ท้ายไฟล์:
```markdown
## Lab 03 Submission

- Repository: https://github.com/gamewatcharin53-cyber/BJT-DC-Bias-Web-App
- Commit SHA: `<เติมหลัง commit สุดท้าย>`
- AI-assisted: (นักศึกษาเติม: ส่วนที่ AI ช่วย เช่น ร่างโค้ด/เอกสาร/ตรวจ browser)
- Student verification: (นักศึกษาเติม: สิ่งที่ตรวจด้วยตนเอง เช่น รัน tests, ตรวจ A1–A5, ตรวจสมการ)
```
- ห้ามเขียนคำรับรองแทนนักศึกษาในสองบรรทัดสุดท้าย

- [ ] **Step 2: อัปเดต `docs/validation.md`**

- เปลี่ยนชื่อไฟล์เป็น Lab 02–03 ในหัวเรื่อง
- เปลี่ยนชื่อส่วน Lab 02 เดิมเป็น `## Lab 02 · เกณฑ์ A1–A7` พร้อมหมายเหตุว่า A1–A7 = เกณฑ์ตรวจรับ (คนละชุดกับ Lab 03)
- เพิ่ม `## Lab 03 · กรณีตรวจ A1–A5` + ตารางคอลัมน์: กรณี, อินพุต, ค่าคาดหมาย (ไม่ปัด), ค่าที่เห็นจริง, วิธีตรวจ, สถานะ — เติมค่าคาดหมายจาก §7.7 และค่าที่เห็นจริงจาก Task 3
- ใส่ค่าอ้างอิงอิสระ/สมการของโหมดใหม่อย่างน้อย 1 กรณี (แสดง IB, IC, VCE ที่ยังไม่ปัด)
- ระบุเครื่องมือ: `OpenCode Browser`; `Playwright MCP = NOT RUN` (ไม่มี `node`/`npx`)
- เพิ่มผล `Ran 25 tests — OK` ของรอบ Lab 03
- คงส่วน Lab 02 เดิม (A1–A7, reproducibility) ไว้ทั้งหมด

- [ ] **Step 3: ปรับ `docs/reflection.md` เป็น Lab 03**

เปลี่ยนหัวเป็น `Reflection — Lab 03: BJT Bias Web App (Multi-Mode)` และเปลี่ยนชุดคำถาม (คงรูปแบบ "คำตอบ:" ว่างไว้ ห้ามเติมคำตอบ):
1. เหตุใดจึงแยก `solve_fixed_bias()` / `solve_emitter_bias()` ออกจาก `solve_dc_bias()` แทนการรวมเป็นฟังก์ชันเดียว
2. การเลือกโหมดเดินทางจาก `<select>` → `app.py` → `dc_bias.py` อย่างไร และทำไม POST ที่ไม่มี `mode` จึงยังต้องทำงานแบบ Lab 02
3. การแปลงหน่วย kΩ→Ω และการตรวจ `RB=0` อยู่ที่ใด เพราะเหตุใด `dc_bias.py` จึงไม่รับค่าหน่วย kΩ
4. ทำไม warning ของ Fixed/Emitter ใช้ `IB ≤ 0`/`VCE ≤ 0.2 V` ขณะที่ Divider ยังใช้ `VTH ≤ VBE`/`VCE < 0.3 V` — ผลต่อผู้ใช้คืออะไร
5. สิ่งที่ได้เรียนรู้เพิ่มเติม (เขียนอิสระ)

- [ ] **Step 4: อัปเดต `AGENTS.md`**

- บรรทัดโปรเจกต์: `Lab 02–03`
- เพิ่มหมายเหตุสั้น ๆ ใต้สถาปัตยกรรม: `app.py` เป็นที่ dispatch ตามโหมด (`divider`/`fixed`/`emitter`) และแปลงหน่วย; `dc_bias.py` มี 3 ฟังก์ชันแยก; ห้ามย้ายเงื่อนไขโหมด/HTML ลง `dc_bias.py`
- ไม่เปลี่ยนกฎอื่น

- [ ] **Step 5: อัปเดตสถานะ design doc**

เปลี่ยนบรรทัดที่ 3 เป็น: `สถานะ: อนุมัติแล้ว (17 พ.ย. 2026) · แผน: docs/superpowers/plans/2026-11-17-lab03-multi-mode.md`

- [ ] **Step 6: รัน tests รอบสุดท้าย**

Run: `.venv\Scripts\python.exe -m unittest discover -s tests -v`
Expected: `Ran 25 tests` + `OK`

- [ ] **Step 7: Stage ทุกไฟล์และเสนอข้อความ commit**

```powershell
git add README.md docs/validation.md docs/reflection.md AGENTS.md docs/superpowers/specs/2026-11-17-lab03-multi-mode-design.md docs/superpowers/plans/2026-11-17-lab03-multi-mode.md
git status --short
```
ข้อความ commit ที่เสนอ: `docs: document Lab 03 multi-mode bias`
ห้าม commit เอง — แจ้งนักศึกษาให้ commit/push ผ่าน GitHub Desktop แล้วเติม Commit SHA ใน README
