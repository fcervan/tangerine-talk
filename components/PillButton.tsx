"use client";

import { motion, useMotionValue, useSpring } from "framer-motion";
import { useRef, type ReactNode } from "react";
import { ArrowIcon } from "./icons";
import { scrollToId } from "@/lib/lenis";

type Props = {
  children: ReactNode;
  href?: string;
  variant?: "primary" | "inverted";
  size?: "sm" | "md";
  magnetic?: boolean;
  className?: string;
};

export default function PillButton({ children, href = "#", variant = "primary", size = "md", magnetic = false, className = "" }: Props) {
  const ref = useRef<HTMLAnchorElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const ix = useMotionValue(0);
  const iy = useMotionValue(0);
  const cfg = { stiffness: 220, damping: 14, mass: 0.5 };
  const sx = useSpring(x, cfg), sy = useSpring(y, cfg);
  const six = useSpring(ix, cfg), siy = useSpring(iy, cfg);

  const onMove = (e: React.MouseEvent) => {
    if (!magnetic || !ref.current) return;
    const r = ref.current.getBoundingClientRect();
    const dx = e.clientX - (r.left + r.width / 2);
    const dy = e.clientY - (r.top + r.height / 2);
    x.set(dx * 0.28); y.set(dy * 0.35);
    ix.set(dx * 0.12); iy.set(dy * 0.12);
  };
  const onLeave = () => { x.set(0); y.set(0); ix.set(0); iy.set(0); };

  const primary = variant === "primary";
  const md = size === "md";

  return (
    <motion.a
      ref={ref}
      href={href}
      onClick={(e) => {
        if (href.startsWith("#") && href.length > 1) { e.preventDefault(); scrollToId(href); }
      }}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      style={{ x: sx, y: sy }}
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.96 }}
      transition={{ type: "spring", stiffness: 300, damping: 18 }}
      className={`inline-flex items-center rounded-pill font-semibold ${
        md ? "gap-4 py-2 pl-7 pr-2 text-[16px]" : "gap-2 py-1.5 pl-4 pr-1.5 text-[14px]"
      } ${primary ? "bg-tangerine text-white shadow-cta hover:bg-tangerine-dark" : "bg-white text-tangerine shadow-lift hover:text-tangerine-dark"} ${className}`}
    >
      {children}
      <motion.span
        style={{ x: six, y: siy }}
        className={`flex items-center justify-center rounded-full ${md ? "h-10 w-10" : "h-7 w-7"} ${
          primary ? "bg-white text-tangerine" : "bg-tangerine text-white"
        }`}
      >
        <ArrowIcon size={md ? 20 : 15} className="" />
      </motion.span>
    </motion.a>
  );
}
