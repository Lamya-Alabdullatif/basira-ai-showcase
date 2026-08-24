"""
Automatic data cleaning pipeline.

Design goal: take whatever messy CSV/Excel a user drops in and turn it into a
tidy, typed pandas DataFrame — while keeping a transparent, human-readable
report of exactly what was changed. Nothing here is a black box: every
transformation is logged so the report can be shown to the user.
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass, field

import pandas as pd


CURRENCY_RE = re.compile(r"[^\d.\-]")


def _is_textual(s: pd.Series) -> bool:
    """True for legacy object-dtype text columns AND pandas' newer native
    string dtype (pandas >= 2.x/3.x defaults CSV text columns to StringDtype,
    not object) — both need to be treated as "text" for cleaning purposes."""
    return pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s)


@dataclass
class CleaningReport:
    rows_before: int = 0
    rows_after: int = 0
    columns_before: int = 0
    columns_after: int = 0
    duplicates_removed: int = 0
    empty_rows_removed: int = 0
    missing_filled: dict = field(default_factory=dict)   # column -> count filled
    columns_renamed: dict = field(default_factory=dict)   # original -> cleaned
    columns_typed: dict = field(default_factory=dict)     # column -> detected type
    currency_columns_parsed: list = field(default_factory=list)
    date_columns_parsed: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rows_before": self.rows_before,
            "rows_after": self.rows_after,
            "columns_before": self.columns_before,
            "columns_after": self.columns_after,
            "duplicates_removed": self.duplicates_removed,
            "empty_rows_removed": self.empty_rows_removed,
            "missing_filled": self.missing_filled,
            "columns_renamed": self.columns_renamed,
            "columns_typed": self.columns_typed,
            "currency_columns_parsed": self.currency_columns_parsed,
            "date_columns_parsed": self.date_columns_parsed,
        }


def read_any(filename: str, content: bytes) -> pd.DataFrame:
    """Read a CSV or Excel file from raw bytes into a DataFrame."""
    lower = filename.lower()
    buf = io.BytesIO(content)
    if lower.endswith((".xlsx", ".xls")):
        return pd.read_excel(buf)
    # default to csv; try a couple of common encodings
    for enc in ("utf-8", "utf-8-sig", "cp1256", "latin1"):
        try:
            buf.seek(0)
            return pd.read_csv(buf, encoding=enc)
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    buf.seek(0)
    return pd.read_csv(buf, encoding="utf-8", errors="replace")


def _clean_column_name(name: str) -> str:
    name = str(name).strip()
    name = re.sub(r"\s+", " ", name)
    return name


def _try_parse_currency_series(s: pd.Series) -> tuple[pd.Series, bool]:
    """If a text column looks like currency/number-with-symbols, parse it to float."""
    sample = s.dropna().astype(str).head(30)
    if sample.empty:
        return s, False
    looks_numeric = sample.str.match(r"^\s*[\$\€\£]?\s*(?:SAR)?\s*-?[\d,]+(\.\d+)?\s*$", na=False)
    if looks_numeric.mean() < 0.6:
        return s, False
    parsed = s.astype(str).apply(lambda v: CURRENCY_RE.sub("", v) if v.strip() else v)
    parsed = pd.to_numeric(parsed, errors="coerce")
    return parsed, True


def _try_parse_dates(s: pd.Series) -> tuple[pd.Series, bool]:
    if not _is_textual(s):
        return s, False
    sample = s.dropna().astype(str).head(30)
    if sample.empty:
        return s, False
    parsed_sample = pd.to_datetime(sample, errors="coerce", format="mixed")
    if parsed_sample.notna().mean() < 0.8:
        return s, False
    parsed = pd.to_datetime(s, errors="coerce", format="mixed")
    return parsed, True


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    report = CleaningReport()
    report.rows_before = len(df)
    report.columns_before = len(df.columns)

    # 1. Clean column names
    renamed = {}
    new_cols = []
    for c in df.columns:
        cleaned = _clean_column_name(c)
        if cleaned != c:
            renamed[c] = cleaned
        new_cols.append(cleaned)
    df.columns = new_cols
    report.columns_renamed = renamed

    # 2. Strip whitespace + normalize case artifacts on text (object) columns
    for col in df.columns:
        if _is_textual(df[col]):
            df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)
            df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA, "None": pd.NA, "N/A": pd.NA, "n/a": pd.NA})

    # 3. Drop fully empty rows
    before = len(df)
    df = df.dropna(how="all")
    report.empty_rows_removed = before - len(df)

    # 4. Remove exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    report.duplicates_removed = before - len(df)

    # 5. Try to detect & parse date columns (content-based: most values parse as dates)
    for col in df.columns:
        if _is_textual(df[col]):
            parsed, ok = _try_parse_dates(df[col])
            if ok:
                df[col] = parsed
                report.date_columns_parsed.append(col)

    # 6. Try to detect & parse currency-like text columns into numeric
    for col in df.columns:
        if _is_textual(df[col]):
            parsed, ok = _try_parse_currency_series(df[col])
            if ok:
                df[col] = parsed
                report.currency_columns_parsed.append(col)

    # 7. Fill missing values (typed-aware) + normalize casing on categorical text
    for col in df.columns:
        n_missing = int(df[col].isna().sum())
        if n_missing == 0:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            fill_value = df[col].median()
            df[col] = df[col].fillna(fill_value)
            report.missing_filled[col] = n_missing
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            continue  # leave missing dates as NaT — filling dates would fabricate data
        else:
            df[col] = df[col].fillna("Unknown")
            report.missing_filled[col] = n_missing

    # 8. Normalize inconsistent casing on short categorical text columns
    for col in df.columns:
        if _is_textual(df[col]):
            nunique = df[col].nunique(dropna=True)
            if 0 < nunique <= 60:
                mapping = {}
                for val in df[col].dropna().unique():
                    key = str(val).strip().lower()
                    mapping.setdefault(key, []).append(val)
                canonical = {}
                for key, variants in mapping.items():
                    # prefer the Title Case version if present, else the most common variant
                    title_variant = next((v for v in variants if str(v).istitle()), None)
                    canonical[key] = title_variant or max(set(variants), key=variants.count)
                df[col] = df[col].apply(lambda v: canonical[str(v).strip().lower()] if pd.notna(v) else v)

    # 9. Record final types
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            report.columns_typed[col] = "date"
        elif pd.api.types.is_numeric_dtype(df[col]):
            report.columns_typed[col] = "numeric"
        else:
            report.columns_typed[col] = "categorical"

    df = df.reset_index(drop=True)
    report.rows_after = len(df)
    report.columns_after = len(df.columns)
    return df, report
