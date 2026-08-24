"use client";

import { useI18n } from "@/lib/i18n";

export default function LanguageToggle() {
  const { lang, toggle } = useI18n();
  return (
    <button
      onClick={toggle}
      className="relative flex items-center rounded-full border border-[var(--border)] bg-[var(--surface)] p-1 text-xs font-semibold shadow-[var(--shadow-sm)] transition hover:shadow-[var(--shadow-md)]"
      aria-label="Toggle language"
    >
      <span
        className={`absolute top-1 bottom-1 w-9 rounded-full bg-[var(--accent)] transition-transform duration-300 ease-out ${
          lang === "ar" ? "translate-x-[-2.25rem] rtl:translate-x-[2.25rem]" : "translate-x-0"
        }`}
        style={{
          transform: lang === "en" ? "translateX(0)" : "translateX(2.25rem)",
        }}
      />
      <span className={`relative z-10 w-9 rounded-full py-1 text-center transition-colors ${lang === "en" ? "text-white" : "text-[var(--muted)]"}`}>
        EN
      </span>
      <span className={`relative z-10 w-9 rounded-full py-1 text-center transition-colors ${lang === "ar" ? "text-white" : "text-[var(--muted)]"}`}>
        عربي
      </span>
    </button>
  );
}
