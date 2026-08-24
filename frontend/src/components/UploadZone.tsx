"use client";

import { useCallback, useRef, useState } from "react";
import { useI18n } from "@/lib/i18n";

interface Props {
  onFile: (file: File) => void;
  onSample: () => void;
  disabled?: boolean;
}

export default function UploadZone({ onFile, onSample, disabled }: Props) {
  const { t } = useI18n();
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragActive(false);
      if (disabled) return;
      const file = e.dataTransfer.files?.[0];
      if (file) onFile(file);
    },
    [onFile, disabled]
  );

  return (
    <div className="flex w-full flex-col items-center gap-4 animate-fade-up" style={{ animationDelay: "160ms" }}>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => !disabled && inputRef.current?.click()}
        className={`group flex w-full max-w-xl cursor-pointer flex-col items-center gap-4 rounded-[var(--radius)] border-2 border-dashed px-8 py-10 text-center transition-all ${
          dragActive
            ? "border-[var(--accent)] bg-[var(--accent-soft)]"
            : "border-[var(--border)] bg-[var(--surface)] hover:border-[var(--accent)]/50 hover:bg-[var(--surface-2)]"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onFile(file);
            e.target.value = "";
          }}
        />
        <span className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-white shadow-[var(--shadow-md)] transition-transform group-hover:scale-105">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M12 16V4M12 4L7 9M12 4l5 5M5 20h14"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
        <div>
          <p className="font-semibold text-[var(--text)]">{t("uploadCta")}</p>
          <p className="mt-1 text-sm text-[var(--muted)]">{t("dropHint")}</p>
        </div>
      </div>

      <div className="flex items-center gap-3 text-xs font-medium text-[var(--muted-2)]">
        <span className="h-px w-10 bg-[var(--border)]" />
        {t("sampleCta")}
        <span className="h-px w-10 bg-[var(--border)]" />
      </div>

      <button
        onClick={onSample}
        disabled={disabled}
        className="rounded-full bg-[var(--text)] px-6 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
      >
        {t("sampleCta")}
      </button>
    </div>
  );
}
