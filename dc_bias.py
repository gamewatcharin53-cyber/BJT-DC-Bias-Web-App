"""BJT Common-Emitter Voltage-Divider Bias — DC operating point (engineering module).

แบบจำลอง: Forward-Active Approximation (β คงที่, VBE คงที่)
หน่วย SI ทั้งหมด: V, Ω, A — โมดูลนี้ไม่รู้จัก HTML/HTTP
"""


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
