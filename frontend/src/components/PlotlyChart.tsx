"use client";

import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface Props {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  figure: any;
  height?: number;
  className?: string;
}

export default function PlotlyChart({ figure, height = 260, className }: Props) {
  if (!figure) return null;
  return (
    // Chart axes/numbers always render LTR, even on the Arabic page: Plotly's
    // SVG tick-label text otherwise inherits dir="rtl" from <html> and the
    // browser bidi-reorders/clips mixed number+letter labels like "-150k".
    <div dir="ltr" className={className} style={{ width: "100%", height }}>
      <Plot
        data={figure.data}
        layout={{ ...figure.layout, autosize: true }}
        config={{ displayModeBar: false, responsive: true }}
        useResizeHandler
        style={{ width: "100%", height: "100%" }}
      />
    </div>
  );
}
