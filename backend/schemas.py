from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class DatasetResponse(BaseModel):
    id: int
    original_filename: str
    file_type: str
    file_size_bytes: int
    row_count: Optional[int]
    col_count: Optional[int]
    columns_json: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DataPreviewResponse(BaseModel):
    columns: List[str]
    dtypes: Dict[str, str]
    data: List[Dict[str, Any]]
    total_rows: int
    total_cols: int


class EDAResponse(BaseModel):
    shape: Dict[str, int]
    dtypes: Dict[str, str]
    missing_values: Dict[str, Any]
    duplicate_rows: int
    numeric_columns: List[str]
    categorical_columns: List[str]
    numeric_summary: Dict[str, Any]
    categorical_summary: Dict[str, Any]
    correlation_matrix: Optional[Dict[str, Any]]
    skewness: Dict[str, float]
    kurtosis: Dict[str, float]
    memory_usage_mb: float


class AnomalyResponse(BaseModel):
    method: str
    total_anomalies: int
    anomaly_percentage: float
    anomalous_indices: List[int]
    column_outliers: Dict[str, Any]
    anomaly_scores: Optional[List[float]]


class VisualizationResponse(BaseModel):
    histograms: Optional[str]       # base64 PNG
    correlation_heatmap: Optional[str]
    box_plots: Optional[str]
    bar_charts: Optional[str]
    scatter_matrix: Optional[str]


class AnalysisRecordResponse(BaseModel):
    id: int
    dataset_id: int
    analysis_type: str
    result_summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
