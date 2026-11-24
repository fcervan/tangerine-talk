"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import PillButton from "./PillButton";
import { gsap } from "@/lib/gsap";
import { EASE } from "@/lib/ease";

const STATS = [
  { to: 50, suffix: "+", label: "Idiomas", d: 0 },
  { to: 1, suffix: " mi+", label: "Aulas faladas", d: 0 },
  { to: 98, suffix: "%", label: "Precisão de pronúncia", d: 0 },
  { to: 4.9, suffix: "★", label: "Avaliação do app", d: 1 },
];

function CountUp({ to, suffix, d }: { to: number; suffix: string; d: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const o = { v: 0 };
    const ctx = gsap.context(() => {
      gsap.to(o, {
        v: to,
        duration: 2.2,
        ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 92%", once: true },
        onUpdate: () => { el.textContent = o.v.toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d }) + suffix; },
      });
    });
    return () => ctx.revert();
  }, [to, suffix, d]);
  return <span ref={ref}>{(0).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d }) + suffix}</span>;
}

function Illustration() {
  return (
    <svg viewBox="0 0 420 340" className="h-full w-full" aria-hidden>
      <circle cx="220" cy="180" r="140" fill="#fff" opacity="0.14" />
      <circle cx="220" cy="180" r="96" fill="#fff" opacity="0.14" />
      {/* phone */}
      <rect x="150" y="38" width="150" height="270" rx="28" fill="#111" />
      <rect x="160" y="50" width="130" height="246" rx="20" fill="#fff" />
      <rect x="196" y="56" width="58" height="9" rx="4.5" fill="#111" />
      <circle cx="225" cy="122" r="30" fill="#FF5A0A" />
      <path d="M212 120a3 3 0 1 0 0.1 0M238 120a3 3 0 1 0 0.1 0" fill="#111" />
      <path d="M214 132q11 11 22 0" stroke="#111" strokeWidth="3" fill="none" strokeLinecap="round" />
      <path d="M232 94c6-12 18-14 24-12-2 10-12 16-24 12z" fill="#111" />
      {[0, 1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
        <rect key={i} x={180 + i * 11} y={196 - [10, 22, 34, 18, 40, 26, 14, 30, 8][i] / 2} width="6" height={[10, 22, 34, 18, 40, 26, 14, 30, 8][i]} rx="3" fill={i % 2 ? "#FF5A0A" : "#111"} />
      ))}
      <rect x="178" y="248" width="94" height="30" rx="15" fill="#FF5A0A" />
      <rect x="190" y="260" width="40" height="6" rx="3" fill="#fff" />
      {/* bubbles */}
      <g>
        <rect x="30" y="64" width="124" height="58" rx="22" fill="#fff" stroke="#111" strokeWidth="4" />
        <path d="M120 122l14 20 6-22z" fill="#fff" stroke="#111" strokeWidth="4" strokeLinejoin="round" />
        <rect x="48" y="84" width="60" height="7" rx="3.5" fill="#FF5A0A" />
        <rect x="48" y="100" width="88" height="7" rx="3.5" fill="#111" />
      </g>
      <g>
        <rect x="290" y="168" width="112" height="56" rx="22" fill="#111" />
        <path d="M312 224l-8 22 24-18z" fill="#111" strokeLinejoin="round" />
        <rect x="308" y="186" width="56" height="7" rx="3.5" fill="#fff" />
        <rect x="308" y="202" width="36" height="7" rx="3.5" fill="#FF7A33" />
      </g>
      {/* sparks */}
      <g stroke="#fff" strokeWidth="4" strokeLinecap="round">
        <path d="M330 60v22M319 71h22" />
        <path d="M62 220v14M55 227h14" />
      </g>
      <circle cx="372" cy="110" r="8" fill="#111" />
      <circle cx="92" cy="170" r="6" fill="#fff" />
    </svg>
  );
}

export default function CtaStats() {
  return (
    <section id="pricing" className="bg-white px-4 pb-24 pt-8 sm:px-6">
      <motion.div
        initial={{ opacity: 0, y: 40, scale: 0.98 }}
        whileInView={{ opacity: 1, y: 0, scale: 1 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 1, ease: EASE }}
        className="relative mx-auto max-w-[1320px] overflow-hidden rounded-[32px] bg-gradient-to-br from-tangerine-light via-tangerine to-tangerine-dark px-8 pb-28 pt-14 sm:px-14 lg:pb-32"
      >
        <div className="dot-grid absolute inset-0 opacity-[0.18] [mask-image:radial-gradient(circle_at_85%_20%,#000,transparent_60%)]" style={{ backgroundImage: "radial-gradient(#fff 1.6px, transparent 1.7px)" }} />
        <div className="relative grid items-center gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <p className="mb-4 text-[12px] font-semibold uppercase tracking-[0.12em] text-white/80">Plano gratuito para sempre · Faça upgrade quando quiser</p>
            <h2 className="text-[38px] font-bold leading-[1.08] tracking-tight text-ink sm:text-[54px]">
              Comece sua <span className="text-white">jornada rumo à fluência</span> hoje.
            </h2>
            <p className="mt-5 max-w-md text-[16px] leading-relaxed text-white/90">Junte-se a milhões de pessoas praticando alguns minutos por dia com um tutor de IA que nunca se cansa das suas perguntas.</p>
            <div className="mt-8"><PillButton variant="inverted" magnetic href="#top">Começar a aprender</PillButton></div>
          </div>
          <div className="mx-auto h-[300px] w-full max-w-[420px] lg:h-[340px]">
            <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }} className="h-full w-full"><Illustration /></motion.div>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-40px" }}
        transition={{ duration: 0.9, ease: EASE, delay: 0.1 }}
        className="card relative z-10 mx-auto -mt-16 grid max-w-[1000px] grid-cols-2 rounded-[28px] lg:grid-cols-4"
      >
        {STATS.map((s, i) => (
          <div key={s.label} className={`px-6 py-8 text-center ${i % 2 === 1 ? "border-l border-line" : ""} ${i > 1 ? "border-t border-line lg:border-t-0" : ""} ${i > 0 ? "lg:border-l lg:border-line" : ""}`}>
            <p className="text-[38px] font-bold leading-none text-tangerine"><CountUp {...s} /></p>
            <p className="mt-2 text-[13px] font-medium text-body">{s.label}</p>
          </div>
        ))}
      </motion.div>
    </section>
  );
}
