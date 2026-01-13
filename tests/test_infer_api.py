from pathlib import Path
from unittest.mock import patch


def test_infer_endpoint(client, tmp_path):
    job_id = "test_job_123"

    # Fake job directory structure
    job_dir = tmp_path / job_id
    inputs_dir = job_dir / "inputs"
    outputs_dir = job_dir / "outputs"

    inputs_dir.mkdir(parents=True)
    outputs_dir.mkdir(parents=True)

    input_yaml = inputs_dir / "input.yaml"
    input_yaml.write_text("dummy yaml")

    with patch("app.routers.infer.BASE_JOBS_DIR", tmp_path), \
         patch("app.routers.infer.run_boltz_cli") as mock_run, \
         patch("app.routers.infer.collect_prediction_outputs") as mock_collect:

        mock_collect.return_value = {"dummy": "result"}

        response = client.post(f"/infer/{job_id}")

        assert response.status_code == 200

        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == "COMPLETED"
        assert "results" in data


def test_infer_invalid_job(client):
    response = client.post("/infer/invalid_job_id")
    assert response.status_code == 404

