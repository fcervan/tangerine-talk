"use client";

import { useState } from "react";
import { AnimatePresence, LayoutGroup, motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import PillButton from "./PillButton";
import { CheckIcon } from "./icons";
import { EASE } from "@/lib/ease";

const LANGS = [
  { name: "Espanhol", hello: "¡Hola!", line: "Buenos días", gloss: "Bom dia" },
  { name: "Japonês", hello: "こんにちは", line: "ありがとう", gloss: "Obrigado" },
  { name: "Francês", hello: "Bonjour !", line: "Enchanté", gloss: "Prazer em conhecer" },
  { name: "Alemão", hello: "Hallo!", line: "Wie geht's?", gloss: "Como vai?" },
  { name: "Italiano", hello: "Ciao!", line: "Piacere", gloss: "Prazer em conhecer" },
];

const H1 = ["Domine", "qualquer", "idioma", "naturalmente."];

export default function Hero() {
  const [lang, setLang] = useState(0);
  const L = LANGS[lang];

  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const cfg = { stiffness: 110, damping: 16, mass: 0.6 };
  const sx = useSpring(mx, cfg);
  const sy = useSpring(my, cfg);
  const rotY = useTransform(sx, [-1, 1], [-14, 14]);
  const rotX = useTransform(sy, [-1, 1], [12, -12]);
  const blobX = useTransform(sx, [-1, 1], [18, -18]);
  const blobY = useTransform(sy, [-1, 1], [14, -14]);
  const gridX = useTransform(sx, [-1, 1], [-26, 26]);
  const gridY = useTransform(sy, [-1, 1], [-20, 20]);

  const onMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    mx.set(((e.clientX - r.left) / r.width) * 2 - 1);
    my.set(((e.clientY - r.top) / r.height) * 2 - 1);
  };
  const onLeave = () => { mx.set(0); my.set(0); };

  return (
    <section id="top" className="relative overflow-hidden bg-white">
      <div className="mx-auto grid max-w-[1200px] items-center gap-10 px-5 pb-20 pt-10 lg:grid-cols-[45fr_55fr] lg:pb-28 lg:pt-16">
        {/* LEFT */}
        <div>
          <motion.p initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, ease: EASE }} className="eyebrow mb-5">
            Tutor de idiomas com IA
          </motion.p>
          <h1 className="text-[44px] font-bold leading-[1.04] tracking-tight text-ink sm:text-[58px] lg:text-[62px]">
            {H1.map((w, i) => (
              <span key={w} className="mr-[0.22em] inline-block overflow-hidden align-bottom">
                <motion.span
                  className={`inline-block ${w === "idioma" ? "text-tangerine" : ""}`}
                  initial={{ y: "110%" }}
                  animate={{ y: 0 }}
                  transition={{ duration: 0.9, ease: EASE, delay: 0.1 + i * 0.09 }}
                >
                  {w}
                </motion.span>
              </span>
            ))}
          </h1>
          <motion.p initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: EASE, delay: 0.55 }} className="mt-6 max-w-[460px] text-[17px] leading-relaxed text-body">
            Converse com um tutor de IA que escuta, corrige e torce por você em tempo real. Construa fluência de verdade em poucos minutos por dia — falando, ouvindo, escrevendo e brincando.
          </motion.p>
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: EASE, delay: 0.7 }} className="mt-9 flex flex-wrap items-center gap-5">
            <PillButton magnetic href="/login">Começar a aprender</PillButton>
            <div className="flex items-center gap-2 text-[14px] text-body">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-tangerine-lightBg text-tangerine-darker"><CheckIcon size={14} /></span>
              Grátis para começar · Sem cartão
            </div>
          </motion.div>
        </div>

        {/* RIGHT */}
        <motion.div
          initial={{ opacity: 0, scale: 0.94 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, ease: EASE, delay: 0.2 }}
          onMouseMove={onMove}
          onMouseLeave={onLeave}
          className="relative mx-auto aspect-[1/0.96] w-full max-w-[640px]"
          style={{ perspective: 1200 }}
        >
          {/* dotted grid */}
          <motion.div style={{ x: gridX, y: gridY }} className="dot-grid absolute -right-4 -top-4 h-[46%] w-[46%] opacity-70 [mask-image:radial-gradient(circle_at_70%_30%,#000_30%,transparent_75%)]" />
          <motion.div style={{ x: gridX, y: gridY }} className="dot-grid absolute -bottom-2 -left-4 h-[30%] w-[34%] opacity-60 [mask-image:radial-gradient(circle_at_30%_70%,#000_30%,transparent_75%)]" />

          {/* blob */}
          <motion.svg style={{ x: blobX, y: blobY }} viewBox="0 0 600 560" className="absolute inset-0 h-full w-full" aria-hidden>
            <defs>
              <linearGradient id="blobG" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stopColor="#FF7A33" />
                <stop offset="0.5" stopColor="#FF5A0A" />
                <stop offset="1" stopColor="#E64A00" />
              </linearGradient>
              <radialGradient id="gloss" cx="0.3" cy="0.18" r="0.6">
                <stop offset="0" stopColor="#fff" stopOpacity="0.55" />
                <stop offset="1" stopColor="#fff" stopOpacity="0" />
              </radialGradient>
            </defs>
            <motion.path
              fill="url(#blobG)"
              animate={{
                d: [
                  "M431 60c72 38 130 112 136 200 6 92-52 176-130 224-80 49-186 60-268 14C86 456 30 370 36 280 42 188 104 110 188 68c76-38 166-46 243-8z",
                  "M420 48c78 30 142 118 146 208 4 96-60 186-140 232-84 48-190 52-270 2C78 440 26 356 40 270 54 182 118 98 200 62c72-32 150-40 220-14z",
                  "M431 60c72 38 130 112 136 200 6 92-52 176-130 224-80 49-186 60-268 14C86 456 30 370 36 280 42 188 104 110 188 68c76-38 166-46 243-8z",
                ],
              }}
              transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
            />
            <ellipse cx="220" cy="130" rx="190" ry="110" fill="url(#gloss)" transform="rotate(-18 220 130)" />
          </motion.svg>

          {/* tilted showcase */}
          <motion.div style={{ rotateX: rotX, rotateY: rotY }} className="preserve-3d absolute inset-0">
            {/* mascot */}
            <motion.div style={{ z: 90, x: "-50%", y: "-50%" }} className="absolute left-1/2 top-[46%] w-[56%]">
              <motion.img
                src="/mascot.png"
                alt="Mascote da Tangerine Talk acenando"
                animate={{ y: [0, -14, 0], rotate: [-2, 2, -2] }}
                transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
                className="w-full drop-shadow-[0_24px_30px_rgba(160,40,0,0.35)]"
                draggable={false}
              />
            </motion.div>

            {/* bubbles */}
            <motion.div style={{ z: 140 }} className="absolute left-[2%] top-[10%]">
              <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 4.2, repeat: Infinity, ease: "easeInOut" }}>
                <div className="bubble rounded-[22px] px-5 py-3">
                  <AnimatePresence mode="wait">
                    <motion.p key={L.hello} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.35, ease: EASE }} className="text-[22px] font-bold text-ink">
                      {L.hello}
                    </motion.p>
                  </AnimatePresence>
                </div>
              </motion.div>
            </motion.div>

            <motion.div style={{ z: 120 }} className="absolute right-[0%] top-[32%]">
              <motion.div animate={{ y: [0, 10, 0] }} transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 0.6 }}>
                <div className="bubble tail-right rounded-[22px] px-4 py-3">
                  <AnimatePresence mode="wait">
                    <motion.div key={L.line} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.35, ease: EASE }}>
                      <p className="text-[15px] font-semibold text-ink">{L.line}</p>
                      <p className="text-[11px] text-body">{L.gloss}</p>
                    </motion.div>
                  </AnimatePresence>
                </div>
              </motion.div>
            </motion.div>

            <motion.div style={{ z: 110 }} className="absolute bottom-[22%] left-[0%]">
              <motion.div animate={{ y: [0, -8, 0] }} transition={{ duration: 4.8, repeat: Infinity, ease: "easeInOut", delay: 1.1 }}>
                <div className="bubble flex items-center gap-2 rounded-[20px] px-4 py-2.5">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-tangerine-lightBg text-tangerine-darker"><CheckIcon size={14} /></span>
                  <span className="text-[13px] font-semibold text-ink">98% de precisão</span>
                </div>
              </motion.div>
            </motion.div>

            {/* language selector pill */}
            <motion.div style={{ z: 160, x: "-50%" }} className="absolute bottom-[5%] left-1/2 w-[92%] max-w-[470px]">
              <LayoutGroup>
                <div role="tablist" aria-label="Escolha um idioma" className="flex items-center justify-between gap-1 rounded-pill bg-white p-1.5 shadow-lift">
                  {LANGS.map((l, i) => (
                    <button
                      key={l.name}
                      role="tab"
                      aria-selected={i === lang}
                      onClick={() => setLang(i)}
                      className={`relative flex-1 rounded-pill px-2 py-2 text-[11px] font-semibold transition-colors duration-300 sm:text-[13px] ${i === lang ? "text-white" : "text-ink hover:text-tangerine-darker"}`}
                    >
                      {i === lang && (
                        <motion.span layoutId="langPill" transition={{ type: "spring", stiffness: 420, damping: 30 }} className="absolute inset-0 rounded-pill bg-tangerine-darker shadow-cta" />
                      )}
                      <span className="relative">{l.name}</span>
                    </button>
                  ))}
                </div>
              </LayoutGroup>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
