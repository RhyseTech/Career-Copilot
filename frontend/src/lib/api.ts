// ─── Central API Client ───────────────────────────────────────────────────────
// All backend calls go through this module. Base URL defaults to localhost:8000.

export const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface ParsedResume {
  resume_id: string;
  structured_resume: Record<string, unknown>;
  raw_resume_text: string;
  structured_jd: StructuredJD | null;
}

export interface StructuredJD {
  requirements: JDRequirement[];
  role_title?: string;
  company?: string;
  [key: string]: unknown;
}

export interface JDRequirement {
  skill: string;
  importance: string;
  [key: string]: unknown;
}

export interface ScoreBreakdown {
  label: string;
  score: number;        // 0–100
  weight?: number;
}

export interface ATSScoreResult {
  resume_id: string;
  parsed_data: Record<string, unknown>;
  skills: string[];
  experience: Record<string, unknown>;
  score: {
    total_score: number;         // 0–100
    breakdown: ScoreBreakdown[];
    lagging_fields: string[];
    eligibility: string[];
  };
}

export interface DiagnosticCard {
  title: string;
  badge: string;
  description: string;
  recommendation: string;
  impact: string;
}

export interface DiagnoseResult {
  diagnostics: DiagnosticCard[];
}

export interface Suggestion {
  id: string;
  section: string;
  badge?: string;
  original: string;
  suggested: string;
  rationale: string;
  ats_points?: string;
}

export interface SuggestAllResult {
  suggestions: Suggestion[];
  strategic_advice?: string;
}

// ─── API Functions ────────────────────────────────────────────────────────────

/**
 * Upload a resume file (and optional JD text) — uses the v1 intelligence router
 * which returns structured JSON directly, bypassing the older parser.
 */
export async function uploadAndParse(
  file: File,
  jdText?: string,
): Promise<ParsedResume> {
  const form = new FormData();
  form.append('file', file);
  if (jdText) form.append('jd_text', jdText);

  const res = await fetch(`${BACKEND_URL}/v1/documents/parse`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Upload failed');
  }
  return res.json();
}

/**
 * Run the full ATS scoring pipeline for an already-uploaded file.
 */
export async function analyzeResume(
  resumeId: string,
  filename: string,
): Promise<ATSScoreResult> {
  const params = new URLSearchParams({ resume_id: resumeId, filename });
  const res = await fetch(`${BACKEND_URL}/ats/analyze?${params}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'ATS analysis failed');
  }
  return res.json();
}

/**
 * Generate diagnostic cards for the lagging score categories.
 */
export async function diagnose(
  resumeText: string,
  laggingFields: string[],
): Promise<DiagnoseResult> {
  const res = await fetch(`${BACKEND_URL}/ats/diagnose`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text: resumeText, lagging_fields: laggingFields }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Diagnosis failed');
  }
  return res.json();
}

/**
 * Generate AI optimization suggestions across all resume sections at once.
 */
export async function suggestAll(
  rawResumeText: string,
  jdRequirements: JDRequirement[],
  evidenceMap: unknown[],
): Promise<SuggestAllResult> {
  const res = await fetch(`${BACKEND_URL}/v1/optimization/suggest-all`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      raw_resume_text: rawResumeText,
      jd_requirements: jdRequirements,
      evidence_map: evidenceMap,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Suggest-all failed');
  }
  return res.json();
}

/**
 * Render the resume as a PDF using RenderCV. Returns a Blob for download.
 */
export async function renderPdf(
  resumeText: string,
  theme: string = 'classic',
  rendercvJson?: Record<string, unknown>
): Promise<Blob> {
  const res = await fetch(`${BACKEND_URL}/optimization/render-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_text: resumeText,
      jd_text: null,
      resume_version_id: 'live',
      theme,
      rendercv_json: rendercvJson,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'PDF render failed');
  }
  return res.blob();
}

/**
 * Check if the backend is reachable.
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${BACKEND_URL}/`, { signal: AbortSignal.timeout(3000) });
    return res.ok;
  } catch {
    return false;
  }
}
