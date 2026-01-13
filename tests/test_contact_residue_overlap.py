from app.analysis.protein_protein import compute_contact_residue_overlap


def test_contact_residue_overlap():
    cif_path = (
        "/tmp/boltz_jobs/a55f74b4a5fb46b7937345d604d0783f/"
        "outputs/boltz_results_input/predictions/input/input_model_0.cif"
    )

    result = compute_contact_residue_overlap(cif_path)

    assert result is not None
