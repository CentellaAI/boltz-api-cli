from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.utils.cli import run_boltz_cli
from app.utils.results import collect_prediction_outputs

BASE_JOBS_DIR = Path("/tmp/boltz_jobs")

router = APIRouter(prefix="/infer", tags=["infer"])


@router.post("/{job_id}")
def run_inference(job_id: str):
    """
    Run Boltz CLI inference and return results immediately.
    """

    job_dir = BASE_JOBS_DIR / job_id
    input_yaml = job_dir / "inputs" / "input.yaml"
    output_dir = job_dir / "outputs"

    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")

    if not input_yaml.exists():
        raise HTTPException(status_code=400, detail="input.yaml not found")

    try:
        # Run CLI inference
        run_boltz_cli(input_yaml=input_yaml, output_dir=output_dir)

        # Collect results
        outputs = collect_prediction_outputs(job_id)

        return {
            "job_id": job_id,
            "status": "COMPLETED",
            "results": outputs,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
