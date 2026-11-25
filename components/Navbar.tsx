"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Logo from "./Logo";
import PillButton from "./PillButton";
import { CloseIcon, MenuIcon } from "./icons";
import { scrollToId } from "@/lib/lenis";
import { EASE } from "@/lib/ease";

const LINKS = [
  { label: "Recursos", href: "#features" },
  { label: "Como funciona", href: "#how-it-works" },
  { label: "Gamificação", href: "#gamification" },
  { label: "Idiomas", href: "#languages" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const on = () => setScrolled(window.scrollY > 8);
    on();
    window.addEventListener("scroll", on, { passive: true });
    return () => window.removeEventListener("scroll", on);
  }, []);

  const go = (e: React.MouseEvent, href: string) => {
    e.preventDefault();
    setOpen(false);
    scrollToId(href);
  };

  return (
    <header className={`sticky top-0 z-50 bg-white transition-shadow duration-500 ${scrolled ? "shadow-[0_1px_0_#EDEDED,0_8px_24px_rgba(17,17,17,0.04)]" : ""}`}>
      <div className="mx-auto flex h-[72px] max-w-[1200px] items-center justify-between px-5">
        <a href="#top" onClick={(e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: "smooth" }); }} aria-label="Início da Tangerine Talk">
          <Logo />
        </a>
        <nav className="hidden items-center gap-8 lg:flex">
          {LINKS.map((l) => (
            <a key={l.href} href={l.href} onClick={(e) => go(e, l.href)} className="group relative text-[14px] font-medium text-ink">
              {l.label}
              <span className="absolute -bottom-1 left-0 h-[2px] w-full origin-left scale-x-0 rounded-full bg-tangerine transition-transform duration-500 ease-brand group-hover:scale-x-100" />
            </a>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <PillButton size="sm" href="/login" variant="inverted" className="hidden sm:inline-flex">Entrar</PillButton>
          <PillButton size="sm" href="/cadastro" className="hidden sm:inline-flex">Começar grátis</PillButton>
          <button onClick={() => setOpen((o) => !o)} className="flex h-10 w-10 items-center justify-center rounded-full bg-tangerine-soft text-tangerine lg:hidden" aria-label="Menu">
            {open ? <CloseIcon /> : <MenuIcon />}
          </button>
        </div>
      </div>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.45, ease: EASE }} className="overflow-hidden border-t border-line bg-white lg:hidden">
            <div className="flex flex-col gap-1 px-5 py-4">
              {LINKS.map((l) => (
                <a key={l.href} href={l.href} onClick={(e) => go(e, l.href)} className="rounded-xl px-3 py-3 text-[15px] font-medium text-ink hover:bg-tangerine-soft">{l.label}</a>
              ))}
              <a href="/login" className="mt-2 self-start rounded-xl px-3 py-3 text-[15px] font-medium text-ink hover:bg-tangerine-soft">Entrar</a>
              <PillButton size="sm" href="/cadastro" className="mt-2 self-start">Começar grátis</PillButton>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
