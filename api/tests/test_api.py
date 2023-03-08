import json
from unittest import TestCase
from unittest.mock import patch

from app import app


class TestIntegration(TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_predict_bad_parameters(self):
        response = self.client.post(
            "/predict",
            data=json.dumps({"not_a_file": "blabla"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data.keys()), 3)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["prediction"], None)
        self.assertEqual(data["score"], None)

    @patch("views.model_predict")
    def test_predict_ok(self, mock):
        # Mocks
        pred_class = "Eskimo_dog"
        pred_score = 0.9346
        mock.return_value = (pred_class, pred_score)
        app.config["UPLOAD_FOLDER"] = "/tmp"

        data = {"file": (open("tests/dog.jpeg", "rb"), "dog.jpeg")}
        response = self.client.post(
            "/predict",
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data.keys()), 3)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["prediction"], pred_class)
        self.assertAlmostEqual(data["score"], pred_score, 5)

    def test_feedback(self):
        import os
        import settings

        # Check current status for feedback folder
        if os.path.exists(settings.FEEDBACK_FILEPATH):
            curr_feedback_lines = len(
                open(settings.FEEDBACK_FILEPATH).read().splitlines()
            )
        else:
            curr_feedback_lines = 0

        data = {
            "report": "{'filename': 'test', 'prediction': 'test-pred', 'score': 1. }"
        }
        response = self.client.post(
            "/feedback",
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.exists(settings.FEEDBACK_FILEPATH))

        # Check the feedback file was written
        new_feedback_lines = len(open(settings.FEEDBACK_FILEPATH).read().splitlines())
        self.assertEqual(curr_feedback_lines + 1, new_feedback_lines)

        # Check the content is correct
        new_line = open(settings.FEEDBACK_FILEPATH).read().splitlines()[-1]
        self.assertEqual(data["report"], new_line)


class TestEnpointsAvailability(TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/")
        self.assertEqual(response.status_code, 302)

    def test_feedback(self):
        response = self.client.get("/feedback")
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/feedback")
        self.assertEqual(response.status_code, 200)

    def test_predict(self):
        response = self.client.get("/predict")
        # Method not allowed
        self.assertEqual(response.status_code, 405)
        response = self.client.post("/predict")
        # Bad args
        self.assertEqual(response.status_code, 400)
