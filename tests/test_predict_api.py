from pathlib import Path
from unittest.mock import patch


def test_predict_endpoint(client):
    with patch("app.routers.predict.create_workspace") as mock_workspace, \
         patch("app.routers.predict.write_boltz_input_yaml") as mock_yaml:

        mock_workspace.return_value = {
            "inputs": Path("/tmp/fake_inputs")
        }

        response = client.post(
            "/predict",
            json={
                "sequences": [
                    {
                        "id": "A",
                        "type": "protein",
                        "sequence": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ"
                    }
                ]
            }
        )

        assert response.status_code == 200

        data = response.json()
        assert "job_id" in data
        assert data["status"] == "READY_FOR_INFERENCE"

def test_predict_invalid_payload(client):
    response = client.post("/predict", json={})
    assert response.status_code == 422

