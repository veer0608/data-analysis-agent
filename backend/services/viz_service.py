import io
import base64
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — must be set before pyplot import
import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style="whitegrid", palette="muted")
FIGSIZE_LARGE = (14, 8)
FIGSIZE_SMALL = (10, 6)
DPI = 100


def _fig_to_b64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=DPI)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def generate_histograms(df: pd.DataFrame) -> str:
    """Grid of histograms for all numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return None

    n_cols = min(3, len(numeric_cols))
    n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 4 * n_rows))
    axes = np.array(axes).flatten() if len(numeric_cols) > 1 else [axes]

    for i, col in enumerate(numeric_cols):
        data = df[col].dropna()
        axes[i].hist(data, bins=30, color="#4C72B0", edgecolor="white", alpha=0.85)
        axes[i].set_title(col, fontsize=11, fontweight="bold")
        axes[i].set_xlabel("Value")
        axes[i].set_ylabel("Frequency")

    # Hide unused axes
    for j in range(len(numeric_cols), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Histograms — Numeric Columns", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    return _fig_to_b64(fig)


def generate_correlation_heatmap(df: pd.DataFrame) -> str:
    """Correlation heatmap for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        return None

    corr = df[numeric_cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))  # Show lower triangle only

    fig, ax = plt.subplots(figsize=FIGSIZE_LARGE)
    sns.heatmap(
        corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
        center=0, vmin=-1, vmax=1, square=True, linewidths=0.5,
        ax=ax, cbar_kws={"shrink": 0.8}
    )
    ax.set_title("Correlation Heatmap", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    return _fig_to_b64(fig)


def generate_box_plots(df: pd.DataFrame) -> str:
    """Box plots to visualize spread and outliers for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return None

    # Normalize columns to z-scores so very different scales don't squish the chart
    plot_df = df[numeric_cols].copy()
    for col in numeric_cols:
        std = plot_df[col].std()
        if std > 0:
            plot_df[col] = (plot_df[col] - plot_df[col].mean()) / std

    fig, ax = plt.subplots(figsize=FIGSIZE_LARGE)
    plot_df.boxplot(ax=ax, vert=True, patch_artist=True)
    ax.set_title("Box Plots (Z-Score Normalized)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Column")
    ax.set_ylabel("Z-Score")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return _fig_to_b64(fig)


def generate_bar_charts(df: pd.DataFrame) -> str:
    """Bar charts for top-10 values of categorical columns."""
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if not cat_cols:
        return None

    # Limit to first 6 categorical columns to keep chart readable
    cat_cols = cat_cols[:6]
    n_cols = min(2, len(cat_cols))
    n_rows = (len(cat_cols) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(10 * n_cols, 5 * n_rows))
    axes = np.array(axes).flatten() if len(cat_cols) > 1 else [axes]

    colors = sns.color_palette("muted", 10)
    for i, col in enumerate(cat_cols):
        vc = df[col].value_counts().head(10)
        axes[i].barh(vc.index.astype(str), vc.values, color=colors)
        axes[i].set_title(col, fontsize=11, fontweight="bold")
        axes[i].set_xlabel("Count")
        axes[i].invert_yaxis()  # Highest bar at top

    for j in range(len(cat_cols), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Top-10 Value Counts — Categorical Columns", fontsize=14, fontweight="bold")
    plt.tight_layout()
    return _fig_to_b64(fig)


def generate_scatter_matrix(df: pd.DataFrame) -> str:
    """Pairwise scatter plot matrix for numeric columns (max 5 cols)."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        return None

    plot_cols = numeric_cols[:5]  # Limit to 5 to keep matrix manageable
    sample_df = df[plot_cols].dropna().sample(min(500, len(df)), random_state=42)

    fig = plt.figure(figsize=(12, 12))
    pd.plotting.scatter_matrix(
        sample_df, alpha=0.5, figsize=(12, 12), diagonal="hist",
        color="#4C72B0", grid=True
    )
    fig = plt.gcf()
    fig.suptitle("Scatter Matrix (sampled ≤ 500 rows)", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    return _fig_to_b64(fig)


def generate_all_visualizations(df: pd.DataFrame) -> dict:
    return {
        "histograms": generate_histograms(df),
        "correlation_heatmap": generate_correlation_heatmap(df),
        "box_plots": generate_box_plots(df),
        "bar_charts": generate_bar_charts(df),
        "scatter_matrix": generate_scatter_matrix(df),
    }
