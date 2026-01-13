def has_ligand(cif_path: str) -> bool:
    """
    Detect whether a CIF contains a true small-molecule ligand.
    Avoids false positives from modified residues or caps.
    """
    import freesasa
    from collections import defaultdict

    structure = freesasa.Structure(cif_path)

    protein_residues = {
        "ALA","ARG","ASN","ASP","CYS","GLU","GLN","GLY","HIS",
        "ILE","LEU","LYS","MET","PHE","PRO","SER","THR","TRP",
        "TYR","VAL"
    }

    excluded = {"HOH", "WAT", "NA", "CL", "K", "MG", "ZN", "CA"}

    residue_atom_counts = defaultdict(int)

    for i in range(structure.nAtoms()):
        resname = structure.residueName(i).strip()
        residue_atom_counts[resname] += 1

    for resname, atom_count in residue_atom_counts.items():
        if resname in protein_residues or resname in excluded:
            continue

        if atom_count >= 8:
            return True

    return False
def compute_ligand_burial_percent(cif_path: str) -> dict:
    """
    Compute ligand burial percentage using SASA difference.
    """
    import freesasa
    from collections import defaultdict

    structure = freesasa.Structure(cif_path)

    protein_residues = {
        "ALA","ARG","ASN","ASP","CYS","GLU","GLN","GLY","HIS",
        "ILE","LEU","LYS","MET","PHE","PRO","SER","THR","TRP",
        "TYR","VAL"
    }

    excluded = {"HOH", "WAT", "NA", "CL", "K", "MG", "ZN", "CA"}

    residue_atom_map = defaultdict(list)

    for i in range(structure.nAtoms()):
        resname = structure.residueName(i).strip()
        residue_atom_map[resname].append(i)

    ligand_resnames = [
        r for r, atoms in residue_atom_map.items()
        if r not in protein_residues
        and r not in excluded
        and len(atoms) >= 8
    ]

    if not ligand_resnames:
        raise ValueError("No ligand detected in CIF")

    ligand_atoms = residue_atom_map[ligand_resnames[0]]

    # --- bound SASA ---
    result_bound = freesasa.calc(structure)
    sasa_bound = sum(result_bound.atomArea(i) for i in ligand_atoms)

    # --- free ligand SASA ---
    ligand_structure = freesasa.Structure()

    for i in ligand_atoms:
        x, y, z = structure.coord(i)
        ligand_structure.addAtom(
            structure.atomName(i),
            structure.residueName(i),
            structure.chainLabel(i),
            structure.residueNumber(i),
            x, y, z
        )

    sasa_free = freesasa.calc(ligand_structure).totalArea()

    burial_percent = ((sasa_free - sasa_bound) / sasa_free) * 100

    return {
        "sasa_free_ligand": round(sasa_free, 2),
        "sasa_bound_ligand": round(sasa_bound, 2),
        "ligand_burial_percent": round(burial_percent, 2)
    }
def compute_pocket_consistency(
    cif_path: str,
    pae_path: str,
    cutoff: float = 4.5
) -> dict:
    """
    Pocket consistency based on:
    - geometric compactness (BioPython)
    - confidence from PAE
    """
    from Bio.PDB import MMCIFParser
    import numpy as np
    import math

    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure("model", cif_path)
    pae = np.load(pae_path)["pae"]

    protein_residues = {
        "ALA","ARG","ASN","ASP","CYS","GLU","GLN","GLY","HIS",
        "ILE","LEU","LYS","MET","PHE","PRO","SER","THR","TRP",
        "TYR","VAL"
    }

    excluded = {"HOH", "WAT", "NA", "K", "MG", "ZN", "CA"}

    protein_atoms = []
    ligand_atoms = []

    for atom in structure.get_atoms():
        resname = atom.get_parent().get_resname().strip()
        if resname in protein_residues:
            protein_atoms.append(atom)
        elif resname not in excluded:
            ligand_atoms.append(atom)

    if not ligand_atoms:
        raise ValueError("No ligand found")

    # --- Ligand centroid ---
    coords = [atom.coord for atom in ligand_atoms]
    ligand_center = np.mean(coords, axis=0)

    pocket_distances = []
    pocket_residue_ids = set()

    for atom in protein_atoms:
        dist = np.linalg.norm(atom.coord - ligand_center)
        if dist <= cutoff:
            pocket_distances.append(dist)
            pocket_residue_ids.add(atom.get_parent().get_id()[1])

    if not pocket_distances:
        raise ValueError("No pocket residues detected")

    mean_dist = float(np.mean(pocket_distances))
    std_dev = float(np.std(pocket_distances))

    geometric_score = 1 / (1 + std_dev)

    pae_values = []
    for r in pocket_residue_ids:
        idx = r - 1
        if 0 <= idx < pae.shape[0]:
            pae_values.append(pae[idx, idx])

    mean_pae = float(np.mean(pae_values))
    confidence_score = 1 / (1 + mean_pae)

    pocket_consistency = geometric_score * confidence_score

    return {
        "pocket_residue_count": len(pocket_residue_ids),
        "mean_distance": round(mean_dist, 2),
        "distance_std_dev": round(std_dev, 2),
        "mean_pocket_pae": round(mean_pae, 2),
        "geometric_score": round(geometric_score, 3),
        "confidence_score": round(confidence_score, 3),
        "pocket_consistency_score": round(pocket_consistency, 3)
    }
