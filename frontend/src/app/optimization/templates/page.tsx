'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useResumeStore } from '@/lib/resumeStore';
import { renderPdf } from '@/lib/api';

type Template = {
  id: string;
  name: string;
  tagline: string;
  description: string;
  recommended?: boolean;
  fontStyle: 'sans' | 'serif' | 'mono';
  accentColor?: string;
  backendTheme?: string;
};

const templates: Template[] = [
  {
    id: 'classic',
    name: 'Classic',
    tagline: 'Universal ATS',
    description: 'Clean, timeless design suitable for mass recruiting drives.',
    fontStyle: 'sans',
    backendTheme: 'classic',
  },
  {
    id: 'harvard',
    name: 'Harvard',
    tagline: 'Academic / PSU',
    description: 'Academic and formal. Perfect for core engineering and higher studies.',
    fontStyle: 'serif',
    backendTheme: 'harvard',
  },
  {
    id: 'modern-cv',
    name: 'Modern CV',
    tagline: 'SDE / Product',
    description: 'Sleek design. Best optimized for product companies and tech startups.',
    fontStyle: 'sans',
    backendTheme: 'moderncv',
  },
  {
    id: 'engineering-resumes',
    name: 'Eng Resumes',
    tagline: 'Software Engineering',
    description: 'Standard layout highly recommended by the EngineeringResumes community.',
    fontStyle: 'sans',
    backendTheme: 'engineeringresumes',
    recommended: true,
  },
  {
    id: 'engineering-classic',
    name: 'Eng Classic',
    tagline: 'Traditional Tech',
    description: 'A more traditional engineering layout with high density.',
    fontStyle: 'serif',
    backendTheme: 'engineeringclassic',
  },
  {
    id: 'sb2nov',
    name: 'SB2Nov',
    tagline: 'Compact',
    description: 'Space-optimized for experienced candidates with extensive projects.',
    fontStyle: 'sans',
    backendTheme: 'sb2nov',
  },
  {
    id: 'ember',
    name: 'Ember',
    tagline: 'Creative',
    description: 'A modern, vibrant theme with distinct sections.',
    fontStyle: 'sans',
    backendTheme: 'ember',
  },
  {
    id: 'ink',
    name: 'Ink',
    tagline: 'Executive',
    description: 'Polished layout for business-oriented roles and management consulting.',
    fontStyle: 'sans',
    backendTheme: 'ink',
  },
  {
    id: 'opal',
    name: 'Opal',
    tagline: 'Minimalist',
    description: 'Clean and minimal design focusing on typography and spacing.',
    fontStyle: 'sans',
    backendTheme: 'opal',
  }
];

function ResumePreview({ template }: { template: Template }) {
  // Map template IDs to the sample PDF filenames in rendercv/examples/
  const pdfMap: Record<string, string> = {
    'classic': 'John_Doe_ClassicTheme_CV.pdf',
    'harvard': 'John_Doe_HarvardTheme_CV.pdf',
    'modern-cv': 'John_Doe_ModerncvTheme_CV.pdf',
    'engineering-resumes': 'John_Doe_EngineeringresumesTheme_CV.pdf',
    'engineering-classic': 'John_Doe_EngineeringclassicTheme_CV.pdf',
    'sb2nov': 'John_Doe_Sb2novTheme_CV.pdf',
    'ember': 'John_Doe_EmberTheme_CV.pdf',
    'ink': 'John_Doe_InkTheme_CV.pdf',
    'opal': 'John_Doe_OpalTheme_CV.pdf',
  };

  const pdfFilename = pdfMap[template.id] || 'John_Doe_ClassicTheme_CV.pdf';
  
  return (
    <div
      className="w-full max-w-[320px] mx-auto bg-white rounded-sm shadow-xl flex flex-col select-none overflow-hidden text-slate-800 relative"
      style={{ aspectRatio: '1.414 / 1' }}
    >
      <div className="absolute inset-0 z-10 w-full h-full pointer-events-none shadow-[inset_0_0_0_1px_rgba(0,0,0,0.1)]"></div>
      <iframe 
        src={`/templates/${pdfFilename}#toolbar=0&navpanes=0&scrollbar=0&view=FitH`}
        className="border-0 pointer-events-none origin-top bg-white [color-scheme:light]"
        scrolling="no"
        title={`${template.name} preview`}
        style={{ 
          width: 'calc(100% + 24px)', 
          height: '200%', 
          overflow: 'hidden' 
        }}
      />
    </div>
  );
}

