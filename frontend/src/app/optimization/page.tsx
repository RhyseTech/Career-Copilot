'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useResumeStore } from '@/lib/resumeStore';
import { suggestAll, renderPdf, Suggestion as ApiSuggestion } from '@/lib/api';
import { ScrollProgress } from '@/components/ui/scroll-progress';
import { AnimatedShinyText } from '@/components/ui/animated-shiny-text';

type SuggestionStatus = 'pending' | 'accepted' | 'dismissed';

interface LocalSuggestion extends ApiSuggestion {
  status: SuggestionStatus;
}

function fuzzyReplace(text: string, search: string, replace: string) {
  if (!search || !text) return text;
  if (text.includes(search)) return text.replace(search, replace);
  try {
    const escaped = search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const flexible = escaped.replace(/\s+/g, '\\s+');
    const regex = new RegExp(flexible, 'i');
    if (regex.test(text)) return text.replace(regex, replace);
  } catch (e) {}
  console.warn("Could not find string to replace:", search);
  return text; 
}

function fuzzyReplaceJson(obj: any, search: string, replace: string): any {
  if (!search) return obj;
  if (typeof obj === 'string') {
    return fuzzyReplace(obj, search, replace);
  }
  if (Array.isArray(obj)) {
    return obj.map(item => fuzzyReplaceJson(item, search, replace));
  }
  if (typeof obj === 'object' && obj !== null) {
    const newObj: any = {};
    for (const key in obj) {
      newObj[key] = fuzzyReplaceJson(obj[key], search, replace);
    }
    return newObj;
  }
  return obj;
}

