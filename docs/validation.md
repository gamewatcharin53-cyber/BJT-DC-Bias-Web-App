# Validation — BJT DC Bias Web App (Lab 02–03)

วันที่ตรวจ: 10 พฤศจิกายน 2026 (Lab 02) · 17 พฤศจิกายน 2026 (Lab 03)
ตรวจบนเครื่อง Windows + Python 3.15.2 (`py`)

> หมายเหตุเรื่องรหัส: `Lab 02 · เกณฑ์ A1–A7` คือ **เกณฑ์ตรวจรับ** ของ Lab 02
> ส่วน `Lab 03 · กรณีตรวจ A1–A5` คือ **กรณีทดสอบ** ตามใบงาน Lab 03 —
> เป็นคนละ rubric จึงแยกหัวข้อไว้

## Lab 02 · เกณฑ์ A1–A7

### 1. เทียบผลเว็บกับการคำนวณอิสระ (เกณฑ์ A3)

อินพุต: VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V

| ปริมาณ | คำนวณอิสระ (สมการแบบจำลองเดียวกัน) | แสดงบนหน้าเว็บ | ผล |
|---|---|---|---|
| VTH | 2.163934 V | 2.164 V | ✓ |
| RTH | 18.032787 kΩ | 18.033 kΩ | ✓ |
| IB | 12.298581 µA | 12.299 µA | ✓ |
| IC | 1.229858 mA | 1.230 mA | ✓ |
| IE | 1.242157 mA | 1.242 mA | ✓ |
| VE | 1.242157 V | 1.242 V | ✓ |
| VB | 1.942157 V | 1.942 V | ✓ |
| VC | 9.294312 V | 9.294 V | ✓ |
| VCE | 8.052155 V | 8.052 V | ✓ |

VCE = 8.052 V > 0.3 V และ VTH > VBE → **Active region** ไม่มีคำเตือน ✓

### 2. Automated Tests (เกณฑ์ A6)

คำสั่ง: `python -m unittest discover -s tests -v` (จาก root ของ repo, ใน venv)

ผล: **Ran 25 tests — OK**

- `tests/test_dc_bias.py` — 9 tests วิศวกรรม: ค่าอ้างอิง, validation (R1=0,
  β=0, VCC ติดลบ), Cutoff warning, Saturation warning, ขอบเขต VTH=VBE,
  ค่าสุดขั้ว (β=10¹², VBE ติดลบ)
- `tests/test_web.py` — 16 tests ผ่าน Flask test client: GET / (200 + ฟอร์ม),
  POST ค่าถูกต้อง, กรอกไม่ใช่ตัวเลข (`abc`, `2,2`), ฟิลด์ขาด, R ติดลบ,
  ค่าไม่จำกัด (`inf`), คำเตือน Cutoff/Saturation แสดงบนหน้าเว็บ,
  GET /calculate → 405, และแผนผังวงจร (GET / ยังไม่มีค่า, POST valid
  ค่า input + VB/VE/VC ขึ้นบนรูป, ค่า invalid ไม่ถูก echo — รวม `nan`,
  VBE/β ไม่ถูกต้อง → แสดงแค่ "NPN" ไม่มีหมายเหตุ VBE, Cutoff/Saturation
  ยังแสดงค่า input และแรงดันโหนด, ค่า overflow `2e305` kΩ ถูกปฏิเสธ
  ไม่แสดง `nan` ทั้งตารางและรูป)

### 3. ตรวจ HTTP จริงผ่าน Flask Server (เกณฑ์ A1, A2, A4, A5)

รัน: `flask --app app run --port 5001` → `http://127.0.0.1:5001/`

