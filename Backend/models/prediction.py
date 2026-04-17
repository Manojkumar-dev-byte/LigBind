from pydantic import BaseModel
from typing import List

class PredictionRequest(BaseModel):
    disease: str
    drugs: List[str]