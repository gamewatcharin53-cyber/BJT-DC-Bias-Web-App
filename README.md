# BJT DC Bias Web App

Web Application คำนวณ **DC Operating Point (Q-Point)** ของวงจรขยาย BJT
Common-Emitter แบบ **Voltage-Divider Bias** — สร้างด้วย Flask (Python) สำหรับ
Lab 02 วิชา ENG29 2121 Computer Programming for Electrical Engineers (2/2569)

## แบบจำลองและสมการ

Forward-Active Approximation (β คงที่, VBE คงที่) — NPN transistor:

```
VTH = VCC · R2 / (R1 + R2)
RTH = R1 · R2 / (R1 + R2)
IB  = (VTH − VBE) / (RTH + (β+1)·RE)
IC  = β · IB
IE  = (β+1) · IB
VE  = IE · RE
VB  = VE + VBE
VC  = VCC − IC · RC
VCE = VC − VE
```

**ข้อจำกัดของแบบจำลอง:** ไม่ใช่ SPICE — กรณี Q-Point ออกนอก Forward-Active
region (Cutoff: VTH ≤ VBE, Saturation: VCE < 0.3 V) โปรแกรมจะแสดงคำเตือนและ
ผลลัพธ์ไม่ควรนำไปใช้อ้างอิง

## โครงสร้างไฟล์

```
BJT DC Bias Web App/
├── app.py                  # Flask routes + แปลงหน่วย kΩ→Ω
├── dc_bias.py              # engineering module (ไม่รู้จัก HTML/HTTP)
├── templates/index.html    # ฟอร์ม + ผลลัพธ์ (Jinja)
├── static/style.css        # การแสดงผล
├── tests/
│   ├── test_dc_bias.py     # unit tests วิศวกรรม (9 tests)
│   └── test_web.py         # Flask test client tests (9 tests)
├── requirements.txt        # Flask
└── docs/                   # design-note, validation, reflection
```

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

ผลที่คาดหวัง: **18 tests OK** (9 engineering + 9 web)

## ชุดข้อมูลทดลอง

VCC = 12 V · R1 = 100 kΩ · R2 = 22 kΩ · RC = 2.2 kΩ · RE = 1 kΩ · β = 100 ·
VBE = 0.70 V

ผลที่ควรเห็นบนหน้าเว็บ:

| ปริมาณ | ค่า |
|---|---|
| VB | 1.942 V |
| VE | 1.242 V |
| VC | 9.294 V |
| VCE | 8.052 V |
| IC | 1.230 mA |
| IB | 12.299 µA |
| IE | 1.242 mA |
| VTH | 2.164 V |
| RTH | 18.033 kΩ |

(Active region — ไม่มีคำเตือน)

## การตรวจรับอินพุต

- ฟิลด์ว่าง / ไม่ใช่ตัวเลข (เช่น `abc`, `2,2`) → ข้อความ "ต้องกรอกเป็นตัวเลข"
- R1, R2, RC, RE, β, VCC ≤ 0 → ข้อความ "ต้องมากกว่า 0"
- ทุกกรณีหน้าเว็บไม่ล้ม (HTTP 200) และค่าที่กรอกไว้ยังอยู่ในฟอร์ม
