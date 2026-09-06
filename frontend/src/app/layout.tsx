import type { Metadata } from 'next';
import './globals.css';
import ThreeBackground from '@/components/ui/ThreeBackground';
import GlassNav from '@/components/ui/GlassNav';
import { ResumeProvider } from '@/lib/resumeStore';

export const metadata: Metadata = {
  title: 'Career Copilot — Campus Placement & ATS Suite',
  description: 'AI-powered resume analysis, ATS scoring, and optimization for campus placements across India.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark h-full antialiased" suppressHydrationWarning>
      <head>
        {/* Set initial theme before paint: default dark, respect saved choice */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('theme');if(t==='light'){document.documentElement.classList.remove('dark')}else{document.documentElement.classList.add('dark')}}catch(e){document.documentElement.classList.add('dark')}})();`,
          }}
        />
      </head>
      <body className="relative bg-[#e9edf6] text-[#0f172a] dark:bg-[#070a13] dark:text-slate-100 font-sans min-h-screen flex flex-col overflow-x-hidden selection:bg-indigo-500/30 selection:text-indigo-100" suppressHydrationWarning>
        <ResumeProvider>
          {/* Three.js animated background + vignette overlay */}
          <ThreeBackground />

          {/* All page content sits above the Three.js canvas */}
          <div className="relative z-10 flex flex-col min-h-screen">
            {/* Glassmorphic sticky navigation */}
            <GlassNav />

            {/* Page content */}
            <main className="flex-1">
              {children}
            </main>
          </div>
        </ResumeProvider>
      </body>
    </html>
  );
}
