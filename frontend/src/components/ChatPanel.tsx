"use client";

import { useEffect, useRef, useState } from "react";
import { askQuery, ApiClientError } from "@/lib/api";
import { buildQueryFigure } from "@/lib/buildQueryFigure";
import { useI18n } from "@/lib/i18n";
import type { ColumnInfo } from "@/lib/types";
import PlotlyChart from "./PlotlyChart";

interface Message {
  role: "user" | "assistant";
  text: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  figure?: any;
  loading?: boolean;
  error?: boolean;
}

interface Props {
  sessionId: string;
  columns: ColumnInfo[];
}

function buildSuggestions(columns: ColumnInfo[], lang: "en" | "ar"): string[] {
  const metric = columns.find((c) => c.role === "metric" && c.canonical === "revenue") ?? columns.find((c) => c.role === "metric");
  const dim = columns.find((c) => c.role === "dimension");
  const m = metric?.name ?? (lang === "ar" ? "القيمة" : "the value");
  const d = dim?.name ?? (lang === "ar" ? "الفئة" : "the category");

  if (lang === "ar") {
    return [`ما هي أعلى 5 ${d} من ناحية ${m}؟`, `أرني اتجاه ${m} مع الوقت`, `لماذا انخفض ${m}؟`, `ما هو متوسط ${m} حسب ${d}؟`];
  }
  return [`What are the top 5 ${d} by ${m}?`, `Show me the trend of ${m} over time`, `Why did ${m} decrease?`, `What is the average ${m} by ${d}?`];
}

export default function ChatPanel({ sessionId, columns }: Props) {
  const { t, lang } = useI18n();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function send(question: string) {
    const q = question.trim();
    if (!q || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: q }, { role: "assistant", text: "", loading: true }]);
    setBusy(true);
    try {
      const result = await askQuery(sessionId, q);
      const figure = buildQueryFigure(result.data, result.chart_type);
      setMessages((m) => [...m.slice(0, -1), { role: "assistant", text: result.answer, figure }]);
    } catch (err) {
      const msg = err instanceof ApiClientError ? err.message : lang === "ar" ? "تعذر معالجة السؤال." : "Couldn't process that question.";
      setMessages((m) => [...m.slice(0, -1), { role: "assistant", text: msg, error: true }]);
    } finally {
      setBusy(false);
    }
  }

  const suggestions = buildSuggestions(columns, lang);

  return (
    <div className="animate-fade-up flex flex-col overflow-hidden rounded-[var(--radius)] border border-[var(--border-soft)] bg-[var(--surface)] shadow-[var(--shadow-sm)]">
      <div className="border-b border-[var(--border-soft)] p-5">
        <div className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-[var(--accent)] to-[var(--accent-2)] text-white">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path d="M8 12h8M8 16h5M4 5h16v11a2 2 0 0 1-2 2H9l-5 4V5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </span>
          <p className="font-semibold">{t("chatTitle")}</p>
        </div>
        <p className="mt-1.5 text-sm text-[var(--muted)]">{t("chatSubtitle")}</p>
      </div>

      <div ref={scrollRef} className="flex max-h-[420px] min-h-[160px] flex-col gap-4 overflow-y-auto p-5">
        {messages.length === 0 && <p className="text-sm text-[var(--muted-2)]">{t("chatEmpty")}</p>}
        {messages.map((m, i) => (
          <div key={i} className="flex flex-col gap-2">
            <div className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed sm:max-w-[75%] ${
                  m.role === "user"
                    ? "bg-[var(--accent)] text-white"
                    : m.error
                      ? "bg-[var(--danger)]/10 text-[var(--danger)]"
                      : "bg-[var(--surface-2)] text-[var(--text)]"
                }`}
              >
                {m.loading ? (
                  <span className="flex items-center gap-1.5 py-0.5">
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current opacity-60" style={{ animationDelay: "0ms" }} />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current opacity-60" style={{ animationDelay: "120ms" }} />
                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-current opacity-60" style={{ animationDelay: "240ms" }} />
                  </span>
                ) : (
                  <p>{m.text}</p>
                )}
              </div>
            </div>
            {/* Rendered full-width rather than inside the narrow speech-bubble —
                a bar/line/pie chart needs more room than a 75%-wide bubble gives it. */}
            {m.figure && (
              <div className="rounded-xl border border-[var(--border-soft)] bg-[var(--surface)] p-2">
                <PlotlyChart figure={m.figure} height={220} />
              </div>
            )}
          </div>
        ))}
      </div>

      {messages.length === 0 && (
        <div className="flex flex-wrap gap-2 px-5 pb-3">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="rounded-full border border-[var(--border)] bg-[var(--surface-2)] px-3 py-1.5 text-xs font-medium text-[var(--text)] transition hover:border-[var(--accent)] hover:text-[var(--accent)]"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex items-center gap-2 border-t border-[var(--border-soft)] p-4"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t("chatPlaceholder")}
          disabled={busy}
          className="flex-1 rounded-full border border-[var(--border)] bg-[var(--bg)] px-4 py-2.5 text-sm outline-none transition focus:border-[var(--accent)] disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          className="shrink-0 rounded-full bg-[var(--text)] px-5 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-40"
        >
          {t("chatSend")}
        </button>
      </form>
    </div>
  );
}
