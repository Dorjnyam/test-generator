"use client";

import { useState } from "react";
import { UploadCard } from "../components/UploadCard";
import { GenerateCard } from "../components/GenerateCard";
import { MCQList } from "../components/MCQList";
import { MCQ, UploadResponse } from "../lib/api";

export default function HomePage() {
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [mcqs, setMcqs] = useState<MCQ[]>([]);

  return (
    <main className="mx-auto max-w-6xl px-4 py-10">
      <header className="mb-10 space-y-3 text-center">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-brand-600">RAG MCQ Generator</p>
        <h1 className="text-4xl font-bold text-slate-900">Create bilingual MCQs from textbooks</h1>
        <p className="text-base text-slate-600">
          Upload any chapter, let the pipeline extract concepts, and get deep-understanding MCQs with traceable
          sources.
        </p>
      </header>

      <div className="mb-8 grid gap-6 lg:grid-cols-2">
        <UploadCard
          onSuccess={(data) => {
            setUploadResult(data);
            setMcqs([]);
          }}
        />
        <GenerateCard
          pdfId={uploadResult?.pdf_id ?? null}
          pageDefaults={{
            start: Number(uploadResult?.ingested_range?.start_page ?? 1),
            end: Number(uploadResult?.ingested_range?.end_page ?? uploadResult?.total_pages ?? 1),
          }}
          onComplete={setMcqs}
        />
      </div>

      <section className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-brand-600">Step 3</p>
            <h2 className="text-2xl font-bold text-slate-900">Review & export MCQs</h2>
            <p className="text-sm text-slate-500">
              Each question cites its source text and includes English + Mongolian phrasing.
            </p>
          </div>
          {mcqs.length > 0 && (
            <button
              onClick={() => {
                const blob = new Blob([JSON.stringify(mcqs, null, 2)], { type: "application/json" });
                const url = URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = url;
                link.download = `mcqs_${uploadResult?.pdf_id ?? "export"}.json`;
                link.click();
                URL.revokeObjectURL(url);
              }}
              className="rounded-xl border border-brand-200 px-4 py-2 text-sm font-semibold text-brand-700 shadow-sm transition hover:bg-brand-50"
            >
              Export JSON
            </button>
          )}
        </div>
        <MCQList data={mcqs} />
      </section>
    </main>
  );
}

