from app.analysis.protein_dna_rna import compute_groove_consistency


def test_groove_consistency():
    cif_path = (
        "/tmp/boltz_jobs/9021b9c48ad74be1b2bb560bcfd6d93c/"
        "outputs/boltz_results_input/predictions/input/input_model_0.cif"
    )

    result = compute_groove_consistency(cif_path)

    assert result is not None
