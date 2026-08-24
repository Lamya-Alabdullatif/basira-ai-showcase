"use client";

import { useCallback, useState } from "react";
import { ApiClientError, loadSample, uploadFile } from "@/lib/api";
import type { UploadResponse } from "@/lib/types";
import Hero from "@/components/Hero";
import LoadingState from "@/components/LoadingState";
import ErrorState from "@/components/ErrorState";
import Navbar from "@/components/Navbar";
import CleaningReportBanner from "@/components/CleaningReportBanner";
import KpiCards from "@/components/KpiCards";
import SummaryCard from "@/components/SummaryCard";
import ChartsGrid from "@/components/ChartsGrid";
import ChatPanel from "@/components/ChatPanel";
import Footer from "@/components/Footer";

type Status = "idle" | "loading" | "ready" | "error";

export default function Home() {
  const [status, setStatus] = useState<Status>("idle");
  const [session, setSession] = useState<UploadResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [lastAction, setLastAction] = useState<"sample" | "upload" | null>(null);
  const [lastFile, setLastFile] = useState<File | null>(null);

  const runUpload = useCallback(async (file: File) => {
    setStatus("loading");
    setLastAction("upload");
    setLastFile(file);
    try {
      const res = await uploadFile(file);
      setSession(res);
      setStatus("ready");
    } catch (err) {
      setErrorMsg(err instanceof ApiClientError ? err.message : "Unexpected error. Please try again.");
      setStatus("error");
    }
  }, []);

  const runSample = useCallback(async () => {
    setStatus("loading");
    setLastAction("sample");
    try {
      const res = await loadSample();
      setSession(res);
      setStatus("ready");
    } catch (err) {
      setErrorMsg(err instanceof ApiClientError ? err.message : "Unexpected error. Please try again.");
      setStatus("error");
    }
  }, []);

  const retry = useCallback(() => {
    if (lastAction === "sample") runSample();
    else if (lastAction === "upload" && lastFile) runUpload(lastFile);
    else setStatus("idle");
  }, [lastAction, lastFile, runSample, runUpload]);

  const reset = useCallback(() => {
    setSession(null);
    setStatus("idle");
    setErrorMsg("");
  }, []);

  if (status === "loading") return <LoadingState />;
  if (status === "error") return <ErrorState message={errorMsg} onRetry={retry} />;

  if (status === "ready" && session) {
    return (
      <div className="flex min-h-screen flex-col">
        <Navbar onReset={reset} filename={session.filename} />
        <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-6 px-5 py-6 sm:px-8 sm:py-8">
          <CleaningReportBanner report={session.cleaning_report} />
          <KpiCards kpis={session.kpis} />
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">
            <ChartsGrid charts={session.charts} />
            <ChatPanel sessionId={session.session_id} columns={session.columns} />
          </div>
          <SummaryCard summary={session.summary} />
        </main>
        <Footer />
      </div>
    );
  }

  return <Hero onFile={runUpload} onSample={runSample} disabled={false} />;
}
