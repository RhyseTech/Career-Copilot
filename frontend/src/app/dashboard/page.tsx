'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useResumeStore } from '@/lib/resumeStore';
import { analyzeResume, diagnose } from '@/lib/api';
import { SyncedScoreRing } from '@/components/dashboard/synced-score-ring';
import { SyncedBreakdownBar } from '@/components/dashboard/synced-breakdown-bar';
import { AnimatedShinyText } from '@/components/ui/animated-shiny-text';

export default function DashboardPage() {
  const router = useRouter();
  const { resumeId, filename, rawText, atsScore, diagnostics, setAtsData } = useResumeStore();
  const [loading, setLoading] = useState(!atsScore);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!resumeId || !filename || !rawText) {
      router.push('/upload');
      return;
    }

    if (!atsScore) {
      const fetchData = async () => {
        try {
          // 1. Analyze
          const scoreResult = await analyzeResume(resumeId, filename);
          
          // 2. Diagnose lagging fields
          let diags = null;
          if (scoreResult.score.lagging_fields.length > 0) {
            diags = await diagnose(rawText, scoreResult.score.lagging_fields);
          }

          setAtsData(scoreResult, diags || undefined);
        } catch (err: any) {
          console.error("Dashboard fetch failed:", err);
          setError(err.message || 'Failed to analyze resume.');
        } finally {
          setLoading(false);
        }
      };
      
      fetchData();
    } else {
      setLoading(false);
    }
  }, [resumeId, filename, rawText, atsScore, router, setAtsData]);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-screen">
        <svg className="animate-spin h-10 w-10 text-[#0284C7] dark:text-cyan-400 mb-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <p className="text-[#0284C7] dark:text-cyan-300 font-mono tracking-wider animate-pulse">RUNNING ATS ENGINE...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-screen px-4">
        <div className="p-4 bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/30 rounded-xl text-rose-600 dark:text-rose-300 max-w-lg text-center">
          <h2 className="text-lg font-bold mb-2">Analysis Failed</h2>
          <p>{error}</p>
          <button onClick={() => router.push('/upload')} className="mt-4 px-4 py-2 bg-rose-50 dark:bg-rose-500/20 rounded hover:bg-rose-100 dark:hover:bg-rose-500/30 transition-colors">
            Return to Upload
          </button>
        </div>
      </div>
    );
  }

  if (!atsScore) return null;

  const totalScore = atsScore.score.total_score;
  const isGood = totalScore >= 75;
  const breakdown = atsScore.score.breakdown || [];

  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-7 pb-10 space-y-6">
        {/* Sub-header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-1">
          <div>
            <div className="flex items-center gap-2 text-xs font-medium text-[#0284C7] dark:text-cyan-400 mb-1">
              <Link href="/" className="hover:underline text-slate-500 dark:text-slate-400">Home</Link>
              <span className="text-slate-600">/</span>
              <span>Resume Analysis</span>
            </div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">Resume Analysis</h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/25">
                Live Scan Complete
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
              Evaluated against 40+ Campus Placement ATS parameters (Superset, CoCubes, AMCAT &amp; Product Bar).
            </p>
          </div>
          <Link
            href="/optimization"
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:shadow-[0_0_25px_rgba(0,240,255,0.4)] text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition-all transform hover:-translate-y-0.5"
          >
            <svg className="w-4 h-4 text-cyan-200" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <AnimatedShinyText className="text-white text-sm font-semibold" shimmerWidth={120}>
              Optimize Resume
            </AnimatedShinyText>
          </Link>
        </div>

        {/* 3-column dashboard */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Score card */}
          <section className="lg:col-span-3 backdrop-blur-2xl border border-slate-200 dark:border-white/15 shadow-[0_12px_32px_-16px_rgba(15,23,42,0.25)] dark:shadow-[0_12px_40px_rgba(0,0,0,0.5)] rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden bg-white/90 dark:bg-[rgba(15,23,42,0.6)]" data-purpose="score-summary-card">
            <div className="absolute -top-12 -left-12 w-36 h-36 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent" />
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold tracking-wider uppercase text-slate-500 dark:text-slate-400">Readiness Score</span>
                <span className={`w-2.5 h-2.5 rounded-full shadow-sm animate-pulse ${isGood ? 'bg-emerald-400 shadow-emerald-500' : 'bg-amber-400 shadow-amber-500'}`} />
              </div>
              <h2 className="text-sm font-semibold text-slate-600 dark:text-slate-200 mt-2">ATS Compatibility Score</h2>
            </div>
            {/* Score ring — number ticker + circle bar in sync */}
            <div className="my-6 text-center flex flex-col items-center justify-center">
              <SyncedScoreRing value={totalScore} isGood={isGood} />
              <span className={`mt-4 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border shadow-md ${isGood ? 'bg-emerald-50 dark:bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-500/30 shadow-emerald-500/20' : 'bg-amber-50 dark:bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-200 dark:border-amber-500/30 shadow-amber-500/20'}`}>
                {isGood ? 'GOOD • CAMPUS READY' : 'NEEDS OPTIMIZATION'}
              </span>
            </div>
            {/* Eligibility */}
            <div className="space-y-2 border-t border-slate-200 dark:border-white/10 pt-4">
              <p className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Placement Eligibility</p>
              <div className="flex flex-wrap gap-1.5">
                {atsScore.score.eligibility?.map((t: string) => (
                  <span key={t} className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/40">{t} ✓</span>
                ))}
                {!isGood && <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-300 border border-amber-200 dark:border-amber-800/40">Tier-1 Profiles (Needs Fix) ⚠️</span>}
              </div>
            </div>
          </section>

          {/* Score breakdown */}
          <section className="lg:col-span-4 backdrop-blur-2xl border border-slate-200 dark:border-white/15 shadow-[0_12px_32px_-16px_rgba(15,23,42,0.25)] dark:shadow-[0_12px_40px_rgba(0,0,0,0.5)] rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden bg-white/90 dark:bg-[rgba(15,23,42,0.6)]" data-purpose="score-breakdown-card">
            <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-indigo-400/50 to-transparent" />
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-white/10">
                <h2 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">Score Breakdown</h2>
                <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">{breakdown.length} Key Signals</span>
              </div>
              <div className="space-y-3.5 mt-5">
                {breakdown.map((item, i) => (
                  <SyncedBreakdownBar key={item.label} label={item.label} value={item.score} index={i} />
                ))}
              </div>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-5 pt-3 border-t border-slate-200 dark:border-white/10 flex items-center gap-1.5">
              <svg className={`w-3.5 h-3.5 shrink-0 ${atsScore.score.lagging_fields.length > 0 ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
              </svg>
              {atsScore.score.lagging_fields.length > 0 
                ? `${atsScore.score.lagging_fields.length} categories are below the threshold required for tier-1 IT firms.`
                : 'All categories meet or exceed tier-1 ATS thresholds.'}
            </p>
          </section>

          {/* Section verifications */}
          <section className="lg:col-span-5 backdrop-blur-2xl border border-slate-200 dark:border-white/15 shadow-[0_12px_32px_-16px_rgba(15,23,42,0.25)] dark:shadow-[0_12px_40px_rgba(0,0,0,0.5)] rounded-2xl p-6 flex flex-col justify-between relative overflow-hidden bg-white/90 dark:bg-[rgba(15,23,42,0.6)]" data-purpose="sections-checklist-card">
            <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent" />
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-white/10">
                <h2 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">ATS Section Verifications</h2>
                <span className="text-xs px-2 py-0.5 rounded-full border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 font-medium bg-white dark:bg-white/[0.05]">Live Results</span>
              </div>
              <div className="mt-4 space-y-3.5">
                {/* Dynamically build verification list based on backend checks */}
                <div className="rounded-xl border border-slate-200 dark:border-white/10 backdrop-blur-sm p-3.5 space-y-3 bg-slate-50 dark:bg-[rgba(2,6,23,0.5)]">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                    <span>CONTENT CHECK</span>
                  </div>
                  
                  <div className="flex items-start space-x-2.5">
                    <span className={`shrink-0 mt-0.5 text-emerald-600 dark:text-emerald-400`}>
                      <svg className="w-4 h-4 drop-shadow-[0_0_6px_rgba(16,185,129,0.5)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" />
                      </svg>
                    </span>
                    <div className="flex-grow">
                      <div className="flex items-center justify-between">
                        <h3 className="text-xs font-semibold text-slate-600 dark:text-slate-200">Skills Extracted</h3>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full border bg-emerald-50 dark:bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-500/20">Passed</span>
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">Found {atsScore.skills.length} verified technical &amp; core skills.</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-2.5">
                    <span className={`shrink-0 mt-0.5 ${atsScore.experience ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                       {atsScore.experience ? (
                        <svg className="w-4 h-4 drop-shadow-[0_0_6px_rgba(16,185,129,0.5)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4 drop-shadow-[0_0_6px_rgba(244,63,94,0.4)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" />
                        </svg>
                      )}
                    </span>
                    <div className="flex-grow">
                      <div className="flex items-center justify-between">
                        <h3 className="text-xs font-semibold text-slate-600 dark:text-slate-200">Experience Entries</h3>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${atsScore.experience ? 'bg-emerald-50 dark:bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-200 dark:border-emerald-500/20' : 'bg-rose-50 dark:bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-200 dark:border-rose-500/20'}`}>
                          {atsScore.experience ? 'Passed' : 'Failed'}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                        {atsScore.experience ? `Parsed ${Object.keys(atsScore.experience).length} distinct roles.` : 'No clear experience section detected.'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>

        {/* Diagnostic report */}
        {diagnostics && diagnostics.diagnostics && diagnostics.diagnostics.length > 0 && (
          <section className="backdrop-blur-2xl border border-slate-200 dark:border-white/15 rounded-2xl p-6 sm:p-7 shadow-[0_12px_32px_-16px_rgba(15,23,42,0.25)] dark:shadow-[0_12px_40px_rgba(0,0,0,0.5)] space-y-5 relative overflow-hidden bg-white/90 dark:bg-[rgba(15,23,42,0.6)]" data-purpose="diagnostic-report-section">
            <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent" />
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200 dark:border-white/10">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/30 flex items-center justify-center text-amber-600 dark:text-amber-400">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                    Diagnostic Report: {diagnostics.diagnostics.length} critical fixes required
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Immediate corrections to pass automated filters and elevate your profile.</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500 dark:text-slate-400">Targeting:</span>
                <span className="text-xs font-semibold px-3 py-1 rounded-full bg-sky-50 dark:bg-cyan-500/10 text-[#0284C7] dark:text-cyan-300 border border-sky-200 dark:border-cyan-500/30">
                  Campus Placement (SDE)
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {diagnostics.diagnostics.map((card, idx) => (
                <article key={idx} className="rounded-xl border border-amber-200 dark:border-amber-500/30 backdrop-blur-md p-5 sm:p-6 relative flex flex-col justify-between hover:border-amber-500/50 transition-colors shadow-lg bg-slate-50 dark:bg-[rgba(2,6,23,0.6)]">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-bold text-amber-600 dark:text-amber-400 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                        {card.title}
                      </h3>
                      <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-amber-50 dark:bg-amber-500/20 text-amber-600 dark:text-amber-300 border border-amber-200 dark:border-amber-500/30">{card.badge}</span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mt-2.5">{card.description}</p>
                    <div className="mt-4 p-3 rounded-lg border border-amber-200 dark:border-amber-500/20 text-[11px] text-slate-600 dark:text-slate-300 bg-white dark:bg-[rgba(15,23,42,0.8)]">
                      <strong className="text-amber-600 dark:text-amber-300">ATS Recommendation:</strong> {card.recommendation}
                    </div>
                  </div>
                  <div className="mt-5 pt-3.5 border-t border-amber-200 dark:border-amber-500/20 flex items-center justify-between">
                    <span className="text-[11px] text-slate-500 dark:text-slate-400">Impact on Shortlist: <span className="text-amber-600 dark:text-amber-400 font-bold font-mono">{card.impact}</span></span>
                    <Link href="/optimization" className="px-3.5 py-1.5 rounded-lg bg-amber-50 dark:bg-amber-500/20 hover:bg-amber-100 dark:hover:bg-amber-500/30 text-amber-600 dark:text-amber-300 font-semibold text-xs transition-colors flex items-center gap-1.5 border border-amber-200 dark:border-amber-500/30 hover:border-amber-500/50">
                      Fix in Optimizer ↗
                    </Link>
                  </div>
                </article>
              ))}
            </div>
          </section>
        )}

        {/* CTA banner */}
        <div className="backdrop-blur-2xl border border-slate-200 dark:border-white/15 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-[0_12px_32px_-16px_rgba(15,23,42,0.25)] dark:shadow-[0_12px_40px_rgba(0,0,0,0.5)] relative overflow-hidden bg-white/90 dark:bg-[rgba(15,23,42,0.6)]">
          <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent" />
          <div className="flex items-center space-x-3.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 border border-sky-200 dark:border-cyan-500/30 flex items-center justify-center text-[#0284C7] dark:text-cyan-400 shrink-0">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">Ready to boost your score?</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">Our AI will automatically rewrite your bullets to match the required format and metrics.</p>
            </div>
          </div>
          <div className="flex items-center space-x-3 w-full sm:w-auto">
            <button type="button" onClick={() => window.print()} className="w-full sm:w-auto px-4 py-2.5 rounded-xl text-slate-600 dark:text-slate-200 font-medium text-xs border border-slate-200 dark:border-white/10 transition-colors hover:border-slate-300 dark:hover:border-white/20 bg-white dark:bg-white/[0.04]">
              Download PDF Report
            </button>
            <Link href="/optimization" className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:shadow-[0_0_25px_rgba(0,240,255,0.4)] text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-1.5 whitespace-nowrap">
              <AnimatedShinyText className="text-white text-xs font-semibold" shimmerWidth={120}>
                Apply 1-Click Fixes →
              </AnimatedShinyText>
            </Link>
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-200 dark:border-white/[0.07] backdrop-blur-md px-6 lg:px-8 py-4 text-xs text-slate-500 dark:text-slate-400 bg-white/90 dark:bg-[rgba(15,23,42,0.5)]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-slate-600 dark:text-slate-300">Career Copilot</span>
            <span>© 2025 Indian University Campus Placement Protocol</span>
          </div>
          <div className="flex items-center space-x-6">
            {['TPO Guidelines', 'ATS Checker Rules', 'Tier-1 Benchmarks', 'Placement Cell Support'].map((l) => (
              <a key={l} href="#" className="hover:text-[#0284C7] dark:hover:text-cyan-300 transition-colors">{l}</a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}
