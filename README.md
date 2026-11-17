# BJT DC Bias Web App

Web Application คำนวณ **DC Operating Point (Q-Point)** ของวงจรขยาย BJT
Common-Emitter (NPN) **3 โหมดไบอัส** — Voltage Divider Bias, Fixed Bias และ
Emitter Bias (single supply) — สร้างด้วย Flask (Python) สำหรับ Lab 02–03
วิชา ENG29 2121 Computer Programming for Electrical Engineers (2/2569)

## แบบจำลองและสมการ

Forward-Active Approximation (β คงที่, VBE คงที่) — NPN transistor:

**Voltage Divider Bias (Lab 02)**

```
VTH = VCC · R2 / (R1 + R2)
RTH = R1 · R2 / (R1 + R2)
IB  = (VTH − VBE) / (RTH + (β+1)·RE)
```

**Fixed Bias** — RB ต่อจาก VCC ไป Base, Emitter ลงกราวด์ตรง ๆ (VE = 0)

```
IB = (VCC − VBE) / RB
```

**Emitter Bias (single supply)**

```
IB = (VCC − VBE) / (RB + (β+1)·RE)
```

สมการร่วมของทุกโหมด:

```
IC  = β · IB
IE  = (β+1) · IB
VE  = IE · RE          (Fixed Bias: VE = 0)
VB  = VE + VBE
VC  = VCC − IC · RC
VCE = VC − VE
```

**ข้อจำกัดของแบบจำลอง:** ไม่ใช่ SPICE — กรณี Q-Point ออกนอก Forward-Active
region โปรแกรมจะแสดงคำเตือนและผลลัพธ์ไม่ควรนำไปใช้อ้างอิง

| โหมด | เกณฑ์ Cutoff | เกณฑ์ Saturation |
|---|---|---|
| Voltage Divider | `VTH ≤ VBE` | `VCE < 0.3 V` |
| Fixed / Emitter | `IB ≤ 0 A` | `VCE ≤ 0.2 V` |

## การเลือกโหมดวงจร

หน้าแรกมีแถบ **"เลือกโหมดวงจร"** — เลือกโหมดจาก dropdown แล้วกด
**เปลี่ยนโหมด** หน้าเว็บจะโหลดใหม่ (GET) และแสดงเฉพาะช่องที่โหมดนั้นใช้:

| โหมด | ฟิลด์ |
|---|---|
| Voltage Divider Bias | VCC, R1, R2, RC, RE, β, VBE |
| Fixed Bias | VCC, RB, RC, β, VBE |
| Emitter Bias (single supply) | VCC, RB, RC, RE, β, VBE |

ช่องที่ไม่ใช้ในโหมดนั้นจะไม่ถูกบังคับกรอก ผลลัพธ์และข้อผิดพลาดระบุชื่อโหมด
ที่เลือกไว้เสมอ การ์ดแผนผังวงจร SVG แสดงเฉพาะโหมด Voltage Divider

## โครงสร้างไฟล์

```
BJT DC Bias Web App/
├── app.py                  # Flask routes + เลือกโหมด + แปลงหน่วย kΩ→Ω + label วงจร
├── dc_bias.py              # engineering module 3 ฟังก์ชัน (ไม่รู้จัก HTML/HTTP)
├── templates/index.html    # ฟอร์มเลือกโหมด + ฟอร์มคำนวณ + ผลลัพธ์ (Jinja)
├── templates/circuit.html  # แผนผังวงจร SVG (Voltage Divider) + ค่า input/node voltage
├── static/style.css        # การแสดงผล
├── tests/
│   ├── test_dc_bias.py     # unit tests วิศวกรรม (9 tests)
│   └── test_web.py         # Flask test client tests (16 tests)
├── requirements.txt        # Flask
└── docs/                   # design-note, validation, reflection
```

## แผนผังวงจรบนหน้าเว็บ

การ์ด **"Circuit: Common-Emitter Amplifier"** วาดด้วย SVG แสดงวงจร
Voltage-Divider Bias พร้อม**ค่าที่กรอกกำกับบนตำแหน่งจริง** (R1, R2, RC,
RE เป็น kΩ · VCC เป็น V · β/VBE ข้าง transistor) — ค่าอัปเดตทุกครั้งที่กด
Calculate เมื่อคำนวณสำเร็จจะแสดง**แรงดันโหนด** VB, VE, VC (ตัวหนา) ที่ขา
transistor ด้วย ฟิลด์ที่กรอกไม่ถูกต้อง (ไม่ใช่ตัวเลข, inf, ค่าติดลบ) จะ
แสดงแค่ชื่ออุปกรณ์ ไม่ echo ค่านั้นขึ้นรูป — โหมด Fixed/Emitter ไม่มีการ์ดนี้

