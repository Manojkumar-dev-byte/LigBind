from io import StringIO

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.prediction import PredictionRequest, PredictionResponse
from services.predictor import rank_protein_target
from utils.disease_mapping import resolve_disease_to_protein

router = APIRouter(prefix="/predict", tags=["Prediction"])


# Protein ranking
@router.post("/rank", response_model=PredictionResponse)
def predict(data: PredictionRequest):
    try:
        # Resolve disease to protein if disease_name is provided
        protein_sequence = data.protein_sequence
        if data.disease_name:
            protein_sequence = resolve_disease_to_protein(data.disease_name)
        elif not protein_sequence:
            raise ValueError("Either protein_sequence or disease_name must be provided")
        
        results = rank_protein_target(
            protein_sequence=protein_sequence,
            top_n=data.top_n,
            candidate_smiles=data.candidate_smiles,
        )

        return results

    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Prediction failed") from exc


@router.post("/csv")
def predict_csv(data: PredictionRequest):
    try:
        # Resolve disease to protein if disease_name is provided
        protein_sequence = data.protein_sequence
        if data.disease_name:
            protein_sequence = resolve_disease_to_protein(data.disease_name)
        elif not protein_sequence:
            raise ValueError("Either protein_sequence or disease_name must be provided")
        
        results = rank_protein_target(
            protein_sequence=protein_sequence,
            top_n=data.top_n,
            candidate_smiles=data.candidate_smiles,
        )

        csv_buffer = StringIO()
        pd.DataFrame(results["rankings"]).to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        filename = "ligbind_rankings.csv"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

        return StreamingResponse(
            csv_buffer,
            media_type="text/csv",
            headers=headers,
        )

    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="CSV export failed") from exc