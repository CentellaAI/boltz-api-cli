import uuid
from fastapi import APIRouter, HTTPException

from app.schemas.predict import (
    PredictComplexRequest,
    PredictComplexResponse,
)
from app.utils.workspace import create_workspace
from app.utils.yaml_input import write_boltz_input_yaml
from app.utils.cli import run_boltz_cli
from app.utils.results import collect_prediction_outputs

router = APIRouter()


@router.post(
    "/predict",
    summary="Run Boltz prediction end-to-end (sync)",
)
def predict_complex(request: PredictComplexRequest):
    """
    Prepare + run a Boltz job in one call.

    Supports:
    - protein
    - protein–protein
    - protein–ligand
    - protein–DNA/RNA

    This endpoint:
    1) creates job
    2) writes input.yaml
    3) runs boltz predict (blocking)
    4) returns results
    """

    try:
        # 1️⃣ Generate job_id
        job_id = uuid.uuid4().hex

        # 2️⃣ Create workspace
        workspace = create_workspace(job_id)

        # 3️⃣ Write INLINE YAML using unified sequences
        yaml_path = workspace["inputs"] / "input.yaml"

        write_boltz_input_yaml(
            yaml_path=yaml_path,
            sequences=request.sequences,
        )

        # 4️⃣ Run Boltz CLI inference (BLOCKING)
        run_boltz_cli(
            input_yaml=yaml_path,
            output_dir=workspace["outputs"],
        )

        # 5️⃣ Collect outputs
        outputs = collect_prediction_outputs(job_id)

        return {
            "job_id": job_id,
            "status": "COMPLETED",
            "results": outputs,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {e}",
        )