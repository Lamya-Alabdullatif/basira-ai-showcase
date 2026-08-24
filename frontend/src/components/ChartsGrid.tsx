"use client";

import { useI18n } from "@/lib/i18n";
import type { ChartConfig } from "@/lib/types";
import PlotlyChart from "./PlotlyChart";

interface Props {
  charts: ChartConfig[];
}

export default function ChartsGrid({ charts }: Props) {
  const { t, lang } = useI18n();
  if (!charts.length) return null;

  return (
    <div>
      <p className="mb-3 font-semibold">{t("chartsTitle")}</p>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {charts.map((chart, i) => (
          <div
            key={chart.id}
            className="animate-fade-up rounded-[var(--radius)] border border-[var(--border-soft)] bg-[var(--surface)] p-4 shadow-[var(--shadow-sm)] sm:p-5"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <p className="mb-2 text-sm font-semibold text-[var(--text)]">{lang === "ar" ? chart.title_ar : chart.title_en}</p>
            <PlotlyChart figure={chart.figure} height={260} />
          </div>
        ))}
      </div>
    </div>
  );
}
