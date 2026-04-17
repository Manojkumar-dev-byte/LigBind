from fastapi import APIRouter
from models.prediction import PredictionRequest
from services.predictor import run_prediction
from database import predictions_collection

router = APIRouter(prefix="/predict", tags=["Prediction"])


# Manual Ranking
@router.post("/")
def predict(data: PredictionRequest):
    results = run_prediction(data.disease, data.drugs)

    predictions_collection.insert_one({
        "mode": "manual",
        "disease": data.disease,
        "drugs": data.drugs,
        "results": results
    })

    return {
        "disease": data.disease,
        "rankings": results
    }


# Auto Top 10 Drugs
@router.get("/top10/{disease}")
def top10_drugs(disease: str):

    drug_library = [
        "Gefitinib",
        "Erlotinib",
        "Osimertinib",
        "Imatinib",
        "Doxorubicin",
        "Cisplatin",
        "Paclitaxel",
        "Tamoxifen",
        "Sorafenib",
        "Metformin",
        "Docetaxel",
        "Trastuzumab",
        "Sunitinib",
        "Capecitabine",
        "Lapatinib"
    ]

    results = run_prediction(disease, drug_library)

    return {
        "disease": disease,
        "top_drugs": results[:10]
    }