from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from collections import Counter
import json
from typing import Iterable, Optional

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parent
ML_DIR = PROJECT_ROOT / "ML"
DATA_DIR = ML_DIR / "data"
ARTIFACT_DIR = ML_DIR / "models"

DRUGS_FILE = DATA_DIR / "drugs (1).csv"
PROTEINS_FILE = DATA_DIR / "proteins (1).csv"
AFFINITY_FILE = DATA_DIR / "drug_protein_affinity (1).csv"

MODEL_FILE = ARTIFACT_DIR / "xgboost_dta_model.pkl"
SCALER_FILE = ARTIFACT_DIR / "feature_scaler.pkl"
DRUG_FEATURES_FILE = ARTIFACT_DIR / "drug_features.pkl"
METADATA_FILE = ARTIFACT_DIR / "model_metadata.json"


AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
HYDROPHOBICITY = {
    "A": 1.8,
    "C": 2.5,
    "D": -3.5,
    "E": -3.5,
    "F": 2.8,
    "G": -0.4,
    "H": -3.2,
    "I": 4.5,
    "K": -3.9,
    "L": 3.8,
    "M": 1.9,
    "N": -3.5,
    "P": -1.6,
    "Q": -3.5,
    "R": -4.5,
    "S": -0.8,
    "T": -0.7,
    "V": 4.2,
    "W": -0.9,
    "Y": -1.3,
}
CHARGE = {"D": -1.0, "E": -1.0, "K": 1.0, "R": 1.0, "H": 0.5}


@dataclass
class ArtifactBundle:
    model: xgb.XGBRegressor
    scaler: StandardScaler
    drug_features: dict[int, np.ndarray]
    metadata: dict


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _find_data_file(preferred: Path, pattern: str) -> Path:
    if preferred.exists():
        return preferred

    matches = sorted(DATA_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"Could not find dataset file matching {pattern!r} in {DATA_DIR}")
    return matches[0]


def load_datasets() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    drugs_path = _find_data_file(DRUGS_FILE, "drugs*.csv")
    proteins_path = _find_data_file(PROTEINS_FILE, "proteins*.csv")
    affinity_path = _find_data_file(AFFINITY_FILE, "drug_protein_affinity*.csv")

    drugs_df = pd.read_csv(drugs_path)
    proteins_df = pd.read_csv(proteins_path)
    affinity_df = pd.read_csv(affinity_path)

    return drugs_df, proteins_df, affinity_df


def load_drug_library() -> pd.DataFrame:
    drugs_df, _, _ = load_datasets()
    return drugs_df


def generate_drug_features(smiles: str, radius: int = 2, n_bits: int = 256) -> Optional[np.ndarray]:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    fingerprint = AllChem.GetMorganFingerprintAsBitVect(mol, radius=radius, nBits=n_bits)
    fp_array = np.asarray(fingerprint, dtype=np.float32)

    descriptors = np.asarray(
        [
            Descriptors.MolWt(mol),
            Descriptors.MolLogP(mol),
            Descriptors.TPSA(mol),
            Descriptors.NumHDonors(mol),
            Descriptors.NumHAcceptors(mol),
            Descriptors.NumRotatableBonds(mol),
            Descriptors.RingCount(mol),
            Descriptors.NumAromaticRings(mol),
            Descriptors.FractionCSP3(mol),
            Descriptors.HeavyAtomCount(mol),
            rdMolDescriptors.CalcNumAmideBonds(mol),
            Descriptors.NumHeteroatoms(mol),
        ],
        dtype=np.float32,
    )

    return np.concatenate([fp_array, descriptors])


def _resize_feature_vector(vector: np.ndarray, target_dim: int) -> np.ndarray:
    """Resize a 1D feature vector to the model-required width via truncate/pad."""
    if target_dim <= 0:
        raise ValueError("target_dim must be a positive integer")

    current_dim = int(vector.shape[0])
    if current_dim == target_dim:
        return vector
    if current_dim > target_dim:
        return vector[:target_dim]

    padded = np.zeros(target_dim, dtype=vector.dtype)
    padded[:current_dim] = vector
    return padded


