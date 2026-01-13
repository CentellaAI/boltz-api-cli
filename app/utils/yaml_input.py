import yaml
from pathlib import Path
from typing import List


def write_boltz_input_yaml(
    yaml_path: Path,
    sequences: List,
):
    """
    Write Boltz inline YAML input.
    Automatically enables affinity prediction if ligand is present.
    """

    yaml_data = {
        "version": 1,
        "sequences": [],
    }

    ligand_ids = []

    # --- sequences ---
    for entity in sequences:
        entity_type = entity.type
        entity_id = entity.id

        if entity_type == "protein":
            yaml_data["sequences"].append(
                {
                    "protein": {
                        "id": entity_id,
                        "sequence": entity.sequence,
                    }
                }
            )

        elif entity_type in ("dna", "rna"):
            yaml_data["sequences"].append(
                {
                    entity_type: {
                        "id": entity_id,
                        "sequence": entity.sequence,
                    }
                }
            )

        elif entity_type == "ligand":
            ligand_ids.append(entity_id)
            yaml_data["sequences"].append(
                {
                    "ligand": {
                        "id": entity_id,
                        "smiles": entity.smiles,
                    }
                }
            )

        else:
            raise ValueError(f"Unsupported sequence type: {entity_type}")

    # --- properties (affinity) ---
    if ligand_ids:
        yaml_data["properties"] = [
            {
                "affinity": {
                    "binder": ligand_ids[0]
                }
            }
        ]

    yaml_path.parent.mkdir(parents=True, exist_ok=True)

    with open(yaml_path, "w") as f:
        yaml.safe_dump(yaml_data, f, sort_keys=False)
