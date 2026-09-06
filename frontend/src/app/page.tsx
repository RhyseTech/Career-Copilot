import Link from 'next/link';
import { AuroraText } from '@/components/ui/aurora-text';
import { Text3DFlip } from '@/components/ui/text-3d-flip';

const resumeOnlyFeatures = ['Instant 10s Score', 'College TPO Rules', 'ATS Keyword Audit'];
const resumeJdFeatures = ['Role-Specific Match %', 'Skill Gap Analyzer', 'Custom Bullet Tailoring'];

function FeatureBadge({ text, color = 'indigo' }: { text: string; color?: 'indigo' | 'cyan' }) {
  const styles =
    color === 'cyan'
      ? 'bg-sky-50 text-[#0284C7] border-sky-200 dark:bg-cyan-950/40 dark:text-cyan-200 dark:border-cyan-500/30'
      : 'bg-indigo-50 text-indigo-600 border-indigo-200 dark:bg-indigo-950/40 dark:text-indigo-200 dark:border-indigo-500/30';
  return (
    <span className={`badge-shimmer text-[11px] font-medium px-3 py-1 rounded-lg border flex items-center gap-1.5 shadow-sm ${styles}`}>
      <svg className="w-3 h-3 text-emerald-600 dark:text-emerald-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" clipRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
      </svg>
      {text}
    </span>
  );
}

