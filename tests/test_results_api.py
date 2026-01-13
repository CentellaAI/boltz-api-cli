def test_results_endpoint(client):
    response = client.get(
        "/results/a55f74b4a5fb46b7937345d604d0783f"
    )

    assert response.status_code in (200, 404)

def test_results_invalid_job(client):
    response = client.get("/results/invalid_job_id")
    assert response.status_code == 404
