"use client";

import { useI18n } from "@/lib/i18n";

interface Props {
  message: string;
  onRetry: () => void;
}

export default function ErrorState({ message, onRetry }: Props) {
  const { t } = useI18n();
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-5 px-6 text-center">
      <span className="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--danger)]/10 text-[var(--danger)]">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
          <path
            d="M12 9v4m0 4h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </span>
      <div>
        <p className="text-lg font-bold">{t("errorTitle")}</p>
        <p className="mt-1.5 max-w-sm text-sm text-[var(--muted)]">{message}</p>
      </div>
      <button
        onClick={onRetry}
        className="rounded-full bg-[var(--text)] px-6 py-2.5 text-sm font-semibold text-white transition hover:opacity-90"
      >
        {t("tryAgain")}
      </button>
    </div>
  );
}
