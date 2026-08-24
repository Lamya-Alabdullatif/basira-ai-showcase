"""
Rule-based bilingual (Arabic/English) natural-language query engine.

No external LLM/API — this is deterministic: normalize the question, classify
its intent from a bilingual keyword vocabulary, fuzzy-match the metric/dimension
columns it's talking about, run the matching pandas aggregation, and render the
result back into a short natural-language sentence in the same language the
question was asked in. Also produces `generate_smart_summary`, an unprompted
auto-generated overview + recommendations shown when a dataset is first loaded.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from .profiling import (
    ColumnProfile, get_dimensions, get_date_column, get_metrics, primary_metric,
)
from .vocab import COLUMN_ALIASES, INTENT_KEYWORDS, INTENT_PRIORITY, VALUE_ALIASES_AR_EN, normalize

_ARABIC_RANGE = re.compile(r"[؀-ۿ]")


def detect_language(query: str) -> str:
    return "ar" if _ARABIC_RANGE.search(query) else "en"


def classify_intent(norm_query: str) -> str:
    scores: dict[str, int] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0
        for kw in keywords:
            kw_n = normalize(kw)
            if kw_n and kw_n in norm_query:
                score += len(kw_n)
        scores[intent] = score
    best_intent, best_score = None, 0
    for intent in INTENT_PRIORITY:
        if scores.get(intent, 0) > best_score:
            best_intent, best_score = intent, scores[intent]
    return best_intent or "total"


def extract_n(query: str, default: int = 5) -> int:
    m = re.search(r"\d+", query)
    if m:
        return max(1, min(int(m.group()), 50))
    return default


def match_column(norm_query: str, candidates: list[ColumnProfile]) -> ColumnProfile | None:
    best, best_len = None, 0
    for p in candidates:
        keys = [p.name] + COLUMN_ALIASES.get(p.canonical, []) if p.canonical else [p.name]
        for k in keys:
            kn = normalize(k)
            if kn and kn in norm_query and len(kn) > best_len:
                best, best_len = p, len(kn)
    return best


def match_dimension_values(norm_query: str, df: pd.DataFrame, dim_col: ColumnProfile, max_values: int = 4) -> list:
    # translate any Arabic value names in the query to their English data-value
    # equivalent first (e.g. "الرياض" -> "Riyadh"), so Arabic queries can match
    # English-valued columns the same way English queries do.
    translated_terms = {normalize(v) for k, v in VALUE_ALIASES_AR_EN.items() if k in norm_query}

    matched = []
    for val in df[dim_col.name].dropna().unique():
        val_n = normalize(str(val))
        if val_n and (val_n in norm_query or val_n in translated_terms):
            matched.append(val)
    return matched[:max_values]


def _fmt(v: float) -> str:
    return f"{v:,.0f}" if abs(v) >= 100 else f"{v:,.2f}"


def _no_data_answer(lang: str) -> dict:
    msg = "لا يوجد عمود رقمي (مقياس) في هذه البيانات لأحلله." if lang == "ar" \
        else "This dataset doesn't have a numeric column I can analyze."
    return {"answer": msg, "data": [], "chart_type": "none"}


def _handle_top_bottom(df, raw_q, lang, metric, dim, ascending):
    if dim is None:
        return _handle_total(df, raw_q, lang, metric, None)
    n = extract_n(raw_q, default=5)
    grouped = df.groupby(dim.name)[metric.name].sum().sort_values(ascending=ascending).head(n)
    data = [{"label": str(idx), "value": round(float(val), 2)} for idx, val in grouped.items()]
    lines = "، ".join(f"{d['label']} ({_fmt(d['value'])})" for d in data) if lang == "ar" \
        else ", ".join(f"{d['label']} ({_fmt(d['value'])})" for d in data)
    if lang == "ar":
        word = "الأقل" if ascending else "الأعلى"
        answer = f"{word} {n} في {dim.name} حسب {metric.name}: {lines}."
    else:
        word = "Bottom" if ascending else "Top"
        answer = f"{word} {n} {dim.name} by {metric.name}: {lines}."
    return {"answer": answer, "data": data, "chart_type": "bar"}


def _handle_average(df, raw_q, lang, metric, dim, norm_q):
    if dim is not None and normalize(dim.name) in norm_q:
        grouped = df.groupby(dim.name)[metric.name].mean().sort_values(ascending=False)
        data = [{"label": str(i), "value": round(float(v), 2)} for i, v in grouped.items()][:8]
        lines = ("، " if lang == "ar" else ", ").join(f"{d['label']} ({_fmt(d['value'])})" for d in data)
        answer = f"متوسط {metric.name} حسب {dim.name}: {lines}." if lang == "ar" \
            else f"Average {metric.name} by {dim.name}: {lines}."
        return {"answer": answer, "data": data, "chart_type": "bar"}
    val = float(df[metric.name].mean())
    answer = f"متوسط {metric.name} هو {_fmt(val)}." if lang == "ar" else f"The average {metric.name} is {_fmt(val)}."
    return {"answer": answer, "data": [{"label": metric.name, "value": round(val, 2)}], "chart_type": "kpi"}


def _handle_total(df, raw_q, lang, metric, dim, norm_q=""):
    if dim is not None and normalize(dim.name) in norm_q:
        grouped = df.groupby(dim.name)[metric.name].sum().sort_values(ascending=False)
        data = [{"label": str(i), "value": round(float(v), 2)} for i, v in grouped.items()][:8]
        lines = ("، " if lang == "ar" else ", ").join(f"{d['label']} ({_fmt(d['value'])})" for d in data)
        answer = f"إجمالي {metric.name} حسب {dim.name}: {lines}." if lang == "ar" \
            else f"Total {metric.name} by {dim.name}: {lines}."
        return {"answer": answer, "data": data, "chart_type": "bar"}
    val = float(df[metric.name].sum())
    answer = f"إجمالي {metric.name} هو {_fmt(val)}." if lang == "ar" else f"The total {metric.name} is {_fmt(val)}."
    return {"answer": answer, "data": [{"label": metric.name, "value": round(val, 2)}], "chart_type": "kpi"}


def _handle_count(df, raw_q, lang, dim, norm_q):
    if dim is not None:
        counts = df[dim.name].value_counts()
        data = [{"label": str(i), "value": int(v)} for i, v in counts.items()][:8]
        lines = ("، " if lang == "ar" else ", ").join(f"{d['label']} ({d['value']})" for d in data)
        answer = f"عدد السجلات حسب {dim.name}: {lines}." if lang == "ar" else f"Record count by {dim.name}: {lines}."
        return {"answer": answer, "data": data, "chart_type": "bar"}
    n = len(df)
    answer = f"عدد السجلات الإجمالي هو {n:,}." if lang == "ar" else f"There are {n:,} records in total."
    return {"answer": answer, "data": [{"label": "count", "value": n}], "chart_type": "kpi"}


def _handle_distribution(df, raw_q, lang, metric, dim):
    if dim is None:
        return _handle_total(df, raw_q, lang, metric, None)
    counts = df[dim.name].value_counts(normalize=True) * 100
    data = [{"label": str(i), "value": round(float(v), 1)} for i, v in counts.items()][:8]
    lines = ("، " if lang == "ar" else ", ").join(f"{d['label']} {d['value']}%" for d in data)
    answer = f"توزيع {dim.name}: {lines}." if lang == "ar" else f"Distribution of {dim.name}: {lines}."
    return {"answer": answer, "data": data, "chart_type": "pie"}


def _handle_trend(df, raw_q, lang, metric, date_col):
    if date_col is None:
        answer = "لا يوجد عمود تاريخ لتحليل الاتجاه." if lang == "ar" else "There's no date column to analyze a trend."
        return {"answer": answer, "data": [], "chart_type": "none"}
    tmp = df[[date_col.name, metric.name]].dropna()
    tmp = tmp.assign(_period=tmp[date_col.name].dt.to_period("M").astype(str))
    grouped = tmp.groupby("_period")[metric.name].sum().sort_index()
    data = [{"label": p, "value": round(float(v), 2)} for p, v in grouped.items()]
    if len(grouped) >= 2:
        y = grouped.values.astype(float)
        x = np.arange(len(y))
        slope = float(np.polyfit(x, y, 1)[0])
        direction = "increasing" if slope > 0 else ("decreasing" if slope < 0 else "stable")
    else:
        direction = "stable"
    direction_ar = {"increasing": "تصاعدي", "decreasing": "تنازلي", "stable": "مستقر"}[direction]
    answer = f"اتجاه {metric.name} عبر الوقت {direction_ar} على مدى {len(data)} فترة شهرية." if lang == "ar" \
        else f"The trend of {metric.name} over time is {direction} across {len(data)} monthly periods."
    return {"answer": answer, "data": data, "chart_type": "line"}


def _split_halves(df: pd.DataFrame, date_col: str, metric: str, dim_name: str | None):
    cols = [date_col, metric] + ([dim_name] if dim_name else [])
    tmp = df[cols].dropna(subset=[date_col, metric]).sort_values(date_col)
    if tmp.empty:
        return None
    mid = tmp[date_col].min() + (tmp[date_col].max() - tmp[date_col].min()) / 2
    return tmp[tmp[date_col] < mid], tmp[tmp[date_col] >= mid]


def _handle_why(df, raw_q, lang, metric, dim, date_col, direction):
    if date_col is None:
        answer = f"لا أستطيع تحليل سبب تغير {metric.name} بدون عمود تاريخ في هذه البيانات." if lang == "ar" \
            else f"I can't analyze why {metric.name} changed without a date column in this dataset."
        return {"answer": answer, "data": [], "chart_type": "none"}

    halves = _split_halves(df, date_col.name, metric.name, dim.name if dim else None)
    if halves is None:
        answer = "لا توجد بيانات كافية لهذا التحليل." if lang == "ar" else "There isn't enough data for this analysis."
        return {"answer": answer, "data": [], "chart_type": "none"}
    first_half, second_half = halves
    total_first = float(first_half[metric.name].sum())
    total_second = float(second_half[metric.name].sum())
    pct_change = ((total_second - total_first) / total_first * 100) if total_first else 0.0

    data = []
    contributor_en = contributor_ar = ""
    if dim is not None:
        g1 = first_half.groupby(dim.name)[metric.name].sum()
        g2 = second_half.groupby(dim.name)[metric.name].sum()
        keys = set(g1.index) | set(g2.index)
        deltas = sorted(
            ((k, float(g2.get(k, 0.0)) - float(g1.get(k, 0.0)), float(g1.get(k, 0.0)), float(g2.get(k, 0.0))) for k in keys),
            key=lambda x: x[1],
        )
        top = deltas[:3] if direction == "decrease" else list(reversed(deltas[-3:]))
        data = [{"label": str(k), "value": round(d, 2), "before": round(v1, 2), "after": round(v2, 2)} for k, d, v1, v2 in top]
        if top:
            k0, d0, v10, v20 = top[0]
            contributor_en = f" The biggest contributor is {dim.name} = {k0}, which changed from {_fmt(v10)} to {_fmt(v20)}."
            contributor_ar = f" أكبر مساهم هو {dim.name} = {k0} حيث تغيّر من {_fmt(v10)} إلى {_fmt(v20)}."

    if lang == "ar":
        word = "انخفض" if pct_change < 0 else "ارتفع"
        answer = f"{metric.name} {word} بنسبة {abs(pct_change):.1f}% مقارنة بين الفترتين ({_fmt(total_first)} → {_fmt(total_second)}).{contributor_ar}"
    else:
        word = "decreased" if pct_change < 0 else "increased"
        answer = f"{metric.name} {word} by {abs(pct_change):.1f}% comparing the two halves of the period ({_fmt(total_first)} → {_fmt(total_second)}).{contributor_en}"

    return {
        "answer": answer, "data": data, "chart_type": "bar",
        "period_totals": {"before": round(total_first, 2), "after": round(total_second, 2), "pct_change": round(pct_change, 2)},
    }


def _handle_compare(df, raw_q, lang, metric, dim, norm_q):
    if dim is None:
        return _handle_total(df, raw_q, lang, metric, None)
    values = match_dimension_values(norm_q, df, dim, max_values=4)
    if len(values) < 2:
        grouped_all = df.groupby(dim.name)[metric.name].sum().sort_values(ascending=False)
        values = list(grouped_all.index[:2])
    sub = df[df[dim.name].isin(values)]
    grouped = sub.groupby(dim.name)[metric.name].sum()
    data = [{"label": str(v), "value": round(float(grouped.get(v, 0.0)), 2)} for v in values]
    if len(data) == 2:
        a, b = data
        diff = a["value"] - b["value"]
        pct = (diff / b["value"] * 100) if b["value"] else 0
        answer = f"{a['label']} = {_fmt(a['value'])} مقابل {b['label']} = {_fmt(b['value'])} في {metric.name} (الفرق {_fmt(diff)}, {pct:+.1f}%)." if lang == "ar" \
            else f"{a['label']} = {_fmt(a['value'])} vs {b['label']} = {_fmt(b['value'])} in {metric.name} (difference {_fmt(diff)}, {pct:+.1f}%)."
    else:
        lines = ("، " if lang == "ar" else ", ").join(f"{d['label']} ({_fmt(d['value'])})" for d in data)
        answer = f"مقارنة {metric.name}: {lines}." if lang == "ar" else f"Comparison of {metric.name}: {lines}."
    return {"answer": answer, "data": data, "chart_type": "bar"}


def answer_query(df: pd.DataFrame, profiles: list[ColumnProfile], query: str) -> dict:
    lang = detect_language(query)
    norm_q = normalize(query)
    intent = classify_intent(norm_q)

    dims = get_dimensions(profiles)
    metrics = get_metrics(profiles)
    date_col = get_date_column(profiles)

    metric = match_column(norm_q, metrics) or primary_metric(profiles)
    dim = match_column(norm_q, dims) or (dims[0] if dims else None)

    if metric is None:
        result = _no_data_answer(lang)
    elif intent == "top_n":
        result = _handle_top_bottom(df, query, lang, metric, dim, ascending=False)
    elif intent == "bottom_n":
        result = _handle_top_bottom(df, query, lang, metric, dim, ascending=True)
    elif intent == "average":
        result = _handle_average(df, query, lang, metric, dim, norm_q)
    elif intent == "count":
        result = _handle_count(df, query, lang, dim, norm_q)
    elif intent == "distribution":
        result = _handle_distribution(df, query, lang, metric, dim)
    elif intent == "trend":
        result = _handle_trend(df, query, lang, metric, date_col)
    elif intent == "why_decrease":
        result = _handle_why(df, query, lang, metric, dim, date_col, direction="decrease")
    elif intent == "why_increase":
        result = _handle_why(df, query, lang, metric, dim, date_col, direction="increase")
    elif intent == "compare":
        result = _handle_compare(df, query, lang, metric, dim, norm_q)
    else:
        result = _handle_total(df, query, lang, metric, dim, norm_q)

    result["intent"] = intent
    result["language"] = lang
    result["metric"] = metric.name if metric else None
    result["dimension"] = dim.name if dim else None
    return result


def generate_smart_summary(df: pd.DataFrame, profiles: list[ColumnProfile]) -> dict:
    """Unprompted overview + recommendations generated the moment a dataset loads —
    both languages are returned together since this isn't tied to a single question."""
    metric = primary_metric(profiles)
    dims = get_dimensions(profiles)
    date_col = get_date_column(profiles)
    if metric is None:
        return {"summary_en": "", "summary_ar": "", "recommendations_en": [], "recommendations_ar": []}

    total = float(df[metric.name].sum())
    lines_en = [f"Total {metric.name} across {len(df):,} records is {_fmt(total)}."]
    lines_ar = [f"إجمالي {metric.name} عبر {len(df):,} سجل هو {_fmt(total)}."]

    top_dim = dims[0] if dims else None
    if top_dim is not None:
        grouped = df.groupby(top_dim.name)[metric.name].sum().sort_values(ascending=False)
        if not grouped.empty:
            lines_en.append(f"{grouped.index[0]} leads in {top_dim.name} with {_fmt(float(grouped.iloc[0]))} in {metric.name}.")
            lines_ar.append(f"{grouped.index[0]} يتصدر في {top_dim.name} بـ {_fmt(float(grouped.iloc[0]))} من {metric.name}.")

    recs_en: list[str] = []
    recs_ar: list[str] = []

    if date_col is not None:
        halves = _split_halves(df, date_col.name, metric.name, top_dim.name if top_dim else None)
        if halves is not None:
            first_half, second_half = halves
            t1, t2 = float(first_half[metric.name].sum()), float(second_half[metric.name].sum())
            pct = ((t2 - t1) / t1 * 100) if t1 else 0.0
            if abs(pct) >= 3:
                word_en = "grew" if pct > 0 else "declined"
                word_ar = "نما" if pct > 0 else "تراجع"
                lines_en.append(f"{metric.name} {word_en} {abs(pct):.1f}% between the first and second half of the period.")
                lines_ar.append(f"{metric.name} {word_ar} بنسبة {abs(pct):.1f}% بين النصف الأول والثاني من الفترة.")

                if top_dim is not None:
                    g1 = first_half.groupby(top_dim.name)[metric.name].sum()
                    g2 = second_half.groupby(top_dim.name)[metric.name].sum()
                    keys = set(g1.index) | set(g2.index)
                    deltas = sorted(((k, float(g2.get(k, 0)) - float(g1.get(k, 0))) for k in keys), key=lambda x: x[1])
                    if deltas:
                        if pct < 0:
                            worst = deltas[0]
                            recs_en.append(f"Investigate {top_dim.name} \"{worst[0]}\" — it dropped by {_fmt(abs(worst[1]))} and is the largest contributor to the decline.")
                            recs_ar.append(f"راجع {top_dim.name} \"{worst[0]}\" — انخفض بمقدار {_fmt(abs(worst[1]))} وهو أكبر مساهم في التراجع.")
                        else:
                            best = deltas[-1]
                            recs_en.append(f"Double down on {top_dim.name} \"{best[0]}\" — it grew the most and is driving overall performance.")
                            recs_ar.append(f"ركّز أكثر على {top_dim.name} \"{best[0]}\" — حقق أكبر نمو ويقود الأداء العام.")

    if top_dim is not None:
        grouped = df.groupby(top_dim.name)[metric.name].sum().sort_values()
        if len(grouped) >= 2:
            weakest = grouped.index[0]
            recs_en.append(f"\"{weakest}\" is the weakest {top_dim.name} in {metric.name} — consider reviewing pricing or promotion there.")
            recs_ar.append(f"\"{weakest}\" هو الأضعف في {top_dim.name} من ناحية {metric.name} — يُنصح بمراجعة التسعير أو الترويج هناك.")

    if not recs_en:
        recs_en.append("Data looks stable overall — keep monitoring monthly trends for early signals.")
        recs_ar.append("البيانات تبدو مستقرة بشكل عام — استمر بمتابعة الاتجاهات الشهرية لرصد أي إشارات مبكرة.")

    return {
        "summary_en": " ".join(lines_en),
        "summary_ar": " ".join(lines_ar),
        "recommendations_en": recs_en[:3],
        "recommendations_ar": recs_ar[:3],
    }
