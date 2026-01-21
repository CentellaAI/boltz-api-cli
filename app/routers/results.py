from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

BASE_JOBS_DIR = Path("/tmp/boltz_jobs")

router = APIRouter(prefix="/results", tags=["results"])


def get_prediction_dir(job_id: str) -> Path:
    return (
        BASE_JOBS_DIR
        / job_id
        / "outputs"
        / "boltz_results_input"
        / "predictions"
        / "input"
    )


# -------------------------------
# HTML RESULTS PAGE (HUMANS)
# -------------------------------
@router.get("/{job_id}", response_class=HTMLResponse)
def view_results_html(job_id: str):
    """
    Human-friendly HTML results page with clickable downloads.
    """
    pred_dir = get_prediction_dir(job_id)

    if not pred_dir.exists():
        raise HTTPException(status_code=404, detail="Results not found")

    files = [
        f.name for f in pred_dir.iterdir()
        if f.suffix in (".cif", ".json", ".npz")
    ]

    html = f"""
    <html>
        <head>
            <title>Boltz Results – {job_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                ul {{ line-height: 1.8; }}
            </style>
        </head>
        <body>
            <h1>Boltz Prediction Results</h1>
            <p><b>Job ID:</b> {job_id}</p>

            <h2>Generated Files</h2>
            <ul>
                {''.join(
                    f'<li><a href="/results/{job_id}/file/{name}" download>{name}</a></li>'
                    for name in files
                )}
            </ul>

            <p><i>Click a file to download.</i></p>
        </body>
    </html>
    """

    return HTMLResponse(content=html)


# -------------------------------
# FILE SERVING (BROWSER DOWNLOAD)
# -------------------------------
@router.get("/{job_id}/file/{filename}")
def download_result_file(job_id: str, filename: str):
    """
    Serve result files for browser download.
    """
    pred_dir = get_prediction_dir(job_id)
    file_path = pred_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )
