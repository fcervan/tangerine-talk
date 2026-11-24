"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Waveform from "./Waveform";
import { MicIcon } from "../icons";
import { EASE } from "@/lib/ease";

const WORDS = [
  { w: "Buenos", s: 98 },
  { w: "días,", s: 95 },
  { w: "¿cómo", s: 72 },
  { w: "estás?", s: 99 },
];
const AVG = Math.round(WORDS.reduce((a, b) => a + b.s, 0) / WORDS.length);
type Phase = "idle" | "listening" | "feedback";

export default function Speaking() {
  const [phase, setPhase] = useState<Phase>("idle");
  const level = useRef(0.08);
  const target = useRef(0.08);
  const timers = useRef<number[]>([]);

  const clear = () => { timers.current.forEach(clearTimeout); timers.current = []; };

  const run = useCallback(() => {
    clear();
    setPhase("listening");
    target.current = 0.95;
    timers.current.push(
      window.setTimeout(() => { setPhase("feedback"); target.current = 0.06; }, 3000),
      window.setTimeout(() => setPhase("idle"), 8200)
    );
  }, []);

  useEffect(() => {
    const t0 = window.setTimeout(run, 700);
    const iv = window.setInterval(run, 9400);
    let raf = 0;
    const loop = () => {
      const jitter = target.current > 0.5 ? 0.78 + Math.random() * 0.22 : 1;
      level.current += (target.current * jitter - level.current) * 0.14;
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => { clearTimeout(t0); clearInterval(iv); clear(); cancelAnimationFrame(raf); };
  }, [run]);

  return (
    <div className="flex h-full flex-col px-5 pb-5 pt-12">
      <p className="eyebrow">Fala · Espanhol</p>
      <p className="mt-1 text-[13px] text-body">Diga isto em voz alta</p>

      <p className="mt-4 flex flex-wrap gap-x-2 text-[26px] font-bold leading-tight">
        {WORDS.map(({ w, s }) => (
          <span
            key={w}
            className={`transition-colors duration-500 ${
              phase === "feedback" ? (s >= 90 ? "text-tangerine" : "text-ink underline decoration-tangerine decoration-wavy underline-offset-4") : phase === "listening" ? "text-ink" : "text-ink/30"
            }`}
          >
            {w}
          </span>
        ))}
      </p>

      <div className="mt-6 rounded-[22px] bg-tangerine-soft px-3 py-5">
        <Waveform level={level} />
      </div>

      <div className="mt-4 min-h-[112px]">
        <AnimatePresence mode="wait">
          {phase === "feedback" ? (
            <motion.div key="fb" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.5, ease: EASE }} className="rounded-[20px] bg-white p-4 shadow-card">
              <div className="flex items-center gap-4">
                <div className="relative h-14 w-14 shrink-0">
                  <svg viewBox="0 0 48 48" className="-rotate-90">
                    <circle cx="24" cy="24" r="20" fill="none" stroke="#FFE9DC" strokeWidth="5" />
                    <motion.circle cx="24" cy="24" r="20" fill="none" stroke="#FF5A0A" strokeWidth="5" strokeLinecap="round" initial={{ pathLength: 0 }} animate={{ pathLength: AVG / 100 }} transition={{ duration: 1, ease: EASE }} />
                  </svg>
                  <span className="absolute inset-0 flex items-center justify-center text-[14px] font-bold text-ink">{AVG}%</span>
                </div>
                <div>
                  <p className="text-[15px] font-semibold text-ink">Ótima pronúncia!</p>
                  <p className="text-[12px] leading-snug text-body">Suavize o <b className="text-tangerine">“ó”</b> em <i>cómo</i> — deixe curto e aberto.</p>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.p key="hint" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="pt-6 text-center text-[13px] text-body">
              {phase === "listening" ? "Ouvindo…" : "Toque no microfone para tentar de novo"}
            </motion.p>
          )}
        </AnimatePresence>
      </div>

      <div className="mt-auto flex justify-center">
        <motion.button onClick={run} whileTap={{ scale: 0.9 }} whileHover={{ scale: 1.06 }} transition={{ type: "spring", stiffness: 400, damping: 18 }} className="relative flex h-16 w-16 items-center justify-center rounded-full bg-tangerine text-white shadow-cta" aria-label="Gravar">
          {phase === "listening" && <span className="absolute inset-0 animate-ping rounded-full bg-tangerine/40" />}
          <MicIcon size={26} className="relative" />
        </motion.button>
      </div>
    </div>
  );
}
