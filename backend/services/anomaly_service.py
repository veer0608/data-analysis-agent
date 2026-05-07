import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from services.data_service import serialize


def _zscore_outliers(df: pd.DataFrame, threshold: float = 3.0) -> dict:
    """Per-column Z-score outlier detection for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    column_outliers = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if series.std() == 0:
            continue
        z_scores = np.abs((series - series.mean()) / series.std())
        outlier_indices = z_scores[z_scores > threshold].index.tolist()
        if outlier_indices:
            column_outliers[col] = {
                "outlier_count": len(outlier_indices),
                "outlier_percentage": round(len(outlier_indices) / len(series) * 100, 2),
                "threshold_used": threshold,
                "sample_indices": outlier_indices[:20],  # cap for JSON size
            }
    return column_outliers


def detect_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> dict:
    """
    Run IsolationForest on numeric columns for multivariate anomaly detection,
    plus per-column Z-score outlier analysis.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    column_outliers = _zscore_outliers(df)

    if len(numeric_cols) < 2:
        return {
            "method": "z-score (IsolationForest requires ≥ 2 numeric columns)",
            "total_anomalies": sum(v["outlier_count"] for v in column_outliers.values()),
            "anomaly_percentage": 0.0,
            "anomalous_indices": [],
            "column_outliers": column_outliers,
            "anomaly_scores": None,
        }

    # Drop rows with any NaN in numeric columns for the model
    numeric_df = df[numeric_cols].dropna()
    if len(numeric_df) < 10:
        return {
            "method": "insufficient data",
            "total_anomalies": 0,
            "anomaly_percentage": 0.0,
            "anomalous_indices": [],
            "column_outliers": column_outliers,
            "anomaly_scores": None,
        }

    scaler = StandardScaler()
    X = scaler.fit_transform(numeric_df)

    iso = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
    labels = iso.fit_predict(X)            # -1 = anomaly, 1 = normal
    scores = iso.score_samples(X).tolist() # lower = more anomalous

    anomaly_mask = labels == -1
    anomalous_indices = numeric_df.index[anomaly_mask].tolist()
    total_anomalies = int(anomaly_mask.sum())
    anomaly_pct = round(total_anomalies / len(numeric_df) * 100, 2)

    return {
        "method": "IsolationForest + Z-Score per column",
        "total_anomalies": total_anomalies,
        "anomaly_percentage": anomaly_pct,
        "anomalous_indices": [int(i) for i in anomalous_indices[:100]],  # cap for JSON
        "column_outliers": serialize(column_outliers),
        "anomaly_scores": [round(s, 4) for s in scores[:500]],  # cap for JSON
    }
