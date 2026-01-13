def compute_buried_surface_area(cif_path: str) -> dict:
    """
    Compute buried surface area (BSA) for protein–protein complexes.
    BSA = SASA(chain A) + SASA(chain B) − SASA(complex)
    """
    import freesasa
    import tempfile
    import os
    from Bio.PDB import MMCIFParser, PDBIO, Select

    class ChainSelect(Select):
        def __init__(self, chain_id):
            self.chain_id = chain_id

        def accept_chain(self, chain):
            return chain.id == self.chain_id

    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure("model", cif_path)

    chains = list(structure.get_chains())
    if len(chains) < 2:
        raise ValueError("Protein–protein complex requires at least 2 chains")

    chainA_id = chains[0].id
    chainB_id = chains[1].id

    io = PDBIO()

    with tempfile.TemporaryDirectory() as tmp:
        complex_pdb = os.path.join(tmp, "complex.pdb")
        chainA_pdb = os.path.join(tmp, "chainA.pdb")
        chainB_pdb = os.path.join(tmp, "chainB.pdb")

        # Write complex
        io.set_structure(structure)
        io.save(complex_pdb)

        # Write chain A
        io.save(chainA_pdb, ChainSelect(chainA_id))

        # Write chain B
        io.save(chainB_pdb, ChainSelect(chainB_id))

        sasa_complex = freesasa.calc(freesasa.Structure(complex_pdb)).totalArea()
        sasa_A = freesasa.calc(freesasa.Structure(chainA_pdb)).totalArea()
        sasa_B = freesasa.calc(freesasa.Structure(chainB_pdb)).totalArea()

    buried_surface_area = (sasa_A + sasa_B) - sasa_complex

    return {
        "chain_A": chainA_id,
        "chain_B": chainB_id,
        "sasa_chain_A": round(sasa_A, 2),
        "sasa_chain_B": round(sasa_B, 2),
        "sasa_complex": round(sasa_complex, 2),
        "buried_surface_area": round(buried_surface_area, 2),
        "units": "Å²"
    }
def compute_contact_residue_overlap(
    cif_path: str,
    cutoff: float = 5.0
) -> dict:
    """
    Compute contact residue overlap between two protein chains.
    """
    from Bio.PDB import MMCIFParser
    import numpy as np

    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure("model", cif_path)

    chains = list(structure.get_chains())
    if len(chains) < 2:
        raise ValueError("Protein–protein interface requires at least 2 chains")

    chainA, chainB = chains[0], chains[1]

    contacts_A = set()
    contacts_B = set()
    shared_contacts = set()

    for resA in chainA:
        if not resA.has_id("CA"):
            continue

        for resB in chainB:
            if not resB.has_id("CA"):
                continue

            # Atom-level distance check
            for atomA in resA.get_atoms():
                for atomB in resB.get_atoms():
                    dist = np.linalg.norm(atomA.coord - atomB.coord)

                    if dist <= cutoff:
                        ida = (chainA.id, resA.get_id()[1])
                        idb = (chainB.id, resB.get_id()[1])

                        contacts_A.add(ida)
                        contacts_B.add(idb)
                        shared_contacts.add((ida, idb))
                        break

    return {
        "chain_A_contact_residues": len(contacts_A),
        "chain_B_contact_residues": len(contacts_B),
        "shared_interface_contacts": len(shared_contacts),
        "contact_cutoff_angstrom": cutoff
    }

