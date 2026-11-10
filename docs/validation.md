# Validation — BJT DC Bias Web App (Lab 02)

วันที่ตรวจ: 10 พฤศจิกายน 2026 · ตรวจบนเครื่อง Windows + Python 3.15.2 (`py`)

## 1. เทียบผลเว็บกับการคำนวณอิสระ (เกณฑ์ A3)

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

## 2. Automated Tests (เกณฑ์ A6)

คำสั่ง: `python -m unittest discover -s tests -v` (จาก root ของ repo, ใน venv)

ผล: **Ran 19 tests — OK**

- `tests/test_dc_bias.py` — 9 tests วิศวกรรม: ค่าอ้างอิง, validation (R1=0,
  β=0, VCC ติดลบ), Cutoff warning, Saturation warning, ขอบเขต VTH=VBE,
  ค่าสุดขั้ว (β=10¹², VBE ติดลบ)
- `tests/test_web.py` — 10 tests ผ่าน Flask test client: GET / (200 + ฟอร์ม),
  POST ค่าถูกต้อง, กรอกไม่ใช่ตัวเลข (`abc`, `2,2`), ฟิลด์ขาด, R ติดลบ,
  ค่าไม่จำกัด (`inf`), คำเตือน Cutoff/Saturation แสดงบนหน้าเว็บ,
  GET /calculate → 405

## 3. ตรวจ HTTP จริงผ่าน Flask Server (เกณฑ์ A1, A2, A4, A5)

รัน: `flask --app app run --port 5001` → `http://127.0.0.1:5001/`

| เกณฑ์ | การทดสอบ | ผล |
|---|---|---|
| A1 · GET / | เปิดหน้าแรก | HTTP 200 + ฟอร์มครบ 7 ช่อง + ปุ่ม Calculate DC Bias ✓ |
| A2 · POST /calculate | กรอกชุดข้อมูลอ้างอิง | HTTP 200 + ค่า VCE=8.052 V, IC=1.230 mA จาก backend จริง ✓ |
| A4 · Validation | กรอก R1 = "abc" | HTTP 200 + ข้อความ "R1 ต้องกรอกเป็นตัวเลข" หน้าไม่ล้ม ✓ |
| A4 · Non-finite | กรอก VCC = "inf" | HTTP 200 + ข้อความ "VCC ต้องกรอกเป็นตัวเลข" ไม่แสดงตารางผล ✓ |
| A5 · Region warning | วงจร saturation (VCC=2 V, RC=390 Ω, RE=10 Ω) | HTTP 200 + คำเตือน Saturation ✓ |

## 4. Reproducibility (เกณฑ์ A7)

ลบ `.venv` ทั้งโฟลเดอร์ → สร้างใหม่ด้วย `py -m venv .venv` →
`pip install -r requirements.txt` → รัน tests → **18 tests OK**
(ตามขั้นตอนใน README จากไฟล์ว่าง)

## 5. ข้อจำกัดของแบบจำลอง

- Forward-Active Approximation (β และ VBE คงที่) — **ไม่ใช่ SPICE/ngspice**
- กรณี Cutoff (VTH ≤ VBE) หรือ Saturation (VCE < 0.3 V): โปรแกรมยังแสดงค่า
 ที่คำนวณได้ พร้อมคำเตือนว่าผลลัพธ์ใช้อ้างอิงไม่ได้ — ตามเกณฑ์ A5
- เกณฑ์ VCE(sat) = 0.3 V เป็นค่าทั่วไปของ BJT (โจทย์ไม่ได้กำหนดตัวเลข)
- Flask dev server สำหรับพัฒนา/สาธิตเฉพาะ localhost เท่านั้น
