import re
from rdkit import Chem


def validate_protein_sequence(sequence: str) -> str:
    """
    Validate protein sequence (single-letter amino acids).
    """
    seq = sequence.strip().upper()

    if not seq:
        raise ValueError("Protein sequence is empty")

    if not re.fullmatch(r"[ACDEFGHIKLMNPQRSTVWY]+", seq):
        raise ValueError("Protein sequence contains invalid characters")

    return seq


def validate_smiles(smiles: str) -> str:
    """
    Validate ligand SMILES string.
    """
    smi = smiles.strip()

    if not smi:
        raise ValueError("SMILES string is empty")

    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        raise ValueError("Invalid SMILES string")

    return smi

