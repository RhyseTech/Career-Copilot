"use client";

import { useEffect, useRef } from "react";
import { useInView, useMotionValue, useSpring } from "motion/react";
import { cn } from "@/lib/utils";

interface SyncedBreakdownBarProps {
  label: string;
  value: number;
  index?: number;
}

export function SyncedBreakdownBar({ label, value, index = 0 }: SyncedBreakdownBarProps) {
  const warning = value < 70;
  const wrapRef = useRef<HTMLDivElement>(null);
  const numberRef = useRef<HTMLSpanElement>(null);
  const barRef = useRef<HTMLDivElement>(null);

  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, { damping: 60, stiffness: 100 });
  const isInView = useInView(wrapRef, { once: true, margin: "0px" });

  // Stagger each row slightly, after the main ring (0.2s + index * 0.1s)
  const delay = 0.3 + index * 0.12;

  useEffect(() => {
    if (!isInView) return;
    const timer = setTimeout(() => motionValue.set(value), delay * 1000);
    return () => clearTimeout(timer);
  }, [isInView, motionValue, value, delay]);

  // One spring drives BOTH % number and bar width — perfect sync
  useEffect(
    () =>
      springValue.on("change", (latest) => {
        const clamped = Math.max(0, Math.min(100, latest));
        if (numberRef.current) {
          numberRef.current.textContent = `${Math.round(clamped)}%`;
        }
        if (barRef.current) {
          barRef.current.style.width = `${clamped}%`;
        }
      }),
    [springValue]
  );

  // Re-run when score changes
  useEffect(() => {
    motionValue.set(0);
    if (!isInView) return;
    const timer = setTimeout(() => motionValue.set(value), delay * 1000);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return (
    <div ref={wrapRef}>
      <div className="flex justify-between text-xs font-semibold mb-1.5">
        <span className="text-slate-600 dark:text-slate-300 flex items-center gap-1.5">
          {label}
          {warning && <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />}
        </span>
        <span
          ref={numberRef}
          className={cn("font-mono tabular-nums", warning ? "text-amber-600 dark:text-amber-400 font-bold" : "text-[#0284C7] dark:text-cyan-300")}
        >
          0%
        </span>
      </div>
      <div className="w-full h-2 bg-slate-200 dark:bg-slate-800/80 rounded-full overflow-hidden">
        <div
          ref={barRef}
          className={cn(
            "h-full rounded-full",
            warning
              ? "bg-gradient-to-r from-amber-500 to-amber-400 shadow-[0_0_8px_rgba(245,158,11,0.4)]"
              : "bg-gradient-to-r from-indigo-500 to-cyan-400 shadow-[0_0_8px_rgba(0,240,255,0.4)]"
          )}
          style={{ width: "0%" }}
        />
      </div>
    </div>
  );
}
