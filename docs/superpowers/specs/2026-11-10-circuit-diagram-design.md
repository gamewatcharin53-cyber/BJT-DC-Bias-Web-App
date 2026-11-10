# Design — Circuit Diagram on Results Page (Lab 02 follow-up)

สถานะ: อนุมัติแล้ว (ฉบับ v2 — ปรับสไตล์ให้คล้ายรูปในเอกสาร Lab ผู้ใช้เลือกแถวเดียว + คง VB/VE/VC) · 10 พฤศจิกายน 2026

## Intent

เพิ่ม**แผนผังวงจร NPN Common-Emitter แบบ Voltage-Divider Bias** ลงบนหน้าเว็บ
โดยรูปต้อง**กำกับค่าจาก input ของผู้ใช้บนตัววงจร** — ค่าเปลี่ยนตามที่กรอกทุกครั้ง
และเมื่อคำนวณสำเร็จ แสดง**แรงดันโหนด** VB/VE/VC ที่ขา transistor (ผู้ใช้เลือกคงไว้)

**สไตล์ภาพ: ลอกจากรูป mockup ในเอกสาร Lab** (อ่านด้วยโมเดล Vision-Language
แล้วบรรยายกลับมา — ภาพต้นฉบับคือ `01B / THIS WEEK'S TARGET PREVIEW` ใน
Lab02 HTML): R หยักซิกแซกสไตล์อเมริกัน, โทนขาว-ดำ, ground แยก 2 จุด, label
R1/R2 ซ้าย · RC/RE ขวา, หัวการ์ด "Circuit: Common-Emitter Amplifier" + ไอคอน
หยักสีเขียว, "NPN (β = …)" ขวาวงกลม transistor

เหตุผล: ทำให้ผลลัพธ์อ่านเข้าใจง่าย — เห็นว่าค่าที่กรอกไปอยู่ตรงไหนของวงจร
และ Q-Point ไปโผล่ที่ขาใด (เสริมเกณฑ์ความเข้าใจงานของ Lab)

## Goals / Non-goals

**Goals**
- แผนผังวงจร topology ตายตัวตาม Lab: R1 จาก VCC–Base, R2 จาก Base–GND,
  RC จาก VCC–Collector, RE จาก Emitter–GND, NPN ตรงกลาง, VCC rail บน,
  **ground symbol แยก 2 จุด** (ใต้ R2 และใต้ RE — ไม่มีรางล่าง)
- สไตล์ตามรูปในเอกสาร: **R หยักซิกแซก**, เส้น+ตัวอักษรดำบนการ์ดขาว, หัวการ์ด
  "Circuit: Common-Emitter Amplifier" พร้อมไอคอนหยักสีเขียว
- กำกับค่า input ที่ตำแหน่งตัวต้านทาน/ราง VCC เมื่อฟิลด์นั้นกรอกเป็นตัวเลข valid
  (ตำแหน่ง label: R1/R2 ซ้าย · RC/RE ขวา · VCC เหนือรางบนตรงกลาง)
- กำกับ "NPN (β = …)" ทางขวาของวงกลม transistor + บรรทัดรอง "VBE = … V"
- แสดง VB, VE, VC เมื่อคำนวณสำเร็จ (format `%.3f V` เหมือนตารางผล) — ตัวหนา
- คมชัดทุกขนาด (SVG), เข้าธีมของหน้าเว็บ, responsive บนมือถือ

**Non-goals (anti-goals)**
- **ไม่เปลี่ยนเลย์เอาต์หน้าเว็บ** — คงแถวเดียว (ฟอร์ม → วงจร → ตาราง) ตามเดิม
  ไม่ทำ 3 คอลัมน์แบบรูปในเอกสาร (ผู้ใช้เลือกแถวเดียวแล้ว)
- ไม่มีแอนิเมชันกระแส/ลูกศรไหล, ไม่มี DC load line, ไม่มี topology อื่น
  (เก็บไว้ W3), ไม่มีการคลิก/แก้ไขวงจรบนรูป
- ไม่ใช้ภาพ WebP จากเอกสาร Lab โดยตรง (ภาพนิ่ง แสดงค่า input ไม่ได้)

## Constraints

- **ไม่เพิ่ม dependency** — วาด SVG เองใน template
- ตามสถาปัตยกรรม AGENTS.md: `templates/` แสดงผลอย่างเดียว — **ข้อความค่า
  ทั้งหมด (input values, node voltages, หมายเหตุ β/VBE) ต้องสร้างใน `app.py`**
  ส่งเข้า template เป็น context ห้ามฝังตัวเลขผลลัพธ์ใน HTML
- UI ภาษาไทย + ศัพท์อังกฤษตามแบบเดิม (หัวการ์ดวงจรเป็นอังกฤษตามรูปในเอกสาร)

## Approach ที่เลือก

**A — วาด inline SVG ใน template (เลือก):** Jinja render ค่าจริงจาก context
ลง label ของ SVG ค่าอัปเดตทุก POST คมชัด ไม่มี dependency

ตัวที่ตัดทิ้ง:
- **B — ฝังภาพ WebP จากเอกสาร Lab:** ภาพนิ่ง แสดงค่า input ไม่ได้ — ไม่ผ่าน
  requirement หลัก
- **C — ไลบรารี `schemdraw` ฝั่ง backend:** dependency เพิ่ม ซับซ้อนเกิน
  วงจรเดียวที่ topology ตายตัว
