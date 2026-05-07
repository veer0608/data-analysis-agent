import pandas as pd
import numpy as np
from services.data_service import serialize


def run_eda(df: pd.DataFrame) -> dict:
    """Perform comprehensive exploratory data analysis on a dataframe."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

    # --- Missing values ---
    missing = {}
    for col in df.columns:
        count = int(df[col].isna().sum())
        missing[col] = {
            "count": count,
            "percentage": round(count / len(df) * 100, 2) if len(df) > 0 else 0,
        }

    # --- Numeric summary ---
    numeric_summary = {}
    if numeric_cols:
        desc = df[numeric_cols].describe().T
        for col in numeric_cols:
            numeric_summary[col] = {
                "count": serialize(desc.loc[col, "count"]),
                "mean": serialize(desc.loc[col, "mean"]),
                "std": serialize(desc.loc[col, "std"]),
                "min": serialize(desc.loc[col, "min"]),
                "25%": serialize(desc.loc[col, "25%"]),
                "50%": serialize(desc.loc[col, "50%"]),
                "75%": serialize(desc.loc[col, "75%"]),
                "max": serialize(desc.loc[col, "max"]),
            }

    # --- Categorical summary ---
    categorical_summary = {}
    for col in categorical_cols:
        vc = df[col].value_counts()
        categorical_summary[col] = {
            "unique_count": int(df[col].nunique()),
            "top_values": {str(k): int(v) for k, v in vc.head(10).items()},
            "mode": str(df[col].mode().iloc[0]) if not df[col].mode().empty else None,
        }

    # --- Correlation matrix (numeric only) ---
    correlation_matrix = None
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        correlation_matrix = serialize(corr.to_dict())

    # --- Skewness & Kurtosis ---
    skewness = {}
    kurtosis = {}
    for col in numeric_cols:
        skewness[col] = serialize(df[col].skew())
        kurtosis[col] = serialize(df[col].kurtosis())

    # --- Memory usage ---
    memory_mb = round(df.memory_usage(deep=True).sum() / (1024 ** 2), 3)

    return {
        "shape": {"rows": len(df), "cols": len(df.columns)},
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": missing,
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "datetime_columns": datetime_cols,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "correlation_matrix": correlation_matrix,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "memory_usage_mb": memory_mb,
    }
