from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.analysis.protein_ligand import (
    detect_prediction_type,
    compute_ligand_burial_percent,
    compute_pocket_consistency,
    compute_steric_clashes,
)

from app.analysis.protein_protein import (
    compute_buried_surface_area,
    compute_contact_residue_overlap,
)

from app.analysis.protein_dna_rna import (
    compute_electrostatic_contact_density,
    compute_groove_consistency,
)

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"]
)

BASE_JOBS_DIR = Path("/tmp/boltz_jobs")


def get_cif_path(job_id: str) -> Path:
    cif_path = (
        BASE_JOBS_DIR
        / job_id
        / "outputs"
        / "boltz_results_input"
        / "predictions"
        / "input"
        / "input_model_0.cif"
    )

    if not cif_path.exists():
        raise FileNotFoundError(f"CIF file not found for job_id: {job_id}")

    return cif_path


def get_pae_path(job_id: str) -> Path:
    pae_path = (
        BASE_JOBS_DIR
        / job_id
        / "outputs"
        / "boltz_results_input"
        / "predictions"
        / "input"
        / "pae_input_model_0.npz"
    )

    if not pae_path.exists():
        raise FileNotFoundError("PAE file not found")

    return pae_path


@router.post("/{job_id}")
def analyze_job(job_id: str):
    """
    Unified analysis endpoint.
    """
    try:
        cif_path = get_cif_path(job_id)
        prediction_type = detect_prediction_type(str(cif_path))

        # -------------------------
        # Protein–Ligand
        # -------------------------
        if prediction_type == "protein_ligand":
            burial = compute_ligand_burial_percent(str(cif_path))
            pocket = compute_pocket_consistency(
                str(cif_path),
                str(get_pae_path(job_id))
            )
            clashes = compute_steric_clashes(str(cif_path))

            return {
                "job_id": job_id,
                "prediction_type": "protein_ligand",
                "protein_ligand_metrics": {
                    "ligand_burial_percentage": {
                        "value": burial["ligand_burial_percent"],
                        "units": "percent",
                        "details": {
                            "sasa_free_ligand": burial["sasa_free_ligand"],
                            "sasa_bound_ligand": burial["sasa_bound_ligand"]
                        }
                    },
                    "pocket_consistency": pocket,
                    "steric_clashes": clashes
                }
            }

        # -------------------------
        # Protein–Protein
        # -------------------------
        elif prediction_type == "protein_protein":
            bsa = compute_buried_surface_area(str(cif_path))
            contacts = compute_contact_residue_overlap(str(cif_path))

            return {
                "job_id": job_id,
                "prediction_type": "protein_protein",
                "protein_protein_metrics": {
                    "buried_surface_area": {
                        "value": bsa["buried_surface_area"],
                        "units": "Å²",
                        "details": {
                            "chain_A": bsa["chain_A"],
                            "chain_B": bsa["chain_B"],
                            "sasa_chain_A": bsa["sasa_chain_A"],
                            "sasa_chain_B": bsa["sasa_chain_B"],
                            "sasa_complex": bsa["sasa_complex"]
                        }
                    },
                    "contact_residue_overlap": {
                        "chain_A_contact_residues": contacts["chain_A_contact_residues"],
                        "chain_B_contact_residues": contacts["chain_B_contact_residues"],
                        "shared_interface_contacts": contacts["shared_interface_contacts"],
                        "contact_cutoff_angstrom": contacts["contact_cutoff_angstrom"]
                    }
                }
            }

        # -------------------------
        # Protein–DNA / RNA
        # -------------------------
        elif prediction_type == "protein_dna_rna":
            electro = compute_electrostatic_contact_density(str(cif_path))
            groove = compute_groove_consistency(str(cif_path))

            return {
                "job_id": job_id,
                "prediction_type": "protein_dna_rna",
                "protein_dna_rna_metrics": {
                    "electrostatic_contact_density": electro,
                    "groove_consistency": groove
                }
            }

        # -------------------------
        # Protein-only
        # -------------------------
        else:
            return {
                "job_id": job_id,
                "prediction_type": prediction_type,
                "message": "No analysis metrics implemented for this prediction type."
            }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