- **D — เลย์เอาต์ 3 คอลัมน์ตามรูปในเอกสาร:** ผู้ใช้เลือกคงแถวเดียวแล้ว

## Design

### สไตล์วงจร (ตามรูปในเอกสาร Lab — mockup v2 ที่ผู้ใช้เห็นแล้ว)

- viewBox ~`0 0 520 412` · เส้นลวงดำ `#1b2733` หนา 2 (base bar หนากว่า)
- **ตัวต้านทานหยักซิกแซก:** polyline 6 ช่วงทแยง (ครึ่ง-เต็ม-เต็ม-เต็ม-ครึ่ง)
  amplitude ±9 px, ความยาวตัว R ~48 px
- **Transistor:** วงกลม r=48 รอบ base bar + ขา C/E เฉียง, ลูกศร emitter
  ชี้ออก (มาตรฐาน NPN), ป้าย "Q1" เหนือวงกลม
- **Ground symbol มาตรฐาน** (ขีด 3 ขั้น) แยกใต้ R2 และใต้ RE — ไม่มีรางล่าง
- **Label ดำ:** ชื่ออุปกรณ์ (R1, RC ฯลฯ) ตัวหนา 14px · ค่า input ปกติ 13px
  · แรงดันโหนด VB/VE/VC ตัวหนา 14px · VBE note สีเทา `--muted` 12px
- **หัวการ์ด:** ไอคอน SVG หยักสีเขียว `--teal` (24×14, decorative) +
  "Circuit: Common-Emitter Amplifier" สี `--blue` ตามหัวการ์ดอื่นของเว็บ
- การ์ดวงจรวางระหว่างกล่อง warnings กับ results card (แถวเดียวตามเดิม)

### กติกาการแสดงค่า (decision table)

| สถานะหน้า | ค่า input บนตัว R / VCC | NPN (β) / VBE note | VB/VE/VC |
|---|---|---|---|
| GET / (ฟอร์มว่าง) | แสดงแค่ชื่อ R1, R2, ... ไม่มีค่า | "NPN" เฉย ๆ ไม่มีค่า | ไม่แสดง |
| POST ฟิลด์นั้น valid | แสดงค่าตามที่พิมพ์ (เช่น "100 kΩ") | แสดงค่า β/VBE | — |
| POST มีฟิลด์ invalid | ฟิลด์นั้น**ไม่ echo** ค่า (เช่น "abc") เหลือแค่ชื่อ | ตาม valid | ไม่แสดง |
| POST คำนวณสำเร็จ | แสดงครบ | แสดงครบ | **แสดง** `%.3f V` |

หมายเหตุ format: R แสดงเป็น kΩ ตามที่ผู้ใช้พิมพ์ในฟอร์ม (เช่น "100" → "100 kΩ"),
VCC/β/VBE แสดงตามที่พิมพ์ (ตัวเลขเดิม ไม่จัดทศนิยมใหม่)

### การ implement

1. `app.py`: เพิ่ม `build_circuit_labels(form, results)` → dict ของสตริง label
   พร้อมหน่วย (`"100 kΩ"`, `"12 V"`, `"NPN (β = 100)"`, `"VBE = 0.70 V"`,
   `"VB = 1.942 V"` หรือ `None`) — เรียกใช้ทั้ง `index()` และ `calculate()`
   ส่งเป็น context `circuit`
2. `templates/circuit.html` (include ใหม่): SVG วงจรสไตล์ mockup v2 + label
   จาก `circuit` — เรียกด้วย `{% include 'circuit.html' %}` วางระหว่าง warnings
   และ results card
3. `static/style.css`: `.circuit-card` — จัดกลาง, svg responsive (max-width)
4. `tests/test_web.py`: +4 tests (ด้านล่าง)
5. `README.md` + `docs/validation.md`: อัปเดตโครงสร้าง/ผลตรวจ

### Tests (TDD — เขียนก่อนแล้วรันให้ fail)

1. `test_get_index_shows_circuit`: GET / → มี `<svg` + หัวการ์ด "Circuit:
   Common-Emitter Amplifier", **ไม่มี** "VB =" (ยังไม่คำนวณ)
2. `test_post_valid_circuit_labels`: POST ชุดอ้างอิง → มี "100 kΩ", "2.2 kΩ",
   "VB = 1.942 V", "VE = 1.242 V", "VC = 9.294 V"
3. `test_post_invalid_field_not_echoed`: POST r1="abc" → **ไม่มี** "abc"
   ในหน้า (ค่า invalid ไม่ขึ้นบนวงจร) แต่ "22 kΩ" (R2 valid) ยังแสดง
4. `test_post_cutoff_shows_input_values`: POST แบบ cutoff (r2="1") →
   ค่า input ยังแสดงบนวงจรแม้ผลออกนอก region (VB/VE/VC แสดงตามผลคำนวณ)

Suite รวม: 19 → **23 tests**

## What's left to the builder

- พิกัดจริงของ SVG (ยึดตาม mockup v2 ที่ตรวจแล้ว) และการวาง label ไม่ทับกัน
- ลูกศร emitter ใช้ SVG marker (เหมือน mockup)
- สี: เส้นดำ `#1b2733` · หัวการ์ด `--blue` · ไอคอน/VBE note `--teal`/`--muted`

## ขั้นตอนถัดไป

อนุมัติ → `superpowers:writing-plans` → ลงมือแบบ Native execution + TDD
(คุณ commit ผ่าน GitHub Desktop เหมือนเดิม)
