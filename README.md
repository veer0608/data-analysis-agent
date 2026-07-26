# Data Analysis Agent

Upload a messy dataset, get an instant analysis. **Data Analysis Agent** is an
automated exploratory-data-analysis tool: drop in a CSV, Excel, or JSON file and it
profiles the data, generates charts, flags anomalies, and produces a downloadable
PDF report — no notebook required.

FastAPI backend + Streamlit UI, powered by pandas · scikit-learn · matplotlib.

## Features

**Upload & manage**
- CSV, Excel (`.xlsx` / `.xls`), and JSON files (up to 50 MB)
- Each upload is stored with metadata (row/column counts, dtypes) in a datasets
  library you can revisit, preview, or delete

**Automated EDA** — `GET /api/analysis/{id}/eda`
- Shape, dtypes, and memory footprint
- Missing-value and duplicate-row counts
- Separate numeric and categorical summaries
- Correlation matrix, plus per-column skewness and kurtosis

**Visualizations** — `GET /api/analysis/{id}/visualizations`
- Histograms, box plots, and bar charts (top categories)
- Correlation heatmap and scatter matrix
- Rendered server-side (matplotlib / seaborn), returned as PNG images

**Anomaly detection** — `GET /api/analysis/{id}/anomalies`
- Multivariate outliers via **IsolationForest**
- Per-column outliers via **Z-score** (|z| > 3)
- Returns the anomaly count, percentage, and the offending row indices

**PDF report** — `GET /api/reports/{id}/pdf`
- One call runs the whole pipeline (EDA + anomalies + charts) and returns a
  formatted PDF with the visualizations embedded

**Analysis history**
- Every analysis is recorded per dataset, so you can see what was run and when

## Architecture

```
Streamlit UI (:8501)  ──HTTP──▶  FastAPI (:8000)  ──▶  pandas / scikit-learn / matplotlib
                                       │
                                       ├── SQLite (SQLAlchemy): datasets + analysis history
                                       └── uploads/ : stored dataset files
```

- **backend/** — FastAPI app; thin routers (`upload`, `analysis`, `reports`) call
  stateless services (`data`, `eda`, `viz`, `anomaly`, `report`).
- **frontend/** — Streamlit app that talks to the backend over HTTP.

## Tech stack

| Layer | Tools |
|---|---|
| API | FastAPI, Uvicorn |
| Data / ML | pandas, NumPy, scikit-learn, SciPy |
| Charts | Matplotlib, Seaborn |
| Reports | fpdf2 |
| Storage | SQLite via SQLAlchemy |
| UI | Streamlit |

## Quickstart

```bash
git clone https://github.com/veer0608/data-analysis-agent
cd data-analysis-agent
pip install -r requirements.txt
```

Start both servers with the helper script:

```bash
./run.sh
```

- **UI** → http://localhost:8501
- **API** → http://localhost:8000 (interactive docs at `/docs`)

Or run them manually in two terminals:

```bash
cd backend && uvicorn main:app --reload --port 8000
```

```bash
cd frontend && streamlit run app.py --server.port 8501
```

The SQLite database (`backend/analysis.db`) is created automatically on first run.

### Try it
`sample_data/sales_dataset.csv` is included — upload it from the UI, then run EDA,
visualizations, anomalies, and download the PDF report.

### Configuration (optional)

| Env var | Default | Purpose |
|---|---|---|
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload size |
| `UPLOAD_DIR` | `uploads` | Where uploaded files are stored |
| `BACKEND_URL` | `http://localhost:8000` | Backend URL the frontend calls |

## API reference

All endpoints are under `/api` (full interactive docs at `/docs`).

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload a CSV / Excel / JSON dataset |
| `GET` | `/api/datasets` | List uploaded datasets |
| `GET` | `/api/datasets/{id}` | Dataset metadata |
| `DELETE` | `/api/datasets/{id}` | Delete a dataset and its file |
| `GET` | `/api/analysis/{id}/preview?n=10` | First _n_ rows (max 100) |
| `GET` | `/api/analysis/{id}/eda` | Full EDA profile |
| `GET` | `/api/analysis/{id}/visualizations` | Charts as base64 PNGs |
| `GET` | `/api/analysis/{id}/anomalies` | IsolationForest + Z-score outliers |
| `GET` | `/api/analysis/{id}/history` | Past analyses for a dataset |
| `GET` | `/api/reports/{id}/pdf` | Full analysis as a downloadable PDF |

## Project structure

```
backend/
  main.py          FastAPI app, CORS, startup
  database.py      SQLAlchemy engine/session (SQLite)
  models.py        Dataset, AnalysisRecord
  schemas.py       Pydantic response models
  routers/         upload · analysis · reports
  services/        data · eda · viz · anomaly · report
frontend/
  app.py           Streamlit UI
sample_data/       example CSV to try the pipeline
run.sh             start backend + frontend together
```
