"""
Dataset profiling: classify each column's role (metric / dimension / date /
identifier) and compute the summary stats + KPI cards used by both the
dashboard and the NL query engine. Pure pandas, no external calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .vocab import COLUMN_ALIASES, normalize


@dataclass
class ColumnProfile:
    name: str
    role: str          # "metric" | "dimension" | "date" | "identifier"
    dtype: str          # "numeric" | "categorical" | "date"
    canonical: str | None = None   # matched business-term key from COLUMN_ALIASES, if any
    n_unique: int = 0
    n_missing: int = 0
    sample_values: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)


def _match_canonical(col_name: str) -> str | None:
    norm_col = normalize(col_name)
    best_key, best_len = None, 0
    for key, keywords in COLUMN_ALIASES.items():
        for kw in keywords:
            kw_norm = normalize(kw)
            if kw_norm and (kw_norm in norm_col or norm_col in kw_norm):
                if len(kw_norm) > best_len:
                    best_key, best_len = key, len(kw_norm)
    return best_key


def _looks_like_identifier(col_name: str, series: pd.Series) -> bool:
    """An identifier is a near-unique integer key (e.g. Order ID), never a
    continuous float — floats with high cardinality (Revenue, Profit, ...) are
    normal metrics, not identifiers, so only integer dtype triggers the
    cardinality check."""
    norm_col = normalize(col_name)
    if "id" in norm_col.split() or norm_col.endswith(" id") or norm_col == "id":
        return True
    if pd.api.types.is_integer_dtype(series) and series.nunique(dropna=True) >= max(1, len(series) * 0.95):
        return True
    return False


def profile_dataframe(df: pd.DataFrame) -> list[ColumnProfile]:
    profiles: list[ColumnProfile] = []
    for col in df.columns:
        s = df[col]
        canonical = _match_canonical(col)
        n_missing = int(s.isna().sum())
        n_unique = int(s.nunique(dropna=True))

        if pd.api.types.is_datetime64_any_dtype(s):
            dtype = "date"
            role = "date"
            valid = s.dropna()
            stats = {}
            if not valid.empty:
                stats = {"min": str(valid.min()), "max": str(valid.max())}
            sample = [str(v) for v in valid.head(3).tolist()]
        elif pd.api.types.is_numeric_dtype(s):
            dtype = "numeric"
            if _looks_like_identifier(col, s):
                role = "identifier"
            else:
                role = "metric"
            valid = s.dropna()
            stats = {}
            if not valid.empty:
                stats = {
                    "min": float(valid.min()),
                    "max": float(valid.max()),
                    "mean": float(valid.mean()),
                    "median": float(valid.median()),
                    "sum": float(valid.sum()),
                }
            sample = [float(v) for v in valid.head(3).tolist()]
        else:
            dtype = "categorical"
            role = "identifier" if _looks_like_identifier(col, s) else "dimension"
            stats = {}
            sample = [str(v) for v in s.dropna().unique().tolist()[:5]]

        profiles.append(ColumnProfile(
            name=col, role=role, dtype=dtype, canonical=canonical,
            n_unique=n_unique, n_missing=n_missing, sample_values=sample, stats=stats,
        ))
    return profiles


def get_metrics(profiles: list[ColumnProfile]) -> list[ColumnProfile]:
    return [p for p in profiles if p.role == "metric"]


def get_dimensions(profiles: list[ColumnProfile]) -> list[ColumnProfile]:
    return [p for p in profiles if p.role == "dimension"]


def get_date_column(profiles: list[ColumnProfile]) -> ColumnProfile | None:
    dates = [p for p in profiles if p.role == "date"]
    return dates[0] if dates else None


def primary_metric(profiles: list[ColumnProfile]) -> ColumnProfile | None:
    """Prefer a column matched to 'revenue', else the metric with the largest sum."""
    metrics = get_metrics(profiles)
    if not metrics:
        return None
    for p in metrics:
        if p.canonical == "revenue":
            return p
    return max(metrics, key=lambda p: p.stats.get("sum", 0))


def build_kpis(df: pd.DataFrame, profiles: list[ColumnProfile]) -> list[dict]:
    """Business-generic KPI cards: total/avg for each metric, row count, top dimension value,
    and date range if available. Works for any dataset shape, not just the sales sample."""
    kpis: list[dict] = []
    kpis.append({
        "key": "row_count",
        "label_en": "Total Records",
        "label_ar": "إجمالي السجلات",
        "value": int(len(df)),
        "format": "int",
    })

    metrics = get_metrics(profiles)
    for m in metrics[:4]:
        kpis.append({
            "key": f"total_{m.name}",
            "label_en": f"Total {m.name}",
            "label_ar": f"إجمالي {m.name}",
            "value": round(m.stats.get("sum", 0), 2),
            "format": "number",
        })
    for m in metrics[:2]:
        kpis.append({
            "key": f"avg_{m.name}",
            "label_en": f"Average {m.name}",
            "label_ar": f"متوسط {m.name}",
            "value": round(m.stats.get("mean", 0), 2),
            "format": "number",
        })

    dims = get_dimensions(profiles)
    pm = primary_metric(profiles)
    if dims and pm:
        top_dim = dims[0]
        grouped = df.groupby(top_dim.name)[pm.name].sum().sort_values(ascending=False)
        if not grouped.empty:
            kpis.append({
                "key": f"top_{top_dim.name}",
                "label_en": f"Top {top_dim.name}",
                "label_ar": f"الأعلى في {top_dim.name}",
                "value": str(grouped.index[0]),
                "format": "text",
            })

    date_col = get_date_column(profiles)
    if date_col and date_col.stats:
        kpis.append({
            "key": "date_range",
            "label_en": "Date Range",
            "label_ar": "الفترة الزمنية",
            "value": f"{date_col.stats['min'][:10]} → {date_col.stats['max'][:10]}",
            "format": "text",
        })

    return kpis
