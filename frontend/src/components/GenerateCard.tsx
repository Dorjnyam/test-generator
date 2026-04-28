"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { generateMCQs, MCQ } from "../lib/api";

type GenerateCardProps = {
  pdfId: string | null;
  pageDefaults?: { start: number; end: number };
  onComplete: (mcqs: MCQ[]) => void;
};

export function GenerateCard({ pdfId, pageDefaults, onComplete }: GenerateCardProps) {
  const [numQuestions, setNumQuestions] = useState("10");
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard">("medium");

  // Automatically use page defaults from Step 1
  const pageStart = pageDefaults?.start ?? 1;
  const pageEnd = pageDefaults?.end ?? 1;

  const mutation = useMutation({
    mutationFn: () =>
      generateMCQs({
        pdfId: pdfId!,
        pageStart,
        pageEnd,
        numQuestions: Number(numQuestions),
        difficulty,
      }),
    onSuccess: (data) => onComplete(data.mcqs),
  });

  const disabled = !pdfId || !pageDefaults || mutation.isPending;

  return (
    <section className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <header className="mb-4">
        <p className="text-sm font-semibold uppercase tracking-wide text-brand-600">Step 2</p>
        <h2 className="text-2xl font-bold text-slate-900">Generate MCQs</h2>
        <p className="text-sm text-slate-500">
          Pulls concepts, runs RAG for distractors, and returns bilingual questions.
        </p>
      </header>

      {pageDefaults && (
        <div className="mb-4 rounded-lg bg-slate-50 p-3 text-sm text-slate-600">
          <p>
            Using pages <span className="font-semibold text-slate-900">{pageStart}</span> to{" "}
            <span className="font-semibold text-slate-900">{pageEnd}</span> from uploaded PDF
          </p>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm font-medium text-slate-700">
          Number of Questions
          <input
            type="number"
            value={numQuestions}
            min={1}
            max={20}
            onChange={(e) => setNumQuestions(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 shadow-inner focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm font-medium text-slate-700">
          Difficulty
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value as typeof difficulty)}
            className="rounded-lg border border-slate-200 px-3 py-2 shadow-inner focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </label>
      </div>

      <button
        disabled={disabled}
        onClick={() => mutation.mutate()}
        className="mt-5 inline-flex items-center justify-center rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {mutation.isPending ? "Generating..." : "Generate MCQs"}
      </button>

      {!pdfId && (
        <p className="mt-3 text-sm text-slate-500">Upload and process a PDF first to enable generation.</p>
      )}

      {mutation.isError && (
        <p className="mt-3 text-sm text-red-600">
          {(mutation.error as Error).message || "Generation failed. Please retry."}
        </p>
      )}
    </section>
  );
}

