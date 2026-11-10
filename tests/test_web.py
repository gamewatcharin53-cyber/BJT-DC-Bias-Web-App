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

    def test_get_calculate_405(self):
        rv = self.client.get("/calculate")
        self.assertEqual(rv.status_code, 405)


if __name__ == "__main__":
    unittest.main()
