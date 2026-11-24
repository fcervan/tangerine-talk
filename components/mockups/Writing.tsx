"use client";

import { useState } from "react";
import { AnimatePresence, LayoutGroup, motion } from "framer-motion";
import { CheckIcon } from "../icons";
import { EASE } from "@/lib/ease";

const ANSWER = ["I", "would", "like", "a", "coffee,", "please"];
const START = ["coffee,", "a", "please", "I", "like", "would"];
const SPRING = { type: "spring", stiffness: 520, damping: 32 } as const;

export default function Writing() {
  const [placed, setPlaced] = useState<string[]>([]);
  const [result, setResult] = useState<null | "ok" | "no">(null);
  const bank = START.filter((w) => !placed.includes(w));

  const add = (w: string) => { setResult(null); setPlaced((p) => [...p, w]); };
  const remove = (w: string) => { setResult(null); setPlaced((p) => p.filter((x) => x !== w)); };
  const check = () => setResult(placed.join(" ") === ANSWER.join(" ") ? "ok" : "no");

  const tile = (w: string, inAnswer: boolean) => (
    <motion.button
      key={w}
      layout
      layoutId={`tile-${w}`}
      transition={SPRING}
      onClick={() => (inAnswer ? remove(w) : add(w))}
      whileHover={{ y: -3 }}
      whileTap={{ scale: 0.9 }}
      className={`rounded-xl px-4 py-2.5 text-[15px] font-semibold shadow-[0_4px_0_#FFD2B8] ${inAnswer ? "bg-tangerine text-white shadow-[0_4px_0_#E64A00]" : "bg-white text-ink ring-1 ring-tangerine-tint"}`}
    >
      {w}
    </motion.button>
  );

  return (
    <div className="flex h-full flex-col bg-tangerine-soft px-5 pb-5 pt-12">
      <p className="eyebrow">Escrita · Inglês</p>
      <p className="mt-1 text-[13px] text-body">Traduza esta frase</p>
      <p className="mt-3 rounded-2xl bg-white p-4 text-[17px] font-semibold leading-snug text-ink shadow-card">“Eu gostaria de um café, por favor.”</p>

      <LayoutGroup>
        <motion.div
          animate={result === "no" ? { x: [0, -8, 8, -6, 6, 0] } : { x: 0 }}
          transition={{ duration: 0.45, ease: EASE }}
          className={`mt-5 flex min-h-[112px] flex-wrap content-start gap-2 rounded-2xl border-2 border-dashed p-3 transition-colors duration-300 ${result === "ok" ? "border-tangerine bg-white" : "border-tangerine-tint bg-white/60"}`}
        >
          {placed.map((w) => tile(w, true))}
          {placed.length === 0 && <span className="m-auto text-[13px] text-body/70">Toque nas palavras para montar a frase</span>}
        </motion.div>
        <div className="mt-5 flex min-h-[110px] flex-wrap content-start justify-center gap-2.5">{bank.map((w) => tile(w, false))}</div>
      </LayoutGroup>

      <div className="mt-auto">
        <AnimatePresence mode="wait">
          {result === "ok" ? (
            <motion.div key="ok" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="flex items-center justify-between rounded-2xl bg-tangerine px-4 py-3 text-white">
              <span className="flex items-center gap-2 text-[14px] font-semibold"><CheckIcon size={18} /> Perfeito! +15 XP</span>
              <button onClick={() => { setPlaced([]); setResult(null); }} className="text-[12px] font-medium underline">De novo</button>
            </motion.div>
          ) : (
            <motion.button
              key="check"
              disabled={placed.length < ANSWER.length}
              onClick={check}
              whileTap={{ scale: 0.97 }}
              className="w-full rounded-pill bg-tangerine py-3 text-[15px] font-semibold text-white shadow-cta transition-opacity duration-300 disabled:bg-tangerine-tint disabled:text-tangerine disabled:shadow-none"
            >
              {result === "no" ? "Quase — tente de novo" : "Verificar"}
            </motion.button>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
