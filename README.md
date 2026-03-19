# Candidate Skill Extraction ML Project

This repository contains a complete skill prediction workflow for job descriptions:

- synthetic dataset generation
- multi-label model training
- CLI prediction
- a FastAPI backend
- a React dashboard for interactive testing

The current frontend talks to the root FastAPI app in `app.py`. There is also a separate rule-based extractor in `backend/` that is kept as an additional utility, not the main frontend backend.

## Current Project Structure

```text
COE/
|-- app.py                       # Main FastAPI prediction API used by the React frontend
|-- run.ps1                     # Windows helper to install/start backend + frontend
|-- web_app.py                  # Optional simple Flask UI
|-- README.md
|-- requirements.txt
|-- backend/
|   |-- app.py                  # Alternate FastAPI app for heuristic extraction
|   |-- requirements.txt
|   |-- skill_extractor.py      # Rule-based skill extraction utility
|   `-- skills_lexicon.json
|-- data/
|   |-- raw/
|   |   |-- sample_job_description.txt
|   |   |-- sample_job_description_ml_engineer.txt
|   |   `-- skills_lexicon.json
|   `-- processed/
|       |-- job_skill_dataset.jsonl
|       |-- job_skill_dataset.csv
|       `-- job_skill_dataset_summary.json
|-- models/
|   |-- skill_classifier.joblib
|   |-- skill_classifier.pkl
|   `-- training_metrics.json
|-- src/
|   |-- common.py
|   |-- prepare_dataset.py
|   |-- train_model.py
|   `-- predict_model.py
|-- frontend/
|   |-- package.json
|   `-- src/
`-- notebooks/
```

## Main Components

### 1. ML Pipeline

- `src/prepare_dataset.py` generates a synthetic multi-label training dataset from the lexicon
- `src/train_model.py` trains the classifier and writes the model bundle + metrics
- `src/predict_model.py` runs local CLI inference against the trained model

### 2. Main API

- `app.py` serves the trained model through FastAPI
- endpoints:
  - `GET /api/health`
  - `GET /api/sample`
  - `POST /api/predict`
  - `POST /api/match`
  - `POST /api/extract-document`

### 3. React Frontend

The React app in `frontend/` provides:

- pasted or uploaded job description input
- TXT, PDF, and DOCX upload support for job descriptions and resumes
- sample text loading
- threshold, top-k, and minimum-result controls
- summary cards
- category distribution chart
- ranked predicted skill list with confidence
- optional raw JSON preview

### 4. Alternate Utilities

- `web_app.py` is a lightweight Flask UI for quick browser testing
- `backend/skill_extractor.py` is a rule-based extractor with its own alternate API in `backend/app.py`

## Requirements

### Python

Install the root Python dependencies:

```bash
python -m pip install -r requirements.txt
```

### Frontend

Install frontend dependencies:

```bash
cd frontend
npm install
```

## Quick Start

### Option 1: Windows helper

If you are on Windows, this is the easiest way to run the project:

```powershell
.\run.ps1
```

What `run.ps1` does:

- installs Python dependencies from `requirements.txt`
- trains the model automatically if `models/skill_classifier.joblib` is missing
- starts the FastAPI backend on `http://127.0.0.1:8000`
- starts the React frontend on `http://127.0.0.1:3000`

### Option 2: Manual startup

#### Step 1: Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

#### Step 2: Generate the dataset if needed

```bash
python src/prepare_dataset.py --samples-per-skill 24
```

#### Step 3: Train the model

```bash
python src/train_model.py
```

#### Step 4: Start the FastAPI backend

```bash
python app.py
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

#### Step 5: Start the React frontend

```bash
cd frontend
npm install
npm start
```

The frontend will be available at:

```text
http://127.0.0.1:3000
```

If needed, the frontend API base URL can be overridden with `REACT_APP_API_BASE_URL`.

## Free Hosting

The project is now set up so the FastAPI app can serve the built React frontend from one service. The simplest free deployment path is Render.

### Render

1. Push this folder to a GitHub repository.
2. Open Render and create a new Web Service from that repository.
3. Render will detect `render.yaml` and use:
   - build command: install Python dependencies, then build the React app
   - start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. After deployment, Render will give you a public URL in this format:

```text
https://your-service-name.onrender.com
```

Useful notes:

- the frontend and API are served from the same URL
- the health check is `GET /api/health`
- local development still works with `.\run.ps1`

## ML Workflow

### 1. Create or refresh the dataset

```bash
python src/prepare_dataset.py --samples-per-skill 24
```

Outputs:

- `data/processed/job_skill_dataset.jsonl`
- `data/processed/job_skill_dataset.csv`
- `data/processed/job_skill_dataset_summary.json`

### 2. Train the classifier

```bash
python src/train_model.py
```

Outputs:

- `models/skill_classifier.joblib`
- `models/skill_classifier.pkl`
- `models/training_metrics.json`

### 3. Run CLI prediction

Using a file:

```bash
python src/predict_model.py --text-file data/raw/sample_job_description.txt
```

Using inline text:

```bash
python src/predict_model.py --text "We need a data engineer with Python, SQL, Spark, and AWS experience."
```

Useful options:

- `--threshold`
- `--top-k`
- `--min-predictions`

## Main API Example

### Sample request

```json
{
  "text": "We are hiring a data engineer with Python, SQL, AWS, and Spark experience.",
  "threshold": 0.2,
  "top_k": 12,
  "min_predictions": 5
}
```

### Sample response shape

```json
{
  "summary": {
    "total_predicted_skills": 5,
    "threshold": 0.2,
    "top_category": "Data/AI"
  },
  "predicted_skills": [
    {
      "name": "Python",
      "category": "Programming Language",
      "confidence": 0.97
    }
  ]
}
```

## Alternate Rule-Based Extractor

The `backend/` folder contains a separate heuristic extractor that is useful for keyword-style extraction experiments.

Run it from the CLI:

```bash
python backend/skill_extractor.py data/raw/sample_job_description.txt --pretty
```

Start its separate API:

```bash
python backend/app.py
```

This alternate API exposes:

- `GET /api/health`
- `GET /api/sample`
- `POST /api/extract`

## Notes

- The trained-model workflow uses `data/raw/skills_lexicon.json` as the label source
- The React app currently uses the root FastAPI app in `app.py`
- `backend/skills_lexicon.json` belongs to the alternate rule-based extractor
- `web_app.py` is optional and not required for the React dashboard