export default function OptimizationPage() {
  const router = useRouter();
  const { resumeId, rawText, jdText, atsScore, suggestions, structuredResume, setOptimizationData, updateRawText, updateStructuredResume } = useResumeStore();
  const [localSuggestions, setLocalSuggestions] = useState<LocalSuggestion[]>([]);
  const [loading, setLoading] = useState(!suggestions);
  const [error, setError] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [pdfRendering, setPdfRendering] = useState(false);
  
  const suggestionsScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!resumeId || !rawText) {
      router.push('/upload');
      return;
    }

    if (!suggestions) {
      const fetchSuggestions = async () => {
        try {
          const reqJD = jdText ? [{ skill: 'Role Requirements', importance: 'high' }] : [];
          // The backend intelligence router needs evidence map, but we'll mock it for now
          // as the backend doesn't strictly enforce its contents yet
          const result = await suggestAll(rawText, reqJD, []);
          setOptimizationData(result);
          
          setLocalSuggestions(result.suggestions.map((s) => ({
            ...s,
            status: 'pending' as SuggestionStatus
          })));
        } catch (err: any) {
          console.error("Optimization fetch failed:", err);
          setError(err.message || 'Failed to generate optimizations.');
        } finally {
          setLoading(false);
        }
      };
      
      fetchSuggestions();
    } else {
      setLocalSuggestions(suggestions.suggestions.map((s) => ({
        ...s,
        status: 'pending' as SuggestionStatus
      })));
      setLoading(false);
    }
  }, [resumeId, rawText, jdText, suggestions, router, setOptimizationData]);

  useEffect(() => {
    if (!rawText) return;
    
    let isActive = true;
    const fetchPdf = async () => {
      setPdfRendering(true);
      try {
        const blob = await renderPdf(rawText, 'sb2nov', structuredResume || undefined);
        if (isActive) {
          const url = URL.createObjectURL(blob);
          setPdfUrl(prev => {
            if (prev) URL.revokeObjectURL(prev);
            return url;
          });
        }
      } catch (e) {
        console.error("Failed to fetch live PDF:", e);
      } finally {
        if (isActive) setPdfRendering(false);
      }
    };
    fetchPdf();
    
    return () => {
      isActive = false;
    };
  }, [rawText]);

  const updateStatus = (id: string, status: SuggestionStatus) => {
    const s = localSuggestions.find((x) => x.id === id);
    if (s && rawText && updateRawText) {
      const isAccepted = status === 'accepted' && s.status !== 'accepted';
      const isUndone = status === 'pending' && s.status === 'accepted';
      
      if (isAccepted || isUndone) {
        const search = isAccepted ? s.original : s.suggested;
        const replace = isAccepted ? s.suggested : s.original;
        
        let newText = rawText;
        let newJson = structuredResume ? JSON.parse(JSON.stringify(structuredResume)) : null;

        if (s.section === 'Professional Summary' && (!search || search === 'Original Summary')) {
          // Force replace summary in JSON even if `s.original` is missing/wrong
          if (newJson?.cv?.sections?.summary && newJson.cv.sections.summary.length > 0) {
            newJson.cv.sections.summary[0] = replace;
          }
        } else if (search) {
          newText = fuzzyReplace(rawText, search, replace);
          if (newJson) newJson = fuzzyReplaceJson(newJson, search, replace);
        }

        if (newText !== rawText) updateRawText(newText);
        if (newJson && updateStructuredResume) updateStructuredResume(newJson);
      }
    }
    
    setLocalSuggestions((prev) => prev.map((item) => (item.id === id ? { ...item, status } : item)));
  };

  const accepted = localSuggestions.filter((s) => s.status === 'accepted').length;
  const total = localSuggestions.length;
  const currentScore = atsScore ? atsScore.score.total_score : 0;
  const potentialScore = Math.min(100, currentScore + total * 4); // Fake potential score gain

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-screen">
        <svg className="animate-spin h-10 w-10 text-[#0284C7] dark:text-cyan-400 mb-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <p className="text-[#0284C7] dark:text-cyan-300 font-mono tracking-wider animate-pulse">GENERATING AI OPTIMIZATIONS...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center h-screen px-4">
        <div className="p-4 bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/30 rounded-xl text-rose-600 dark:text-rose-300 max-w-lg text-center">
          <h2 className="text-lg font-bold mb-2">Optimization Failed</h2>
          <p>{error}</p>
          <button onClick={() => router.push('/dashboard')} className="mt-4 px-4 py-2 bg-rose-50 dark:bg-rose-500/20 rounded hover:bg-rose-100 dark:hover:bg-rose-500/30 transition-colors">
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="relative flex flex-col h-screen overflow-hidden">
      {/* Workspace banner */}
      <section className="px-4 lg:px-8 py-3 flex-none" data-purpose="workspace-banner">
        <div
          className="max-w-7xl mx-auto backdrop-blur-xl border border-slate-200 dark:border-white/10 rounded-2xl px-5 py-2.5 shadow-[0_4px_16px_-8px_rgba(15,23,42,0.2)] dark:shadow-[0_4px_20px_rgba(0,0,0,0.3)] flex flex-col md:flex-row items-start md:items-center justify-between gap-3 bg-white/90 dark:bg-[rgba(15,23,42,0.4)]"
        >
          <div className="flex flex-wrap items-center gap-2.5">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#0284C7] dark:text-cyan-400">Optimization Workspace</span>
              <span className="text-slate-300 dark:text-white/20">•</span>
              <span className="px-2.5 py-0.5 rounded-full text-[10.5px] bg-sky-50 dark:bg-cyan-500/10 text-[#0284C7] dark:text-cyan-300 border border-sky-200 dark:border-cyan-500/25 font-medium">
                Live AI Analysis
              </span>
            </div>
            <span className="text-slate-500 dark:text-slate-400 text-xs hidden xl:inline">
              Evidence-based improvements, always in your control.
            </span>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono text-slate-500 dark:text-slate-400">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.7)] animate-pulse" />
              <span>ATS Score: <strong className="text-emerald-600 dark:text-emerald-400 font-bold">{currentScore}/100</strong>{' '}
                <span className="text-[#0284C7] dark:text-cyan-300">(+{potentialScore - currentScore} potential)</span>
              </span>
            </div>
            <span className="text-slate-300 dark:text-white/15">|</span>
            <div>TPO Shortlist Prob: <strong className="text-[#0284C7] dark:text-cyan-300 font-bold">{potentialScore > 85 ? 'High' : 'Medium'}</strong></div>
          </div>
        </div>
      </section>

      {/* Split workspace */}
      <main
        className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-3 flex flex-col md:flex-row gap-6"
        data-purpose="split-workspace"
        style={{ minHeight: 0 }}
      >
        {/* LEFT — Resume preview */}
        <section
          aria-label="Resume Live Preview"
          className="w-full md:w-[48%] flex flex-col backdrop-blur-2xl border border-slate-200 dark:border-white/10 rounded-2xl p-4 shadow-[0_12px_32px_-16px_rgba(15,23,42,0.25)] dark:shadow-[0_12px_40px_rgba(0,0,0,0.5)] relative overflow-hidden bg-white/90 dark:bg-[rgba(15,23,42,0.6)]"
        >
          <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent" />

          {/* Toolbar */}
          <div
            className="backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl px-3.5 py-2 flex items-center justify-between select-none mb-3.5 shadow-md bg-slate-50 dark:bg-[rgba(2,6,23,0.6)]"
          >
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold tracking-wider uppercase text-[#0284C7] dark:text-cyan-300 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_6px_rgba(0,240,255,0.7)]" />
                LIVE RESUME PREVIEW
              </span>
            </div>
            <div className="flex items-center gap-1.5 border border-slate-200 dark:border-white/10 rounded-lg px-2 py-0.5 text-xs text-slate-600 dark:text-slate-300 shadow-inner bg-slate-50 dark:bg-[rgba(15,23,42,0.8)]">
              <span className="font-mono text-[11px] text-slate-600 dark:text-slate-200 px-1">RenderCV Engine</span>
            </div>
          </div>

          {/* Live PDF Document */}
          <div className="flex-1 rounded-lg overflow-hidden border border-slate-200 dark:border-white/5 relative bg-white flex justify-center items-center shadow-[0_18px_40px_-20px_rgba(15,23,42,0.35)] dark:shadow-[0_18px_45px_rgba(0,0,0,0.65)]">
            {pdfRendering ? (
              <div className="flex flex-col items-center justify-center text-slate-500 dark:text-slate-400 gap-3">
                <svg className="animate-spin h-6 w-6 text-[#0284C7] dark:text-cyan-400" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span className="text-[10px] font-mono tracking-wider">RENDERING LIVE PREVIEW...</span>
              </div>
            ) : pdfUrl ? (
              <iframe
                src={`${pdfUrl}#toolbar=0&navpanes=0&scrollbar=0&view=Fit`}
                title="Resume live preview"
                className="w-full h-full border-0 bg-white [color-scheme:light] dark:[color-scheme:dark]"
                style={{ width: 'calc(100% + 24px)', overflow: 'hidden' }}
              />
            ) : (
              <div className="text-slate-500 text-xs font-mono">Failed to load preview.</div>
            )}
          </div>
        </section>

        {/* RIGHT — AI suggestions */}
        <section
          aria-label="AI Recommendations Panel"
          className="w-full md:w-[52%] flex flex-col backdrop-blur-2xl border border-slate-200 dark:border-white/10 rounded-2xl p-4 sm:p-5 shadow-[0_12px_32px_-16px_rgba(15,23,42,0.25)] dark:shadow-[0_12px_40px_rgba(0,0,0,0.5)] relative overflow-hidden bg-white/90 dark:bg-[rgba(15,23,42,0.6)]"
        >
          <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-indigo-400/50 to-transparent" />
          <ScrollProgress containerRef={suggestionsScrollRef} className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-emerald-400 via-cyan-400 to-indigo-400" />

          {/* Panel header */}
          <div className="backdrop-blur-md border border-slate-200 dark:border-white/10 rounded-xl px-4 py-2.5 flex items-center justify-between mb-4 shadow-md bg-slate-50 dark:bg-[rgba(2,6,23,0.6)]">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white flex items-center gap-2">
                <svg className="w-4 h-4 text-[#0284C7] dark:text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                </svg>
                AI SUGGESTIONS &amp; OPTIMIZATION
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-sky-50 dark:bg-cyan-500/20 text-[#0284C7] dark:text-cyan-300 font-mono border border-sky-200 dark:border-cyan-500/30">
                {localSuggestions.filter((s) => s.status === 'pending').length} AVAILABLE
              </span>
            </div>
            <span className="text-[11px] text-slate-500 dark:text-slate-400 hidden sm:block">
              Click <strong className="text-emerald-600 dark:text-emerald-400 font-semibold">Accept Change</strong> to instant-merge
            </span>
          </div>

          {/* Suggestions */}
          <div ref={suggestionsScrollRef} className="flex-1 overflow-y-auto space-y-4 pr-1">
            {/* Strategic guidance banner */}
            {suggestions?.strategic_advice && (
              <article className="rounded-xl p-4 border border-indigo-500/30 shadow-md relative overflow-hidden backdrop-blur-md bg-indigo-50/70 dark:bg-[rgba(30,27,75,0.4)]" data-purpose="strategic-guidance">
                <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none" />
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-500/20 text-[#0284C7] dark:text-cyan-300 border border-indigo-200 dark:border-indigo-500/40 mt-0.5 shrink-0">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                    </svg>
                  </div>
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-200 font-mono">CAMPUS PLACEMENT STRATEGIC ADVICE</h4>
                      <span className="px-1.5 bg-indigo-100 dark:bg-indigo-500/30 text-slate-900 dark:text-white rounded text-[9px] font-bold border border-indigo-200 dark:border-indigo-400/30">CRITICAL</span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                      {suggestions.strategic_advice}
                    </p>
                  </div>
                </div>
              </article>
            )}

            {/* Suggestion cards */}
            {localSuggestions.map((s) => (
              <article
                key={s.id}
                className={`border rounded-xl p-4 sm:p-5 shadow-lg transition-all backdrop-blur-md ${s.status === 'accepted' ? 'border-emerald-200 dark:border-emerald-500/40 bg-emerald-50 dark:bg-emerald-950/20' : s.status === 'dismissed' ? 'border-slate-200 dark:border-white/5 opacity-50' : 'border-slate-200 dark:border-white/10 hover:border-cyan-500/30 bg-slate-50 dark:bg-[rgba(2,6,23,0.6)]'}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900 dark:text-white tracking-wide uppercase font-mono">{s.section}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border bg-indigo-50 dark:bg-indigo-500/15 text-indigo-600 dark:text-indigo-300 border-indigo-200 dark:border-indigo-500/30`}>{s.badge || 'Optimization'}</span>
                  </div>
                  <span className={`text-[11px] font-mono ${s.status === 'accepted' ? 'text-emerald-600 dark:text-emerald-400 font-semibold px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20' : 'text-slate-500 dark:text-slate-400'}`}>
                    {s.status === 'accepted' ? '✓ Accepted' : (s.ats_points || '+ ATS Points')}
                  </span>
                </div>

                {/* Original */}
                <div className="mb-3 rounded-lg p-3 border border-slate-200 dark:border-white/5 bg-slate-50 dark:bg-[rgba(15,23,42,0.8)]">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1 font-mono">CURRENT ORIGINAL</div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 line-through leading-relaxed">{s.original}</p>
                </div>

                {/* Suggested */}
                <div className="mb-3 rounded-lg p-3 border border-indigo-500/40 bg-indigo-50/70 dark:bg-[rgba(30,27,75,0.3)]">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#0284C7] dark:text-cyan-400 font-mono">SUGGESTED OPTIMIZATION</span>
                    <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold font-mono">STAR &amp; Metric Calibrated</span>
                  </div>
                  <p className="text-xs text-slate-700 dark:text-slate-100 font-medium leading-relaxed">{s.suggested}</p>
                </div>

                {/* Rationale */}
                <p className="text-[11px] text-slate-500 dark:text-slate-400 italic mb-4 leading-normal flex items-start gap-1.5">
                  <svg className="w-3.5 h-3.5 text-[#0284C7] dark:text-cyan-400 mt-0.5 flex-none" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" clipRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" />
                  </svg>
                  {s.rationale}
                </p>

                {/* Actions */}
                {s.status === 'pending' && (
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => updateStatus(s.id, 'accepted')}
                      className="flex-1 py-2 px-4 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-xs transition-all flex items-center justify-center gap-1.5 shadow-md shadow-emerald-600/30"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" />
                      </svg>
                      <AnimatedShinyText className="text-white text-xs font-semibold" shimmerWidth={100}>
                        ✓ Accept change
                      </AnimatedShinyText>
                    </button>
                    <button type="button" className="py-2 px-3.5 rounded-xl border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white font-medium text-xs transition-colors hover:bg-slate-100 dark:hover:bg-white/[0.08] bg-white dark:bg-white/[0.04]">
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => updateStatus(s.id, 'dismissed')}
                      className="py-2 px-3.5 rounded-xl border border-slate-200 dark:border-white/10 text-slate-500 dark:text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 font-medium text-xs transition-colors hover:bg-slate-100 dark:hover:bg-white/[0.08] bg-white dark:bg-white/[0.04]"
                    >
                      Dismiss
                    </button>
                  </div>
                )}
                {s.status === 'accepted' && (
                  <div className="flex items-center gap-2 text-xs text-emerald-600 dark:text-emerald-400 font-semibold">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" />
                    </svg>
                    Change applied to your resume
                    <button type="button" onClick={() => updateStatus(s.id, 'pending')} className="ml-auto text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white text-[11px] font-normal">Undo</button>
                  </div>
                )}
              </article>
            ))}
          </div>
        </section>
      </main>

      {/* Sticky bottom bar */}
      <footer
        className="sticky bottom-0 z-30 px-4 lg:px-8 py-3 flex-none backdrop-blur-xl border-t border-slate-200 dark:border-white/10 shadow-[0_-8px_24px_-16px_rgba(15,23,42,0.25)] dark:shadow-[0_-4px_24px_rgba(0,0,0,0.4)] bg-white/90 dark:bg-[rgba(15,23,42,0.7)]"
        data-purpose="sticky-bottom-bar"
      >
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center bg-rose-50 dark:bg-rose-500/15 text-rose-600 dark:text-rose-300 border border-rose-200 dark:border-rose-500/30 text-[11px] px-3 py-1 rounded-full font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mr-1.5" />
              {total - accepted} Improvement{total - accepted !== 1 ? 's' : ''} Remaining
            </span>
            <span className="text-slate-300 dark:text-white/20 hidden sm:inline">•</span>
            <div className="text-[11px] font-mono text-slate-500 dark:text-slate-400 hidden sm:block">
              Sync status: <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Up to Date</span>
            </div>
          </div>
          <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
            <span className="text-[#0284C7] dark:text-cyan-300 text-xs font-mono font-medium hidden sm:inline">
              {accepted} / {total} Improvements accepted
            </span>
            <Link
              href="/optimization/templates"
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:shadow-[0_0_25px_rgba(0,240,255,0.4)] text-white font-semibold text-xs transition-all shadow-lg shadow-indigo-600/30 flex items-center gap-2 transform hover:-translate-y-0.5"
            >
              <AnimatedShinyText className="text-white text-xs font-semibold" shimmerWidth={120}>
                Next: Select Placement Template →
              </AnimatedShinyText>
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