def generate_protein_features(sequence: str, max_len: int = 5000, target_dim: Optional[int] = None) -> np.ndarray:
    seq = (sequence or "").upper().strip()[:max_len]
    seq_len = len(seq)

    aa_count = Counter(seq)
    aa_comp = np.asarray([aa_count.get(aa, 0) / max(seq_len, 1) for aa in AMINO_ACIDS], dtype=np.float32)

    dipeptides = [left + right for left in AMINO_ACIDS for right in AMINO_ACIDS]
    dipeptide_count = Counter(seq[index : index + 2] for index in range(max(seq_len - 1, 0)))
    n_dipeptides = max(seq_len - 1, 1)
    dipeptide_comp = np.asarray([dipeptide_count.get(dp, 0) / n_dipeptides for dp in dipeptides], dtype=np.float32)

    hydrophobic_values = [HYDROPHOBICITY.get(aa, 0.0) for aa in seq]
    avg_hydrophobicity = float(np.mean(hydrophobic_values)) if hydrophobic_values else 0.0
    std_hydrophobicity = float(np.std(hydrophobic_values)) if hydrophobic_values else 0.0
    net_charge = float(sum(CHARGE.get(aa, 0.0) for aa in seq))

    physico = np.asarray(
        [
            seq_len / max_len,
            (seq_len * 110.0) / 100000.0,
            avg_hydrophobicity,
            std_hydrophobicity,
            net_charge / max(seq_len, 1),
            sum(1 for aa in seq if aa in "FWY") / max(seq_len, 1),
            sum(1 for aa in seq if aa in "KRH") / max(sum(1 for aa in seq if aa in "DE"), 1),
            sum(1 for aa in seq if aa in "AELM") / max(seq_len, 1),
            sum(1 for aa in seq if aa in "FIVWY") / max(seq_len, 1),
            sum(1 for aa in seq if aa in "GPNS") / max(seq_len, 1),
        ],
        dtype=np.float32,
    )

    features = np.concatenate([aa_comp, dipeptide_comp, physico])
    if target_dim is not None:
        features = _resize_feature_vector(features, target_dim)
    return features


def balance_affinity_data(
    affinity_df: pd.DataFrame,
    floor_value: float = 5.0,
    max_floor_to_active_ratio: float = 1.0,
    random_state: int = 42,
) -> pd.DataFrame:
    active = affinity_df[affinity_df["Affinity"] > floor_value]
    floor = affinity_df[affinity_df["Affinity"] == floor_value]

    if active.empty or floor.empty:
        return affinity_df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)

    n_floor_keep = min(len(floor), int(len(active) * max_floor_to_active_ratio))
    floor_sampled = floor.sample(n=n_floor_keep, random_state=random_state)

    balanced = pd.concat([active, floor_sampled], ignore_index=True)
    return balanced.sample(frac=1.0, random_state=random_state).reset_index(drop=True)


def build_feature_cache(drugs_df: pd.DataFrame) -> tuple[dict[int, np.ndarray], list[int]]:
    drug_features: dict[int, np.ndarray] = {}
    failed: list[int] = []

    for _, row in drugs_df.iterrows():
        drug_index = int(row["Drug_Index"])
        smiles = row["Canonical_SMILES"]
        features = generate_drug_features(smiles)
        if features is None:
            failed.append(drug_index)
            continue
        drug_features[drug_index] = features

    return drug_features, failed


def build_feature_matrix(
    affinity_df: pd.DataFrame,
    drug_features: dict[int, np.ndarray],
    protein_features: dict[int, np.ndarray],
) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    feature_rows: list[np.ndarray] = []
    targets: list[float] = []
    meta_rows: list[dict] = []

    skipped = 0
    for _, row in affinity_df.iterrows():
        drug_index = int(row["Drug_Index"])
        protein_index = int(row["Protein_Index"])

        if drug_index not in drug_features or protein_index not in protein_features:
            skipped += 1
            continue

        combined = np.concatenate([drug_features[drug_index], protein_features[protein_index]])
        feature_rows.append(combined)
        targets.append(float(row["Affinity"]))
        meta_rows.append({"drug_index": drug_index, "protein_index": protein_index})

    if not feature_rows:
        raise ValueError("No valid affinity pairs were found while building the feature matrix.")

    X = np.asarray(feature_rows, dtype=np.float32)
    y = np.asarray(targets, dtype=np.float32)

    if skipped:
        print(f"Skipped {skipped} affinity pairs because of missing features.")

    return X, y, meta_rows


def _default_model() -> xgb.XGBRegressor:
    return xgb.XGBRegressor(
        n_estimators=1500,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.75,
        colsample_bytree=0.55,
        colsample_bylevel=0.75,
        min_child_weight=10,
        reg_alpha=1.0,
        reg_lambda=5.0,
        gamma=0.5,
        random_state=42,
        n_jobs=-1,
        objective="reg:squarederror",
        eval_metric="rmse",
    )


