"use client";

import { useI18n } from "@/lib/i18n";

export default function Footer() {
  const { t } = useI18n();
  return (
    <footer className="mt-10 border-t border-[var(--border-soft)] py-8 text-center">
      <p className="mx-auto max-w-xl px-5 text-xs leading-relaxed text-[var(--muted-2)]">{t("footerNote")}</p>
    </footer>
  );
}
