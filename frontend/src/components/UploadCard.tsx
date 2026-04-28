"use client";

import { useState, ChangeEvent } from "react";
import { useMutation } from "@tanstack/react-query";
import { uploadPdf, UploadResponse } from "../lib/api";

type UploadCardProps = {
  onSuccess: (data: UploadResponse) => void;
};

export function UploadCard({ onSuccess }: UploadCardProps) {
  const [file, setFile] = useState<File | null>(null);
  const [startPage, setStartPage] = useState<string>("");
  const [endPage, setEndPage] = useState<string>("");

  const mutation = useMutation({
    mutationFn: () =>
      uploadPdf({
        file: file as File,
        startPage: startPage ? Number(startPage) : undefined,
        endPage: endPage ? Number(endPage) : undefined,
      }),
    onSuccess,
  });

  const disabled = !file || mutation.isPending;

  return (
    <section className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <header className="mb-4">
        <p className="text-sm font-semibold uppercase tracking-wide text-brand-600">Step 1</p>
        <h2 className="text-2xl font-bold text-slate-900">Upload textbook PDF</h2>
        <p className="text-sm text-slate-500">
          Intelligent chunking + embedding happens automatically after upload.
        </p>
      </header>

      <div className="mb-4 grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
          Start page
          <input
            type="number"
            min={1}
            placeholder="e.g. 45"
            value={startPage}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setStartPage(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-base shadow-inner focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
          />
        </label>
        <label className="flex flex-col gap-2 text-sm font-medium text-slate-700">
          End page
          <input
            type="number"
            min={1}
            placeholder="e.g. 65"
            value={endPage}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setEndPage(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-base shadow-inner focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
          />
        </label>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <input
          type="file"
          accept=".pdf"
          onChange={(e: ChangeEvent<HTMLInputElement>) => setFile(e.target.files?.[0] ?? null)}
          className="text-sm"
        />
        <button
          disabled={disabled}
          onClick={() => mutation.mutate()}
          className="inline-flex items-center justify-center rounded-xl bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {mutation.isPending ? "Processing..." : "Process PDF"}
        </button>
      </div>

      {mutation.isError && (
        <p className="mt-3 text-sm text-red-600">
          {(mutation.error as Error).message || "Upload failed. Please try again."}
        </p>
      )}

      {mutation.data && (
        <div className="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-700">
          <p className="font-semibold text-slate-900">Processed successfully!</p>
          <p>PDF ID: {mutation.data.pdf_id}</p>
          <p>
            Ingested pages: {(mutation.data.ingested_range?.start_page ?? startPage) || 1}-
            {(mutation.data.ingested_range?.end_page ?? endPage) || mutation.data.total_pages}
          </p>
        </div>
      )}
    </section>
  );
}

