import type { QueryDataPoint } from "./types";

const PALETTE = ["#6366f1", "#22d3ee", "#f472b6", "#34d399", "#fbbf24", "#a78bfa", "#fb7185", "#38bdf8"];

const baseLayout = {
  margin: { l: 40, r: 8, t: 8, b: 30 },
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: { family: "Inter, Arial, sans-serif", size: 11 },
  showlegend: false,
  xaxis: { automargin: true },
  yaxis: { automargin: true },
};

/** Turns a /api/query `data` payload into a small Plotly figure for the chat
 * bubble — same visual language as the dashboard charts, but built client-side
 * from the raw {label, value} points the query engine returns. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function buildQueryFigure(data: QueryDataPoint[], chartType: string): any | null {
  if (!data?.length || chartType === "none" || chartType === "kpi") return null;
  const labels = data.map((d) => d.label);
  const values = data.map((d) => d.value);

  if (chartType === "pie") {
    return {
      data: [{ type: "pie", labels, values, hole: 0.5, marker: { colors: PALETTE } }],
      layout: { ...baseLayout, showlegend: true, margin: { l: 8, r: 8, t: 8, b: 8 } },
    };
  }
  if (chartType === "line") {
    return {
      data: [{ type: "scatter", mode: "lines+markers", x: labels, y: values, line: { color: PALETTE[1], width: 3 } }],
      layout: baseLayout,
    };
  }
  return {
    data: [{ type: "bar", x: labels, y: values, marker: { color: PALETTE[0] } }],
    layout: baseLayout,
  };
}
