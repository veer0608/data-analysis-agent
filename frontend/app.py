"""
Data Analysis Tool — Streamlit Frontend
Communicates with the FastAPI backend at BACKEND_URL.
"""
import os
import base64
import json
import requests
import streamlit as st
import pandas as pd

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ══════════════════════════════════════════════════════════════════════════════
# Page configuration
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Data Analysis Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Data Analysis Tool — automated EDA, visualizations, and anomaly detection."},
)

# ══════════════════════════════════════════════════════════════════════════════
# Global styles
# ══════════════════════════════════════════════════════════════════════════════
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* === Reset & base typography === */
/* Apply Inter as the body default so it inherits naturally to text content */
html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
/* Force Inter on text components but NOT on icon containers */
.stMarkdown, .stText, .stMarkdown p, .stMarkdown li,
.stButton button, .stDownloadButton button,
.stTextInput input, .stNumberInput input,
.stSelectbox label, .stRadio label, .stCheckbox label,
h1, h2, h3, h4, h5, h6, p, label,
[data-testid="stMetricLabel"], [data-testid="stMetricValue"],
[data-testid="stMarkdownContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
code, pre, .stCodeBlock, [data-testid="stCodeBlock"] {
    font-family: 'JetBrains Mono', 'Courier New', monospace !important;
}

/* Critical: preserve icon fonts (Material Symbols / Icons) so toggle arrows render as glyphs */
[class*="material-symbols"],
[class*="material-icons"],
.material-symbols-rounded, .material-symbols-outlined, .material-icons,
[data-testid="stIconMaterial"],
[data-baseweb="icon"] *, [data-baseweb="icon"] svg,
i.material-icons, i[class*="material"] {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined',
                 'Material Icons' !important;
}

/* === Hide ONLY the unwanted chrome — KEEP the header so the sidebar toggle stays clickable === */
#MainMenu { display: none !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbarActions"] { display: none !important; }
footer { display: none !important; }

/* Make the header transparent but functional (so the sidebar toggle button still works) */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3rem !important;
}

/* Ensure the "collapsed sidebar" toggle button is always visible & on top */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: block !important;
    visibility: visible !important;
    z-index: 999999 !important;
}

.block-container { padding-top: 1.25rem !important; padding-bottom: 4rem !important; max-width: 1400px; }

