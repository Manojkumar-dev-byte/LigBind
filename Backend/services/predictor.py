from functools import lru_cache
from pathlib import Path
import sys

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml_pipeline import load_drug_library, rank_drugs_for_protein  # noqa: E402


@lru_cache(maxsize=1)
def get_drug_library() -> pd.DataFrame:
    library = load_drug_library().copy()
    required_cols = ["Drug_Index", "Canonical_SMILES"]
    optional_cols = [col for col in ["CID", "Drug_Name", "Name"] if col in library.columns]
    return library[required_cols + optional_cols].copy()


def _build_drug_label(record: dict) -> str:
    for key in ("Drug_Name", "Name"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    cid = record.get("CID")
    if pd.notna(cid):
        try:
            return f"CID {int(cid)}"
        except (TypeError, ValueError):
            return f"CID {cid}"

    return f"Drug {int(record['Drug_Index'])}"


def run_prediction(protein_sequence: str, top_n: int = 10, candidate_smiles=None):
    candidate_drugs = None
    if candidate_smiles:
        candidate_drugs = pd.DataFrame(
            {
                "Drug_Index": list(range(1, len(candidate_smiles) + 1)),
                "Canonical_SMILES": candidate_smiles,
                "Drug_Name": [f"Custom Drug {index}" for index in range(1, len(candidate_smiles) + 1)],
            }
        )
    else:
        candidate_drugs = get_drug_library()

    label_map = {
        int(row["Drug_Index"]): _build_drug_label(row)
        for row in candidate_drugs.to_dict(orient="records")
    }

    ranked_df = rank_drugs_for_protein(
        protein_sequence=protein_sequence,
        top_n=top_n,
        candidate_drugs=candidate_drugs,
    )

    ranked_records = []
    for row in ranked_df.to_dict(orient="records"):
        ranked_records.append(
            {
                "rank": int(row["Rank"]),
                "drug_index": int(row["Drug_Index"]),
                "drug_name": label_map.get(int(row["Drug_Index"]), f"Drug {int(row['Drug_Index'])}"),
                "smiles": row["SMILES"],
                "predicted_affinity": round(float(row["Predicted_Affinity"]), 4),
            }
        )

    return ranked_records


def rank_protein_target(protein_sequence: str, top_n: int = 10, candidate_smiles=None):
    ranked_records = run_prediction(
        protein_sequence=protein_sequence,
        top_n=top_n,
        candidate_smiles=candidate_smiles,
    )

    return {
        "protein_sequence": protein_sequence,
        "top_n": top_n,
        "total_candidates": len(ranked_records),
        "rankings": ranked_records,
        "top_drugs": ranked_records[:top_n],
    }