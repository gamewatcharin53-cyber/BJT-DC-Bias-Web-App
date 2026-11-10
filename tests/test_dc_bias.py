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
        self.assertTrue(any("saturation" in w.lower() for w in out["warnings"]))
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
