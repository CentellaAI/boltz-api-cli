import time


def test_predict_protein_only(client):
    """
    Test protein structure prediction (single protein).
    """

    payload = {
        "sequences": [
            {
                "type": "protein",
                "id": "A",
                "sequence": "MKVKVGVNGFGRIGRLVTRAAFNSGKVDIVAINDPF"
            }
        ]
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    data = response.json()

    # Core contract checks
    assert "job_id" in data
    assert data["status"] == "COMPLETED"

    # Optional fields if present
    if "results" in data:
        assert isinstance(data["results"], list)


def test_predict_protein_ligand(client):
    """
    Test protein–ligand complex prediction.
    """

    payload = {
        "sequences": [
            {
                "type": "protein",
                "id": "A",
                "sequence": "HGEGTFTSDLSKQMEEEAVRLFIEWLKNGGPSSGAPPPS"
            },
            {
                "type": "ligand",
                "id": "B",
                "smiles": "c1ccncc1"
            }
        ]
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["status"] == "COMPLETED"

    if "results" in data:
        assert isinstance(data["results"], list)
