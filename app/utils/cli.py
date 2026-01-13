import subprocess
from pathlib import Path


def run_boltz_cli(input_yaml: Path, output_dir: Path):
    """
    Run Boltz CLI prediction using inline YAML.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "boltz",
        "predict",
        str(input_yaml),
        "--use_msa_server",
        "--out_dir",
        str(output_dir),
    ]

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if process.returncode != 0:
        raise RuntimeError(
            f"Boltz CLI failed:\nSTDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
        )

    return output_dir
