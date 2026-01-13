def test_analysis_endpoint(client):
    response = client.post(
        "/analysis/a55f74b4a5fb46b7937345d604d0783f"
    )

    assert response.status_code == 200

def test_analysis_invalid_job(client):
    response = client.post("/analysis/invalid_job_id")
    assert response.status_code == 404

