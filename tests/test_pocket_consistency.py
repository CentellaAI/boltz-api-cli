from app.analysis.protein_ligand import compute_pocket_consistency


def test_pocket_consistency():
    result = compute_pocket_consistency(
        cif_path=(
            "/tmp/boltz_jobs/4cc6fe181d664f9c8fd15670ccc3e317/"
            "outputs/boltz_results_input/predictions/input/input_model_0.cif"
        ),
        pae_path=(
            "/tmp/boltz_jobs/4cc6fe181d664f9c8fd15670ccc3e317/"
            "outputs/boltz_results_input/predictions/input/pae_input_model_0.npz"
        ),
    )

    assert result is not None
