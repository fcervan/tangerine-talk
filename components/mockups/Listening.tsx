"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Waveform from "./Waveform";
import { CheckIcon, PauseIcon, PlayIcon } from "../icons";
import { EASE } from "@/lib/ease";

const OPTS = [
  { t: "Onde fica a padaria?" },
  { t: "Onde fica a estação?", ok: true },
  { t: "Onde fica o hotel?" },
];

export default function Listening() {
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [pick, setPick] = useState<number | null>(null);
  const level = useRef(0.1);
  const target = useRef(0.1);
  const barRef = useRef<HTMLDivElement>(null);
  const prog = useRef(0);
  const playRef = useRef(false);
  const speedRef = useRef(1);

  playRef.current = playing;
  speedRef.current = speed;

  useEffect(() => { target.current = playing ? 0.85 : 0.1; }, [playing]);

  useEffect(() => {
    let raf = 0, last = performance.now();
    const loop = (now: number) => {
      const dt = (now - last) / 1000; last = now;
      const jitter = target.current > 0.5 ? 0.75 + Math.random() * 0.25 : 1;
      level.current += (target.current * jitter - level.current) * 0.14;
      if (playRef.current) {
        prog.current += (dt * speedRef.current) / 3.4;
        if (prog.current >= 1) { prog.current = 0; setPlaying(false); }
      }
      if (barRef.current) barRef.current.style.transform = `scaleX(${prog.current})`;
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    const auto = window.setTimeout(() => setPlaying(true), 800);
    return () => { cancelAnimationFrame(raf); clearTimeout(auto); };
  }, []);

  return (
    <div className="flex h-full flex-col px-5 pb-5 pt-12">
      <p className="eyebrow">Escuta · Espanhol</p>
      <p className="mt-1 text-[13px] text-body">O que você ouviu?</p>

      <div className="mt-5 rounded-[22px] bg-tangerine-soft p-4">
        <Waveform level={level} bars={30} height={72} />
        <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-tangerine-tint">
          <div ref={barRef} className="h-full origin-left rounded-full bg-tangerine" style={{ transform: "scaleX(0)" }} />
        </div>
        <div className="mt-4 flex items-center justify-between">
          <motion.button whileTap={{ scale: 0.9 }} onClick={() => setPlaying((p) => !p)} className="flex h-11 w-11 items-center justify-center rounded-full bg-tangerine text-white shadow-cta" aria-label={playing ? "Pausar" : "Reproduzir"}>
            {playing ? <PauseIcon size={20} /> : <PlayIcon size={20} />}
          </motion.button>
          <div className="flex gap-1 rounded-pill bg-white p-1">
            {[0.75, 1].map((s) => (
              <button key={s} onClick={() => setSpeed(s)} className={`rounded-pill px-3 py-1 text-[12px] font-semibold transition-colors duration-300 ${speed === s ? "bg-tangerine text-white" : "text-ink"}`}>{s}×</button>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-5 flex flex-col gap-2.5">
        {OPTS.map((o, i) => {
          const chosen = pick === i;
          const right = chosen && o.ok;
          return (
            <motion.button
              key={o.t}
              onClick={() => setPick(i)}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.97 }}
              animate={chosen && !o.ok ? { x: [0, -6, 6, -4, 4, 0] } : { x: 0 }}
              transition={{ duration: 0.4, ease: EASE }}
              className={`flex items-center justify-between rounded-2xl border px-4 py-3 text-left text-[14px] font-medium transition-colors duration-300 ${
                right ? "border-tangerine bg-tangerine text-white" : chosen ? "border-ink bg-white text-ink" : "border-line bg-white text-ink hover:border-tangerine"
              }`}
            >
              {o.t}
              <AnimatePresence>{right && <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 500, damping: 18 }}><CheckIcon size={18} /></motion.span>}</AnimatePresence>
            </motion.button>
          );
        })}
      </div>
      <p className="mt-auto text-center text-[12px] text-body">“¿Dónde está la estación?”</p>
    </div>
  );
}
