"use client";

import { useI18n } from "@/lib/i18n";
import LanguageToggle from "./LanguageToggle";

interface Props {
  onReset?: () => void;
  filename?: string;
}

export default function Navbar({ onReset, filename }: Props) {
  const { t } = useI18n();
  return (
    <header className="sticky top-0 z-30 border-b border-[var(--border-soft)] bg-[var(--bg)]/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-white shadow-[var(--shadow-sm)]">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M12 2 L14.2 9.2 L21.5 11.5 L14.2 13.8 L12 21 L9.8 13.8 L2.5 11.5 L9.8 9.2 Z"
                fill="currentColor"
              />
            </svg>
          </span>
          <span className="text-lg font-bold tracking-tight">{t("brandName")}</span>
          {filename && (
            <span className="hidden max-w-[180px] truncate rounded-full bg-[var(--surface-2)] px-2.5 py-1 text-xs text-[var(--muted)] sm:inline-block">
              {filename}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          {onReset && (
            <button
              onClick={onReset}
              className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-3.5 py-1.5 text-xs font-semibold text-[var(--text)] transition hover:border-[var(--accent)] hover:text-[var(--accent)] sm:px-4 sm:text-sm"
            >
              {t("newFile")}
            </button>
          )}
          <LanguageToggle />
        </div>
      </div>
    </header>
  );
}
