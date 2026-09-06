"use client";

import { useEffect, useRef } from "react";
import { useInView, useMotionValue, useSpring } from "motion/react";

interface SyncedScoreRingProps {
  value: number;
  isGood: boolean;
  radius?: number;
  delay?: number;
}

export function SyncedScoreRing({
  value,
  isGood,
  radius = 58,
  delay = 0.2,
}: SyncedScoreRingProps) {
  const circumference = 2 * Math.PI * radius;
  const numberRef = useRef<HTMLSpanElement>(null);
  const ringRef = useRef<SVGCircleElement>(null);
  const wrapRef = useRef<HTMLDivElement>(null);

  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, { damping: 60, stiffness: 100 });
  const isInView = useInView(wrapRef, { once: true, margin: "0px" });

  // Kick off count-up + ring sweep together
  useEffect(() => {
    if (!isInView) return;
    const timer = setTimeout(() => motionValue.set(value), delay * 1000);
    return () => clearTimeout(timer);
  }, [isInView, motionValue, value, delay]);

  // Single spring drives BOTH number text and ring offset — perfect sync
  useEffect(
    () =>
      springValue.on("change", (latest) => {
        const clamped = Math.max(0, Math.min(100, latest));
        if (numberRef.current) {
          numberRef.current.textContent = String(Math.round(clamped));
        }
        if (ringRef.current) {
          const offset = circumference - (clamped / 100) * circumference;
          ringRef.current.setAttribute("stroke-dashoffset", String(offset));
        }
      }),
    [springValue, circumference]
  );

  // Re-run when score changes (e.g. new resume analysed)
  useEffect(() => {
    motionValue.set(0);
    const timer = setTimeout(() => motionValue.set(value), delay * 1000);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return (
    <div ref={wrapRef} className="relative flex items-center justify-center">
      <svg className="w-36 h-36 transform -rotate-90">
        <defs>
          <linearGradient id="scoreRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={isGood ? "#00f0ff" : "#f59e0b"} />
            <stop offset="100%" stopColor={isGood ? "#6366f1" : "#ef4444"} />
          </linearGradient>
        </defs>
        <circle cx="72" cy="72" r={radius} fill="transparent" stroke="currentColor" strokeWidth="10" className="text-slate-200 dark:text-[#1e293b]" />
        <circle
          ref={ringRef}
          cx="72"
          cy="72"
          r={radius}
          fill="transparent"
          stroke="url(#scoreRingGrad)"
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <div className="flex items-baseline">
          <span
            ref={numberRef}
            className="text-5xl font-extrabold text-slate-900 dark:text-white tracking-tight tabular-nums dark:drop-shadow-[0_0_12px_rgba(0,240,255,0.4)]"
          >
            0
          </span>
          <span className="text-lg font-semibold text-slate-500 dark:text-slate-400">/100</span>
        </div>
      </div>
    </div>
  );
}
