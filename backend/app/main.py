"""
FastAPI backend for Basira — upload/clean a CSV or Excel file, profile it,
generate KPI cards + Plotly chart configs + a smart summary, and answer
bilingual natural-language questions against it. No external AI API: the
cleaning, charting, and query-answering are all deterministic pandas + rule-
based logic (see cleaning.py / profiling.py / nlq.py / charts.py).
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .charts import generate_chart_configs
from .cleaning import clean_dataframe, read_any
from .nlq import answer_query, generate_smart_summary
from .profiling import build_kpis, profile_dataframe
from .schemas import QueryRequest
from .session_store import create_session, get_session

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_sales.csv"
MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15MB — generous for a portfolio demo, not a production ingest limit
ALLOWED_EXTENSIONS = (".csv", ".xlsx", ".xls")

app = FastAPI(
    title="Basira API",
    description="Upload a spreadsheet, get an instant cleaned dashboard and a bilingual AI Q&A layer over it.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    # Open CORS is fine here: there's no auth or per-user data separation in this
    # portfolio-scale demo (see session_store.py) — every session is anonymous and
    # self-contained, so there's nothing cross-origin requests could leak.
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _process(filename: str, content: bytes) -> dict:
    try:
        df = read_any(filename, content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read this file: {exc}") from exc
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="The file has no rows to analyze.")

    df, report = clean_dataframe(df)
    profiles = profile_dataframe(df)
    session = create_session(df, profiles, filename)
    kpis = build_kpis(df, profiles)
    charts = generate_chart_configs(df, profiles)
    summary = generate_smart_summary(df, profiles)

    return {
        "session_id": session.session_id,
        "filename": filename,
        "row_count": len(df),
        "cleaning_report": report.to_dict(),
        "columns": [
            {
                "name": p.name, "role": p.role, "dtype": p.dtype,
                "canonical": p.canonical, "n_unique": p.n_unique, "n_missing": p.n_missing,
            }
            for p in profiles
        ],
        "kpis": kpis,
        "charts": charts,
        "summary": summary,
        "preview": df.head(10).astype(str).to_dict(orient="records"),
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Please upload a .csv, .xlsx, or .xls file.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File is too large (max 15MB for this demo).")
    return _process(file.filename, content)


@app.get("/api/sample")
def sample():
    if not SAMPLE_PATH.exists():
        raise HTTPException(status_code=500, detail="Sample dataset is missing on the server.")
    content = SAMPLE_PATH.read_bytes()
    return _process("sample_sales.csv", content)


@app.post("/api/query")
def query(req: QueryRequest):
    session = get_session(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found or expired — please re-upload or reload the sample data.")
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return answer_query(session.df, session.profiles, req.query)


@app.get("/api/session/{session_id}")
def session_data(session_id: str):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    return {
        "session_id": session.session_id,
        "filename": session.filename,
        "row_count": len(session.df),
        "kpis": build_kpis(session.df, session.profiles),
        "charts": generate_chart_configs(session.df, session.profiles),
        "summary": generate_smart_summary(session.df, session.profiles),
    }
