"""BJT Bias Circuits — DC operating point (engineering module).

รองรับ Voltage Divider, Fixed Bias และ Emitter Bias (single supply)
แบบจำลอง: Forward-Active Approximation (β คงที่, VBE คงที่)
หน่วย SI ทั้งหมด: V, Ω, A — โมดูลนี้ไม่รู้จัก HTML/HTTP
"""

import math


def solve_dc_bias(vcc, r1, r2, rc, re, beta, vbe):
    """คำนวณ DC bias ของวงจร NPN Common-Emitter แบบ Voltage-Divider Bias.

    Returns dict: {"errors": list[str], "warnings": list[str], "results": dict|None}
    """
    checks = [
        ("VCC", vcc),
        ("R1", r1),
        ("R2", r2),
        ("RC", rc),
        ("RE", re),
        ("β", beta),
    ]
    errors = [f"{name} ต้องมากกว่า 0" for name, value in checks if value <= 0]
    if errors:
        return {"errors": errors, "warnings": [], "results": None}

    v_th = vcc * r2 / (r1 + r2)
    r_th = r1 * r2 / (r1 + r2)
    ib = (v_th - vbe) / (r_th + (beta + 1) * re)
    ic = beta * ib
    ie = (beta + 1) * ib
    v_e = ie * re
    v_b = v_e + vbe
    v_c = vcc - ic * rc
    v_ce = v_c - v_e

    warnings = []
    if v_th <= vbe:
        warnings.append(
            "คำเตือน Cutoff: VTH ≤ VBE ไบอาสอยู่นอก Forward-Active region "
            "ผลลัพธ์จากแบบจำลองนี้ใช้อ้างอิงไม่ได้"
        )
    if v_ce < 0.3:
        warnings.append(
            "คำเตือน Saturation: VCE < 0.3 V ไบอาสเข้าใกล้ Saturation "
            "ผลจากแบบจำลอง Forward-Active ใช้อ้างอิงไม่ได้"
        )

    results = {
        "v_th": v_th,
        "r_th": r_th,
        "ib": ib,
        "ic": ic,
        "ie": ie,
        "v_b": v_b,
        "v_e": v_e,
        "v_c": v_c,
        "v_ce": v_ce,
    }
    return {"errors": errors, "warnings": warnings, "results": results}


def _forward_active_warnings(ib, v_ce):
    """คำเตือนเกณฑ์ร่วมสำหรับโหมด Fixed/Emitter (ไม่ใช้กับ Divider)"""
    warnings = []
    if ib <= 0:
        warnings.append(
            "คำเตือน Cutoff: IB ≤ 0 A ไบอาสอยู่นอก Forward-Active region "
            "ผลลัพธ์จากแบบจำลองนี้ใช้อ้างอิงไม่ได้"
        )
    if v_ce <= 0.2:
        warnings.append(
            "คำเตือน Saturation: VCE ≤ 0.2 V ไบอาสเข้าใกล้ Saturation "
            "ผลจากแบบจำลอง Forward-Active ใช้อ้างอิงไม่ได้"
        )
    return warnings


def _overflow_result(results):
    """คืน error dict ถ้าผลลัพธ์ใดไม่ finite (overflow จากค่าอินพุตสุดขั้ว)"""
    if all(math.isfinite(value) for value in results.values()):
        return None
    return {
        "errors": [
            "ผลลัพธ์เกินขอบเขตตัวเลข (overflow) — กรุณาลดค่า β หรือค่าอินพุต"
        ],
        "warnings": [],
        "results": None,
    }


def solve_fixed_bias(vcc, rb, rc, beta, vbe):
    """คำนวณ DC bias ของวงจร NPN แบบ Fixed Bias (RB จาก VCC ไป Base).

    Returns dict: {"errors": list[str], "warnings": list[str], "results": dict|None}
    """
    checks = [
        ("VCC", vcc),
        ("RB", rb),
        ("RC", rc),
        ("β", beta),
    ]
    errors = [f"{name} ต้องมากกว่า 0" for name, value in checks if value <= 0]
    if errors:
        return {"errors": errors, "warnings": [], "results": None}

    ib = (vcc - vbe) / rb
    ic = beta * ib
    ie = (beta + 1) * ib
    v_e = 0.0
    v_b = v_e + vbe
    v_c = vcc - ic * rc
    v_ce = v_c - v_e

    warnings = _forward_active_warnings(ib, v_ce)

    results = {
        "ib": ib,
        "ic": ic,
        "ie": ie,
        "v_b": v_b,
        "v_e": v_e,
        "v_c": v_c,
        "v_ce": v_ce,
    }
    overflow = _overflow_result(results)
    if overflow is not None:
        return overflow
    return {"errors": errors, "warnings": warnings, "results": results}


def solve_emitter_bias(vcc, rb, rc, re, beta, vbe):
    """คำนวณ DC bias ของวงจร NPN แบบ Emitter Bias (single supply).

    Returns dict: {"errors": list[str], "warnings": list[str], "results": dict|None}
    """
    checks = [
        ("VCC", vcc),
        ("RB", rb),
        ("RC", rc),
        ("RE", re),
        ("β", beta),
    ]
    errors = [f"{name} ต้องมากกว่า 0" for name, value in checks if value <= 0]
    if errors:
        return {"errors": errors, "warnings": [], "results": None}

    ib = (vcc - vbe) / (rb + (beta + 1) * re)
    ic = beta * ib
    ie = (beta + 1) * ib
    v_e = ie * re
    v_b = v_e + vbe
    v_c = vcc - ic * rc
    v_ce = v_c - v_e

    warnings = _forward_active_warnings(ib, v_ce)

    results = {
        "ib": ib,
        "ic": ic,
        "ie": ie,
        "v_b": v_b,
        "v_e": v_e,
        "v_c": v_c,
        "v_ce": v_ce,
    }
    overflow = _overflow_result(results)
    if overflow is not None:
        return overflow
    return {"errors": errors, "warnings": warnings, "results": results}
