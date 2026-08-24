"use client";

import { useI18n } from "@/lib/i18n";

export default function LoadingState() {
  const { t } = useI18n();
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-6 text-center">
      <div className="relative flex h-20 w-20 items-center justify-center">
        <span className="absolute inset-0 animate-pulse-ring rounded-full" />
        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-white shadow-[var(--shadow-md)]">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" className="animate-spin-slow">
            <path d="M12 3a9 9 0 1 0 9 9" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
          </svg>
        </span>
      </div>
      <div>
        <p className="text-lg font-bold">{t("processingTitle")}</p>
        <p className="mt-1.5 text-sm text-[var(--muted)]">{t("processingSubtitle")}</p>
      </div>
      <div className="flex w-full max-w-sm flex-col gap-2.5">
        <div className="h-3 w-full animate-shimmer rounded-full" />
        <div className="h-3 w-4/5 animate-shimmer rounded-full" style={{ animationDelay: "0.15s" }} />
        <div className="h-3 w-3/5 animate-shimmer rounded-full" style={{ animationDelay: "0.3s" }} />
      </div>
    </div>
  );
}