| เกณฑ์ | การทดสอบ | ผล |
|---|---|---|
| A1 · GET / | เปิดหน้าแรก | HTTP 200 + ฟอร์มครบ 7 ช่อง + ปุ่ม Calculate DC Bias ✓ |
| A2 · POST /calculate | กรอกชุดข้อมูลอ้างอิง | HTTP 200 + ค่า VCE=8.052 V, IC=1.230 mA จาก backend จริง ✓ |
| A4 · Validation | กรอก R1 = "abc" | HTTP 200 + ข้อความ "R1 ต้องกรอกเป็นตัวเลข" หน้าไม่ล้ม ✓ |
| A4 · Non-finite | กรอก VCC = "inf" | HTTP 200 + ข้อความ "VCC ต้องกรอกเป็นตัวเลข" ไม่แสดงตารางผล ✓ |
| วงจร · GET / | เปิดหน้าแรก | HTTP 200 + การ์ด "Circuit: Common-Emitter Amplifier" โครงวงจรไม่มีค่า ✓ |
| วงจร · POST valid | กรอกชุดข้อมูลอ้างอิง | HTTP 200 + "VCC = 12 V", "100 kΩ", "VB = 1.942 V" บนรูป ✓ |
| วงจร · POST invalid | กรอก R1 = "abc" | HTTP 200 + ไม่มี "abc kΩ" บนรูป แต่ "22 kΩ" ยังแสดง ✓ |
| A5 · Region warning | วงจร saturation (VCC=2 V, RC=390 Ω, RE=10 Ω) | HTTP 200 + คำเตือน Saturation ✓ |

### 4. Reproducibility (เกณฑ์ A7)

ลบ `.venv` ทั้งโฟลเดอร์ → สร้างใหม่ด้วย `py -m venv .venv` →
`pip install -r requirements.txt` → รัน tests → **25 tests OK**
(ตามขั้นตอนใน README จากไฟล์ว่าง)

### 5. ข้อจำกัดของแบบจำลอง

- Forward-Active Approximation (β และ VBE คงที่) — **ไม่ใช่ SPICE/ngspice**
- กรณี Cutoff (VTH ≤ VBE) หรือ Saturation (VCE < 0.3 V): โปรแกรมยังแสดงค่า
 ที่คำนวณได้ พร้อมคำเตือนว่าผลลัพธ์ใช้อ้างอิงไม่ได้ — ตามเกณฑ์ A5
- เกณฑ์ VCE(sat) = 0.3 V เป็นค่าทั่วไปของ BJT (โจทย์ไม่ได้กำหนดตัวเลข)
- Flask dev server สำหรับพัฒนา/สาธิตเฉพาะ localhost เท่านั้น

---

## Lab 03 · กรณีตรวจ A1–A5

วันที่ตรวจ: 17 พฤศจิกายน 2026 · ตรวจผ่าน **OpenCode Browser** บน
`http://127.0.0.1:5000/` (Flask dev server)

### 1. ตารางตรวจรับ

ค่ากลาง: VCC = 12 V · RC = 2.2 kΩ · β = 100 · VBE = 0.70 V ·
tolerance IC ±0.01 mA · VCE ±0.02 V (เทียบค่าอิสระที่ยังไม่ปัด)

