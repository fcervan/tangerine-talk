# Tangerine Talk

Landing page do **Tangerine Talk**, um tutor de idiomas com IA. Site estático (Next.js App Router, SSG) com toda a copy em **pt-BR**.

## Stack

Next.js 14 · React 18 · TypeScript · Tailwind CSS v3 · Framer Motion · GSAP/ScrollTrigger · Lenis

## Rodando

```bash
npm install
npm run dev     # http://localhost:3000
```

Tipos:

```bash
npx tsc --noEmit
```

> ⚠️ **Não rode `npm run build` com o `npm run dev` ativo.** Os dois compartilham `.next` e o build apaga o CSS do dev (o site carrega sem estilo). Se acontecer: pare o dev, `rm -rf .next`, `npm run dev`, `Ctrl+Shift+R`.

## Estrutura

```
app/          layout, page, globals.css
components/   Navbar, Hero, Features, Scrolly, Bento, Languages, CtaStats, Footer, mockups
lib/          lenis, gsap, ease, confetti
docs/         prompt de efeitos (laboratório /lab)
public/       mascote
```

## Próxima fase

Construir a aplicação além da landing (auth, lições, tutor de IA, gamificação, SRS). Contexto completo, convenções e roadmap em [`AGENTS.md`](./AGENTS.md).
