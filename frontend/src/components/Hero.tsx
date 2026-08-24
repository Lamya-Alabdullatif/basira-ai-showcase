"use client";

import { useI18n } from "@/lib/i18n";
import LanguageToggle from "./LanguageToggle";
import UploadZone from "./UploadZone";

interface Props {
  onFile: (file: File) => void;
  onSample: () => void;
  disabled?: boolean;
}

const FEATURE_KEYS = ["featureClean", "featureDashboard", "featureChat"] as const;

const FEATURE_ICONS = [
  <path key="1" d="M4 12a8 8 0 1 0 16 0 8 8 0 0 0-16 0Zm4-1 2.5 2.5L15 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />,
  <path key="2" d="M4 19V9m6 10V5m6 14v-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />,
  <path key="3" d="M8 12h8M8 16h5M4 5h16v11a2 2 0 0 1-2 2H9l-5 4V5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />,
];

export default function Hero({ onFile, onSample, disabled }: Props) {
  const { t } = useI18n();

  return (
    <div className="relative flex min-h-screen flex-col overflow-hidden">
      <div
        className="pointer-events-none absolute inset-0 -z-10 opacity-70"
        style={{
          background:
            "radial-gradient(560px circle at 15% 10%, rgba(99,102,241,0.14), transparent 60%), radial-gradient(520px circle at 85% 20%, rgba(34,211,238,0.14), transparent 60%), radial-gradient(480px circle at 50% 90%, rgba(244,114,182,0.10), transparent 60%)",
        }}
      />

      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-5 py-6 sm:px-8">
        <div className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-white shadow-[var(--shadow-sm)]">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2 L14.2 9.2 L21.5 11.5 L14.2 13.8 L12 21 L9.8 13.8 L2.5 11.5 L9.8 9.2 Z" fill="currentColor" />
            </svg>
          </span>
          <span className="text-lg font-bold tracking-tight">{t("brandName")}</span>
        </div>
        <LanguageToggle />
      </div>

      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center justify-center gap-8 px-5 py-14 text-center sm:px-8">
        <span
          className="animate-fade-up rounded-full border border-[var(--border)] bg-[var(--surface)] px-4 py-1.5 text-xs font-semibold text-[var(--accent)] shadow-[var(--shadow-sm)]"
        >
          {t("brandTagline")}
        </span>

        <h1
          className="animate-fade-up text-4xl font-extrabold leading-[1.15] tracking-tight sm:text-5xl md:text-6xl"
          style={{ animationDelay: "60ms" }}
        >
          {t("heroTitle")}
        </h1>

        <p
          className="animate-fade-up max-w-2xl text-balance text-base leading-relaxed text-[var(--muted)] sm:text-lg"
          style={{ animationDelay: "120ms" }}
        >
          {t("heroSubtitle")}
        </p>

        <UploadZone onFile={onFile} onSample={onSample} disabled={disabled} />

        <div
          className="mt-4 grid animate-fade-up grid-cols-1 gap-3 sm:grid-cols-3"
          style={{ animationDelay: "220ms" }}
        >
          {FEATURE_KEYS.map((key, i) => (
            <div
              key={key}
              className="flex items-center gap-2.5 rounded-full border border-[var(--border-soft)] bg-[var(--surface)]/70 px-4 py-2.5 text-sm font-medium text-[var(--text)] shadow-[var(--shadow-sm)]"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" className="shrink-0 text-[var(--accent)]">
                {FEATURE_ICONS[i]}
              </svg>
              {t(key)}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