| กรณี | อินพุตเพิ่ม | ค่าคาดหมาย (ไม่ปัด) | ค่าที่เห็นจริงบนหน้าเว็บ | วิธีตรวจ | สถานะ |
|---|---|---|---|---|---|
| A1 · Voltage Divider (เดิม) | R1=100 kΩ, R2=22 kΩ, RE=1 kΩ | IB 12.298581 µA · IC 1.229858 mA · VCE 8.052155 V | IC 1.230 mA · VCE 8.052 V · IB 12.299 µA · VTH 2.164 V · RTH 18.033 kΩ | เปิด `/`, กรอกฟอร์ม Divider, Calculate | ✓ |
| A2 · Fixed Bias | RB=1000 kΩ | IB 11.300000 µA · IC 1.130000 mA · VCE 9.514000 V | IB 11.300 µA · IC 1.130 mA · VCE 9.514 V · VB 0.700 V · VE 0.000 V · VC 9.514 V | เลือกโหมด Fixed, ตรวจว่ามี RB แต่ไม่มี R1/R2/RE, Calculate | ✓ |
| A3 · Emitter Bias | RB=1000 kΩ, RE=1 kΩ | IB 10.263397 µA · IC 1.026340 mA · VCE 8.705450 V | IB 10.263 µA · IC 1.026 mA · VCE 8.705 V · VB 1.737 V · VE 1.037 V · VC 9.742 V | เลือกโหมด Emitter, Calculate | ✓ |
| A4 · Emitter Bias (RE เพิ่ม) | RB=1000 kΩ, RE=2 kΩ | IB 9.401000 µA · IC 0.940100 mA · VCE 8.032779 V | IB 9.401 µA · IC 0.940 mA · VCE 8.033 V · VB 2.599 V · VE 1.899 V · VC 9.932 V | เปลี่ยน RE=2 แล้ว Calculate — IC ลดลงจาก A3 ✓ | ✓ |
| A5 · Validation RB=0 | Fixed Bias, RB=0 | error `RB ต้องมากกว่า 0`, ไม่มีผลลัพธ์ | HTTP 200 · `พบข้อผิดพลาด (Fixed Bias): RB ต้องมากกว่า 0` · ไม่มีตารางผล · ไม่มี `nan` | กรอก RB=0 แล้ว Calculate | ✓ |

ผลข้างเคียงที่ตรวจเพิ่ม:

- Fixed Bias ไม่กรอก R1/R2/RE → ไม่มี error ของช่องเหล่านั้น ✓
- `GET /?mode=class-a` → `ไม่รู้จักโหมดวงจร: class-a` และไม่มีฟอร์มหลัก/ตารางผล ✓
- Fixed Bias VCC=0.5 V, VBE=0.70 V → warning Cutoff (`IB ≤ 0 A`) และไม่มี `nan` ✓
- การ์ด SVG แสดงเฉพาะโหมด Voltage Divider ✓

### 2. ค่าอ้างอิงอิสระของโหมดใหม่ (ยังไม่ปัดเศษ)

**A2 Fixed Bias** — `IB = (VCC − VBE) / RB = (12 − 0.70) / 1×10⁶ =
11.300000 µA`; `IC = β·IB = 1.130000 mA`; `VC = VCC − IC·RC =
12 − 1.130000×10⁻³ × 2.2×10³ = 9.514000 V`; `VE = 0` → `VCE = 9.514000 V`

**A3 Emitter Bias** — `IB = (12 − 0.70) / (1×10⁶ + 101×1×10³) =
10.263397 µA`; `IC = 1.026340 mA`; `VE = IE·RE = 1.036603 V`;
`VC = 9.742053 V`; `VCE = 8.705450 V`

**A4 Emitter Bias (RE=2 kΩ)** — `IB = (12 − 0.70) / (1×10⁶ + 101×2×10³) =
9.401000 µA`; `IC = 0.940100 mA`; `VCE = 8.032779 V` — IC ลดลงเมื่อ RE
ใหญ่ขึ้น เพราะตัวหาร `RB + (β+1)RE` ใหญ่ขึ้น

### 3. Automated Tests

คำสั่ง: `python -m unittest discover -s tests -v` (จาก root ของ repo, ใน venv)

ผล: **Ran 25 tests — OK** (9 engineering + 16 web — ไม่เพิ่ม test ใหม่ตามใบงาน)

### 4. วิธีตรวจและเครื่องมือ

- ใช้ **OpenCode Browser** เปิดหน้าเว็บจริง: navigate → snapshot → fill →
  click → อ่านค่าจากตารางผล/บล็อก error
- **Playwright MCP = NOT RUN** — เครื่องนี้ไม่มี `node`/`npx`
  (ตรวจ `node --version` และ `npx --version` แล้วไม่พบ) จึงใช้วิธีสำรอง
  ตามที่ใบงานอนุญาต; ไม่ได้เพิ่ม `opencode.json` ในงานนี้
- หลักฐาน: ค่าที่เห็นจริงในตารางข้อ 1 ถูกอ่านจากหน้าเว็บโดยตรง (textual
  evidence); ไม่ได้แนบไฟล์ screenshot

