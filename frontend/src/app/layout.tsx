import type { Metadata } from "next";
import "./globals.css";
import { I18nProvider } from "@/lib/i18n";

export const metadata: Metadata = {
  title: "Basira — AI Data Insight Platform",
  description: "Upload a spreadsheet and get an instant cleaned dashboard with bilingual AI Q&A. No external AI API required.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" dir="ltr" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-[var(--bg)] text-[var(--text)]">
        <I18nProvider>{children}</I18nProvider>
      </body>
    </html>
  );
}
