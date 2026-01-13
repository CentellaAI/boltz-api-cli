import json
from pathlib import Path
from typing import Dict

BASE_JOBS_DIR = Path("/tmp/boltz_jobs")


def create_workspace(job_id: str) -> Dict[str, Path]:
    """
    Create filesystem workspace for a Boltz job.
    """
    job_dir = BASE_JOBS_DIR / job_id
    inputs_dir = job_dir / "inputs"
    outputs_dir = job_dir / "outputs"

    inputs_dir.mkdir(parents=True, exist_ok=False)
    outputs_dir.mkdir(parents=True, exist_ok=False)

    meta = {
        "job_id": job_id,
        "status": "CREATED",
    }

    with open(job_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    return {
        "job_dir": job_dir,
        "inputs": inputs_dir,
        "outputs": outputs_dir,
    }