export default function Home() {
  return (
    <div className="flex-1 flex flex-col justify-center px-4 sm:px-6 lg:px-8 py-10 lg:py-14 max-w-6xl mx-auto w-full">
      <div className="text-center">
        {/* Headline */}
        <h1 className="text-3xl sm:text-5xl lg:text-[3.6rem] font-extrabold tracking-tight leading-[1.15] text-slate-900 dark:text-white drop-shadow-sm">
          Welcome to <AuroraText speed={1}>Career Copilot</AuroraText>
        </h1>

        {/* Subtitle with 3D flip on hover */}
        <Text3DFlip
          as="p"
          className="mt-4 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed font-normal justify-center text-center cursor-default [perspective:800px] py-1"
          textClassName="text-slate-600 dark:text-slate-300/85"
          flipTextClassName="text-[#0284C7] dark:text-cyan-300"
          rotateDirection="top"
          staggerFrom="center"
          staggerDuration={0.015}
        >
          Upload your resume, explore your ATS compatibility, optimize it intelligently, and get tailored for every job description.
        </Text3DFlip>

        {/* Mode cards */}
        <div className="mt-10 sm:mt-12 grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8 text-left" data-purpose="mode-selection-container">
          {/* Card 1: Resume Only */}
          <article className="group relative rounded-2xl backdrop-blur-xl border border-slate-200 dark:border-white/10 bg-white/90 dark:bg-[rgba(10,15,29,0.75)] hover:border-indigo-300 dark:hover:border-indigo-400/50 shadow-[0_8px_30px_-12px_rgba(15,23,42,0.25)] hover:shadow-[0_0_40px_-8px_rgba(99,102,241,0.4)] dark:shadow-[0_8px_32px_0_rgba(0,0,0,0.37)] transition-all duration-300 p-7 sm:p-8 flex flex-col justify-between" data-purpose="option-resume-only">
            <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-indigo-400/50 to-transparent" />
            <div className="space-y-4 text-center">
              <div className="mx-auto p-3 w-fit rounded-2xl bg-gradient-to-br from-indigo-100 to-blue-50 dark:from-indigo-500/20 dark:to-blue-500/10 border border-indigo-200 dark:border-indigo-500/30 text-indigo-600 dark:text-indigo-400 flex items-center justify-center group-hover:scale-110 group-hover:bg-indigo-100 dark:group-hover:bg-indigo-500/30 group-hover:border-indigo-300 dark:group-hover:border-indigo-400 transition-all duration-300">
                <svg className="w-6 h-6 text-indigo-600 dark:text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight pt-1">Resume Only</h2>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed min-h-[44px]">
                Get an instant ATS Compatibility Score, automated TPO cutoff checks, and general optimization tips for campus recruitment.
              </p>
              <div className="pt-2 flex flex-wrap justify-center gap-2">
                {resumeOnlyFeatures.map((f) => <FeatureBadge key={f} text={f} color="indigo" />)}
              </div>
            </div>
            <div className="mt-8 pt-2">
              <Link
                href="/upload"
                className="w-full py-3.5 px-6 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-blue-600 via-indigo-600 to-indigo-700 hover:from-blue-500 hover:to-indigo-600 shadow-[0_4px_20px_rgba(79,70,229,0.35)] hover:shadow-[0_4px_30px_rgba(79,70,229,0.55)] flex items-center justify-center gap-2.5 transition-all duration-300 focus:ring-2 focus:ring-indigo-400 focus:outline-none"
              >
                <svg className="w-4 h-4 text-cyan-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" />
                </svg>
                Upload Resume
              </Link>
            </div>
          </article>

          {/* Card 2: Resume + JD */}
          <article className="group relative rounded-2xl backdrop-blur-xl border border-slate-200 dark:border-white/10 bg-white/90 dark:bg-[rgba(10,15,29,0.75)] hover:border-sky-300 dark:hover:border-cyan-500/40 shadow-[0_8px_30px_-12px_rgba(15,23,42,0.25)] hover:shadow-[0_0_30px_rgba(0,240,255,0.18)] dark:shadow-[0_8px_32px_0_rgba(0,0,0,0.37)] transition-all duration-300 p-7 sm:p-8 flex flex-col justify-between" data-purpose="option-resume-and-jd">
            <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent" />
            <div className="space-y-4 text-center">
              <div className="mx-auto p-3 w-fit rounded-2xl bg-gradient-to-br from-sky-100 to-cyan-50 dark:from-cyan-500/20 dark:to-teal-500/10 border border-sky-200 dark:border-cyan-500/30 text-[#0284C7] dark:text-cyan-400 flex items-center justify-center group-hover:scale-110 group-hover:bg-sky-100 dark:group-hover:bg-cyan-500/30 group-hover:border-sky-300 dark:group-hover:border-cyan-400 transition-all duration-300">
                <svg className="w-6 h-6 text-[#0284C7] dark:text-cyan-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight pt-1">Resume + JD</h2>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed min-h-[44px]">
                Match your resume to a specific job description to find skill gaps, missing keywords, and tailored bullet suggestions.
              </p>
              <div className="pt-2 flex flex-wrap justify-center gap-2">
                {resumeJdFeatures.map((f) => <FeatureBadge key={f} text={f} color="cyan" />)}
              </div>
            </div>
            <div className="mt-8 pt-2">
              <Link
                href="/upload?mode=jd"
                className="w-full py-3.5 px-6 rounded-xl font-semibold text-sm text-[#0284C7] dark:text-slate-100 bg-white dark:bg-[rgba(7,10,19,0.9)] border border-sky-300 dark:border-cyan-500/30 hover:border-[#0284C7] dark:hover:border-cyan-400/60 shadow-sm dark:shadow-[0_4px_20px_rgba(0,0,0,0.6)] hover:shadow-[0_4px_25px_rgba(6,182,212,0.25)] flex items-center justify-center gap-2.5 transition-all duration-300 focus:ring-2 focus:ring-cyan-400 focus:outline-none"
              >
                <svg className="w-4 h-4 text-[#0284C7] dark:text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M13 10V3L4 14h7v7l9-11h-7z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                </svg>
                Upload Resume &amp; JD
              </Link>
            </div>
          </article>
        </div>

        {/* Trust bar */}
        <aside aria-label="Privacy & Standards Notice" className="mt-12 pt-5 max-w-3xl mx-auto">
          <div className="px-5 py-3 rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-white/80 dark:bg-[rgba(255,255,255,0.03)] backdrop-blur-md flex flex-wrap items-center justify-center gap-y-2.5 gap-x-6 text-xs text-slate-600 dark:text-slate-300/90 shadow-sm">
            <div className="flex items-center space-x-2">
              <svg className="w-4 h-4 text-emerald-600 dark:text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
              </svg>
              <span className="font-medium text-slate-700 dark:text-slate-200">100% Student Privacy Guarantee</span>
            </div>
            <span className="text-slate-300 dark:text-white/20 hidden sm:inline">•</span>
            <div className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#0284C7]" />
              <span>Aligned with IIT/NIT &amp; Tier 1/2 Formats</span>
            </div>
            <span className="text-slate-300 dark:text-white/20 hidden sm:inline">•</span>
            <div className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
              <span>Superset &amp; CoCubes Calibrated</span>
            </div>
          </div>
        </aside>
      </div>

      {/* Footer */}
      <footer className="mt-16 border-t border-slate-200 dark:border-white/[0.06] pt-5 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 dark:text-slate-400">
        <span>© 2025 Career Copilot. Empowering campus candidates across India.</span>
        <div className="flex items-center space-x-6">
          {['TPO Handbook', 'ATS Guidelines', 'Privacy', 'Feedback'].map((link) => (
            <a key={link} href="#" className="hover:text-[#0284C7] dark:hover:text-cyan-300 transition-colors">{link}</a>
          ))}
        </div>
      </footer>
    </div>
  );
}
