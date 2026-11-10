import unittest

from app import app

VALID = {"vcc": "12", "r1": "100", "r2": "22", "rc": "2.2", "re": "1",
         "beta": "100", "vbe": "0.70"}


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_index(self):
        rv = self.client.get("/")
        self.assertEqual(rv.status_code, 200)
        html = rv.get_data(as_text=True)
        self.assertIn("Calculate DC Bias", html)
        self.assertIn('name="vcc"', html)
        self.assertIn('name="beta"', html)

    def test_post_valid_reference(self):
        rv = self.client.post("/calculate", data=VALID)
        self.assertEqual(rv.status_code, 200)
        html = rv.get_data(as_text=True)
        self.assertIn("8.052 V", html)
        self.assertIn("1.230 mA", html)
        self.assertIn("12.299 µA", html)
        self.assertNotIn("Cutoff", html)
        self.assertNotIn("Saturation", html)

    def test_post_non_numeric(self):
        rv = self.client.post("/calculate", data={**VALID, "r1": "abc"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("R1 ต้องกรอกเป็นตัวเลข", rv.get_data(as_text=True))

    def test_post_bad_decimal(self):
        rv = self.client.post("/calculate", data={**VALID, "r2": "2,2"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("R2 ต้องกรอกเป็นตัวเลข", rv.get_data(as_text=True))

    def test_post_missing_fields(self):
        rv = self.client.post("/calculate", data={"vcc": "12"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("R1 ต้องกรอกเป็นตัวเลข", rv.get_data(as_text=True))

    def test_post_negative_resistor(self):
        rv = self.client.post("/calculate", data={**VALID, "re": "-1"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("RE ต้องมากกว่า 0", rv.get_data(as_text=True))

    def test_post_cutoff_warning_shown(self):
        rv = self.client.post("/calculate", data={**VALID, "r2": "1"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("Cutoff", rv.get_data(as_text=True))

    def test_post_saturation_warning_shown(self):
        rv = self.client.post("/calculate",
                             data={"vcc": "2", "r1": "10", "r2": "10",
                                   "rc": "0.39", "re": "0.01",
                                   "beta": "100", "vbe": "0.7"})
        self.assertEqual(rv.status_code, 200)
        self.assertIn("Saturation", rv.get_data(as_text=True))

    def test_post_non_finite(self):
        rv = self.client.post("/calculate", data={**VALID, "vcc": "inf"})
        self.assertEqual(rv.status_code, 200)
        html = rv.get_data(as_text=True)
        self.assertIn("VCC ต้องกรอกเป็นตัวเลข", html)
        self.assertNotIn("VCE (Collector-Emitter)", html)

    def test_get_index_shows_circuit(self):
        rv = self.client.get("/")
        self.assertEqual(rv.status_code, 200)
        html = rv.get_data(as_text=True)
        self.assertIn("Circuit: Common-Emitter Amplifier", html)
        self.assertIn("<svg", html)
        self.assertNotIn("VB =", html)
        self.assertNotIn("100 kΩ", html)

    def test_post_valid_circuit_labels(self):
        rv = self.client.post("/calculate", data=VALID)
        self.assertEqual(rv.status_code, 200)
        html = rv.get_data(as_text=True)
        self.assertIn("VCC = 12 V", html)
        self.assertIn("100 kΩ", html)
        self.assertIn("22 kΩ", html)
        self.assertIn("2.2 kΩ", html)
        self.assertIn("1 kΩ", html)
        self.assertIn("NPN (β = 100)", html)
        self.assertIn("VBE = 0.70 V", html)
        self.assertIn("VB = 1.942 V", html)
        self.assertIn("VE = 1.242 V", html)
        self.assertIn("VC = 9.294 V", html)

    def test_post_invalid_input_not_echoed_on_circuit(self):
        rv = self.client.post("/calculate", data={**VALID, "r1": "abc"})
        html = rv.get_data(as_text=True)
        self.assertNotIn("abc kΩ", html)
        self.assertIn("22 kΩ", html)
        rv = self.client.post("/calculate", data={**VALID, "re": "-1"})
        html = rv.get_data(as_text=True)
        self.assertNotIn("-1 kΩ", html)
        rv = self.client.post("/calculate", data={**VALID, "vcc": "inf"})
        html = rv.get_data(as_text=True)
        self.assertNotIn("inf V", html)

    def test_post_cutoff_shows_input_values(self):
        rv = self.client.post("/calculate", data={**VALID, "r2": "1.5"})
        self.assertEqual(rv.status_code, 200)
        html = rv.get_data(as_text=True)
        self.assertIn("Cutoff", html)
        self.assertIn("1.5 kΩ", html)
        self.assertIn("VB =", html)

    def test_get_calculate_405(self):
        rv = self.client.get("/calculate")
        self.assertEqual(rv.status_code, 405)


if __name__ == "__main__":
    unittest.main()