## การติดตั้งและรัน

**สิ่งที่ต้องมี:** Python 3.10+ (บนเครื่องนี้ใช้ `py` launcher — ถ้าเครื่องคุณ
พิมพ์ `python` ได้ก็ใช้ `python` แทนได้ทุกคำสั่ง)

```powershell
# 1) สร้าง virtual environment (ครั้งแรกครั้งเดียว)
py -m venv .venv

# 2) เปิดใช้งาน venv
#    PowerShell:
.venv\Scripts\Activate.ps1
#    cmd:
.venv\Scripts\activate

# 3) ติดตั้ง dependencies
pip install -r requirements.txt

# 4) รันเว็บ (developer mode)
flask --app app run --debug
```

แล้วเปิด Browser ไปที่ **http://127.0.0.1:5000/**

> หมายเหตุ: ต้องเปิดผ่าน Flask server เท่านั้น ไม่ใช่การ double-click เปิด
> `templates/index.html` ตรง ๆ เพราะการคำนวณเกิดที่ Python Backend

## การรัน Tests

```powershell
# จาก root ของ repo (ใน venv ที่ activate แล้ว)
python -m unittest discover -s tests -v
```

ผลที่คาดหวัง: **25 tests OK** (9 engineering + 16 web)

> ตามใบงาน Lab 03 ไม่มีการเพิ่ม unittest หรือสคริปต์ Playwright —
> โหมดใหม่ตรวจรับผ่าน browser (ดู `docs/validation.md`)

## ชุดข้อมูลทดลอง

ค่ากลาง: VCC = 12 V · RC = 2.2 kΩ · β = 100 · VBE = 0.70 V

| กรณี | อินพุตเพิ่ม | IC | VCE |
|---|---|---|---|
| A1 Voltage Divider | R1=100 kΩ, R2=22 kΩ, RE=1 kΩ | 1.230 mA | 8.052 V |
| A2 Fixed Bias | RB=1000 kΩ | 1.130 mA | 9.514 V |
| A3 Emitter Bias | RB=1000 kΩ, RE=1 kΩ | 1.026 mA | 8.705 V |
| A4 Emitter Bias | RB=1000 kΩ, RE=2 kΩ | 0.940 mA | 8.033 V |

A4 มี IC ลดลงจาก A3 เพราะ `RE` ใหญ่ขึ้นทำให้ตัวหาร
`RB + (β+1)·RE` ใหญ่ขึ้น — ทุกกรณีข้างต้นอยู่ใน Active region ไม่มีคำเตือน

A5 (validation): โหมด Fixed Bias, `RB = 0` → ข้อความ `RB ต้องมากกว่า 0`
และไม่แสดงตารางผล

## การตรวจรับอินพุต

- ฟิลด์ว่าง / ไม่ใช่ตัวเลข (เช่น `abc`, `2,2`) → ข้อความ "ต้องกรอกเป็นตัวเลข"
- VCC, RB, R1, R2, RC, RE, β ≤ 0 → ข้อความ "ต้องมากกว่า 0"
- ตรวจเฉพาะฟิลด์ของโหมดที่เลือก — ช่องที่ไม่ใช้ไม่ถูกบังคับ
- ค่า `mode` ที่ไม่รู้จัก → ข้อความ `ไม่รู้จักโหมดวงจร: <mode>` (ไม่เดาเป็น Divider)
- ทุกกรณีหน้าเว็บไม่ล้ม (HTTP 200) และค่าที่กรอกไว้ยังอยู่ในฟอร์ม

## Lab 03 Submission

- Repository: https://github.com/gamewatcharin53-cyber/BJT-DC-Bias-Web-App
- Commit SHA: `<เติมหลัง commit สุดท้าย>`
- AI-assisted: (นักศึกษาเติม: ส่วนที่ AI ช่วย เช่น ร่างโค้ด/เอกสาร/ตรวจ browser)
- Student verification: (นักศึกษาเติม: สิ่งที่ตรวจด้วยตนเอง เช่น รัน tests, ตรวจ A1–A5, ตรวจสมการ)
