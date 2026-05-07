import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Dataset, AnalysisRecord
from services.data_service import load_dataframe, get_preview
from services.eda_service import run_eda
from services.viz_service import generate_all_visualizations
from services.anomaly_service import detect_anomalies

router = APIRouter()


def _get_dataset_or_404(dataset_id: int, db: Session) -> Dataset:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


def _load_df(dataset: Dataset):
    try:
        return load_dataframe(dataset.file_path, dataset.file_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/analysis/{dataset_id}/preview")
def preview_data(dataset_id: int, n: int = 10, db: Session = Depends(get_db)):
    """Return first n rows of the dataset for quick preview."""
    dataset = _get_dataset_or_404(dataset_id, db)
    df = _load_df(dataset)
    return get_preview(df, n=min(n, 100))  # cap at 100 rows


@router.get("/analysis/{dataset_id}/eda")
def eda(dataset_id: int, db: Session = Depends(get_db)):
    """Run full exploratory data analysis."""
    dataset = _get_dataset_or_404(dataset_id, db)
    df = _load_df(dataset)
    result = run_eda(df)

    # Persist a record of this analysis
    record = AnalysisRecord(
        dataset_id=dataset_id,
        analysis_type="eda",
        result_summary=json.dumps({"shape": result["shape"]}),
    )
    db.add(record)
    db.commit()
    return result


@router.get("/analysis/{dataset_id}/visualizations")
def visualizations(dataset_id: int, db: Session = Depends(get_db)):
    """Generate all charts and return them as base64-encoded PNG strings."""
    dataset = _get_dataset_or_404(dataset_id, db)
    df = _load_df(dataset)
    result = generate_all_visualizations(df)

    record = AnalysisRecord(
        dataset_id=dataset_id,
        analysis_type="visualizations",
        result_summary=json.dumps({"charts_generated": [k for k, v in result.items() if v]}),
    )
    db.add(record)
    db.commit()
    return result


@router.get("/analysis/{dataset_id}/anomalies")
def anomalies(dataset_id: int, db: Session = Depends(get_db)):
    """Run anomaly / outlier detection using IsolationForest and Z-score."""
    dataset = _get_dataset_or_404(dataset_id, db)
    df = _load_df(dataset)
    result = detect_anomalies(df)

    record = AnalysisRecord(
        dataset_id=dataset_id,
        analysis_type="anomaly",
        result_summary=json.dumps({
            "total_anomalies": result["total_anomalies"],
            "anomaly_percentage": result["anomaly_percentage"],
        }),
    )
    db.add(record)
    db.commit()
    return result


@router.get("/analysis/{dataset_id}/history")
def analysis_history(dataset_id: int, db: Session = Depends(get_db)):
    """Fetch all past analysis records for a dataset."""
    _get_dataset_or_404(dataset_id, db)
    records = (
        db.query(AnalysisRecord)
        .filter(AnalysisRecord.dataset_id == dataset_id)
        .order_by(AnalysisRecord.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "analysis_type": r.analysis_type,
            "result_summary": r.result_summary,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]