/* === Page background (force light theme) === */
.stApp { background-color: #f8fafc !important; font-size: 16px; }
.stApp, .stApp p, .stApp span, .stApp label { color: #1e293b; }

/* === Typography === */
h1, h2, h3 { color: #0f172a !important; font-weight: 700 !important; letter-spacing: -0.025em; }
h1 { font-size: 2rem !important; margin-bottom: 0.5rem !important; }
h2 { font-size: 1.5rem !important; margin: 1.25rem 0 0.75rem 0 !important; }
h3 { font-size: 1.2rem !important; margin: 1rem 0 0.5rem 0 !important; }
h4, h5, h6 { color: #1e293b !important; font-weight: 600 !important; }
p, label, .stMarkdown p { color: #334155; line-height: 1.6; }

/* === Page header === */
.page-header {
    margin-bottom: 1.75rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e2e8f0;
}
.page-header h1 {
    margin: 0 0 0.4rem 0 !important;
    font-size: 1.75rem !important;
    color: #0f172a !important;
}
.page-header .subtitle {
    color: #64748b;
    font-size: 0.95rem;
    margin: 0;
    font-weight: 500;
}

/* === Hero (home page) === */
.hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #4f46e5 100%);
    color: white;
    padding: 2.5rem 2.75rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(30, 58, 138, 0.15);
}
.hero h1 {
    color: white !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    margin: 0 0 0.5rem 0 !important;
    letter-spacing: -0.03em;
    line-height: 1.1;
}
.hero p {
    color: rgba(255,255,255,0.92) !important;
    font-size: 1.1rem;
    margin: 0;
    line-height: 1.55;
    max-width: 720px;
}

/* === Step cards (home page) === */
.step-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-top: 12px; }
.step-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px 20px;
    transition: all 0.2s ease;
}
.step-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.06);
    border-color: #c7d2fe;
}
.step-num {
    display: inline-flex;
    align-items: center; justify-content: center;
    width: 32px; height: 32px;
    background: #eef2ff;
    color: #4f46e5;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 10px;
}
.step-title { font-size: 1rem; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.step-desc  { font-size: 0.9rem; color: #64748b; line-height: 1.5; margin: 0; }

/* === Card / panel === */
.panel {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}

/* === Status badge === */
.badge { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.02em; text-transform: uppercase; }
.badge-green  { background: #dcfce7; color: #166534; }
.badge-yellow { background: #fef3c7; color: #92400e; }
.badge-red    { background: #fee2e2; color: #991b1b; }
.badge-blue   { background: #dbeafe; color: #1e40af; }

/* === Sidebar === */
section[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    padding-top: 1.5rem;
}
section[data-testid="stSidebar"] > div:first-child { padding: 0 1rem; }
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] hr { border-color: #1e293b !important; margin: 1rem 0 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: white !important; }

.sidebar-brand {
    display: flex; align-items: center; gap: 12px;
    padding: 0 0.5rem 0.5rem 0.5rem;
    margin-bottom: 0.5rem;
}
.sidebar-brand-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}
.sidebar-brand-text {
    font-size: 1.05rem;
    font-weight: 700;
    color: white !important;
    line-height: 1.1;
}
.sidebar-brand-sub {
    font-size: 0.72rem;
    color: #94a3b8 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 2px;
}
.sidebar-section-label {
    color: #64748b !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 0 0.5rem;
    margin: 8px 0 4px 0;
}

section[data-testid="stSidebar"] .stRadio > div { gap: 2px; }
section[data-testid="stSidebar"] .stRadio label {
    background: transparent;
    padding: 9px 12px !important;
    border-radius: 8px;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    transition: background 0.15s ease;
    cursor: pointer;
    color: #cbd5e1 !important;
}
section[data-testid="stSidebar"] .stRadio label:hover { background: #1e293b; }
section[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none; }

.sidebar-dataset-card {
    background: #1e293b;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 8px;
    border: 1px solid #334155;
}
.sidebar-dataset-name { color: white !important; font-weight: 600; font-size: 0.9rem; word-break: break-word; }
.sidebar-dataset-meta { color: #94a3b8 !important; font-size: 0.78rem; margin-top: 4px; }

section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #1e293b !important;
    border-color: #334155 !important;
    color: white !important;
}

/* === Metrics === */
div[data-testid="metric-container"], div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    transition: border-color 0.15s ease;
}
div[data-testid="metric-container"]:hover, div[data-testid="stMetric"]:hover {
    border-color: #c7d2fe;
}
div[data-testid="metric-container"] label, div[data-testid="stMetric"] label {
    font-size: 0.75rem !important;
    color: #64748b !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"],
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    margin-top: 4px;
}

/* === Buttons === */
.stButton button {
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.1rem !important;
    transition: all 0.15s ease;
    letter-spacing: 0.01em;
    border: 1px solid #e2e8f0 !important;
}
.stButton button[kind="primary"] {
    background: #4f46e5 !important;
    color: white !important;
    border: 1px solid #4f46e5 !important;
    box-shadow: 0 1px 3px rgba(79, 70, 229, 0.2);
}
.stButton button[kind="primary"]:hover {
    background: #4338ca !important;
    border-color: #4338ca !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
}
.stButton button[kind="secondary"]:hover {
    background: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
}
.stDownloadButton button { background: #10b981 !important; color: white !important; border-color: #10b981 !important; }
.stDownloadButton button:hover { background: #059669 !important; border-color: #059669 !important; }

/* === Tabs === */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid #e2e8f0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px 8px 0 0;
    padding: 10px 16px !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    color: #64748b !important;
}
.stTabs [aria-selected="true"] {
    color: #4f46e5 !important;
    font-weight: 600 !important;
    background: #eef2ff !important;
}

/* === Dataframes === */
[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
}

/* === Inputs === */
[data-baseweb="input"] input, [data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
    border-radius: 8px !important;
}

/* === File uploader === */
[data-testid="stFileUploader"] section {
    background: white !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 2rem !important;
    transition: all 0.2s ease;
}
[data-testid="stFileUploader"] section:hover {
    border-color: #4f46e5 !important;
    background: #f5f7ff !important;
}

/* === Alerts === */
[data-testid="stAlert"] {
    border-radius: 10px;
    border-left-width: 4px !important;
    padding: 12px 16px !important;
}

/* === Expanders === */
.streamlit-expanderHeader {
    background: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

/* === Section spacing === */
.section-spacer { height: 1.5rem; }
.section-divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }

/* === Empty state === */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    background: white;
    border: 1px dashed #cbd5e1;
    border-radius: 12px;
}
.empty-state-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.empty-state h3 { color: #475569 !important; margin-bottom: 0.5rem !important; }
.empty-state p { color: #94a3b8; margin: 0; font-size: 0.95rem; }

/* === Stat tile === */
.stat-tile {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 14px 16px;
    display: flex; flex-direction: column; gap: 4px;
}
.stat-tile-label { font-size: 0.7rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
.stat-tile-value { font-size: 1.3rem; font-weight: 700; color: #0f172a; }

/* === HR styling === */
.element-container hr { border-color: #e2e8f0 !important; margin: 1.25rem 0 !important; }
</style>
""")


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════
def api(method: str, path: str, **kwargs):
    try:
        r = getattr(requests, method)(f"{BACKEND_URL}{path}", timeout=120, **kwargs)
        r.raise_for_status()
        return r
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach backend. Make sure the FastAPI server is running on port 8000.")
        st.stop()
    except requests.exceptions.HTTPError as e:
        detail = ""
        try:
            detail = e.response.json().get("detail", "")
        except Exception:
            pass
        st.error(f"API error {e.response.status_code}: {detail or str(e)}")
        st.stop()


def show_b64_image(b64: str, caption: str = ""):
    if b64:
        st.image(base64.b64decode(b64), caption=caption, width="stretch")


def fetch_datasets():
    return api("get", "/api/datasets").json()


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f'<div class="page-header"><h1>{title}</h1>'
        f'<p class="subtitle">{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, message: str):
    st.markdown(
        f'<div class="empty-state">'
        f'<div class="empty-state-icon">{icon}</div>'
        f'<h3>{title}</h3><p>{message}</p></div>',
        unsafe_allow_html=True,
    )


def require_dataset(active_id):
    if not active_id:
        empty_state("📭", "No dataset selected",
                    "Upload a dataset from the Upload Data page to begin analysis.")
        st.stop()


def severity_badge(pct: float) -> str:
    if pct == 0: return '<span class="badge badge-green">No anomalies</span>'
    if pct < 5:  return '<span class="badge badge-blue">Low</span>'
    if pct < 10: return '<span class="badge badge-yellow">Moderate</span>'
    return '<span class="badge badge-red">High</span>'


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════
PAGES = [
    ("🏠", "Home"),
    ("📤", "Upload Data"),
    ("🔍", "Preview & EDA"),
    ("🎨", "Visualizations"),
    ("🚨", "Anomaly Detection"),
    ("📄", "Download Report"),
    ("📜", "History"),
]

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">'
        '<div class="sidebar-brand-icon">📊</div>'
        '<div>'
        '<div class="sidebar-brand-text">Data Analysis</div>'
        '<div class="sidebar-brand-sub">Tool</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-label">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        [f"{ic}  {nm}" for ic, nm in PAGES],
        label_visibility="collapsed",
    )
    page_name = page.split("  ", 1)[1]

    # Datasets
    datasets = fetch_datasets()
    dataset_options = {f"#{d['id']} · {d['original_filename']}": d["id"] for d in datasets}

    st.markdown('<div class="sidebar-section-label" style="margin-top:1.25rem;">Active Dataset</div>',
                unsafe_allow_html=True)
    if dataset_options:
        selected_label = st.selectbox(
            "Active Dataset", options=list(dataset_options.keys()),
            label_visibility="collapsed",
        )
        active_id = dataset_options[selected_label]
        active_ds = next((d for d in datasets if d["id"] == active_id), None)
        if active_ds:
            st.markdown(
                f'<div class="sidebar-dataset-card">'
                f'<div class="sidebar-dataset-name">{active_ds["original_filename"]}</div>'
                f'<div class="sidebar-dataset-meta">'
                f'{active_ds["row_count"]:,} rows · {active_ds["col_count"]} cols · '
                f'{active_ds["file_type"].upper()}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
    else:
        active_id = None
        st.markdown(
            '<div class="sidebar-dataset-card">'
            '<div class="sidebar-dataset-name">No dataset</div>'
            '<div class="sidebar-dataset-meta">Upload a file to get started</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="position:absolute; bottom:1.5rem; left:1.5rem; right:1.5rem; '
        'color:#475569 !important; font-size:0.75rem;">'
        'v1.0 · FastAPI + Streamlit'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Home
# ══════════════════════════════════════════════════════════════════════════════
if page_name == "Home":
    st.markdown(
        '<div class="hero">'
        '<h1>Data Analysis Tool</h1>'
        '<p>Upload a dataset and instantly explore its structure, statistics, '
        'distributions, and anomalies — all in one place.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    c1.metric("Datasets", len(datasets))
    c2.metric("Formats", "CSV · XLSX · JSON")
    c3.metric("Modules", "4")
    c4.metric("Outputs", "PDF · CSV")

    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.subheader("How it works")

    steps = [
        ("Upload", "Drop a CSV, Excel, or JSON file. We parse it and store metadata for fast access."),
        ("Explore", "Run full EDA — shape, dtypes, missing values, statistics, correlations."),
        ("Visualize", "Auto-generate histograms, box plots, correlation heatmaps, and scatter matrices."),
        ("Detect anomalies", "Find outliers using IsolationForest and per-column Z-score analysis."),
        ("Export", "Download a polished PDF report with everything included."),
    ]
    cards = "".join(
        f'<div class="step-card">'
        f'<div class="step-num">{i+1}</div>'
        f'<div class="step-title">{title}</div>'
        f'<div class="step-desc">{desc}</div>'
        f'</div>'
        for i, (title, desc) in enumerate(steps)
    )
    st.markdown(f'<div class="step-grid">{cards}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Upload Data
# ══════════════════════════════════════════════════════════════════════════════
elif page_name == "Upload Data":
    page_header("Upload Dataset", "CSV, Excel, or JSON · Max 50 MB")

    uploaded = st.file_uploader(
        "Drop your file here or browse",
        type=["csv", "xlsx", "xls", "json"],
        label_visibility="collapsed",
    )

    if uploaded:
        c1, c2 = st.columns([3, 1], gap="medium", vertical_alignment="center")
        c1.markdown(
            f'<div class="panel" style="margin:0;">'
            f'<div style="display:flex; align-items:center; gap:14px;">'
            f'<div style="width:44px; height:44px; background:#eef2ff; border-radius:10px; '
            f'display:flex; align-items:center; justify-content:center; font-size:22px;">📄</div>'
            f'<div><div style="font-weight:600; color:#0f172a;">{uploaded.name}</div>'
            f'<div style="font-size:0.85rem; color:#64748b;">{uploaded.size / 1024:.1f} KB · '
            f'{uploaded.type or "auto-detect"}</div></div></div></div>',
            unsafe_allow_html=True,
        )
        if c2.button("Upload", type="primary", width="stretch"):
            with st.spinner("Uploading and parsing..."):
                r = api("post", "/api/upload",
                        files={"file": (uploaded.name, uploaded, uploaded.type)})
                data = r.json()
            st.success(f"Dataset #{data['id']} uploaded — "
                       f"{data['row_count']:,} rows × {data['col_count']} columns")
            st.rerun()

        # Preview
        with st.expander("Preview first 5 rows", expanded=True):
            try:
                if uploaded.name.endswith(".csv"):
                    preview_df = pd.read_csv(uploaded, nrows=5)
                elif uploaded.name.endswith((".xlsx", ".xls")):
                    preview_df = pd.read_excel(uploaded, nrows=5)
                else:
                    preview_df = pd.read_json(uploaded).head(5)
                st.dataframe(preview_df, width="stretch", hide_index=True)
                uploaded.seek(0)
            except Exception as e:
                st.warning(f"Local preview failed: {e}")

    # Existing datasets
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
    st.subheader("Uploaded Datasets")

    if datasets:
        rows = [{
            "ID": d["id"],
            "Filename": d["original_filename"],
            "Type": d["file_type"].upper(),
            "Size": f"{d['file_size_bytes'] / 1024:.1f} KB",
            "Rows": f"{d['row_count']:,}",
            "Cols": d["col_count"],
            "Uploaded": d["created_at"][:19].replace("T", " "),
        } for d in datasets]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

        # Delete control — cleaner than free-form number_input
        with st.expander("Delete a dataset"):
            del_options = {f"#{d['id']} — {d['original_filename']}": d["id"] for d in datasets}
            target = st.selectbox("Choose dataset to delete", options=list(del_options.keys()))
            if st.button("Delete dataset", type="secondary"):
                api("delete", f"/api/datasets/{del_options[target]}")
                st.success(f"Deleted: {target}")
                st.rerun()
    else:
        empty_state("📤", "No datasets yet", "Upload a file above to get started.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Preview & EDA
# ══════════════════════════════════════════════════════════════════════════════
elif page_name == "Preview & EDA":
    page_header("Preview & Exploratory Analysis",
                "Inspect your data and run automated EDA")
    require_dataset(active_id)

    tab_preview, tab_overview, tab_numeric, tab_categorical = st.tabs(
        ["Data Preview", "Overview", "Numeric", "Categorical"]
    )

    with tab_preview:
        n_rows = st.slider("Rows to preview", 5, 100, 10)
        with st.spinner("Loading preview..."):
            data = api("get", f"/api/analysis/{active_id}/preview",
                       params={"n": n_rows}).json()
        st.caption(f"Showing **{len(data['data'])}** of **{data['total_rows']:,}** rows · "
                   f"**{data['total_cols']}** columns")
        st.dataframe(pd.DataFrame(data["data"]), width="stretch", hide_index=True)

        st.markdown("##### Column Data Types")
        dtype_df = pd.DataFrame(
            [{"Column": k, "Type": v} for k, v in data["dtypes"].items()]
        )
        st.dataframe(dtype_df, width="stretch", hide_index=True)

    # Cache EDA so other tabs don't re-fetch
    if "eda_cache" not in st.session_state or st.session_state.get("eda_cache_id") != active_id:
        with st.spinner("Running EDA..."):
            st.session_state["eda_cache"] = api("get", f"/api/analysis/{active_id}/eda").json()
            st.session_state["eda_cache_id"] = active_id
    eda = st.session_state["eda_cache"]
    shape = eda["shape"]

    with tab_overview:
        c1, c2, c3, c4, c5 = st.columns(5, gap="small")
        c1.metric("Rows", f"{shape['rows']:,}")
        c2.metric("Columns", shape["cols"])
        c3.metric("Numeric", len(eda["numeric_columns"]))
        c4.metric("Categorical", len(eda["categorical_columns"]))
        c5.metric("Duplicates", eda["duplicate_rows"])

        st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

        c_left, c_right = st.columns([1, 1], gap="medium")
        with c_left:
            st.markdown("##### Memory")
            st.markdown(
                f'<div class="stat-tile">'
                f'<div class="stat-tile-label">Memory Usage</div>'
                f'<div class="stat-tile-value">{eda["memory_usage_mb"]} MB</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with c_right:
            missing_rows = [
                {"Column": col, "Missing": v["count"], "%": v["percentage"]}
                for col, v in eda["missing_values"].items() if v["count"] > 0
            ]
            st.markdown("##### Missing Values")
            if missing_rows:
                st.dataframe(pd.DataFrame(missing_rows),
                             width="stretch", hide_index=True)
            else:
                st.markdown('<div class="panel" style="margin:0;">'
                            '<span class="badge badge-green">Clean</span> '
                            'No missing values found in any column.</div>',
                            unsafe_allow_html=True)

    with tab_numeric:
        if eda["numeric_summary"]:
            stats_rows = []
            for col, s in eda["numeric_summary"].items():
                stats_rows.append({
                    "Column": col,
                    "Mean": s.get("mean"),
                    "Std": s.get("std"),
                    "Min": s.get("min"),
                    "25%": s.get("25%"),
                    "Median": s.get("50%"),
                    "75%": s.get("75%"),
                    "Max": s.get("max"),
                    "Skew": eda["skewness"].get(col),
                    "Kurt": eda["kurtosis"].get(col),
                })
            st.dataframe(pd.DataFrame(stats_rows),
                         width="stretch", hide_index=True)
        else:
            empty_state("📐", "No numeric columns", "This dataset has no numeric columns to analyze.")

    with tab_categorical:
        if eda["categorical_summary"]:
            for col, info in eda["categorical_summary"].items():
                with st.expander(f"{col} — {info['unique_count']} unique"):
                    vc_df = pd.DataFrame(
                        [{"Value": k, "Count": v} for k, v in info["top_values"].items()]
                    )
                    st.dataframe(vc_df, width="stretch", hide_index=True)
        else:
            empty_state("🏷️", "No categorical columns", "This dataset has no categorical columns.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Visualizations
# ══════════════════════════════════════════════════════════════════════════════
elif page_name == "Visualizations":
    page_header("Visualizations", "Auto-generated charts for every analysis dimension")
    require_dataset(active_id)

    if "viz_cache" not in st.session_state or st.session_state.get("viz_cache_id") != active_id:
        with st.spinner("Generating charts (10–20s)..."):
            st.session_state["viz_cache"] = api(
                "get", f"/api/analysis/{active_id}/visualizations"
            ).json()
            st.session_state["viz_cache_id"] = active_id
    viz = st.session_state["viz_cache"]

    tabs = st.tabs(["Histograms", "Correlation", "Box Plots", "Bar Charts", "Scatter Matrix"])

    with tabs[0]:
        if viz.get("histograms"):
            show_b64_image(viz["histograms"])
        else:
            empty_state("📊", "No histograms", "Need at least one numeric column.")
    with tabs[1]:
        if viz.get("correlation_heatmap"):
            show_b64_image(viz["correlation_heatmap"])
        else:
            empty_state("🔥", "No heatmap", "Need at least 2 numeric columns to compute correlations.")
    with tabs[2]:
        if viz.get("box_plots"):
            show_b64_image(viz["box_plots"])
            st.caption("Box plots are z-score normalized so columns with different scales fit one chart.")
        else:
            empty_state("📦", "No box plots", "Need at least one numeric column.")
    with tabs[3]:
        if viz.get("bar_charts"):
            show_b64_image(viz["bar_charts"])
        else:
            empty_state("📊", "No bar charts", "No categorical columns found.")
    with tabs[4]:
        if viz.get("scatter_matrix"):
            show_b64_image(viz["scatter_matrix"])
            st.caption("Scatter matrix uses up to 5 numeric columns and a sample of ≤500 rows.")
        else:
            empty_state("🎯", "No scatter matrix", "Need at least 2 numeric columns.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Anomaly Detection
# ══════════════════════════════════════════════════════════════════════════════
elif page_name == "Anomaly Detection":
    page_header("Anomaly Detection",
                "IsolationForest (multivariate) + Z-score (per column)")
    require_dataset(active_id)

    if "anom_cache" not in st.session_state or st.session_state.get("anom_cache_id") != active_id:
        with st.spinner("Running detection..."):
            st.session_state["anom_cache"] = api(
                "get", f"/api/analysis/{active_id}/anomalies"
            ).json()
            st.session_state["anom_cache_id"] = active_id
    result = st.session_state["anom_cache"]

    pct = result["anomaly_percentage"]
    method_short = result["method"].split("+")[0].strip()

    c1, c2, c3 = st.columns(3, gap="small")
    c1.metric("Method", method_short)
    c2.metric("Total Anomalies", result["total_anomalies"])
    c3.metric("Rate", f"{pct}%")

    st.markdown(
        f'<div style="margin:1rem 0 1.5rem 0;">'
        f'<span style="color:#64748b; font-size:0.9rem; margin-right:8px;">Severity:</span>'
        f'{severity_badge(pct)}</div>',
        unsafe_allow_html=True,
    )

    if pct > 10:
        st.warning(f"High anomaly rate ({pct}%). Worth investigating the data quality.")
    elif result["total_anomalies"] == 0:
        st.success("No significant anomalies detected.")

    # Anomalous indices
    if result["anomalous_indices"]:
        st.markdown("##### Multivariate Anomalies (IsolationForest)")
        idx = result["anomalous_indices"]
        st.caption(f"Showing first {min(50, len(idx))} of {len(idx)} flagged rows")
        idx_df = pd.DataFrame({"Row Index": idx[:50]})
        st.dataframe(idx_df, width="stretch", hide_index=True, height=240)

    # Per-column outliers
    col_outliers = result.get("column_outliers", {})
    st.markdown("##### Per-Column Z-Score Outliers")
    if col_outliers:
        rows = [{
            "Column": col,
            "Outliers": info["outlier_count"],
            "% of Column": info["outlier_percentage"],
            "Threshold": f"±{info['threshold_used']}σ",
        } for col, info in col_outliers.items()]
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        st.markdown(
            '<div class="panel" style="margin:0;">'
            '<span class="badge badge-green">Clean</span> '
            'No per-column outliers detected at the 3σ threshold.</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Download Report
# ══════════════════════════════════════════════════════════════════════════════
elif page_name == "Download Report":
    page_header("Download Analysis Report",
                "Get a polished PDF with overview, statistics, anomalies, and all visualizations")
    require_dataset(active_id)

    st.markdown(
        '<div class="panel">'
        '<div style="display:flex; align-items:center; gap:16px;">'
        '<div style="width:48px; height:48px; background:#fef3c7; border-radius:10px; '
        'display:flex; align-items:center; justify-content:center; font-size:24px;">📄</div>'
        '<div>'
        '<div style="font-weight:600; color:#0f172a; font-size:1.05rem;">Comprehensive PDF Report</div>'
        '<div style="font-size:0.9rem; color:#64748b; margin-top:2px;">'
        'Includes dataset overview, statistical summary, anomaly detection, and all charts. '
        'Generation takes 10–30 seconds.'
        '</div></div></div></div>',
        unsafe_allow_html=True,
    )

    if st.button("Generate PDF Report", type="primary", width="stretch"):
        with st.spinner("Building report — please wait..."):
            r = api("get", f"/api/reports/{active_id}/pdf")
        ds = next((d for d in datasets if d["id"] == active_id), {})
        filename = ds.get("original_filename", "report").rsplit(".", 1)[0] + "_report.pdf"
        st.session_state["pdf_bytes"] = r.content
        st.session_state["pdf_filename"] = filename
        st.success(f"Report ready ({len(r.content) / 1024:.0f} KB)")

    if st.session_state.get("pdf_bytes"):
        st.download_button(
            "⬇️ Download PDF",
            data=st.session_state["pdf_bytes"],
            file_name=st.session_state.get("pdf_filename", "report.pdf"),
            mime="application/pdf",
            width="stretch",
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: History
# ══════════════════════════════════════════════════════════════════════════════
elif page_name == "History":
    page_header("Analysis History", "Every analysis run for the active dataset")
    require_dataset(active_id)

    data = api("get", f"/api/analysis/{active_id}/history").json()
    if data:
        type_emoji = {"eda": "🔍", "visualizations": "🎨",
                      "anomaly": "🚨", "stats": "📊"}
        rows = []
        for r in data:
            try:
                summary_obj = json.loads(r.get("result_summary") or "{}")
                summary = ", ".join(f"{k}={v}" for k, v in summary_obj.items())
            except Exception:
                summary = r.get("result_summary", "") or ""
            rows.append({
                "ID": r["id"],
                "Type": f"{type_emoji.get(r['analysis_type'], '•')} {r['analysis_type']}",
                "Summary": summary[:140],
                "Run At": r["created_at"][:19].replace("T", " "),
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    else:
        empty_state("📜", "No history yet",
                    "Analyses you run on this dataset will appear here.")
