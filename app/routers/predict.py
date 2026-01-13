import uuid
from fastapi import APIRouter, HTTPException

from app.schemas.predict import (
    PredictComplexRequest,
    PredictComplexResponse,
)
from app.utils.workspace import create_workspace
from app.utils.yaml_input import write_boltz_input_yaml

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictComplexResponse,
    summary="Prepare Boltz inline prediction job",
)
def predict_complex(request: PredictComplexRequest):
    """
    Prepare a Boltz job by generating an inline YAML input.
    Supports:
    - protein
    - protein–protein
    - protein–ligand
    - protein–DNA/RNA
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

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Job preparation failed: {e}",
        )

    return PredictComplexResponse(
        job_id=job_id,
        status="READY_FOR_INFERENCE",
    )
