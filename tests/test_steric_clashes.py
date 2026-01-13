from app.analysis.protein_ligand import compute_steric_clashes


def test_steric_clashes():
    cif_path = (
        "/tmp/boltz_jobs/4cc6fe181d664f9c8fd15670ccc3e317/"
        "outputs/boltz_results_input/predictions/input/input_model_0.cif"
    )

    result = compute_steric_clashes(cif_path)

    assert result is not None
