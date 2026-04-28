"use client";

import { MCQ } from "../lib/api";
import clsx from "clsx";

type Props = {
  data: MCQ[];
};

export function MCQList({ data }: Props) {
  if (!data.length) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 px-6 py-14 text-center text-slate-500">
        Generated MCQs will appear here.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {data.map((mcq) => (
        <article key={mcq.question_number} className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-100">
          <header className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-brand-600">Concept</p>
              <p className="text-lg font-semibold text-slate-900">{mcq.concept}</p>
            </div>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600">
              {mcq.difficulty}
            </span>
          </header>

          <div className="space-y-2">
            <p className="font-semibold text-slate-900">{mcq.question_en}</p>
            <p className="text-sm text-slate-600">{mcq.question_mn}</p>
          </div>

          <ul className="mt-4 space-y-2">
            {mcq.choices.map((choice) => (
              <li
                key={choice.id}
                className={clsx(
                  "rounded-xl border px-4 py-3 text-sm shadow-inner",
                  choice.is_correct
                    ? "border-emerald-200 bg-emerald-50 text-emerald-900"
                    : "border-slate-200 bg-slate-50 text-slate-700"
                )}
              >
                <div className="font-semibold">
                  {choice.id}. {choice.text_en}
                </div>
                <div className="text-xs text-slate-600">{choice.text_mn}</div>
                {choice.source && <p className="mt-1 text-xs text-slate-500">Source: {choice.source}</p>}
              </li>
            ))}
          </ul>

          <div className="mt-4 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
            <p className="font-semibold text-slate-900">Explanation</p>
            <p>{mcq.explanation_en}</p>
            <p className="text-xs text-slate-500">{mcq.explanation_mn}</p>
          </div>
        </article>
      ))}
    </div>
  );
}

