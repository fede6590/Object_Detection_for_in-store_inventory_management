import unittest

import ml_service


class TestMLService(unittest.TestCase):
    def test_predict(self):
        ml_service.settings.UPLOAD_FOLDER = "tests"
        class_name, pred_probability = ml_service.predict("dog.jpeg")
        self.assertEqual(class_name, "Eskimo_dog")
        self.assertAlmostEqual(pred_probability, 0.9346, 5)


if __name__ == "__main__":
    unittest.main()
