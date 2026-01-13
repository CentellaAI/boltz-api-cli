"""
Protein–DNA / Protein–RNA analysis metrics
"""

from Bio.PDB import MMCIFParser
import numpy as np
import math


# --- Common residue definitions ---

PROTEIN_RESIDUES = {
    "ALA","ARG","ASN","ASP","CYS","GLU","GLN","GLY","HIS",
    "ILE","LEU","LYS","MET","PHE","PRO","SER","THR","TRP",
    "TYR","VAL"
}

DNA_RNA_RESIDUES = {
    "DA","DT","DG","DC",   # DNA
    "A","U","G","C"       # RNA
}

EXCLUDED = {"HOH", "WAT", "NA", "K", "MG", "ZN", "CA"}


def load_structure(cif_path: str):
    """
    Load CIF structure safely.
    """
    parser = MMCIFParser(QUIET=True)
    return parser.get_structure("model", cif_path)

def compute_electrostatic_contact_density(
    cif_path: str,
    cutoff: float = 4.5
) -> dict:
    """
    Compute electrostatic contact density between protein and DNA/RNA.
    """
    structure = load_structure(cif_path)

    positive_residues = {"ARG", "LYS", "HIS"}
    phosphate_atoms = {"P", "OP1", "OP2", "O1P", "O2P"}

    protein_atoms = []
    nucleic_atoms = []

    # --- Separate atoms ---
    for atom in structure.get_atoms():
        res = atom.get_parent()
        resname = res.get_resname().strip()

        if resname in positive_residues:
            protein_atoms.append(atom)

        elif resname in DNA_RNA_RESIDUES:
            if atom.get_name().strip() in phosphate_atoms:
                nucleic_atoms.append(atom)

    if not protein_atoms or not nucleic_atoms:
        raise ValueError("Insufficient protein or nucleic acid atoms")

    contact_pairs = set()
    interface_residues = set()

    # --- Distance check ---
    for p in protein_atoms:
        for n in nucleic_atoms:
            dist = np.linalg.norm(p.coord - n.coord)
            if dist <= cutoff:
                contact_pairs.add((p.serial_number, n.serial_number))
                interface_residues.add(p.get_parent().get_id()[1])

    density = len(contact_pairs) / max(1, len(interface_residues))

    return {
        "charged_contacts": len(contact_pairs),
        "interface_residues": len(interface_residues),
        "electrostatic_contact_density": round(density, 3),
        "distance_cutoff_angstrom": cutoff
    }

def compute_groove_consistency(
    cif_path: str,
    cutoff: float = 5.0
) -> dict:
    """
    Measure groove consistency by evaluating spatial variance
    of protein contacts along the nucleic acid backbone.
    """
    structure = load_structure(cif_path)

    protein_atoms = []
    nucleic_atoms = []

    # --- Collect atoms ---
    for atom in structure.get_atoms():
        res = atom.get_parent()
        resname = res.get_resname().strip()

        if resname in PROTEIN_RESIDUES:
            protein_atoms.append(atom)
        elif resname in DNA_RNA_RESIDUES:
            nucleic_atoms.append(atom)

    if not protein_atoms or not nucleic_atoms:
        raise ValueError("Protein or nucleic acid atoms missing")

    contact_vectors = []

    # --- Identify contact vectors ---
    for p in protein_atoms:
        for n in nucleic_atoms:
            dist = np.linalg.norm(p.coord - n.coord)
            if dist <= cutoff:
                vec = p.coord - n.coord
                contact_vectors.append(vec)

    if len(contact_vectors) < 2:
        raise ValueError("Insufficient groove contacts detected")

    contact_vectors = np.array(contact_vectors)

    # Project along principal axis
    mean_vector = np.mean(contact_vectors, axis=0)
    deviations = np.linalg.norm(contact_vectors - mean_vector, axis=1)

    std_dev = float(np.std(deviations))

    groove_consistency_score = 1 / (1 + std_dev)

    return {
        "contact_pairs": len(contact_vectors),
        "projection_std_dev": round(std_dev, 3),
        "groove_consistency_score": round(groove_consistency_score, 3),
        "distance_cutoff_angstrom": cutoff
    }

