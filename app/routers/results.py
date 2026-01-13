from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

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
# JSON view (for machines / Swagger)
# -------------------------------
@router.get("/{job_id}/view")
def view_results(job_id: str):
    """
    List generated prediction files with download links (JSON).
    """
    pred_dir = get_prediction_dir(job_id)

    if not pred_dir.exists():
        raise HTTPException(status_code=404, detail="Results not found")

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

    return {
        "job_id": job_id,
        "files": files,
    }


# -------------------------------
# HTML view (for humans / browser)
# -------------------------------
@router.get("/{job_id}", response_class=HTMLResponse)
def view_results_html(job_id: str):
    """
    Human-friendly HTML page with one-click downloads.
    """
    pred_dir = get_prediction_dir(job_id)

    if not pred_dir.exists():
        return HTMLResponse(
            "<h2>Results not found</h2>",
            status_code=404,
        )

    rows = ""
    for f in pred_dir.iterdir():
        if f.suffix in (".cif", ".json", ".npz"):
            rows += f"""
            <tr>
                <td>{f.name}</td>
                <td>{f.suffix}</td>
                <td>
                    <a href="/results/{job_id}/download/{f.name}" download>
                        ⬇ Download
                    </a>
                </td>
            </tr>
            """

    html = f"""
    <html>
    <head>
        <title>Boltz Results</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #f9f9f9;
            }}
            a {{
                text-decoration: none;
                color: #007bff;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <h2>Results for Job ID: {job_id}</h2>
        <table>
            <tr>
                <th>File</th>
                <th>Type</th>
                <th>Download</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """

    return HTMLResponse(html)


# -------------------------------
# Download endpoint (actual file)
# -------------------------------
@router.get("/{job_id}/download/{filename}")
def download_result(job_id: str, filename: str):
    """
    Download a specific result file.
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
