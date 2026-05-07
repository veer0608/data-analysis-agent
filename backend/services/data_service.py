import pandas as pd
import numpy as np
import os
from typing import Tuple


ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "json"}
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))


def validate_file(filename: str, file_size: int) -> Tuple[bool, str]:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '.{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"File too large. Max allowed: {MAX_FILE_SIZE_MB} MB"
    return True, ""


def get_file_type(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower()


def load_dataframe(file_path: str, file_type: str) -> pd.DataFrame:
    """Load a dataframe from file, handling various encodings gracefully."""
    try:
        if file_type == "csv":
            try:
                return pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                return pd.read_csv(file_path, encoding="latin-1")
        elif file_type in ("xlsx", "xls"):
            return pd.read_excel(file_path)
        elif file_type == "json":
            return pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        raise ValueError(f"Failed to load file: {str(e)}")


def serialize(obj):
    """Recursively convert numpy/pandas types & NaN/inf to JSON-safe values."""
    # Order matters — NaN check must come before generic float branch
    if obj is None:
        return None
    if isinstance(obj, bool):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        if np.isnan(v) or np.isinf(v):
            return None
        return v
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    if isinstance(obj, np.ndarray):
        return [serialize(i) for i in obj.tolist()]
    if isinstance(obj, (pd.Timestamp, np.datetime64)):
        return str(obj)
    if isinstance(obj, pd.Series):
        return {str(k): serialize(v) for k, v in obj.items()}
    if isinstance(obj, dict):
        return {str(k): serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serialize(i) for i in obj]
    if pd.isna(obj):  # catches pd.NA, pd.NaT, etc.
        return None
    return obj


def get_preview(df: pd.DataFrame, n: int = 10) -> dict:
    """Return first n rows as a JSON-safe dict."""
    preview_df = df.head(n).copy()

    # Stringify columns that won't survive JSON natively
    for col in preview_df.columns:
        if preview_df[col].dtype == "object":
            # Keep NaN as NaN (don't stringify), only cast non-null values
            preview_df[col] = preview_df[col].where(preview_df[col].isna(),
                                                     preview_df[col].astype(str))
        elif pd.api.types.is_datetime64_any_dtype(preview_df[col]):
            preview_df[col] = preview_df[col].astype(str)

    records = preview_df.to_dict(orient="records")
    return {
        "columns": [str(c) for c in df.columns],
        "dtypes": {str(col): str(dtype) for col, dtype in df.dtypes.items()},
        "data": serialize(records),  # ensure NaN/inf/numpy types are JSON-safe
        "total_rows": int(len(df)),
        "total_cols": int(len(df.columns)),
    }
