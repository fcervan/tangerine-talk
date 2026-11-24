"use client";

import { useRef, useState, type ReactNode } from "react";
import { motion, useInView } from "framer-motion";
import { burstFrom } from "@/lib/confetti";
import { EASE } from "@/lib/ease";
import { BoltIcon, ChatIcon, CheckIcon, FlameIcon, LockIcon, StarIcon, TreeIcon, TrophyIcon } from "./icons";

function Card({ className = "", children, delay = 0 }: { className?: string; children: ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 32 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.9, ease: EASE, delay }}
      className={className}
    >
      <motion.div whileHover={{ y: -4 }} transition={{ duration: 0.4, ease: EASE }} className="card h-full p-7 transition-shadow duration-500 hover:shadow-lift">
        {children}
      </motion.div>
    </motion.div>
  );
}

function Ring({ value, size = 120, stroke = 10, children }: { value: number; size?: number; stroke?: number; children?: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });
  const r = (size - stroke) / 2;
  return (
    <div ref={ref} className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <defs>
          <linearGradient id={`rg${size}${value}`} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#FF7A33" /><stop offset="1" stopColor="#E64A00" />
          </linearGradient>
        </defs>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#FFE9DC" strokeWidth={stroke} />
        <motion.circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={`url(#rg${size}${value})`} strokeWidth={stroke} strokeLinecap="round" initial={{ pathLength: 0 }} animate={{ pathLength: inView ? value / 100 : 0 }} transition={{ duration: 1.6, ease: EASE, delay: 0.2 }} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">{children}</div>
    </div>
  );
}

function Badge({ label, icon: Icon, unlocked = true }: { label: string; icon: typeof StarIcon; unlocked?: boolean }) {
  return (
    <motion.button
      whileHover={{ y: -4, scale: 1.04 }}
      whileTap={{ scale: 0.9 }}
      transition={{ type: "spring", stiffness: 400, damping: 18 }}
      onClick={(e) => burstFrom(e.currentTarget)}
      className={`flex flex-col items-center gap-1.5 rounded-2xl px-3 py-3 text-[11px] font-semibold ${unlocked ? "bg-tangerine-soft text-ink" : "bg-mist text-body"}`}
    >
      <span className={`flex h-10 w-10 items-center justify-center rounded-full ${unlocked ? "bg-tangerine text-white" : "bg-white text-body"}`}><Icon size={20} /></span>
      {label}
    </motion.button>
  );
}

/* ---------- Streak ---------- */
function Streak() {
  const days = ["S", "T", "Q", "Q", "S", "S", "D"];
  return (
    <Card className="lg:col-span-4 lg:row-span-2" delay={0}>
      <div className="flex h-full flex-col">
        <p className="eyebrow mb-4">Sequência diária</p>
        <div className="flex items-center gap-4">
          <motion.button
            onClick={(e) => burstFrom(e.currentTarget)}
            whileTap={{ scale: 0.88 }}
            animate={{ scale: [1, 1.06, 1] }}
            transition={{ scale: { duration: 2.2, repeat: Infinity, ease: "easeInOut" } }}
            className="flex h-20 w-20 items-center justify-center rounded-[26px] bg-gradient-to-br from-tangerine-light to-tangerine-dark text-white shadow-cta"
            aria-label="Comemorar sequência"
          >
            <FlameIcon size={40} />
          </motion.button>
          <div>
            <p className="text-[56px] font-bold leading-none text-ink">27</p>
            <p className="text-[14px] text-body">dias seguidos</p>
          </div>
        </div>
        <div className="mt-7 flex justify-between">
          {days.map((d, i) => (
            <div key={i} className="flex flex-col items-center gap-2">
              <span className="text-[11px] font-medium text-body">{d}</span>
              <span className={`flex h-9 w-9 items-center justify-center rounded-full ${i < 5 ? "bg-tangerine text-white" : i === 5 ? "bg-tangerine-tint text-tangerine ring-2 ring-tangerine" : "bg-mist text-body/40"}`}>
                {i < 5 ? <CheckIcon size={16} /> : null}
              </span>
            </div>
          ))}
        </div>
        <p className="mt-6 text-[13px] leading-relaxed text-body">Pratique hoje para manter a chama acesa. Maior sequência: <b className="text-ink">41 dias</b>.</p>
        <div className="mt-auto grid grid-cols-3 gap-3 pt-6">
          <Badge label="7 dias" icon={BoltIcon} />
          <Badge label="30 dias" icon={FlameIcon} />
          <Badge label="100 dias" icon={StarIcon} unlocked={false} />
        </div>
      </div>
    </Card>
  );
}