def compute_steric_clashes(
    cif_path: str,
    scale: float = 0.75
) -> dict:
    """
    Quantitative steric clash detection between protein and ligand.
    """
    from Bio.PDB import MMCIFParser
    import math

    # Van der Waals radii (Å)
    VDW = {
        "H": 1.20,
        "C": 1.70,
        "N": 1.55,
        "O": 1.52,
        "F": 1.47,
        "P": 1.80,
        "S": 1.80,
        "CL": 1.75,
        "BR": 1.85,
        "I": 1.98,
    }

    protein_residues = {
        "ALA","ARG","ASN","ASP","CYS","GLU","GLN","GLY","HIS",
        "ILE","LEU","LYS","MET","PHE","PRO","SER","THR","TRP",
        "TYR","VAL"
    }

    excluded = {"HOH", "WAT", "NA", "K", "MG", "ZN", "CA"}

    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure("model", cif_path)

    protein_atoms = []
    ligand_atoms = []

    for atom in structure.get_atoms():
        resname = atom.get_parent().get_resname().strip()

        if resname in protein_residues:
            protein_atoms.append(atom)
        elif resname not in excluded:
            ligand_atoms.append(atom)

    if not ligand_atoms:
        raise ValueError("No ligand found")

    clash_count = 0
    worst_overlap = 0.0

    for p in protein_atoms:
        pe = p.element.strip().upper()
        if pe not in VDW:
            continue

        for l in ligand_atoms:
            le = l.element.strip().upper()
            if le not in VDW:
                continue

            dx = p.coord[0] - l.coord[0]
            dy = p.coord[1] - l.coord[1]
            dz = p.coord[2] - l.coord[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)

            cutoff = scale * (VDW[pe] + VDW[le])

            if dist < cutoff:
                clash_count += 1
                overlap = cutoff - dist
                worst_overlap = max(worst_overlap, overlap)

    clash_score = min(1.0, clash_count / 20.0)

    return {
        "clash_count": clash_count,
        "worst_overlap_angstrom": round(worst_overlap, 3),
        "clash_score": round(clash_score, 3)
    }
def detect_prediction_type(cif_path: str) -> str:
    """
    Detect prediction type from CIF.
    """
    from Bio.PDB import MMCIFParser

    protein_residues = {
        "ALA","ARG","ASN","ASP","CYS","GLU","GLN","GLY","HIS",
        "ILE","LEU","LYS","MET","PHE","PRO","SER","THR","TRP",
        "TYR","VAL"
    }

    dna_rna = {"DA","DT","DG","DC","A","U","G","C"}
    excluded = {"HOH", "WAT", "NA", "K", "MG", "ZN", "CA"}

    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure("model", cif_path)

    chains = set()
    has_ligand = False
    has_nucleic = False

    for residue in structure.get_residues():
        resname = residue.get_resname().strip()
        chains.add(residue.get_parent().id)

        if resname in dna_rna:
            has_nucleic = True
        elif resname not in protein_residues and resname not in excluded:
            has_ligand = True

    if has_ligand:
        return "protein_ligand"
    if has_nucleic:
        return "protein_dna_rna"
    if len(chains) > 1:
        return "protein_protein"

    return "protein_only"
