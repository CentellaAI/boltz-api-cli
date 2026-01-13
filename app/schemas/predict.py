from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class SequenceEntity(BaseModel):
    type: Literal["protein", "dna", "rna", "ligand"]
    id: str = Field(..., example="A")
    sequence: Optional[str] = None
    smiles: Optional[str] = None


class PredictComplexRequest(BaseModel):
    sequences: List[SequenceEntity]


class PredictComplexResponse(BaseModel):
    job_id: str
    status: str
