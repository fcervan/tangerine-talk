"use client";

import { motion } from "framer-motion";
import { EarIcon, MicIcon, PenIcon, TestIcon } from "./icons";
import { EASE } from "@/lib/ease";

const ITEMS = [
  { icon: MicIcon, title: "Fala", text: "Converse com um parceiro de IA e receba feedback de pronúncia na hora." },
  { icon: EarIcon, title: "Escuta", text: "Treine seu ouvido com áudio em velocidade nativa, no seu ritmo." },
  { icon: PenIcon, title: "Escrita", text: "Monte frases peça por peça até a gramática virar automática." },
  { icon: TestIcon, title: "Testes", text: "Flashcards e quizzes inteligentes que retomam o que você esquece." },
];

export default function Features() {
  return (
    <section id="features" className="bg-white pb-24">
      <div className="mx-auto max-w-[1200px] px-5">
        <div className="mb-10 max-w-xl">
          <p className="eyebrow mb-3">Tudo o que você precisa</p>
          <h2 className="h2">Quatro habilidades. <span className="hl">Uma</span> rotina diária.</h2>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {ITEMS.map(({ icon: Icon, title, text }, i) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.8, ease: EASE, delay: i * 0.08 }}
              whileHover={{ y: -4 }}
              className="card p-7"
            >
              <span className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-tangerine-soft text-tangerine"><Icon size={24} /></span>
              <h3 className="mb-2 text-[18px] font-semibold text-ink">{title}</h3>
              <p className="text-[14px] leading-relaxed text-body">{text}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