export default function TemplatesPage() {
  const router = useRouter();
  const { resumeId, rawText } = useResumeStore();
  const [selected, setSelected] = useState('modern-cv');
  const [filter, setFilter] = useState('All');
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const filters = ['All', 'ATS-Safe', 'Modern', 'Minimal'];

  const filtered = filter === 'All' ? templates
    : filter === 'ATS-Safe' ? templates.filter((t) => ['classic', 'harvard', 'sb2nov'].includes(t.id))
    : filter === 'Modern' ? templates.filter((t) => ['modern-cv', 'ink', 'ember'].includes(t.id))
    : templates.filter((t) => ['engineering-classic', 'engineering-resumes', 'opal'].includes(t.id));

  const handleDownload = async (template: Template) => {
    if (!resumeId || !rawText) {
      alert("No active session. Please upload a resume first.");
      router.push('/upload');
      return;
    }
    
    setDownloadingId(template.id);
    try {
      const backendTheme = template.backendTheme || 'classic';
      const blob = await renderPdf(rawText, backendTheme);
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Resume_${template.name.replace(' ', '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (err: any) {
      console.error("PDF generation failed:", err);
      alert(`PDF generation failed: ${err.message}`);
    } finally {
      setDownloadingId(null);
    }
  };

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-12 py-7 flex flex-col space-y-6">
      {/* Sub-header */}
      <section className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <Link href="/optimization" className="inline-flex items-center justify-center w-8 h-8 rounded-xl border border-slate-200 dark:border-white/10 hover:border-cyan-400/40 bg-white dark:bg-white/[0.04] hover:bg-slate-100 dark:hover:bg-white/[0.08] text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-all">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M15 19l-7-7 7-7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
              </svg>
            </Link>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Select a Template</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1 pl-11">
            Preview every layout and download the version you just approved for ongoing placement drives.
          </p>
        </div>
        {/* Format selector */}
        <div className="flex items-center space-x-3 pl-11 sm:pl-0">
          <div className="inline-flex rounded-xl p-1 border border-slate-200 dark:border-white/10 backdrop-blur-md text-xs text-slate-500 dark:text-slate-400 bg-white dark:bg-[rgba(255,255,255,0.03)]">
            {['Standard (A4)', 'US Letter'].map((fmt, i) => (
              <button
                key={fmt}
                type="button"
                className={`px-3.5 py-1.5 rounded-lg transition-colors ${i === 0 ? 'bg-gradient-to-r from-indigo-600/40 to-cyan-600/40 border border-cyan-500/40 text-white font-semibold shadow-sm' : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/[0.04]'}`}
              >
                {fmt}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Filter tabs */}
      <div className="flex items-center gap-2">
        {filters.map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all border ${
              filter === f
                ? 'bg-gradient-to-r from-indigo-600/50 to-cyan-600/50 border-cyan-500/40 text-white shadow-sm'
                : 'border-slate-200 dark:border-white/10 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:border-slate-200 dark:hover:border-white/20 bg-white dark:bg-[rgba(255,255,255,0.03)]'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Template grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-1" data-purpose="template-grid">
        {filtered.map((tmpl) => {
          const isSelected = selected === tmpl.id;
          const isDownloading = downloadingId === tmpl.id;
          return (
            <div
              key={tmpl.id}
              className={`group backdrop-blur-2xl rounded-2xl p-4 transition-all duration-300 flex flex-col justify-between relative overflow-hidden cursor-pointer ${
                isSelected
                  ? 'border-2 border-cyan-400 card-active-glow bg-white/90 dark:bg-[rgba(15,23,42,0.75)]'
                  : 'border border-slate-200 dark:border-white/10 hover:border-cyan-400/40 hover:shadow-[0_0_30px_rgba(0,240,255,0.15)] bg-white/90 dark:bg-[rgba(15,23,42,0.6)]'
              }`}
              onClick={() => setSelected(tmpl.id)}
            >
              {/* Recommended badge */}
              {tmpl.recommended && (
                <div className="absolute top-2.5 left-2.5 z-20">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 text-white text-[9.5px] font-extrabold tracking-wide uppercase shadow-lg shadow-cyan-500/30">
                    <svg className="w-3 h-3 text-cyan-200" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    RECOMMENDED FOR SDE
                  </span>
                </div>
              )}

              <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

              <div>
                {/* Preview thumbnail */}
                <div className={`relative py-1.5 px-0.5 rounded-xl border flex items-center justify-center overflow-hidden mb-4 bg-slate-50 dark:bg-[rgba(2,6,23,0.8)] ${isSelected ? 'border-cyan-500/30' : 'border-slate-200 dark:border-white/10'}`}>
                  <span className={`absolute top-2 right-2 z-10 px-2 py-0.5 rounded-md text-[9px] font-extrabold tracking-wider uppercase shadow ${isSelected ? 'bg-gradient-to-r from-indigo-600 to-cyan-500 text-white shadow-cyan-500/30' : 'bg-white/90 text-slate-900'}`}>
                    PREVIEW
                  </span>
                  <ResumePreview template={tmpl} />
                </div>

                {/* Meta */}
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight">{tmpl.name}</h3>
                      {isSelected && (
                        <span className="px-2 py-0.5 text-[10px] font-semibold bg-sky-50 dark:bg-cyan-500/20 text-[#0284C7] dark:text-cyan-300 rounded-full border border-sky-200 dark:border-cyan-500/30">Active</span>
                    )}
                  </div>
                  {isSelected ? (
                    <svg className="w-5 h-5 text-[#0284C7] dark:text-cyan-400 dark:drop-shadow-[0_0_6px_rgba(0,240,255,0.5)]" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" clipRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
                    </svg>
                  ) : (
                    <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wide">{tmpl.tagline}</span>
                  )}
                </div>
                <p className={`text-xs leading-relaxed ${isSelected ? 'text-slate-600 dark:text-slate-300' : 'text-slate-500 dark:text-slate-400'}`}>{tmpl.description}</p>
              </div>

              {/* Download button */}
              <div className="pt-4">
                <button
                  type="button"
                  disabled={isDownloading}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDownload(tmpl);
                  }}
                  className={`w-full py-2.5 px-4 rounded-xl font-medium text-xs flex items-center justify-center space-x-2 border transition-all shadow-sm active:scale-[0.99] ${
                    isSelected
                      ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:shadow-[0_0_25px_rgba(0,240,255,0.4)] text-white font-semibold border-transparent shadow-lg shadow-indigo-600/30 disabled:opacity-70 disabled:cursor-not-allowed'
                      : 'text-slate-900 dark:text-white border-slate-200 dark:border-white/10 hover:border-cyan-400/40 hover:bg-slate-100 dark:hover:bg-white/[0.08] disabled:opacity-50 disabled:cursor-not-allowed bg-white dark:bg-[rgba(255,255,255,0.04)]'
                  }`}
                >
                  {isDownloading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-slate-900 dark:text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Generating PDF...</span>
                    </>
                  ) : (
                    <>
                      <svg className={`w-4 h-4 ${isSelected ? 'text-cyan-200' : 'text-[#0284C7] dark:text-cyan-300'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                      </svg>
                      <span>Download PDF</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-white/[0.07] pt-5 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500 dark:text-slate-400">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-slate-600 dark:text-slate-300">Career Copilot</span>
          <span>© 2025 Indian University Campus Placement Protocol</span>
        </div>
        <div className="flex items-center space-x-6">
          {['ATS Guide', 'Tier-1 Benchmarks', 'Placement Cell Support'].map((l) => (
            <a key={l} href="#" className="hover:text-[#0284C7] dark:hover:text-cyan-300 transition-colors">{l}</a>
          ))}
        </div>
      </footer>
    </div>
  );
}
