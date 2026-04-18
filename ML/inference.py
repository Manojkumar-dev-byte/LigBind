from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
	sys.path.insert(0, str(ROOT_DIR))

from ml_pipeline import load_ranker_bundle, rank_drugs_for_protein  # noqa: E402


def get_model_metadata() -> dict:
	bundle = load_ranker_bundle()
	return bundle.metadata


def rank_drugs(protein_sequence: str, top_n: int = 10, candidate_smiles=None) -> pd.DataFrame:
	return rank_drugs_for_protein(
		protein_sequence=protein_sequence,
		top_n=top_n,
		candidate_smiles=candidate_smiles,
	)


def rank_and_export(
	protein_sequence: str,
	output_csv: str = "drug_rankings.csv",
	top_n: int = 10,
	candidate_smiles=None,
) -> pd.DataFrame:
	ranked_df = rank_drugs(protein_sequence=protein_sequence, top_n=top_n, candidate_smiles=candidate_smiles)
	ranked_df.to_csv(output_csv, index=False)
	return ranked_df


if __name__ == "__main__":
	print("LigBind inference helper")
	print("Load model metadata with get_model_metadata()")
