"use client";

import { useI18n } from "@/lib/i18n";
import type { Kpi } from "@/lib/types";

interface Props {
  kpis: Kpi[];
}

function formatValue(kpi: Kpi): string {
  if (kpi.format === "text") return String(kpi.value);
  const n = Number(kpi.value);
  if (Number.isNaN(n)) return String(kpi.value);
  // Large numbers (e.g. 2,351,426.96) don't fit a 2-column mobile card at
  // readable font size — compact-notation them ("2.35M") instead of relying
  // on ellipsis truncation, which hides the magnitude entirely.
  if (Math.abs(n) >= 100_000) {
    return n.toLocaleString(undefined, { notation: "compact", maximumFractionDigits: 2 });
  }
  return n.toLocaleString(undefined, { maximumFractionDigits: kpi.format === "int" ? 0 : 2 });
}

function fullValue(kpi: Kpi): string | undefined {
  if (kpi.format === "text") return undefined;
  const n = Number(kpi.value);
  if (Number.isNaN(n) || Math.abs(n) < 100_000) return undefined;
  return n.toLocaleString(undefined, { maximumFractionDigits: kpi.format === "int" ? 0 : 2 });
}

const ACCENTS = ["var(--accent)", "var(--accent-2)", "var(--accent-3)"];

export default function KpiCards({ kpis }: Props) {
  const { lang } = useI18n();
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
      {kpis.map((kpi, i) => (
        <div
          key={kpi.key}
          className="animate-fade-up rounded-2xl border border-[var(--border-soft)] bg-[var(--surface)] p-4 shadow-[var(--shadow-sm)]"
          style={{ animationDelay: `${i * 40}ms` }}
        >
          <div className="mb-2 h-1.5 w-8 rounded-full" style={{ background: ACCENTS[i % ACCENTS.length] }} />
          <p
            title={fullValue(kpi)}
            className={`font-extrabold tabular-nums ${
              kpi.format === "text" ? "text-base leading-snug" : "truncate text-2xl"
            }`}
          >
            {formatValue(kpi)}
          </p>
          <p className="mt-1 truncate text-xs font-medium text-[var(--muted)]">{lang === "ar" ? kpi.label_ar : kpi.label_en}</p>
        </div>
      ))}
    </div>
  );
}