def train_affinity_model(random_state: int = 42) -> dict:
    drugs_df, proteins_df, affinity_df = load_datasets()
    balanced_affinity = balance_affinity_data(affinity_df, random_state=random_state)

    drug_features, failed_drugs = build_feature_cache(drugs_df)
    protein_features = {
        int(row["Protein_Index"]): generate_protein_features(row["Sequence"])
        for _, row in proteins_df.iterrows()
    }

    X, y, _ = build_feature_matrix(balanced_affinity, drug_features, protein_features)

    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=random_state)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=random_state)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    model = _default_model()
    model.fit(
        X_train_scaled,
        y_train,
        eval_set=[(X_val_scaled, y_val)],
        verbose=False,
        early_stopping_rounds=50,
    )

    train_pred = model.predict(X_train_scaled)
    val_pred = model.predict(X_val_scaled)
    test_pred = model.predict(X_test_scaled)

    metrics = {
        "train_r2": float(r2_score(y_train, train_pred)),
        "val_r2": float(r2_score(y_val, val_pred)),
        "test_r2": float(r2_score(y_test, test_pred)),
        "train_rmse": float(np.sqrt(mean_squared_error(y_train, train_pred))),
        "val_rmse": float(np.sqrt(mean_squared_error(y_val, val_pred))),
        "test_rmse": float(np.sqrt(mean_squared_error(y_test, test_pred))),
        "train_mae": float(mean_absolute_error(y_train, train_pred)),
        "val_mae": float(mean_absolute_error(y_val, val_pred)),
        "test_mae": float(mean_absolute_error(y_test, test_pred)),
        "best_iteration": int(getattr(model, "best_iteration", model.n_estimators)),
    }

    metadata = {
        "model_type": "XGBRegressor",
        "drug_feature_dim": int(len(next(iter(drug_features.values())))),
        "protein_feature_dim": int(len(generate_protein_features(proteins_df.iloc[0]["Sequence"]))),
        "total_feature_dim": int(X.shape[1]),
        "n_samples": int(len(y)),
        "n_train": int(len(y_train)),
        "n_val": int(len(y_val)),
        "n_test": int(len(y_test)),
        "failed_drugs": failed_drugs,
        **metrics,
    }

    save_artifacts(model, scaler, drug_features, metadata)

    return {
        "model": model,
        "scaler": scaler,
        "drug_features": drug_features,
        "metadata": metadata,
        "metrics": metrics,
    }


def save_artifacts(
    model: xgb.XGBRegressor,
    scaler: StandardScaler,
    drug_features: dict[int, np.ndarray],
    metadata: dict,
) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    joblib.dump(scaler, SCALER_FILE)
    joblib.dump(drug_features, DRUG_FEATURES_FILE)
    _ensure_parent(METADATA_FILE)
    METADATA_FILE.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def load_artifacts() -> ArtifactBundle:
    if not MODEL_FILE.exists() or not SCALER_FILE.exists() or not DRUG_FEATURES_FILE.exists():
        raise FileNotFoundError(
            "Missing trained artifacts. Run ML/train.py first to generate the model files."
        )

    model = joblib.load(MODEL_FILE)
    scaler = joblib.load(SCALER_FILE)
    drug_features = joblib.load(DRUG_FEATURES_FILE)
    metadata = {}

    if METADATA_FILE.exists():
        metadata = json.loads(METADATA_FILE.read_text(encoding="utf-8"))

    return ArtifactBundle(model=model, scaler=scaler, drug_features=drug_features, metadata=metadata)


@lru_cache(maxsize=1)
def load_ranker_bundle() -> ArtifactBundle:
    return load_artifacts()


def _candidate_rows_from_smiles(smiles_list: Iterable[str]) -> pd.DataFrame:
    rows = []
    for index, smiles in enumerate(smiles_list, start=1):
        rows.append({"Drug_Index": index, "Canonical_SMILES": smiles})
    return pd.DataFrame(rows)


def rank_drugs_for_protein(
    protein_sequence: str,
    top_n: int = 10,
    candidate_drugs: Optional[pd.DataFrame] = None,
    candidate_smiles: Optional[Iterable[str]] = None,
    export_csv_path: Optional[Path] = None,
) -> pd.DataFrame:
    bundle = load_ranker_bundle()
    model = bundle.model
    scaler = bundle.scaler
    drug_features = bundle.drug_features

    if candidate_smiles is not None:
        candidate_drugs = _candidate_rows_from_smiles(candidate_smiles)
    elif candidate_drugs is None:
        candidate_drugs = load_drug_library()[["Drug_Index", "Canonical_SMILES"]].copy()

    expected_total_dim = int(getattr(scaler, "n_features_in_", 0))
    drug_feature_dim = len(next(iter(drug_features.values()))) if drug_features else 0
    protein_feature_dim = expected_total_dim - drug_feature_dim if expected_total_dim else None
    protein_features = generate_protein_features(protein_sequence, target_dim=protein_feature_dim)
    ranked_rows: list[dict] = []

    for _, row in candidate_drugs.iterrows():
        drug_index = int(row["Drug_Index"])
        smiles = row["Canonical_SMILES"]

        features = drug_features.get(drug_index)
        if features is None:
            features = generate_drug_features(smiles)
        if features is None:
            continue

        combined = np.concatenate([features, protein_features]).reshape(1, -1)
        scaled = scaler.transform(combined)
        predicted_affinity = float(model.predict(scaled)[0])

        ranked_rows.append(
            {
                "Drug_Index": drug_index,
                "SMILES": smiles,
                "Predicted_Affinity": predicted_affinity,
            }
        )

    if not ranked_rows:
        raise ValueError("No valid candidate drugs were available for ranking.")

    ranked_df = pd.DataFrame(ranked_rows).sort_values("Predicted_Affinity", ascending=False).reset_index(drop=True)
    ranked_df.insert(0, "Rank", np.arange(1, len(ranked_df) + 1))

    if export_csv_path is not None:
        _ensure_parent(export_csv_path)
        ranked_df.to_csv(export_csv_path, index=False)

    return ranked_df
