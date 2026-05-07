import os
import uuid
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Dataset
from schemas import DatasetResponse
from services.data_service import validate_file, get_file_type, load_dataframe

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DatasetResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a CSV, Excel, or JSON dataset file."""
    content = await file.read()
    file_size = len(content)

    ok, error_msg = validate_file(file.filename, file_size)
    if not ok:
        raise HTTPException(status_code=400, detail=error_msg)

    file_type = get_file_type(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(content)

    # Load to extract metadata
    try:
        df = load_dataframe(file_path, file_type)
    except ValueError as e:
        os.remove(file_path)
        raise HTTPException(status_code=422, detail=str(e))

    columns_info = {col: str(dtype) for col, dtype in df.dtypes.items()}

    record = Dataset(
        original_filename=file.filename,
        saved_filename=unique_name,
        file_type=file_type,
        file_path=file_path,
        file_size_bytes=file_size,
        row_count=len(df),
        col_count=len(df.columns),
        columns_json=json.dumps(columns_info),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/datasets", response_model=list[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    """Return all uploaded datasets ordered by newest first."""
    return db.query(Dataset).order_by(Dataset.created_at.desc()).all()


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)

    db.delete(dataset)
    db.commit()
    return {"message": f"Dataset {dataset_id} deleted successfully"}
