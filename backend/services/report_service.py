import io
import base64
from datetime import datetime
from fpdf import FPDF


# Replace common Unicode chars that fpdf's latin-1 Helvetica can't encode
_UNICODE_REPLACEMENTS = {
    "—": "-", "–": "-",       # em-dash, en-dash
    "‘": "'", "’": "'",       # smart single quotes
    "“": '"', "”": '"',       # smart double quotes
    "…": "...",                    # ellipsis
    "•": "*",                      # bullet
    "→": "->", "←": "<-",     # arrows
    "↔": "<->", "⇒": "=>",
    "≤": "<=", "≥": ">=", "≠": "!=",
    "×": "x", "±": "+/-",     # multiplication sign, plus-minus
    "°": " deg",                   # degree sign
    "σ": "sigma", "μ": "mu",  # common Greek letters
    "α": "alpha", "β": "beta",
}


def _sanitize(text) -> str:
    """Make any string safe for fpdf's latin-1 Helvetica encoding."""
    if text is None:
        return ""
    s = str(text)
    for src, dst in _UNICODE_REPLACEMENTS.items():
        s = s.replace(src, dst)
    # Strip any remaining non-latin-1 characters
    return s.encode("latin-1", errors="replace").decode("latin-1")


class AnalysisReport(FPDF):
    """Custom PDF class with header/footer branding."""

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(70, 70, 70)
        self.cell(0, 8, _sanitize("Data Analysis Tool - Automated Report"), align="R")
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, _sanitize(
            f"Page {self.page_no()} | Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
        ), align="C")


def _section_title(pdf: FPDF, title: str):
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 80, 160)
    pdf.ln(6)
    pdf.set_x(pdf.l_margin)
    pdf.cell(0, 8, _sanitize(title))
    pdf.ln(8)
    pdf.set_draw_color(40, 80, 160)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)


def _body_text(pdf: FPDF, text: str, font_size: int = 10):
    pdf.set_font("Helvetica", size=font_size)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(w=pdf.epw, h=6, text=_sanitize(text))
    pdf.ln(1)


def _bullet(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", size=10)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(w=pdf.epw, h=6, text=_sanitize(f"  * {text}"))


def _embed_image(pdf: FPDF, b64_str: str, title: str):
    """Decode a base64 PNG and embed it in the PDF."""
    try:
        img_data = base64.b64decode(b64_str)
        buf = io.BytesIO(img_data)
        pdf.ln(2)
        _body_text(pdf, title, font_size=11)
        x = pdf.get_x()
        y = pdf.get_y()
        page_width = pdf.w - 2 * pdf.l_margin
        pdf.image(buf, x=x, y=y, w=page_width)
        pdf.ln(page_width * 0.55)  # Approximate height offset for landscape charts
    except Exception:
        _body_text(pdf, f"[Could not embed image: {title}]")


def _fmt(val, spec=".4g"):
    """Safely format a value that might be None or NaN."""
    if val is None:
        return "N/A"
    try:
        return format(val, spec)
    except (ValueError, TypeError):
        return str(val)


def generate_pdf_report(
    dataset_name: str,
    eda: dict,
    anomalies: dict,
    visualizations: dict,
) -> bytes:
    """Build a full-page PDF report and return it as bytes."""
    pdf = AnalysisReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Title ──────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(40, 80, 160)
    pdf.set_x(pdf.l_margin)
    pdf.cell(w=pdf.epw, h=12, text=_sanitize("Data Analysis Report"), align="C")
    pdf.ln(12)
    pdf.set_font("Helvetica", size=12)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(pdf.l_margin)
    pdf.cell(w=pdf.epw, h=8, text=_sanitize(f"Dataset: {dataset_name}"), align="C")
    pdf.ln(8)
    pdf.set_x(pdf.l_margin)
    pdf.cell(w=pdf.epw, h=6,
             text=_sanitize(f"Generated: {datetime.utcnow().strftime('%B %d, %Y  %H:%M UTC')}"),
             align="C")
    pdf.ln(6)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # ── Dataset Overview ───────────────────────────────────────────────────
    _section_title(pdf, "1. Dataset Overview")
    shape = eda.get("shape", {})
    _body_text(pdf, f"Rows: {shape.get('rows', 'N/A')}    Columns: {shape.get('cols', 'N/A')}")
    _body_text(pdf, f"Memory Usage: {eda.get('memory_usage_mb', 0)} MB")
    _body_text(pdf, f"Duplicate Rows: {eda.get('duplicate_rows', 0)}")
    _body_text(pdf, f"Numeric Columns: {', '.join(eda.get('numeric_columns', [])) or 'None'}")
    _body_text(pdf, f"Categorical Columns: {', '.join(eda.get('categorical_columns', [])) or 'None'}")

    missing = {k: v for k, v in eda.get("missing_values", {}).items() if v["count"] > 0}
    if missing:
        _body_text(pdf, "Missing Values:")
        for col, info in missing.items():
            _bullet(pdf, f"{col}: {info['count']} missing ({info['percentage']}%)")
    else:
        _body_text(pdf, "No missing values detected.")

    # ── Statistical Summary ────────────────────────────────────────────────
    _section_title(pdf, "2. Statistical Summary")
    for col, stats in eda.get("numeric_summary", {}).items():
        _body_text(pdf, f"{col}:", font_size=10)
        line = (
            f"  Mean={_fmt(stats.get('mean'))}  Std={_fmt(stats.get('std'))}  "
            f"Min={_fmt(stats.get('min'))}  Max={_fmt(stats.get('max'))}  "
            f"Skew={_fmt(eda['skewness'].get(col), '.3g')}"
        )
        _body_text(pdf, line, font_size=9)

    # ── Anomaly Detection ──────────────────────────────────────────────────
    _section_title(pdf, "3. Anomaly Detection")
    _body_text(pdf, f"Method: {anomalies.get('method', 'N/A')}")
    _body_text(pdf, f"Total Anomalies: {anomalies.get('total_anomalies', 0)} "
               f"({anomalies.get('anomaly_percentage', 0)}% of rows)")
    col_outliers = anomalies.get("column_outliers", {})
    if col_outliers:
        _body_text(pdf, "Per-Column Outliers (Z-Score):")
        for col, info in col_outliers.items():
            _bullet(pdf, f"{col}: {info['outlier_count']} outliers ({info['outlier_percentage']}%)")

    # ── Visualizations ─────────────────────────────────────────────────────
    _section_title(pdf, "4. Visualizations")
    viz_map = {
        "histograms": "Histograms",
        "correlation_heatmap": "Correlation Heatmap",
        "box_plots": "Box Plots",
        "bar_charts": "Bar Charts",
    }
    for key, label in viz_map.items():
        img = visualizations.get(key)
        if img:
            pdf.add_page()
            _embed_image(pdf, img, label)

    return pdf.output()
