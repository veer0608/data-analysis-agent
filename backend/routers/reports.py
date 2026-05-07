from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database import get_db
from models import Dataset
from services.data_service import load_dataframe
from services.eda_service import run_eda
from services.viz_service import generate_all_visualizations
from services.anomaly_service import detect_anomalies
from services.report_service import generate_pdf_report

router = APIRouter()


@router.get("/reports/{dataset_id}/pdf")
def download_pdf_report(dataset_id: int, db: Session = Depends(get_db)):
    """
    Run the full analysis pipeline and return a downloadable PDF report.
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    try:
        df = load_dataframe(dataset.file_path, dataset.file_type)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    eda = run_eda(df)
    anomalies = detect_anomalies(df)
    visualizations = generate_all_visualizations(df)

    pdf_bytes = generate_pdf_report(
        dataset_name=dataset.original_filename,
        eda=eda,
        anomalies=anomalies,
        visualizations=visualizations,
    )

    safe_name = dataset.original_filename.rsplit(".", 1)[0].replace(" ", "_")
    return Response(
        content=bytes(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_report.pdf"'},
    )
