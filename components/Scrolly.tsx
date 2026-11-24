"use client";

import { useLayoutEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { gsap, ScrollTrigger } from "@/lib/gsap";
import { getLenis } from "@/lib/lenis";
import { EASE } from "@/lib/ease";
import { EarIcon, MicIcon, PenIcon, TestIcon } from "./icons";
import Speaking from "./mockups/Speaking";
import Listening from "./mockups/Listening";
import Writing from "./mockups/Writing";
import Testing from "./mockups/Testing";

const STEPS = [
  { icon: MicIcon, k: "01 · Fala", title: "Fale desde o primeiro dia", body: "Converse com seu tutor de IA e veja a pronúncia ser pontuada palavra por palavra, na hora.", Screen: Speaking },
  { icon: EarIcon, k: "02 · Escuta", title: "Treine seu ouvido", body: "Áudio em velocidade nativa, com velocidade ajustável e testes de compreensão que se adaptam a você.", Screen: Listening },
  { icon: PenIcon, k: "03 · Escrita", title: "Monte frases, peça por peça", body: "Peças de palavras táteis se encaixam no lugar para a gramática virar memória muscular.", Screen: Writing },
  { icon: TestIcon, k: "04 · Testes", title: "Fixe de vez", body: "Flashcards que você mesmo monta, retomados bem antes de você esquecer.", Screen: Testing },
];

export default function Scrolly() {
  const root = useRef<HTMLElement>(null);
  const pin = useRef<HTMLDivElement>(null);
  const bar = useRef<HTMLDivElement>(null);
  const st = useRef<ScrollTrigger | null>(null);
  const [active, setActive] = useState(0);

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      st.current = ScrollTrigger.create({
        trigger: pin.current,
        start: "top top",
        end: "+=320%",
        pin: true,
        anticipatePin: 1,
        onUpdate: (s) => {
          if (bar.current) bar.current.style.transform = `scaleY(${s.progress})`;
          setActive(Math.min(STEPS.length - 1, Math.floor(s.progress * STEPS.length)));
        },
      });
    }, root);
    return () => ctx.revert();
  }, []);

  const goTo = (i: number) => {
    const s = st.current;
    if (!s) return;
    const y = s.start + ((i + 0.5) / STEPS.length) * (s.end - s.start);
    const lenis = getLenis();
    if (lenis) lenis.scrollTo(y, { duration: 1.3, easing: (t) => 1 - Math.pow(1 - t, 4) });
    else window.scrollTo({ top: y, behavior: "smooth" });
  };

  const Screen = STEPS[active].Screen;

  return (
    <section id="how-it-works" ref={root} className="bg-mist">
      <div ref={pin} className="flex min-h-[700px] items-center overflow-hidden py-16 lg:h-screen lg:py-0">
        <div className="mx-auto grid w-full max-w-[1200px] items-center gap-8 px-5 lg:grid-cols-[1fr_380px] lg:gap-16">
          {/* left */}
          <div className="order-2 lg:order-1 lg:col-span-1">
            <p className="eyebrow mb-3">O ciclo central de aprendizado</p>
            <h2 className="h2 mb-8">Aprenda do jeito que você <span className="hl">realmente</span> vai usar.</h2>
            <div className="relative pl-7">
              <div className="absolute bottom-1 left-0 top-1 w-[3px] rounded-full bg-tangerine-tint">
                <div ref={bar} className="h-full w-full origin-top rounded-full bg-tangerine" style={{ transform: "scaleY(0)" }} />
              </div>
              {STEPS.map(({ icon: Icon, k, title, body }, i) => (
                <button key={k} onClick={() => goTo(i)} className="group mb-2 block w-full rounded-2xl p-3 text-left transition-colors duration-500 hover:bg-white/70">
                  <div className="flex items-center gap-3">
                    <span className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl transition-colors duration-500 ${i === active ? "bg-tangerine text-white" : "bg-white text-tangerine"}`}><Icon size={18} /></span>
                    <div>
                      <p className={`text-[11px] font-semibold uppercase tracking-[0.12em] transition-colors duration-500 ${i === active ? "text-tangerine" : "text-body/60"}`}>{k}</p>
                      <p className={`text-[17px] font-semibold transition-colors duration-500 ${i === active ? "text-ink" : "text-ink/45"}`}>{title}</p>
                    </div>
                  </div>
                  <motion.div initial={false} animate={{ height: i === active ? "auto" : 0, opacity: i === active ? 1 : 0 }} transition={{ duration: 0.5, ease: EASE }} className="overflow-hidden">
                    <p className="pl-12 pt-2 text-[14px] leading-relaxed text-body">{body}</p>
                  </motion.div>
                </button>
              ))}
            </div>
          </div>

          {/* device */}
          <div className="relative order-1 mx-auto lg:order-2">
            <motion.div animate={{ scale: [1, 1.06, 1] }} transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }} className="absolute left-1/2 top-1/2 h-[420px] w-[420px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-tangerine-tint/70 blur-2xl" />
            <div className="relative h-[560px] w-[300px] rounded-[46px] bg-ink p-[10px] shadow-[0_30px_60px_rgba(17,17,17,0.18)] sm:w-[320px]">
              <div className="absolute left-1/2 top-[18px] z-20 h-[22px] w-[84px] -translate-x-1/2 rounded-full bg-ink" />
              <div className="relative h-full w-full overflow-hidden rounded-[36px] bg-white">
                <AnimatePresence mode="wait">
                  <motion.div key={active} initial={{ opacity: 0, y: 28, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -20, scale: 0.98 }} transition={{ duration: 0.5, ease: EASE }} className="absolute inset-0">
                    <Screen />
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
