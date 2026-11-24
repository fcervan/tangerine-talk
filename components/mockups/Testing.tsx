"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckIcon, StarIcon } from "../icons";
import { EASE } from "@/lib/ease";

const DECK = [
  { f: "Gracias", b: "Obrigado" },
  { f: "Hasta luego", b: "Até logo" },
  { f: "Buenos días", b: "Bom dia" },
  { f: "¿Cómo estás?", b: "Como vai?" },
];

export default function Testing() {
  const [i, setI] = useState(0);
  const [flip, setFlip] = useState(false);
  const [known, setKnown] = useState(0);
  const [saved, setSaved] = useState(0);
  const done = i >= DECK.length;

  const next = (ok: boolean) => { if (ok) setKnown((k) => k + 1); setFlip(false); setI((n) => n + 1); };
  const restart = () => { setI(0); setKnown(0); setFlip(false); };

  return (
    <div className="flex h-full flex-col px-5 pb-5 pt-12">
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow">Testes · Flashcards</p>
          <p className="mt-1 text-[13px] text-body">Toque no cartão para virar</p>
        </div>
        <span className="rounded-pill bg-tangerine-soft px-3 py-1 text-[12px] font-semibold text-tangerine">{Math.min(i + 1, DECK.length)}/{DECK.length}</span>
      </div>

      <div className="mt-3 flex gap-1.5">
        {DECK.map((_, n) => (
          <motion.span key={n} animate={{ backgroundColor: n < i ? "#FF5A0A" : n === i ? "#FF7A33" : "#FFE9DC" }} transition={{ duration: 0.4 }} className="h-1.5 flex-1 rounded-full" />
        ))}
      </div>

      <div className="relative mt-6 h-[230px]" style={{ perspective: 1000 }}>
        <AnimatePresence mode="popLayout">
          {!done ? (
            <motion.div key={i} initial={{ x: 120, opacity: 0, rotate: 6 }} animate={{ x: 0, opacity: 1, rotate: 0 }} exit={{ x: -120, opacity: 0, rotate: -6 }} transition={{ type: "spring", stiffness: 300, damping: 26 }} className="absolute inset-0">
              <motion.div onClick={() => setFlip((f) => !f)} animate={{ rotateY: flip ? 180 : 0 }} transition={{ type: "spring", stiffness: 180, damping: 18 }} className="preserve-3d relative h-full w-full cursor-pointer">
                <div className="backface-hidden absolute inset-0 flex flex-col items-center justify-center rounded-[24px] bg-white shadow-lift">
                  <span className="mb-3 rounded-pill bg-tangerine-soft px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-tangerine">Espanhol</span>
                  <p className="text-[32px] font-bold text-ink">{DECK[i].f}</p>
                </div>
                <div className="backface-hidden absolute inset-0 flex flex-col items-center justify-center rounded-[24px] bg-gradient-to-br from-tangerine-light to-tangerine-dark text-white shadow-cta" style={{ transform: "rotateY(180deg)" }}>
                  <span className="mb-3 rounded-pill bg-white/20 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.12em]">Português</span>
                  <p className="text-[30px] font-bold">{DECK[i].b}</p>
                </div>
              </motion.div>
            </motion.div>
          ) : (
            <motion.div key="done" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.6, ease: EASE }} className="absolute inset-0 flex flex-col items-center justify-center rounded-[24px] bg-tangerine-soft text-center">
              <span className="mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-tangerine text-white"><StarIcon size={28} /></span>
              <p className="text-[20px] font-bold text-ink">Baralho concluído!</p>
              <p className="mt-1 text-[13px] text-body">{known}/{DECK.length} de primeira</p>
              <button onClick={restart} className="mt-4 rounded-pill bg-tangerine px-5 py-2 text-[13px] font-semibold text-white">Praticar de novo</button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {!done && (
        <div className="mt-5 grid grid-cols-2 gap-3">
          <motion.button whileTap={{ scale: 0.95 }} onClick={() => next(false)} className="rounded-pill border border-line bg-white py-3 text-[14px] font-semibold text-ink hover:border-tangerine">Revisar de novo</motion.button>
          <motion.button whileTap={{ scale: 0.95 }} onClick={() => next(true)} className="flex items-center justify-center gap-1.5 rounded-pill bg-tangerine py-3 text-[14px] font-semibold text-white shadow-cta"><CheckIcon size={16} />Acertei</motion.button>
        </div>
      )}

      <button onClick={() => setSaved((s) => s + 1)} className="mt-auto flex items-center justify-between rounded-2xl bg-tangerine-soft px-4 py-3 text-left">
        <span className="text-[13px] font-medium text-ink">Monte seu próprio baralho</span>
        <span className="flex items-center gap-2">
          <AnimatePresence mode="popLayout"><motion.span key={saved} initial={{ y: 12, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: -12, opacity: 0 }} className="text-[13px] font-bold text-tangerine">{saved} novo{saved === 1 ? "" : "s"}</motion.span></AnimatePresence>
          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-tangerine text-[16px] leading-none text-white">+</span>
        </span>
      </button>
    </div>
  );
}
