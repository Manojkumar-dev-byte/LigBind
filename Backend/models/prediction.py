from typing import List, Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    protein_sequence: Optional[str] = Field(None, min_length=1)
    disease_name: Optional[str] = Field(None, min_length=1)
    top_n: int = Field(default=10, ge=1, le=100)
    candidate_smiles: Optional[List[str]] = None
    export_csv: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "protein_sequence": "MKTFFVAGVILLLAALATQATADNQSVRLEERLGLIEVQANLQDKN",
                "top_n": 10
            }
        }


class RankedDrug(BaseModel):
    rank: int
    drug_index: int
    drug_name: str
    smiles: str
    predicted_affinity: float


class PredictionResponse(BaseModel):
    protein_sequence: str
    top_n: int
    total_candidates: int
    rankings: List[RankedDrug]
    top_drugs: List[RankedDrug]