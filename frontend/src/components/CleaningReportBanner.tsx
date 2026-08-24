"use client";

import { useState } from "react";
import { useI18n } from "@/lib/i18n";
import type { CleaningReport } from "@/lib/types";

interface Props {
  report: CleaningReport;
}

export default function CleaningReportBanner({ report }: Props) {
  const { t, pick } = useI18n();
  const [open, setOpen] = useState(false);

  const missingTotal = Object.values(report.missing_filled).reduce((a, b) => a + b, 0);

  const stats = [
    { label: t("cleaningRowsBefore"), value: report.rows_before },
    { label: t("cleaningRowsAfter"), value: report.rows_after },
    { label: t("cleaningDuplicates"), value: report.duplicates_removed },
    { label: t("cleaningMissing"), value: missingTotal },
    { label: t("cleaningCurrency"), value: report.currency_columns_parsed.length },
    { label: t("cleaningDates"), value: report.date_columns_parsed.length },
  ];

  return (
    <div className="animate-fade-up rounded-[var(--radius)] border border-[var(--border-soft)] bg-gradient-to-br from-[var(--surface)] to-[var(--surface-2)] p-5 shadow-[var(--shadow-sm)] sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--success)]/10 text-[var(--success)]">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="m5 13 4 4L19 7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
          <p className="font-semibold">{t("cleaningTitle")}</p>
        </div>
        <button
          onClick={() => setOpen((o) => !o)}
          className="text-xs font-semibold text-[var(--accent)] hover:underline"
        >
          {open ? t("cleaningHide") : t("cleaningDetails")}
        </button>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {stats.map((s) => (
          <div key={s.label} className="rounded-xl border border-[var(--border-soft)] bg-[var(--surface)] px-3 py-2.5 text-center">
            <p className="text-lg font-bold tabular-nums">{s.value.toLocaleString()}</p>
            <p className="mt-0.5 text-[11px] leading-tight text-[var(--muted)]">{s.label}</p>
          </div>
        ))}
      </div>

      {open && (
        <div className="mt-4 grid gap-3 border-t border-[var(--border-soft)] pt-4 sm:grid-cols-2">
          {report.currency_columns_parsed.length > 0 && (
            <div className="text-xs text-[var(--muted)]">
              <span className="font-semibold text-[var(--text)]">{t("cleaningCurrency")}: </span>
              {report.currency_columns_parsed.join(pick(", ", "، "))}
            </div>
          )}
          {report.date_columns_parsed.length > 0 && (
            <div className="text-xs text-[var(--muted)]">
              <span className="font-semibold text-[var(--text)]">{t("cleaningDates")}: </span>
              {report.date_columns_parsed.join(pick(", ", "، "))}
            </div>
          )}
          {Object.keys(report.missing_filled).length > 0 && (
            <div className="text-xs text-[var(--muted)] sm:col-span-2">
              <span className="font-semibold text-[var(--text)]">{t("cleaningMissing")}: </span>
              {Object.entries(report.missing_filled)
                .map(([col, n]) => `${col} (${n})`)
                .join(pick(", ", "، "))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
