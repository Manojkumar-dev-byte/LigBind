# LigBind

LigBind is an AI-powered drug candidate ranking platform that helps reduce early discovery time from months to minutes by prioritizing likely binders for a target protein.

## Problem Statement

Traditional drug discovery is often:

- Very slow (can take years)
- Extremely expensive
- Dependent on testing thousands of compounds
- Prone to high failure rates in late stages
- Hard to adapt quickly for emerging diseases

## Our Solution

LigBind converts a disease name or protein sequence into a ranked list of candidate drugs using an ML-based affinity scoring pipeline.

### How It Works

1. User inputs a disease name or protein sequence.
2. System maps disease to a target protein sequence (if disease mode is used).
3. Candidate molecules are featurized from SMILES strings.
4. ML model predicts affinity score for each candidate.
5. Candidates are ranked and returned instantly.
6. Results can be exported as CSV for downstream analysis.

## Unique Selling Proposition (USP)

### From Disease Name to Drug Candidates - Fully Automated

- Most systems evaluate manually entered drugs only.
- LigBind can discover and recommend candidates automatically from a built-in library.

### What Makes LigBind Different

- Disease-name input with automatic target resolution
- Smart ranking based on predicted affinity
- Support for custom candidate SMILES lists
- Fast shortlist generation for early R and D triage
- Simple dashboard workflow for non-expert users
- Built as a reusable full-stack platform (UI + API + ML artifacts)

### Why It Matters

- Faster response in health emergencies
- Better prioritization before expensive wet-lab experiments
- Reduced screening cost and cycle time
- More accessible AI-assisted drug discovery workflow

## Current Output Scope

Current implementation provides:

- Ranked candidate list
- Predicted affinity score per candidate
- Top-N shortlist
- CSV export

Note: Safety-risk scoring is not yet part of the current production output and can be added as a future extension.

## Tech Stack

### Frontend

- React 19
- Vite 8
- React Router
- Axios
- CSS (custom styling)

### Backend

- FastAPI
- Uvicorn
- Pydantic
- Pandas

### Machine Learning

- XGBoost (regression ranker)
- scikit-learn (preprocessing and evaluation)
- NumPy
- Joblib (artifact persistence)
- RDKit (used by training/feature generation pipeline)

### Data and Artifacts

- Davis-style CSV datasets in `ML/data`
- Trained model artifacts in `ML/models`

## Architecture

```text
Frontend (React + Vite)
	|
	| HTTP (JSON / CSV)
	v
Backend API (FastAPI)
	|
	| invokes
	v
ML Pipeline (xgboost + sklearn + artifacts)
	|
	+--> Ranked predictions
	+--> CSV export
```

## Repository Structure

```text
LigBind/
|- Backend/
|  |- app.py
|  |- requirements.txt
|  |- models/
|  |  |- prediction.py
|  |- routes/
|  |  |- predict.py
|  |- services/
|  |  |- predictor.py
|  |- utils/
|     |- disease_mapping.py
|- Frontend/
|  |- package.json
|  |- src/
|     |- App.jsx
|     |- main.jsx
|     |- components/
|     |- pages/
|     |- services/
|     |- styles/
|- ML/
|  |- train.py
|  |- inference.py
|  |- data/
|  |- models/
|- ml_pipeline.py
|- README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm

### 1) Backend Setup

```bash
cd Backend
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Backend runs at `http://127.0.0.1:8000`

### 2) Frontend Setup

```bash
cd Frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Frontend runs at `http://127.0.0.1:5173`

### 3) Optional Frontend Environment Variable

Create `Frontend/.env` if you want a custom API URL:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Training and Model Artifacts

If `ML/models` artifacts are missing, train first.

```bash
python ML/train.py
```

Training pipeline uses RDKit for molecular features. If RDKit is not installed in your training environment, install a compatible package first.

## API Reference

### `GET /`

Health check response.

### `POST /predict/rank`

Predict and rank drug candidates.

Request body (example):

```json
{
  "protein_sequence": "MKTFFVAGVILLLAALATQATADNQSVRLEERLGLIEVQANLQDKN",
  "top_n": 10,
  "candidate_smiles": ["CCO", "CCN"]
}
```

You may use `disease_name` instead of `protein_sequence`.

### `POST /predict/csv`

Returns ranked results as downloadable CSV.

## Frontend Pages

- `/` : Home
- `/about-platform` : Platform overview
- `/how-to-use` : Usage guide
- `/dashboard` : Prediction, ranking, and CSV export

## Vision

Turn years of early screening into minutes of intelligent candidate prioritization, helping teams move faster from hypothesis to actionable compounds.

## Roadmap

- Add safety/toxicity risk scoring
- Add explainable AI panels for ranking rationale
- Add benchmark datasets and model comparison dashboard
- Add deployment profile via Docker Compose

## Disclaimer

LigBind is intended for research and educational use. Predictions are computational estimates and must be validated experimentally.
