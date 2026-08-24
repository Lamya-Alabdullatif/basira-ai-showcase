"use client";

import { useI18n } from "@/lib/i18n";
import type { SmartSummary } from "@/lib/types";

interface Props {
  summary: SmartSummary;
}

export default function SummaryCard({ summary }: Props) {
  const { t, lang } = useI18n();
  const summaryText = lang === "ar" ? summary.summary_ar : summary.summary_en;
  const recs = lang === "ar" ? summary.recommendations_ar : summary.recommendations_en;

  if (!summaryText) return null;

  return (
    <div className="animate-fade-up rounded-[var(--radius)] border border-[var(--border-soft)] bg-[var(--surface)] p-5 shadow-[var(--shadow-sm)] sm:p-6">
      <div className="mb-3 flex items-center gap-2.5">
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--accent-soft)] text-[var(--accent)]">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M12 2 L14.2 9.2 L21.5 11.5 L14.2 13.8 L12 21 L9.8 13.8 L2.5 11.5 L9.8 9.2 Z" fill="currentColor" />
          </svg>
        </span>
        <p className="font-semibold">{t("summaryTitle")}</p>
      </div>
      <p className="text-sm leading-relaxed text-[var(--text)]">{summaryText}</p>

      {recs.length > 0 && (
        <div className="mt-4 border-t border-[var(--border-soft)] pt-4">
          <p className="mb-2 text-xs font-bold uppercase tracking-wide text-[var(--muted-2)]">{t("recommendationsTitle")}</p>
          <ul className="flex flex-col gap-2">
            {recs.map((r, i) => (
              <li key={i} className="flex items-start gap-2.5 text-sm text-[var(--text)]">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--accent-2)]" />
                <span className="leading-relaxed">{r}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
