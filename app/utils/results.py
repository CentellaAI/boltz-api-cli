from pathlib import Path

BASE_JOBS_DIR = Path("/tmp/boltz_jobs")


def collect_prediction_outputs(job_id: str):
    """
    Collect prediction output files and return metadata.
    """
    pred_dir = (
        BASE_JOBS_DIR
        / job_id
        / "outputs"
        / "boltz_results_input"
        / "predictions"
        / "input"
    )

    if not pred_dir.exists():
        return []

    files = []
    for f in pred_dir.iterdir():
        if f.suffix in (".cif", ".json", ".npz"):
            files.append(
                {
                    "name": f.name,
                    "type": f.suffix.replace(".", ""),
                    "download_url": f"/results/{job_id}/download/{f.name}",
                }
            )

    return files
