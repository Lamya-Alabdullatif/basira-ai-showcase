"""
Server-side Plotly figure generation for the dashboard. Each chart is handed
back as a plain dict (`fig.to_dict()`), ready for react-plotly.js on the
frontend to render directly — no rendering happens on the server.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from .profiling import ColumnProfile, get_date_column, get_dimensions, get_metrics, primary_metric

PALETTE = ["#6366f1", "#22d3ee", "#f472b6", "#34d399", "#fbbf24", "#a78bfa", "#fb7185", "#38bdf8"]


def _layout(fig: go.Figure, legend: bool = False) -> go.Figure:
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        template="plotly_white",
        font=dict(family="Inter, Arial, sans-serif", size=13),
        showlegend=legend,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True),
    )
    return fig


def _bar(labels, values, title_en, title_ar, chart_id) -> dict:
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=PALETTE[0])])
    _layout(fig)
    return {"id": chart_id, "type": "bar", "title_en": title_en, "title_ar": title_ar, "figure": fig.to_dict()}


def _pie(labels, values, title_en, title_ar, chart_id) -> dict:
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=PALETTE), hole=0.5)])
    _layout(fig, legend=True)
    return {"id": chart_id, "type": "pie", "title_en": title_en, "title_ar": title_ar, "figure": fig.to_dict()}


def _line(labels, values, title_en, title_ar, chart_id) -> dict:
    fig = go.Figure(data=[go.Scatter(
        x=labels, y=values, mode="lines+markers",
        line=dict(color=PALETTE[1], width=3), fill="tozeroy",
        fillcolor="rgba(34,211,238,0.08)",
    )])
    _layout(fig)
    return {"id": chart_id, "type": "line", "title_en": title_en, "title_ar": title_ar, "figure": fig.to_dict()}


def generate_chart_configs(df: pd.DataFrame, profiles: list[ColumnProfile]) -> list[dict]:
    """Picks a small, sensible default set of charts from whatever shape the
    dataset has: a top-N bar by the primary metric/dimension, a monthly trend
    line if a date column exists, a distribution pie for a second dimension,
    and a bar for a second metric if one exists. Works for any tabular
    dataset, not just the bundled sales sample."""
    charts: list[dict] = []
    metric = primary_metric(profiles)
    if metric is None:
        return charts

    dims = get_dimensions(profiles)
    date_col = get_date_column(profiles)

    if dims:
        primary_dim = dims[0]
        grouped = df.groupby(primary_dim.name)[metric.name].sum().sort_values(ascending=False).head(10)
        charts.append(_bar(
            grouped.index.astype(str).tolist(), [round(float(v), 2) for v in grouped.values],
            f"{metric.name} by {primary_dim.name}", f"{metric.name} حسب {primary_dim.name}",
            "bar_primary_dim",
        ))

    if date_col is not None:
        tmp = df[[date_col.name, metric.name]].dropna()
        tmp = tmp.assign(_period=tmp[date_col.name].dt.to_period("M").astype(str))
        grouped = tmp.groupby("_period")[metric.name].sum().sort_index()
        charts.append(_line(
            grouped.index.tolist(), [round(float(v), 2) for v in grouped.values],
            f"{metric.name} Over Time", f"{metric.name} عبر الوقت",
            "line_trend",
        ))

    pie_dim = dims[1] if len(dims) >= 2 else (dims[0] if dims else None)
    if pie_dim is not None:
        counts = df[pie_dim.name].value_counts().head(8)
        charts.append(_pie(
            counts.index.astype(str).tolist(), [int(v) for v in counts.values],
            f"{pie_dim.name} Distribution", f"توزيع {pie_dim.name}",
            "pie_dim",
        ))

    metrics_all = get_metrics(profiles)
    second_metric = next((m for m in metrics_all if m.name != metric.name), None)
    if second_metric is not None and dims:
        grouped = df.groupby(dims[0].name)[second_metric.name].sum().sort_values(ascending=False).head(10)
        charts.append(_bar(
            grouped.index.astype(str).tolist(), [round(float(v), 2) for v in grouped.values],
            f"{second_metric.name} by {dims[0].name}", f"{second_metric.name} حسب {dims[0].name}",
            "bar_second_metric",
        ))

    return charts
