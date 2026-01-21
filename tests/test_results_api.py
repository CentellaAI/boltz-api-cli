from pathlib import Path


def test_results_html(client, tmp_path):
    job_id = "testjob123"

    # Create fake output structure
    pred_dir = (
        tmp_path
        / job_id
        / "outputs"
        / "boltz_results_input"
        / "predictions"
        / "input"
    )
    pred_dir.mkdir(parents=True)

    # Fake output file
    fake_file = pred_dir / "input_model_0.cif"
    fake_file.write_text("FAKE CIF CONTENT")

    # Patch BASE_JOBS_DIR
    from app.routers import results
    results.BASE_JOBS_DIR = tmp_path

    response = client.get(f"/results/{job_id}")

    assert response.status_code == 200
    assert "Boltz Prediction Results" in response.text
    assert "input_model_0.cif" in response.text
