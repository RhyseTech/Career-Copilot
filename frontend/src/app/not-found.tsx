import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="relative flex flex-col min-h-[calc(100vh-4rem)] select-none" style={{ background: 'transparent' }}>
      {/* CRT scanlines overlay (uses global ThreeBackground behind) */}
      <div
        className="pointer-events-none absolute inset-0 z-[1] opacity-20"
        style={{
          background: 'linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,0.35) 50%, rgba(0,0,0,0.35))',
          backgroundSize: '100% 4px',
        }}
        aria-hidden="true"
      />

      {/* Ambient glow orbs */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[580px] h-[580px] bg-cyan-500/12 rounded-full pointer-events-none animate-glow-pulse z-0" aria-hidden="true" />
      <div className="absolute top-1/2 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[480px] h-[480px] bg-fuchsia-600/12 rounded-full pointer-events-none animate-glow-pulse z-0" style={{ animationDelay: '2.5s' }} aria-hidden="true" />

      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 py-16 text-center max-w-xl mx-auto w-full">
        {/* Glitch 404 */}
        <div className="relative animate-float">
          <div className="absolute inset-0 flex items-center justify-center -z-10 blur-3xl opacity-40" aria-hidden="true">
            <span className="text-8xl md:text-[150px] font-black tracking-tighter text-cyan-400 select-none">404</span>
          </div>
          <h1 className="notfound-glitch text-7xl sm:text-8xl md:text-[140px] font-black tracking-tight leading-none text-slate-900 dark:text-white select-none">
            404
          </h1>
        </div>

        <h2 className="mt-4 text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
          Page not found
        </h2>

        <p className="mt-3 text-sm sm:text-base text-slate-500 dark:text-slate-400 leading-relaxed">
          The page you are looking for doesn&apos;t exist or was moved.
        </p>

        <Link
          href="/"
          className="mt-8 inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 hover:shadow-[0_0_25px_rgba(0,240,255,0.4)] transition-all hover:-translate-y-0.5"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          </svg>
          Go to Home
        </Link>
      </main>

      <style>{`
        .notfound-glitch {
          text-shadow: -2px -1px 0 #00f0ff, 2px 1px 0 #ff007f, 0 0 25px rgba(0,240,255,0.4);
          animation: textGlitchRGB 3.5s infinite;
        }
        html:not(.dark) .notfound-glitch {
          text-shadow: -2px -1px 0 #0284C7, 2px 1px 0 #4F46E5, 0 0 25px rgba(2,132,199,0.35);
          animation-name: textGlitchLight;
        }
        @keyframes textGlitchLight {
          0%, 100% {
            text-shadow: -2px -1px 0 #0284C7, 2px 1px 0 #4F46E5, 0 0 25px rgba(2,132,199,0.35);
          }
          38% { text-shadow: -2px -1px 0 #0284C7, 2px 1px 0 #4F46E5; }
          40% {
            text-shadow: 3px -2px 0 #4F46E5, -3px 2px 0 #0284C7, 0 0 35px rgba(2,132,199,0.5);
            transform: translate(-1px, 1px);
          }
          42% {
            text-shadow: -3px 2px 0 #4F46E5, 3px -2px 0 #0284C7;
            transform: translate(2px, -1px);
          }
          44% {
            text-shadow: -2px -1px 0 #0284C7, 2px 1px 0 #4F46E5;
            transform: translate(0, 0);
          }
          78% { text-shadow: -2px -1px 0 #0284C7, 2px 1px 0 #4F46E5; }
          80% {
            text-shadow: 4px 1px 0 #0284C7, -4px -1px 0 #4F46E5;
            transform: translate(-1.5px, 0);
          }
          82% {
            text-shadow: -2px -1px 0 #0284C7, 2px 1px 0 #4F46E5;
            transform: translate(0, 0);
          }
        }
        @keyframes textGlitchRGB {
          0%, 100% {
            text-shadow: -2px -1px 0 #00f0ff, 2px 1px 0 #ff007f, 0 0 25px rgba(0,240,255,0.4);
          }
          38% { text-shadow: -2px -1px 0 #00f0ff, 2px 1px 0 #ff007f; }
          40% {
            text-shadow: 3px -2px 0 #ff007f, -3px 2px 0 #00f0ff, 0 0 35px rgba(0,240,255,0.7);
            transform: translate(-1px, 1px);
          }
          42% {
            text-shadow: -3px 2px 0 #ff007f, 3px -2px 0 #00f0ff;
            transform: translate(2px, -1px);
          }
          44% {
            text-shadow: -2px -1px 0 #00f0ff, 2px 1px 0 #ff007f;
            transform: translate(0, 0);
          }
          78% { text-shadow: -2px -1px 0 #00f0ff, 2px 1px 0 #ff007f; }
          80% {
            text-shadow: 4px 1px 0 #00f0ff, -4px -1px 0 #ff007f;
            transform: translate(-1.5px, 0);
          }
          82% {
            text-shadow: -2px -1px 0 #00f0ff, 2px 1px 0 #ff007f;
            transform: translate(0, 0);
          }
        }
      `}</style>
    </div>
  );
}
