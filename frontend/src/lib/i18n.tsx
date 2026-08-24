"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

export type Lang = "en" | "ar";

const dict = {
  brandName: { en: "Basira", ar: "بصيرة" },
  brandTagline: {
    en: "See what your data is trying to tell you.",
    ar: "اكتشف ما تحاول بياناتك إخبارك به.",
  },
  heroTitle: {
    en: "Turn any spreadsheet into instant insight.",
    ar: "حوّل أي جدول بيانات إلى رؤى فورية.",
  },
  heroSubtitle: {
    en: "Upload a CSV or Excel file. Basira cleans it automatically, builds an interactive dashboard, and answers your questions about it in plain Arabic or English — no setup, no external AI key.",
    ar: "ارفع ملف CSV أو Excel، وستقوم بصيرة بتنظيفه تلقائيًا، وبناء لوحة تحكم تفاعلية، والإجابة على أسئلتك عنه بلغة عربية أو إنجليزية بسيطة — دون أي إعداد أو مفتاح ذكاء اصطناعي خارجي.",
  },
  uploadCta: { en: "Upload your file", ar: "ارفع ملفك" },
  sampleCta: { en: "Try with sample data", ar: "جرّب ببيانات تجريبية" },
  dropHint: { en: "or drag & drop a .csv / .xlsx file here", ar: "أو اسحب وأفلت ملف CSV أو Excel هنا" },
  featureClean: { en: "Automatic data cleaning", ar: "تنظيف تلقائي للبيانات" },
  featureDashboard: { en: "Instant visual dashboard", ar: "لوحة تحكم مرئية فورية" },
  featureChat: { en: "Ask questions in Arabic or English", ar: "اسأل أسئلتك بالعربية أو الإنجليزية" },
  processingTitle: { en: "Reading & cleaning your data…", ar: "جارٍ قراءة البيانات وتنظيفها…" },
  processingSubtitle: {
    en: "Detecting column types, fixing formatting, and building your dashboard.",
    ar: "يتم تحديد أنواع الأعمدة، وإصلاح التنسيق، وبناء لوحة التحكم الخاصة بك.",
  },
  errorTitle: { en: "Something went wrong", ar: "حدث خطأ ما" },
  tryAgain: { en: "Try again", ar: "حاول مرة أخرى" },
  newFile: { en: "New file", ar: "ملف جديد" },
  rows: { en: "rows", ar: "صف" },
  cleaningTitle: { en: "Your data was cleaned automatically", ar: "تم تنظيف بياناتك تلقائيًا" },
  cleaningRowsBefore: { en: "Rows before", ar: "الصفوف قبل" },
  cleaningRowsAfter: { en: "Rows after", ar: "الصفوف بعد" },
  cleaningDuplicates: { en: "Duplicates removed", ar: "صفوف مكررة محذوفة" },
  cleaningMissing: { en: "Missing values filled", ar: "قيم مفقودة تمت تعبئتها" },
  cleaningCurrency: { en: "Currency columns parsed", ar: "أعمدة عملة تم تحويلها" },
  cleaningDates: { en: "Date columns detected", ar: "أعمدة تاريخ تم اكتشافها" },
  cleaningDetails: { en: "View details", ar: "عرض التفاصيل" },
  cleaningHide: { en: "Hide details", ar: "إخفاء التفاصيل" },
  summaryTitle: { en: "Smart summary", ar: "ملخص ذكي" },
  recommendationsTitle: { en: "Recommendations", ar: "توصيات" },
  chartsTitle: { en: "Dashboard", ar: "لوحة التحكم" },
  chatTitle: { en: "Ask Basira", ar: "اسأل بصيرة" },
  chatSubtitle: {
    en: "Ask about your data in Arabic or English — try one of the suggestions or type your own question.",
    ar: "اسأل عن بياناتك بالعربية أو الإنجليزية — جرّب أحد الاقتراحات أو اكتب سؤالك الخاص.",
  },
  chatPlaceholder: { en: "e.g. What are the top 5 regions by revenue?", ar: "مثال: ما هي أعلى 5 مناطق من ناحية الإيرادات؟" },
  chatSend: { en: "Ask", ar: "اسأل" },
  chatEmpty: { en: "Ask your first question about this data.", ar: "اطرح سؤالك الأول حول هذه البيانات." },
  chatThinking: { en: "Analyzing…", ar: "جارٍ التحليل…" },
  footerNote: {
    en: "All cleaning, charting, and Q&A logic runs locally with rule-based Python — no external AI API is used.",
    ar: "جميع عمليات التنظيف والرسوم البيانية والإجابة على الأسئلة تعمل محليًا بمنطق بايثون قائم على القواعد — دون استخدام أي واجهة ذكاء اصطناعي خارجية.",
  },
} as const;

export type DictKey = keyof typeof dict;

interface I18nContextValue {
  lang: Lang;
  dir: "ltr" | "rtl";
  toggle: () => void;
  setLang: (l: Lang) => void;
  t: (key: DictKey) => string;
  pick: <T,>(en: T, ar: T) => T;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>("en");

  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  }, [lang]);

  const value = useMemo<I18nContextValue>(
    () => ({
      lang,
      dir: lang === "ar" ? "rtl" : "ltr",
      toggle: () => setLang((l) => (l === "en" ? "ar" : "en")),
      setLang,
      t: (key: DictKey) => dict[key][lang],
      pick: (en, ar) => (lang === "ar" ? ar : en),
    }),
    [lang]
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
