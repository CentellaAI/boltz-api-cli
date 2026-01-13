from app.analysis.protein_dna_rna import compute_electrostatic_contact_density


def test_electrostatic_contact_density():
    cif_path = (
        "/tmp/boltz_jobs/9021b9c48ad74be1b2bb560bcfd6d93c/"
        "outputs/boltz_results_input/predictions/input/input_model_0.cif"
    )

    result = compute_electrostatic_contact_density(cif_path)

    assert result is not None
