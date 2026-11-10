"""Flask application — BJT DC Bias Web App (Lab 02, ENG29 2121).

app.py รับ HTTP request แปลงหน่วย (kΩ → Ω) แล้วเรียก dc_bias.solve_dc_bias
ซึ่งเป็น engineering module ที่ไม่รู้จัก HTML/HTTP
"""

from flask import Flask, render_template, request

import math

from dc_bias import solve_dc_bias

app = Flask(__name__)

# (name, label, unit, placeholder) — ฟอร์มรับตัวต้านทานเป็น kΩ
FIELDS = [
    ("vcc", "VCC (Supply Voltage)", "V", "12"),
    ("r1", "R1 (Upper Bias)", "kΩ", "100"),
    ("r2", "R2 (Lower Bias)", "kΩ", "22"),
    ("rc", "RC (Collector)", "kΩ", "2.2"),
    ("re", "RE (Emitter)", "kΩ", "1"),
    ("beta", "β (Current Gain)", "—", "100"),
    ("vbe", "VBE (Base-Emitter)", "V", "0.70"),
]

KOHM_FIELDS = {"r1", "r2", "rc", "re"}


def parse_form(form):
    """แปลงค่าจากฟอร์มเป็น float พร้อมหน่วย SI (ตัวต้านทาน kΩ → Ω)

    Returns (values dict สำหรับส่งเข้า solve_dc_bias, errors list)
    """
    values = {}
    errors = []
    for name, label, _unit, _placeholder in FIELDS:
        raw = (form.get(name) or "").strip()
        if not raw:
            errors.append(f"{label.split(' ')[0]} ต้องกรอกเป็นตัวเลข")
            continue
        try:
            value = float(raw)
        except ValueError:
            errors.append(f"{label.split(' ')[0]} ต้องกรอกเป็นตัวเลข")
            continue
        if not math.isfinite(value):
            errors.append(f"{label.split(' ')[0]} ต้องกรอกเป็นตัวเลข")
            continue
        if name in KOHM_FIELDS:
            value *= 1000.0
        values[name] = value
    return values, errors


def build_rows(results):
    """สร้างแถวผลลัพธ์ [{label, value}] พร้อมหน่วยจาก results ของ solve_dc_bias"""
    return [
        ("VB (Base Voltage)", "%.3f V" % results["v_b"]),
        ("VE (Emitter Voltage)", "%.3f V" % results["v_e"]),
        ("VC (Collector Voltage)", "%.3f V" % results["v_c"]),
        ("VCE (Collector-Emitter)", "%.3f V" % results["v_ce"]),
        ("IC (Collector Current)", "%.3f mA" % (results["ic"] * 1e3)),
        ("IB (Base Current)", "%.3f µA" % (results["ib"] * 1e6)),
        ("IE (Emitter Current)", "%.3f mA" % (results["ie"] * 1e3)),
        ("VTH (Thevenin Voltage)", "%.3f V" % results["v_th"]),
        ("RTH (Thevenin Resistance)", "%.3f kΩ" % (results["r_th"] / 1e3)),
    ]


def _typed_number(form, name, positive=False):
    """คืนสตริงตัวเลขตามที่ผู้ใช้พิมพ์ ถ้าผ่านเงื่อนไข — None ถ้าว่าง/ขยะ/non-finite/ติดลบ(ถ้าบังคับ)"""
    raw = (form.get(name) or "").strip()
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    if positive and value <= 0:
        return None
    return raw


def build_circuit_labels(form, results):
    """สร้าง label ค่าบนแผนผังวงจร — input ตามที่พิมพ์ + แรงดันโหนดเมื่อคำนวณแล้ว"""
    circuit = {}
    vcc = _typed_number(form, "vcc", positive=True)
    circuit["vcc"] = "%s V" % vcc if vcc is not None else None
    for name in ("r1", "r2", "rc", "re"):
        raw = _typed_number(form, name, positive=True)
        circuit[name] = "%s kΩ" % raw if raw is not None else None
    beta = _typed_number(form, "beta", positive=True)
    vbe = _typed_number(form, "vbe")
    circuit["npn"] = "NPN (β = %s)" % beta if beta is not None else "NPN"
    circuit["vbe_note"] = "VBE = %s V" % vbe if vbe is not None else None
    if results is not None:
        circuit["v_b"] = "VB = %.3f V" % results["v_b"]
        circuit["v_e"] = "VE = %.3f V" % results["v_e"]
        circuit["v_c"] = "VC = %.3f V" % results["v_c"]
    else:
        circuit["v_b"] = circuit["v_e"] = circuit["v_c"] = None
    return circuit


def _form_context(form=None):
    """context ร่วมสำหรับ index.html — form เป็น dict[str, str] 7 คีย์"""
    if form is None:
        return {name: "" for name, _l, _u, _p in FIELDS}
    return {name: form.get(name, "") for name, _l, _u, _p in FIELDS}


@app.route("/")
def index():
    return render_template(
        "index.html",
        fields=FIELDS,
        form=_form_context(),
        circuit=build_circuit_labels({}, None),
        errors=[],
        warnings=[],
        rows=[],
    )


@app.route("/calculate", methods=["POST"])
def calculate():
    raw_form = request.form.to_dict()
    values, parse_errors = parse_form(raw_form)

    errors = parse_errors
    warnings = []
    rows = []
    results = None

    if not errors:
        out = solve_dc_bias(**values)
        errors = out["errors"]
        warnings = out["warnings"]
        if out["results"] is not None:
            results = out["results"]
            rows = build_rows(results)

    return render_template(
        "index.html",
        fields=FIELDS,
        form=_form_context(raw_form),
        circuit=build_circuit_labels(raw_form, results),
        errors=errors,
        warnings=warnings,
        rows=rows,
    )
