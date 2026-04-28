const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export type UploadResponse = {
  pdf_id: string;
  filename: string;
  total_pages: number;
  chunks_created: number;
  ingested_range?: { start_page: number; end_page: number };
};

export type MCQChoice = {
  id: string;
  text_en: string;
  text_mn: string;
  is_correct: boolean;
  explanation?: string;
  source?: string;
};

export type MCQ = {
  question_number: number;
  question_en: string;
  question_mn: string;
  choices: MCQChoice[];
  explanation_en: string;
  explanation_mn: string;
  concept: string;
  difficulty: string;
  page_reference?: string;
};

export async function uploadPdf(form: {
  file: File;
  startPage?: number;
  endPage?: number;
}): Promise<UploadResponse> {
  const data = new FormData();
  data.append("file", form.file);
  const params = new URLSearchParams();
  if (form.startPage) params.set("start_page", String(form.startPage));
  if (form.endPage) params.set("end_page", String(form.endPage));

  const res = await fetch(`${BASE_URL}/api/pdf/upload?${params.toString()}`, {
    method: "POST",
    body: data,
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

export async function generateMCQs(payload: {
  pdfId: string;
  pageStart: number;
  pageEnd: number;
  numQuestions: number;
  difficulty: "easy" | "medium" | "hard";
}): Promise<{ total_generated: number; mcqs: MCQ[] }> {
  const res = await fetch(`${BASE_URL}/api/mcq/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      pdf_id: payload.pdfId,
      page_start: payload.pageStart,
      page_end: payload.pageEnd,
      num_questions: payload.numQuestions,
      difficulty: payload.difficulty,
    }),
  });

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json();
}

