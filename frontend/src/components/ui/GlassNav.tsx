'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { AuroraText } from './aurora-text';
import { AnimatedThemeToggler } from './animated-theme-toggler';

const navSteps = [
  { label: '1. Upload & Parse', href: '/upload' },
  { label: '2. ATS Diagnostics', href: '/dashboard' },
  { label: '3. Optimizer', href: '/optimization' },
  { label: '4. Templates', href: '/optimization/templates' },
];

export default function GlassNav() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === '/upload' && pathname === '/') return true;
    return pathname.startsWith(href);
  };

  const isWelcome = pathname === '/';

  return (
    <header
      className="sticky top-0 z-30 backdrop-blur-xl border-b border-slate-200 dark:border-white/[0.08] bg-white/85 dark:bg-[rgba(9,14,24,0.85)] shadow-[0_4px_16px_-8px_rgba(15,23,42,0.2)] dark:shadow-[0_4px_24px_0_rgba(0,0,0,0.35)] transition-all duration-300"
      data-purpose="top-navigation"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Logo */}
        <div className="flex items-center space-x-3">
          <Link href="/" className="flex items-center space-x-2.5 group cursor-pointer">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 p-[1px] shadow-sm group-hover:shadow-indigo-500/30 transition-all duration-200">
              <div className="w-full h-full bg-white dark:bg-[#090e18] rounded-[7px] flex items-center justify-center">
                <svg className="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path d="M13 10V3L4 14h7v7l9-11h-7z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" />
                </svg>
              </div>
            </div>
            <AuroraText className="text-sm sm:text-base font-bold tracking-tight font-sans" speed={1.2}>
              Career Copilot
            </AuroraText>
          </Link>
        </div>

        {/* Step nav — hidden on welcome page */}
        {!isWelcome && (
          <nav
            className="hidden md:flex items-center p-1 rounded-xl bg-slate-100 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.07] backdrop-blur-md space-x-1"
            data-purpose="primary-links"
          >
            {navSteps.map((step) => {
              const active = isActive(step.href);
              return (
                <Link
                  key={step.href}
                  href={step.href}
                  className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 ${
                    active
                      ? 'text-white bg-gradient-to-r from-indigo-600/50 to-cyan-600/50 border border-cyan-500/40 shadow-sm font-semibold'
                      : 'text-slate-500 hover:text-slate-900 hover:bg-slate-200/60 dark:text-slate-400 dark:hover:text-slate-200 dark:hover:bg-white/[0.04]'
                  }`}
                >
                  {active && (
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-300 shadow-[0_0_6px_rgba(0,240,255,0.7)]" />
                  )}
                  {step.label}
                </Link>
              );
            })}
          </nav>
        )}

        {/* Right: theme + profile */}
        <div className="flex items-center space-x-3">
          <AnimatedThemeToggler
            variant="circle"
            duration={500}
            className="flex items-center justify-center w-8 h-8 rounded-full bg-white border-slate-200 text-slate-500 hover:text-[#0284C7] hover:border-sky-300 dark:bg-white/[0.03] dark:border-white/10 dark:text-slate-300 dark:hover:text-cyan-300 dark:hover:border-cyan-500/40 border transition-all cursor-pointer [&_svg]:w-4 [&_svg]:h-4"
          />
          <div className="h-4 w-px bg-slate-200 dark:bg-white/10 hidden sm:block" />
          <div
            className="flex items-center space-x-2 pl-1 pr-3 py-1 rounded-full bg-white border-slate-200 hover:border-slate-300 dark:bg-white/[0.03] dark:border-white/10 dark:hover:border-white/20 border transition-all cursor-pointer"
            data-purpose="student-profile-badge"
          >
            <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-indigo-600 to-cyan-400 p-[1px]">
              <div className="w-full h-full rounded-full bg-white dark:bg-[#0d1424] flex items-center justify-center text-[10px] font-bold text-indigo-600 dark:text-white">
                AK
              </div>
            </div>
            <div className="flex items-center text-xs space-x-1.5 text-slate-700 dark:text-slate-200">
              <span className="font-medium hidden sm:inline">Arun Kumar</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