/* ---------- Leaderboard ---------- */
const BOARD = [
  { n: "Marta S.", xp: 2840 },
  { n: "Você", xp: 2615, me: true },
  { n: "Kenji T.", xp: 2390 },
  { n: "Lucía R.", xp: 1980 },
];
function Leaderboard() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });
  return (
    <Card className="lg:col-span-8" delay={0.08}>
      <div ref={ref}>
        <div className="mb-5 flex items-center justify-between">
          <div>
            <p className="eyebrow mb-1">Ranking de XP</p>
            <h3 className="text-[20px] font-semibold text-ink">Liga Laranja · esta semana</h3>
          </div>
          <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-tangerine-soft text-tangerine"><TrophyIcon size={22} /></span>
        </div>
        <div className="flex flex-col gap-2.5">
          {BOARD.map((p, i) => (
            <div key={p.n} className={`flex items-center gap-4 rounded-2xl px-4 py-3 ${p.me ? "bg-tangerine-soft" : ""}`}>
              <span className="w-5 text-[14px] font-bold text-body">{i + 1}</span>
              <span className={`flex h-9 w-9 items-center justify-center rounded-full text-[13px] font-bold ${p.me ? "bg-tangerine text-white" : "bg-mist text-ink"}`}>{p.n[0]}</span>
              <span className="w-20 text-[14px] font-semibold text-ink">{p.n}</span>
              <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-mist">
                <motion.div initial={{ width: 0 }} animate={{ width: inView ? `${(p.xp / BOARD[0].xp) * 100}%` : 0 }} transition={{ duration: 1.3, ease: EASE, delay: 0.15 + i * 0.1 }} className="h-full rounded-full bg-gradient-to-r from-tangerine-light to-tangerine-dark" />
              </div>
              <span className="w-16 text-right text-[13px] font-semibold text-ink">{p.xp.toLocaleString("pt-BR")}</span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

/* ---------- Milestones ---------- */
function Milestones() {
  return (
    <Card className="lg:col-span-4" delay={0.12}>
      <p className="eyebrow mb-1">Conversas com IA</p>
      <h3 className="mb-5 text-[18px] font-semibold text-ink">Próxima meta: 50</h3>
      <div className="flex items-center gap-5">
        <Ring value={72} size={112}>
          <span className="text-[24px] font-bold leading-none text-ink">36</span>
          <span className="text-[11px] text-body">de 50</span>
        </Ring>
        <div className="flex flex-col gap-2">
          <button onClick={(e) => burstFrom(e.currentTarget)} className="flex items-center gap-2 rounded-pill bg-tangerine-soft px-3 py-1.5 text-[12px] font-semibold text-ink transition-transform duration-300 hover:-translate-y-1"><ChatIcon size={16} className="text-tangerine" />Primeira conversa</button>
          <button onClick={(e) => burstFrom(e.currentTarget)} className="flex items-center gap-2 rounded-pill bg-tangerine-soft px-3 py-1.5 text-[12px] font-semibold text-ink transition-transform duration-300 hover:-translate-y-1"><ChatIcon size={16} className="text-tangerine" />25 conversas</button>
          <span className="flex items-center gap-2 rounded-pill bg-mist px-3 py-1.5 text-[12px] font-semibold text-body"><LockIcon size={16} />50 conversas</span>
        </div>
      </div>
    </Card>
  );
}

/* ---------- Skill tree ---------- */
const NODES = [
  { id: 0, l: "Básico", x: 150, y: 26, p: -1 },
  { id: 1, l: "Saudações", x: 70, y: 86, p: 0 },
  { id: 2, l: "Comida", x: 230, y: 86, p: 0 },
  { id: 3, l: "Viagem", x: 30, y: 146, p: 1 },
  { id: 4, l: "Números", x: 110, y: 146, p: 1 },
  { id: 5, l: "Refeições", x: 190, y: 146, p: 2 },
  { id: 6, l: "Negócios", x: 270, y: 146, p: 2 },
];
function SkillTree() {
  const [open, setOpen] = useState<number[]>([0, 1, 2, 3]);
  const unlock = (id: number, p: number, e: React.MouseEvent) => {
    if (open.includes(id) || !open.includes(p)) return;
    setOpen((o) => [...o, id]);
    burstFrom(e.currentTarget);
  };
  return (
    <Card className="lg:col-span-4" delay={0.16}>
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p className="eyebrow mb-1">Árvore de habilidades</p>
          <h3 className="text-[18px] font-semibold text-ink">{open.length}/7 desbloqueadas</h3>
        </div>
        <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-tangerine-soft text-tangerine"><TreeIcon size={20} /></span>
      </div>
      <svg viewBox="0 0 300 180" className="w-full overflow-visible">
        {NODES.filter((n) => n.p >= 0).map((n) => {
          const p = NODES[n.p];
          const on = open.includes(n.id);
          return <motion.line key={n.id} x1={p.x} y1={p.y} x2={n.x} y2={n.y} strokeWidth={2.5} strokeLinecap="round" animate={{ stroke: on ? "#FF5A0A" : "#EDEDED" }} transition={{ duration: 0.5 }} />;
        })}
        {NODES.map((n) => {
          const on = open.includes(n.id);
          const ready = !on && open.includes(n.p);
          return (
            <g key={n.id} onClick={(e) => unlock(n.id, n.p, e as unknown as React.MouseEvent)} className={ready ? "cursor-pointer" : ""} role="button" aria-label={n.l}>
              {ready && <motion.circle cx={n.x} cy={n.y} r={15} fill="none" stroke="#FF7A33" strokeWidth={1.5} animate={{ r: [15, 21], opacity: [0.8, 0] }} transition={{ duration: 1.6, repeat: Infinity }} />}
              <motion.circle cx={n.x} cy={n.y} r={15} animate={{ fill: on ? "#FF5A0A" : "#F7F7F8", scale: on ? 1 : 0.92 }} style={{ transformOrigin: `${n.x}px ${n.y}px`, transformBox: "fill-box" }} whileHover={ready ? { scale: 1.15 } : {}} transition={{ type: "spring", stiffness: 420, damping: 16 }} stroke={on ? "#E64A00" : "#EDEDED"} strokeWidth={1.5} />
              {on ? <path d={`M${n.x - 5} ${n.y} l3.5 3.5 l6.5 -7`} fill="none" stroke="#fff" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" /> : <circle cx={n.x} cy={n.y} r={3} fill="#5C5C5C" opacity={0.35} />}
              <text x={n.x} y={n.y + 30} textAnchor="middle" fontSize={10.5} fontWeight={600} fill={on ? "#111" : "#5C5C5C"}>{n.l}</text>
            </g>
          );
        })}
      </svg>
    </Card>
  );
}

export default function Bento() {
  return (
    <section id="gamification" className="bg-white py-24">
      <div className="mx-auto max-w-[1200px] px-5">
        <div className="mb-12 max-w-2xl">
          <p className="eyebrow mb-3">Gamificação</p>
          <h2 className="h2">Faça da fluência um <span className="hl">hábito</span> que você realmente ama.</h2>
          <p className="mt-4 text-[16px] leading-relaxed text-body">Sequências, ligas e habilidades desbloqueáveis transformam a prática diária em um jogo que dá vontade de continuar vencendo. Vá em frente — toque em um selo.</p>
        </div>
        <div className="grid gap-6 lg:grid-cols-12">
          <Streak />
          <Leaderboard />
          <Milestones />
          <SkillTree />
        </div>
      </div>
    </section>
  );
}
