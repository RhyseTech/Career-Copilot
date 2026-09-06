'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useResumeStore } from '@/lib/resumeStore';
import { uploadAndParse } from '@/lib/api';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const { setUploadData } = useResumeStore();

  const handleFile = (f: File) => {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(f.type)) {
      setError('Please upload a valid PDF or DOCX file.');
      return;
    }
    setError(null);
    setFile(f);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleAnalyze = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (!file) return;
    
    setAnalyzing(true);
    setError(null);
    
    try {
      // In this demo, we assume no JD text for the default upload route.
      // JD parsing is typically a separate mode or input.
      const parsedData = await uploadAndParse(file);
      
      setUploadData({
        resumeId: parsedData.resume_id,
        filename: parsedData.filename,
        rawText: parsedData.raw_resume_text,
        structuredResume: parsedData.structured_resume,
      });
      
      // Navigate to dashboard automatically
      router.push('/dashboard');
    } catch (err: any) {
      console.error("Upload failed:", err);
      setError(err.message || 'Failed to upload and parse the resume. Ensure backend is running.');
      setAnalyzing(false);
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    return `${Math.round(bytes / 1024)} KB`;
  };

  return (
    <div className="relative flex-1 flex flex-col items-center justify-center px-4 sm:px-6 py-10 lg:py-16">
      <div className="w-full max-w-xl flex flex-col items-center">
        {/* Upload card */}
        <div
          className="w-full backdrop-blur-2xl border border-slate-200 dark:border-white/15 shadow-[0_12px_32px_-16px_rgba(15,23,42,0.25)] dark:shadow-[0_12px_40px_rgba(0,0,0,0.5)] rounded-2xl p-8 max-w-xl mx-auto relative overflow-hidden transition-all duration-300 bg-white/90 dark:bg-[rgba(15,23,42,0.6)]"
        >
          <div className="absolute -top-px left-8 right-8 h-px bg-gradient-to-r from-transparent via-cyan-400/60 to-transparent" />

          {/* Card header */}
          <div className="text-left mb-6">
            <h1 className="text-2xl sm:text-[28px] font-bold tracking-tight leading-snug bg-gradient-to-r from-slate-900 via-slate-700 to-slate-500 dark:from-white dark:via-slate-100 dark:to-slate-400 bg-clip-text text-transparent">
              Upload your Resume
            </h1>
            <div className="mt-2.5 flex flex-wrap items-center gap-2 text-xs">
              <span className="px-2.5 py-1 rounded-md border border-slate-200 dark:border-white/10 text-slate-600 dark:text-slate-300 font-medium bg-white dark:bg-white/[0.04]">
                Supported formats: PDF, DOCX
              </span>
              <span className="px-2.5 py-1 rounded-md border border-slate-200 dark:border-white/10 text-slate-500 dark:text-slate-400 font-medium bg-white dark:bg-white/[0.04]">
                Max size 10MB
              </span>
            </div>
          </div>

          {/* Dropzone */}
          <div
            className="group/dz border-2 border-dashed border-sky-300 dark:border-cyan-500/40 hover:border-[#0284C7] dark:hover:border-cyan-400 hover:shadow-[0_0_24px_rgba(0,240,255,0.18)] rounded-xl p-7 transition-all duration-300 flex flex-col items-center justify-center text-center cursor-pointer relative bg-sky-50/60 dark:bg-[rgba(2,6,23,0.4)]"
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            data-purpose="resume-dropzone"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              className="sr-only"
              id="resumeFileInput"
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
            />

            {/* Icon */}
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-indigo-500/15 border border-cyan-500/30 text-[#0284C7] dark:text-cyan-400 flex items-center justify-center mb-3.5 group-hover/dz:scale-105 group-hover/dz:border-[#0284C7] dark:group-hover/dz:border-cyan-400 transition-all duration-300">
              <svg className="w-7 h-7 group-hover/dz:-translate-y-0.5 transition-transform" fill="none" stroke="currentColor" strokeWidth="1.9" viewBox="0 0 24 24">
                <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>

            <div className="text-base font-semibold text-slate-700 dark:text-slate-100 group-hover/dz:text-slate-900 dark:group-hover/dz:text-white transition-colors">
              Click to upload <span className="font-normal text-slate-500 dark:text-slate-400">or drag &amp; drop</span>
            </div>

            {/* File chip */}
            {file && (
              <div className="mt-4 inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-lg border border-cyan-500/30 text-xs text-slate-600 dark:text-slate-200 shadow-sm dark:shadow-[0_2px_12px_rgba(0,0,0,0.3)] bg-white dark:bg-[rgba(30,41,59,0.8)]">
                <svg className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <span className="font-medium text-slate-700 dark:text-slate-100 tracking-tight">{file.name}</span>
                <span className="text-slate-500 dark:text-slate-400">• {formatSize(file.size)}</span>
                <button
                  type="button"
                  aria-label="Remove file"
                  className="ml-1 text-slate-500 dark:text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 focus:outline-none transition-colors"
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </button>
              </div>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-3 bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/30 rounded-xl text-rose-600 dark:text-rose-300 text-sm font-medium">
              {error}
            </div>
          )}

          {/* CTA */}
          <div className="mt-6">
            <button
              onClick={handleAnalyze}
              disabled={!file || analyzing}
              className={`w-full py-3.5 px-6 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 tracking-wide text-sm sm:text-base cursor-pointer focus:outline-none focus:ring-2 focus:ring-cyan-400 ${
                !file ? 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-500 cursor-not-allowed border border-slate-300 dark:border-slate-700' :
                analyzing ? 'bg-indigo-600 opacity-90 cursor-wait text-white' :
                'bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:shadow-[0_0_25px_rgba(0,240,255,0.4)] active:scale-[0.99] text-white'
              }`}
            >
              {analyzing ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Parsing Document...</span>
                </>
              ) : (
                <>
                  <span>Analyze Resume</span>
                  <span className="text-base leading-none">→</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Trust badges */}
        <aside aria-label="Privacy & Standards Notice" className="mt-8 w-full max-w-xl mx-auto">
          <div
            className="px-5 py-3 rounded-2xl border border-slate-200 dark:border-white/10 backdrop-blur-md flex flex-wrap items-center justify-center gap-y-2.5 gap-x-5 text-xs text-slate-600 dark:text-slate-300 shadow-sm dark:shadow-[0_4px_16px_rgba(0,0,0,0.3)] bg-white/90 dark:bg-[rgba(15,23,42,0.4)]"
          >
            {[
              { icon: 'shield', text: 'Strict Student Privacy Guarantee', color: 'text-emerald-600 dark:text-emerald-400' },
              { icon: 'bolt', text: '10s Instant ATS Scoring', color: 'text-[#0284C7] dark:text-cyan-400' },
              { icon: 'dot-indigo', text: 'Aligned with IIT/NIT & Tier 1/2 Placement Cells', color: '' },
              { icon: 'dot-cyan', text: 'Superset & CoCubes Calibrated', color: '' },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-1.5">
                {item.icon === 'shield' && (
                  <svg className={`w-4 h-4 ${item.color} shrink-0`} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
                {item.icon === 'bolt' && (
                  <svg className={`w-4 h-4 ${item.color} shrink-0`} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path d="M13 10V3L4 14h7v7l9-11h-7z" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
                {item.icon === 'dot-indigo' && <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0" />}
                {item.icon === 'dot-cyan' && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" />}
                <span className={item.icon === 'shield' ? 'font-medium text-slate-600 dark:text-slate-200' : ''}>{item.text}</span>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
