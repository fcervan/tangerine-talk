"use client";

import { useEffect, useRef, type MutableRefObject } from "react";

/** Audio-style bar visualizer. Reads `level` (0..1) from a ref every frame — no React re-renders. */
export default function Waveform({ level, bars = 34, height = 96 }: { level: MutableRefObject<number>; bars?: number; height?: number }) {
  const refs = useRef<(HTMLSpanElement | null)[]>([]);

  useEffect(() => {
    let raf = 0;
    const loop = (t: number) => {
      const l = level.current;
      refs.current.forEach((el, i) => {
        if (!el) return;
        const a = Math.sin(t / 170 + i * 0.55) * 0.5 + 0.5;
        const b = Math.sin(t / 85 + i * 1.3) * 0.5 + 0.5;
        const env = Math.sin((i / (bars - 1)) * Math.PI) * 0.8 + 0.2;
        const h = 5 + l * env * (0.35 * a + 0.65 * b) * (height - 5);
        el.style.height = `${h}px`;
        el.style.opacity = `${0.45 + Math.min(1, l) * 0.55}`;
      });
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [level, bars, height]);

  return (
    <div className="flex items-center justify-center gap-[3px]" style={{ height }} aria-hidden>
      {Array.from({ length: bars }).map((_, i) => (
        <span
          key={i}
          ref={(el) => { refs.current[i] = el; }}
          className="w-[4px] rounded-full bg-gradient-to-b from-tangerine-light to-tangerine-dark"
          style={{ height: 5 }}
        />
      ))}
    </div>
  );
}
