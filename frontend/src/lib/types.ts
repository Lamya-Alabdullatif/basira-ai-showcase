// Types mirroring the FastAPI backend's response shapes (see backend/app/schemas.py
// and the return dicts in backend/app/main.py). Kept hand-written and small rather
// than code-generated — the API surface is tiny and stable.

export type ColumnRole = "metric" | "dimension" | "date" | "identifier";
export type ColumnDType = "numeric" | "categorical" | "date";

export interface ColumnInfo {
  name: string;
  role: ColumnRole;
  dtype: ColumnDType;
  canonical: string | null;
  n_unique: number;
  n_missing: number;
}

export interface CleaningReport {
  rows_before: number;
  rows_after: number;
  columns_before: number;
  columns_after: number;
  duplicates_removed: number;
  empty_rows_removed: number;
  missing_filled: Record<string, number>;
  columns_renamed: Record<string, string>;
  columns_typed: Record<string, string>;
  currency_columns_parsed: string[];
  date_columns_parsed: string[];
}

export interface Kpi {
  key: string;
  label_en: string;
  label_ar: string;
  value: number | string;
  format: "int" | "number" | "text";
}

export interface ChartConfig {
  id: string;
  type: "bar" | "line" | "pie";
  title_en: string;
  title_ar: string;
  // Plotly figure dict: { data: [...], layout: {...} }. Kept loose since we
  // pass it straight through to react-plotly.js.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  figure: any;
}

export interface SmartSummary {
  summary_en: string;
  summary_ar: string;
  recommendations_en: string[];
  recommendations_ar: string[];
}

export interface UploadResponse {
  session_id: string;
  filename: string;
  row_count: number;
  cleaning_report: CleaningReport;
  columns: ColumnInfo[];
  kpis: Kpi[];
  charts: ChartConfig[];
  summary: SmartSummary;
  preview: Record<string, string>[];
}

export interface SessionResponse {
  session_id: string;
  filename: string;
  row_count: number;
  kpis: Kpi[];
  charts: ChartConfig[];
  summary: SmartSummary;
}

export interface QueryDataPoint {
  label: string;
  value: number;
  before?: number;
  after?: number;
}

export interface QueryResult {
  answer: string;
  data: QueryDataPoint[];
  chart_type: "bar" | "line" | "pie" | "kpi" | "none";
  intent: string;
  language: "ar" | "en";
  metric: string | null;
  dimension: string | null;
  period_totals?: { before: number; after: number; pct_change: number };
}

export interface ApiError {
  detail: string;
}
