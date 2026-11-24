# PROMPT INICIAL — Landing Page + Laboratório de Efeitos

> **Para você (humano):** não é obrigatório colar esta nota. Ela explica como usar o documento.
> 1. Marque no **Anexo A** quais efeitos entram no laboratório e quais aparecem na home curada.
> 2. Cole o documento inteiro no LLM (ou o trecho a partir da seção 1).
> 3. Se quiser um efeito específico no futuro, copie só o bloco dele (seção 5) e a "frase pronta".
> 4. O documento funciona tanto como **prompt** quanto como **catálogo de consulta**.

---

## 1. Papel

Você é um **engenheiro front-end sênior especializado em motion design**, com domínio de Next.js (App Router), React, TypeScript, Tailwind CSS, Framer Motion, GSAP/ScrollTrigger e Lenis. Você também tem olhar de diretor de arte: sabe quando um efeito eleva a experiência e quando ele só atrapalha.

Sua tarefa é construir um **site de referência com três camadas**:

1. **Home curada (`/`)** — landing page de produto com hero, benefícios, prova social, CTA e footer, usando **um subconjunto pequeno** de efeitos.
2. **Índice de efeitos (`/lab`)** — catálogo navegável em bento grid, com filtros por categoria e **badge de custo** (leve / médio / pesado) em cada efeito.
3. **Uma página por efeito (`/lab/[slug]`)** — demo **isolada**, ficha técnica (o que é, quando usar, cuidados), dependências e o **prompt copiável** para pedir aquele efeito a qualquer LLM.

**Por que não uma página única?** Colocar tudo numa só rota acumula loops de animação, seções pinadas, camadas de `blur`/`backdrop-filter` e, principalmente, contextos WebGL. O custo do 3D (R3F/Spline) não é de alguns kilobytes: são centenas de kB a vários MB, mais memória de GPU. Em uma página única, tudo isso roda ao mesmo tempo e derruba o desempenho em celulares medianos. **Separar em rotas isola o custo**: Three/Spline só carregam na própria página, cada demo tem um único loop, e você consegue medir o peso real de cada efeito — que é exatamente o que você precisa para decidir o que pedir.

O objetivo de longo prazo é que o site sirva de **menu de referência**: ao abrir uma página de efeito, o usuário entende o que é, vê funcionando, conhece o custo e copia o prompt para reutilizar em qualquer projeto.

---

## 2. Stack obrigatória

Use exatamente esta base (fixe as versões para evitar breaking changes):

| Camada | Tecnologia | Versão |
|---|---|---|
| Framework | Next.js (App Router) | `14.2.15` |
| UI | React / React DOM | `18.3.1` |
| Linguagem | TypeScript (strict) | `5.9.x` |
| Estilo | Tailwind CSS (v3, `tailwind.config.ts`) | `3.4.x` |
| Animação de UI | Framer Motion | `11.18.x` |
| Animação de scroll | GSAP + ScrollTrigger | `3.15.x` |
| Scroll suave | Lenis | `1.3.x` |
| Build | PostCSS + Autoprefixer | `8.5.x` / `10.6.x` |

Regras:

- **Next.js App Router** (`app/layout.tsx`, `app/page.tsx`). Nada de Pages Router.
- Só marque `"use client"` nos componentes que realmente usam hooks, eventos ou animação.
- **Não** adicione bibliotecas além das listadas sem justificar (exceção: Three.js/R3F/Spline **apenas** se o efeito 3D real for selecionado no Anexo A).
- Não use bibliotecas de componentes prontas (shadcn, MUI etc.). O visual é autoral.
- TypeScript em modo `strict`; sem `any` injustificado.
- Tailwind v3: tokens no `theme.extend`, sem CSS-in-JS.
- **Cada efeito selecionado vira uma rota estática** em `/lab/[slug]`, gerada com `generateStaticParams` (SSG, sem servidor).
- Dependências pesadas (`three`, `@react-three/fiber`, `@react-three/drei`, `@splinetool/react-spline`) só podem ser importadas **dentro do componente de demo correspondente**, via `next/dynamic` com `ssr: false`. Elas nunca podem entrar no bundle da home nem do índice.

---

## 3. Regras de engenharia (não negociáveis)

1. **Anime apenas `transform` e `opacity`.** Nunca `width`, `height`, `top`, `left` em loops. Exceções pontuais (barra de progresso, acordeão) são aceitáveis se forem curtas.
2. **60fps é o alvo.** Use `will-change` com parcimônia e remova depois. Evite `filter: blur()` animado em áreas grandes; prefira `transform: scale()` em elementos já desfocados.
3. **`prefers-reduced-motion` é obrigatório.** Ofereça uma versão estática/instantânea:
   - CSS: `@media (prefers-reduced-motion: reduce) { ... }`
   - Framer: `useReducedMotion()`
   - GSAP: `gsap.matchMedia()` com a condição `(prefers-reduced-motion: reduce)`.
4. **Acessibilidade**: HTML semântico, `alt` descritivo, `aria-label` em ícones-botão, foco visível (`focus-visible`), contraste mínimo AA, navegação por teclado em todos os controles. Elementos decorativos levam `aria-hidden`.
5. **Responsivo**: valide em `390px`, `768px`, `1024px` e `1440px`. Nada de overflow horizontal. `scrollWidth === clientWidth` em todos.
6. **Sem erros de console** e **sem warnings de hidratação**. Nada de `Math.random()` ou `Date.now()` no render de componentes server.
7. **Cleanup sempre**: `useEffect`/`useLayoutEffect` devem remover listeners, cancelar `requestAnimationFrame`, matar `ScrollTrigger` e reverter `gsap.context`.
8. **Sem layout shift**: reserve espaço para imagens/vídeos (`width`/`height` ou `aspect-ratio`).
9. **Conteúdo em pt-BR**, tom direto e caloroso, sem clichês de marketing.
10. **Zero placeholders**: nada de "lorem ipsum", "TODO" ou botões sem destino.
11. **Uma demo por página**: `/lab/[slug]` monta **apenas** o componente do efeito daquela rota. O índice nunca monta demos.
12. **Um canvas WebGL por página**, no máximo. Pause o render quando estiver fora da viewport ou com a aba oculta (`frameloop="demand"` + IntersectionObserver).
13. **Orçamento de JavaScript por rota**: home ≤ 220 kB de First Load JS; índice `/lab` ≤ 200 kB; demos leves ≤ 200 kB. Demos 3D podem passar, mas o tamanho precisa ser **declarado no relatório** e o carregamento precisa ser lazy com fallback estático.

---

## 4. Arquitetura e convenções

```
app/
  layout.tsx                # metadata, fontes, LenisProvider, Grain
  page.tsx                  # home curada (subset de efeitos)
  globals.css               # tokens, keyframes, utilitários
  lab/
    page.tsx                # índice de efeitos (server) + filtros (client)
    [slug]/
      page.tsx              # ficha do efeito + demo isolada (server)
components/
  layout/Navbar.tsx
  layout/Footer.tsx
  home/                     # seções da home: Hero, Bento, Scrolly, Marquee, CtaStats
  lab/EffectsGrid.tsx       # grid + filtros (client, sem demos)
  lab/EffectCard.tsx        # card do índice com badge de custo
  lab/DemoFrame.tsx         # moldura do demo: área fixa + remount por slug (client)
  lab/CopyPrompt.tsx        # botão "copiar prompt" (client)
  demos/                    # 1 componente autocontido por efeito
    LenisDemo.tsx
    ScrollytellingDemo.tsx
    KineticTypeDemo.tsx
    TiltDemo.tsx
    BentoDemo.tsx
    GlassDemo.tsx
    AuroraDemo.tsx
    GrainDemo.tsx
    SpotlightDemo.tsx
    MagneticDemo.tsx
    ...
  ui/PillButton.tsx         # botão magnético (só transform/opacity)
  ui/Reveal.tsx             # wrapper de entrada por scroll
  ui/Tilt3D.tsx
lib/
  effects.ts                # REGISTRO: fonte única da verdade
  lenis.ts                  # singleton + scrollToId
  gsap.ts                   # registro do plugin
  ease.ts                   # curvas compartilhadas
```

Convenções:

- **`lib/effects.ts` é a fonte única da verdade.** Cada item tem `slug`, `code` (ex.: `A5`), `name`, `category`, `cost` (`leve` | `medio` | `pesado`), `deps`, `summary`, `prompt` e `onHome` (opcional). O registro alimenta o índice, os badges, os filtros, o `generateStaticParams`, o `generateMetadata` e o botão "copiar prompt". O `slug` é também a chave do componente em `components/demos/index.tsx`.
- Listas de conteúdo (features, passos, cards) ficam em arrays no topo do arquivo, nunca hardcoded no JSX.
- Um componente de demo por efeito, autocontido e com nome que diga o que ele faz.
- `scrollToId(href)` centralizado em `lib/lenis.ts`.
- Curvas de easing compartilhadas em `lib/ease.ts` (ex.: `cubic-bezier(0.22, 1, 0.36, 1)`).
- Provider de Lenis no `app/layout.tsx` (client) envolvendo tudo — o scroll suave vale para o site inteiro.
- O índice importa **apenas** o registro e os cards; nenhum componente de `components/demos` pode ser importado por `/` ou `/lab`.
- `/lab/[slug]` resolve o efeito pelo registro; slug inexistente chama `notFound()`.

---

## 5. Catálogo de efeitos — o menu

Implemente **somente** o que estiver marcado no Anexo A. Cada efeito marcado vira **uma página própria** em `/lab/[slug]`; o subconjunto marcado como "home curada" também aparece em `/`. Para cada efeito escolhido, siga a receita correspondente. A numeração serve para você citar no código, nas rotas e no relatório final.

### A. Movimento e scroll

#### A1. Smooth Scroll / Lenis
**O que é:** rolagem com inércia e interpolação, dando a sensação "pesada e fluida" de sites premiados.
**Quando usar:** quase sempre em landing pages com animação de scroll; é a base para tudo correr bem.
**Como implementar:**
- `new Lenis({ duration: 1.15, easing: t => 1 - Math.pow(1 - t, 4), smoothWheel: true })`.
- Loop com `requestAnimationFrame`; destruir no unmount.
- CSS: `html.lenis, html.lenis body { height: auto }` e `.lenis.lenis-smooth { scroll-behavior: auto !important }`.
- Integração com GSAP: `lenis.on("scroll", ScrollTrigger.update)` + `gsap.ticker.add(t => lenis.raf(t * 1000))` + `gsap.ticker.lagSmoothing(0)`.
- Expõe um singleton (`getLenis()`) para que botões façam `lenis.scrollTo(y, { duration: 1.3 })`.
**Cuidados:** no mobile, considere desligar (scroll nativo é melhor); sempre desligar com `prefers-reduced-motion`.
**Frase pronta:** "Use Lenis para smooth scroll com inércia, integrado ao GSAP ScrollTrigger."

#### A2. Scrollytelling
**O que é:** narrativa sequencial guiada pela rolagem; a cada trecho, o conteúdo (texto, mockup, cor) muda.
**Quando usar:** explicar um produto em etapas (passo 1, 2, 3…) ou contar uma história.
**Como implementar:**
- Seção alta com um contêiner interno `position: sticky` (ou `pin` do ScrollTrigger).
- `ScrollTrigger.create({ trigger, start: "top top", end: "+=320%", pin: true, anticipatePin: 1, onUpdate: self => setActive(Math.min(n-1, Math.floor(self.progress * n))) })`.
- Renderize o passo ativo com `AnimatePresence` + `motion.div` (`opacity`, `y`, `scale`).
- Barra lateral de progresso: `scaleY(progress)` com `transform-origin: top`.
- Cada passo da lista é clicável e faz `scrollTo` para o ponto correspondente do pin.
**Cuidados:** `pin` cria um "pin-spacer"; calcule com `ScrollTrigger.refresh()` após fontes/imagens. Evite pin em telas pequenas — troque por lista estática.
**Frase pronta:** "Faça uma seção de scrollytelling com seção pinada via GSAP ScrollTrigger e troca de conteúdo por passo."

#### A3. Scroll-driven / Scroll-triggered
**O que é:** dois padrões diferentes que costumam ser confundidos:
- **Scroll-driven (scrub):** a animação é proporcional à rolagem; o usuário controla ida e volta.
- **Scroll-triggered:** a animação dispara uma vez quando o elemento entra na viewport.
**Quando usar:** scrub para parallax, desenhos de linha, barras; triggered para revelar cards e títulos.
**Como implementar:**
- Com Framer: `useScroll({ target, offset })` + `useTransform(scrollYProgress, [0, 1], [...])` para scrub; `whileInView` + `viewport={{ once: true, margin: "-60px" }}` para triggered.
- Com GSAP: `scrollTrigger: { trigger: el, start: "top 85%", scrub: 1 }` ou `{ once: true }` para disparo único.
- Count-up de números: `gsap.to(obj, { v: valor, scrollTrigger: { trigger, start: "top 92%", once: true }, onUpdate })`.
**Cuidados:** não misture Framer `useScroll` e GSAP no mesmo elemento; escolha um dono por elemento.
**Frase pronta:** "Implemente scroll-driven animations com scrub para o parallax e scroll-triggered com `once` para revelar conteúdo."

#### A4. Sticky Positioning / Pinned Sections
**O que é:** a seção "trava" na tela enquanto o conteúdo interno avança.
**Quando usar:** comparações, features em etapas, imagens que trocam.
**Como implementar:**
- CSS puro: `position: sticky; top: 0; height: 100vh` dentro de um wrapper alto.
- GSAP: `pin: true` (mais controle, cria espaçador automático).
- Para trocar conteúdo, combine com `A2`.
**Cuidados:** `sticky` não funciona se algum ancestral tiver `overflow: hidden`; `100vh` no mobile tem barra dinâmica — use `100svh`/`100dvh`.
**Frase pronta:** "Crie uma seção sticky que prende na viewport enquanto o conteúdo interno avança."

#### A5. Kinetic Typography
**O que é:** tipografia em movimento — palavras que sobem por trás de máscaras, letras que esticam, texto que reage ao mouse.
**Quando usar:** hero e títulos de seção; ótimo para primeira impressão.
**Como implementar:**
- Quebre o título em palavras (e letras se necessário). Cada palavra em `span` com `overflow: hidden` e `display: inline-block`; o filho anima `y: "110%" → 0` com stagger (`delay: 0.1 + i * 0.09`).
- Destaque uma palavra com cor de acento.
- Reação ao mouse: `useMotionValue` + `useSpring` + `useTransform` aplicando `rotateX/rotateY` ou deslocamento.
- Alternativa premium: GSAP SplitText (plugin pago) — não use se não estiver disponível; o split manual resolve.
**Cuidados:** `overflow: hidden` corta descendentes (g, p, q). Dê `padding-bottom` / `leading` generoso. Evite palavras muito longas em telas pequenas — quebre a headline.
**Frase pronta:** "Crie kinetic typography no hero: palavras reveladas por máscara com stagger e leve reação ao mouse."

### B. 3D e gráficos avançados

#### B1. WebGL / Three.js / React Three Fiber
**O que é:** 3D real renderizado no navegador (malhas, luzes, materiais).
**Quando usar:** quando o 3D é o produto ou o diferencial visual. Custa bundle e bateria.
**Como implementar:**
- `@react-three/fiber` + `@react-three/drei`; carregue com `next/dynamic` e `ssr: false`.
- `<Canvas dpr={[1, 1.75]} frameloop="demand">` para economizar GPU.
- Pausar quando fora da viewport (IntersectionObserver) e quando a aba está oculta.
**Cuidados:** sempre ofereça fallback estático (imagem/vídeo) e nunca bloqueie o LCP. Não use em mobile antigo sem teste.
**Frase pronta:** "Adicione uma cena 3D com React Three Fiber, carregada sob demanda, com fallback estático."

#### B2. Spline 3D
**O que é:** cena 3D interativa montada em editor visual e embutida na página.
**Quando usar:** quando você quer 3D sem programar shaders/malhas.
**Como implementar:** `@splinetool/react-spline` + `@splinetool/runtime`; `dynamic(() => import("@splinetool/react-spline"), { ssr:false })`; `scene` como URL do projeto.
**Cuidados:** pese o carregamento (é um bundle grande); use `loading` placeholder com `aspect-ratio` fixo.
**Frase pronta:** "Incorpore uma cena Spline interativa com carregamento lazy e placeholder."

#### B3. Custom Shaders / GLSL
**O que é:** efeitos de distorção, líquido, ondas, vidro e partículas escritos em GLSL.
**Quando usar:** identidade visual muito específica. Sempre com fallback.
**Como implementar:** `shaderMaterial` do drei ou `THREE.ShaderMaterial`; uniforms alimentados por mouse/tempo; ruído simplex para orgânico.
**Cuidados:** complexidade alta, difícil de manter; prefira GIF/vídeo quando o efeito não precisa reagir ao usuário.
**Frase pronta:** "Aplique um shader GLSL de distorção que reage ao cursor, com fallback em CSS."

#### B4. Interactive 3D Mesh / Tilt 3D
**O que é:** camadas que inclinam em perspectiva conforme o mouse (a versão "sem WebGL" do 3D).
**Quando usar:** cards, mockups, hero — 90% do impacto com 1% do custo.
**Como implementar:**
- Contêiner com `perspective: 1200px`.
- Filho com `transform-style: preserve-3d`.
- No `mousemove`, normalize `-1..1` e aplique `rotateX` (invertido) e `rotateY` com `useSpring`.
- Distribua camadas com `translateZ` (ex.: mascote 90px, bolhas 120–160px).
- `onMouseLeave` volta tudo a zero.
**Cuidados:** mova só no `mousemove` do contêiner; não adicione listeners globais. Em touch, desative.
**Frase pronta:** "Faça um tilt 3D em CSS com `perspective` + `preserve-3d` e camadas em `translateZ`, reagindo ao mouse."

### C. Estilos visuais e estéticas

#### C1. Bento Grid
**O que é:** grade modular assimétrica com blocos de tamanhos diferentes (estilo Apple).
**Quando usar:** apresentar 4–8 recursos de forma visual, sem texto demais.
**Como implementar:** CSS Grid de 12 colunas; `lg:col-span-4`, `lg:col-span-8`, `lg:row-span-2`; cada card com hover `translateY(-4px)` e sombra.
**Cuidados:** no mobile vire coluna única; garanta alturas coerentes (`h-full`) e não deixe buracos na grade.
**Frase pronta:** "Organize os recursos em um bento grid assimétrico de 12 colunas, responsivo."

#### C2. Glassmorphism
**O que é:** vidro fosco: transparência + blur de fundo + borda sutil iluminada.
**Quando usar:** sobre fundos coloridos/fotográficos; badges flutuantes sobre mockups.
**Como implementar:** `bg-white/10 backdrop-blur-xl border border-white/20 shadow-[inset_0_1px_0_rgba(255,255,255,0.35)]`.
**Cuidados:** contraste de texto cai — use texto branco com sombra suave ou escureça o fundo. `backdrop-filter` é caro em áreas grandes.
**Frase pronta:** "Aplique glassmorphism com backdrop-blur, transparência e borda interna iluminada."

#### C3. Mesh Gradients / Aurora Backgrounds
**O que é:** gradientes orgânicos e difusos, em movimento lento.
**Quando usar:** fundos de seção, hero, CTA final.
**Como implementar:** 2–4 blobs com `radial-gradient`, `filter: blur(60–120px)` e animação lenta de `transform` (20–40s, `alternate`). Alternativa: blob SVG com `d` animado entre 2–3 caminhos (Framer Motion `animate={{ d: [a, b, a] }}`, 12s).
**Cuidados:** blur grande em tela cheia derruba FPS; use `scale` em elemento já desfocado, `contain: paint` e `pointer-events: none`.
**Frase pronta:** "Crie um fundo aurora com blobs de gradiente desfocados em movimento lento."

#### C4. Noise / Film Grain Overlay
**O que é:** textura de granulado sutil que remove o aspecto "chapado".
**Quando usar:** por cima de gradientes e fotos; intensidade 3–6%.
**Como implementar:** SVG `feTurbulence` inline como `background-image` em data URI, `position: fixed; inset: 0; pointer-events: none; opacity: .04; mix-blend-mode: overlay; z-index: 50`.
**Cuidados:** não use PNG grande; não interfira em cliques; em `prefers-reduced-motion` pode ficar estático (ele já é).
**Frase pronta:** "Adicione um overlay de film grain com SVG feTurbulence em opacity baixa e `pointer-events: none`."

#### C5. Dark Mode com Neon Glow / Spotlight
**O que é:** fundo escuro com brilho que segue o cursor e ilumina bordas dos cards.
**Quando usar:** seções de destaque, pricing, features "premium".
**Como implementar:**
- No `pointermove`, grave `--mx` e `--my` (em px) no elemento.
- Overlay: `background: radial-gradient(400px circle at var(--mx) var(--my), rgba(255,90,10,.18), transparent 70%)`.
- Borda iluminada: `background: radial-gradient(...)` em um pseudo-elemento com `mask` ou use `border-image`.
- Versão com Framer: `useMotionTemplate` + `useMotionValue` para o gradiente.
**Cuidados:** atualize via `requestAnimationFrame`; em touch, use posições fixas ou desative.
**Frase pronta:** "Crie uma seção escura com spotlight que segue o cursor via CSS vars e gradiente radial."

### D. Micro-interações e bibliotecas

#### D1. Magnetic Buttons
**O que é:** o botão "puxa" o cursor quando ele se aproxima.
**Quando usar:** CTA principal, ícones sociais.
**Como implementar:**
- `useMotionValue` + `useSpring` para `x/y`.
- No `mousemove` do botão: `dx = e.clientX - (rect.left + rect.width/2)`, `x.set(dx * 0.28)`, idem `y` com 0.35.
- O conteúdo interno pode ter um segundo par de springs com fator menor (parallax interno).
- `onMouseLeave` zera tudo; `whileHover={{ scale: 1.04 }}` e `whileTap={{ scale: 0.96 }}`.
**Cuidados:** desative em touch; limite o deslocamento a ~12px para não parecer quebrado.
**Frase pronta:** "Faça botões magnéticos com Framer Motion: motion values + spring seguindo o cursor com parallax interno."

#### D2. Bouncy / Spring Physics
**O que é:** animação com física de mola em vez de easing linear.
**Quando usar:** micro-interações, layout transitions, pills, cards.
**Como implementar:** `transition={{ type: "spring", stiffness: 300, damping: 18, mass: 0.6 }}`. Para "pílula" que desliza entre abas, `layoutId` + `LayoutGroup`.
**Cuidados:** molas muito elásticas cansam; use `damping` alto para elementos grandes. `stiffness` 200–450 é a faixa segura.
**Frase pronta:** "Use spring physics do Framer Motion e `layoutId` para transições de pílula entre abas."

#### D3. GSAP + ScrollTrigger
**O que é:** o padrão da indústria para animações complexas e orquestração de scroll.
**Quando usar:** pin, scrub, timelines longas, sincronização com Lenis.
**Como implementar:**
- Registre o plugin uma única vez (`gsap.registerPlugin(ScrollTrigger)`), em módulo client.
- Sempre dentro de `useLayoutEffect` com `gsap.context(() => {...}, ref)` e `return () => ctx.revert()`.
- Prefira `gsap.matchMedia()` para variantes responsivas.
- `ScrollTrigger.refresh()` depois de carregar fontes/imagens.
**Cuidados:** nunca crie triggers duplicados (Strict Mode roda efeitos 2x) — o `ctx.revert()` resolve. Evite animar propriedades de layout.
**Frase pronta:** "Use GSAP com ScrollTrigger para pin/scrub, dentro de `gsap.context` com cleanup."

### E. Efeitos bônus (já usados no projeto base)

| # | Efeito | Receita curta |
|---|---|---|
| E1 | Reveal em cascata | `whileInView` + `delay: i * 0.08`, `y: 28 → 0`, `once: true` |
| E2 | Parallax de camadas no mouse | springs independentes em grid, blob e mockup (fatores diferentes) |
| E3 | Marquee infinito | linha duplicada + `@keyframes translateX(0 → -50%)` 38s; pausa no hover; desliga em reduced motion |
| E4 | Flip card | `rotateY(180deg)` + `backface-visibility: hidden` + `perspective` |
| E5 | Count-up | GSAP `to(obj, { v })` com `onUpdate` e `scrollTrigger.once`; formate com `toLocaleString("pt-BR")` |
| E6 | Anel de progresso | SVG `stroke-dasharray`/`pathLength` animado com Framer (`pathLength: 0 → value/100`) |
| E7 | Confetti no clique | `element.animate([...], { duration, easing })` (Web Animations API), partículas com `position: fixed` |
| E8 | Acordeão de altura | `AnimatePresence` + `height: 0 → auto` + `opacity` |
| E9 | Pulso / ping | `animate-ping` do Tailwind ou `scale`/`opacity` em loop |
| E10 | Shake de erro | keyframes `x: [0,-8,8,-6,6,0]` por 0.4s |
| E11 | Hover lift | `whileHover={{ y: -4 }}` + sombra com transição longa |
| E12 | Texto com máscara por linha | wrapper `overflow: hidden` + filho `y: 100% → 0` |

---

## 6. Estrutura do site

O site tem **três camadas** e elas não devem ser fundidas em uma página só.

### 6.1 Home curada `/`

Usa no máximo **8 efeitos**, no máximo **1 seção pinada** e **zero WebGL**. Ordem sugerida:

1. **Navbar sticky** — sombra só após scroll (`window.scrollY > 8`), CTA magnético, menu mobile animado.
2. **Hero** — kinetic typography (A5) + tilt 3D (B4) + CTA magnético (D1) + blob/aurora (C3).
3. **Benefícios** — bento grid (C1) com reveal em cascata (E1) e hover lift (E11).
4. **Como funciona** — a única seção pinada da home (A2/A3/A4), com 3–4 passos.
5. **Faixa de idiomas/parceiros** — marquee (E3).
6. **Números** — count-up (E5).
7. **CTA final + footer**.

Opcional: 2–3 glass cards (C2) se o fundo da seção permitir contraste.

Cada seção da home leva `eyebrow` com `TÉCNICA · {NOME}` e um link discreto **"ver demo →"** apontando para `/lab/{slug}`. É isso que transforma a home em porta de entrada do catálogo.

### 6.2 Índice `/lab`

Server component que lê `lib/effects.ts`. Conteúdo:

- Headline curta + explicação do laboratório em 2 linhas.
- **Filtros client-side** por categoria (scroll / 3D / estética / interação) e por custo (leve / médio / pesado), com contador ("13 efeitos"). Estado dos filtros na URL (`?categoria=3d`) para links compartilháveis.
- **Bento grid** de cards. Cada card: código (`A5`), nome, resumo de 1 linha, badge de custo, dependências e link "Abrir demo →".
- **Nenhum demo é montado no índice.** Para não ficar uma vitrine morta: poster estático (imagem/SVG) ou preview em hover **apenas** de efeitos leves em CSS. Nunca WebGL, nunca `ScrollTrigger` no índice.
- Rodapé do índice com a explicação: "cada demo abre em uma página isolada para medir o custo real do efeito".

### 6.3 Página de efeito `/lab/[slug]`

1. **Breadcrumb** `Laboratório / {nome}` + botão "voltar".
2. **Cabeçalho** — código + nome, badge de categoria e de custo, resumo de 1 linha.
3. **`DemoFrame`** — área de altura fixa (`min-h-[60vh]`, fundo neutro, cantos arredondados). O componente do efeito é montado aqui, com `key={slug}` para remontar ao navegar entre demos.
4. **Ficha em 4 blocos** — "O que é", "Quando usar", "Como implementar", "Cuidados".
5. **Dependências e nota de performance** — pacotes usados, tamanho aproximado e impacto esperado.
6. **Prompt copiável** — bloco de código com a "frase pronta" + botão "Copiar prompt".
7. **Navegação** — anterior/próximo + "ver todos os efeitos".

Regras:

- **SSG obrigatório**: `generateStaticParams` a partir do registro; `generateMetadata` com `title`/`description` por efeito.
- Slug inexistente chama `notFound()` (página 404).
- A página é **server component**; só `DemoFrame` e `CopyPrompt` são `"use client"`.
- Cada demo encerra seus loops no unmount — a troca de rota já desmonta o componente, então nada de "esconder" demo com CSS.

### 6.4 Navegação global

- Navbar: **Início**, **Laboratório** e um link para o efeito em destaque.
- No mobile, o menu abre com a mesma animação da home.
- Todo card do índice aponta para a rota; toda rota volta para o índice.

---

## 7. Design system

Use estes tokens (ajuste só se o produto pedir):

```ts
colors: {
  tangerine: { DEFAULT: "#FF5A0A", light: "#FF7A33", dark: "#E64A00", tint: "#FFE9DC", soft: "#FFF5EE" },
  ink: "#111111", body: "#5C5C5C", mist: "#F7F7F8", line: "#EDEDED",
}
fontFamily: { sans: ["Poppins", "system-ui", "sans-serif"] }
borderRadius: { pill: "999px" }
boxShadow: {
  card: "0 10px 30px rgba(17,17,17,0.06)",
  lift: "0 18px 40px rgba(17,17,17,0.10)",
  cta:  "0 12px 28px rgba(255,90,10,0.35)",
}
```

Tipografia: Poppins 400–800 via Google Fonts com `preconnect` e `display=swap`. Títulos com `leading` apertado (1.04–1.1) e `tracking-tight`; corpo 15–17px com `leading-relaxed`.

---

## 8. Critérios de aceite

A entrega só é considerada pronta se:

- [ ] `npm run build` passa sem erros e sem warnings de tipo.
- [ ] `npx tsc --noEmit` limpo.
- [ ] Sem overflow horizontal em 390 / 768 / 1024 / 1440 (`scrollWidth === clientWidth`).
- [ ] Sem erros no console e sem warnings de hidratação.
- [ ] `prefers-reduced-motion` desliga/atenua todas as animações.
- [ ] Navegação por teclado funciona (Tab/Enter/Espaço), com foco visível.
- [ ] Nenhum listener, RAF ou ScrollTrigger vaza após unmount.
- [ ] Imagens com dimensões declaradas (sem CLS).
- [ ] A página continua legível e bonita com o JavaScript desligado (conteúdo no HTML).
- [ ] **Orçamento por rota respeitado**: home ≤ 220 kB, `/lab` ≤ 200 kB, demos leves ≤ 200 kB de First Load JS (demos 3D podem passar, com tamanho declarado).
- [ ] `next build` lista `/`, `/lab` e **uma rota por efeito**; a tabela de First Load JS por rota acompanha o relatório.
- [ ] `/lab` **não monta nenhum demo**: sem `requestAnimationFrame`, `ScrollTrigger` ou canvas WebGL rodando no índice.
- [ ] Navegar entre demos libera tudo: listeners, RAF, `ScrollTrigger` e contextos WebGL são destruídos no unmount.
- [ ] `generateStaticParams` gera exatamente as rotas do Anexo A; slug inexistente retorna **404**.
- [ ] Todo card do índice aponta para a rota certa e toda rota tem link de volta ao índice.

---

## 9. Formato da resposta

1. **Plano curto** (5–10 linhas): o que será construído, quantas rotas e quais efeitos do catálogo entram na home e no laboratório.
2. **Lista de arquivos** a criar/alterar, incluindo `lib/effects.ts` e um arquivo por demo.
3. **Código completo** de cada arquivo, sem trechos omitidos.
4. **Tabela de efeitos implementados**:

| Efeito | Rota | Demo | Dependência | Custo |
|---|---|---|---|---|
| A1 Lenis | `/lab/lenis` | `LenisDemo` | `lenis` | leve |

5. **Tabela de rotas e peso** (copiada do `next build`):

| Rota | First Load JS | Observação |
|---|---|---|
| `/` | 191 kB | home curada |
| `/lab` | 132 kB | índice, sem demos |
| `/lab/tilt-3d` | 140 kB | demo leve |

6. **Como rodar**: comandos e o que observar (abrir `/lab`, testar cada demo isolada, conferir 404 em slug inválido).
7. **O que ficou de fora** e por quê (se algo do Anexo A não couber).

Não peça confirmação no meio do caminho: entregue a versão completa e depois liste os ajustes possíveis.

---

## Anexo A — Checklist de seleção (edite antes de enviar)

Marque com `x` no bloco abaixo os efeitos que ganham **página própria** em `/lab/[slug]`. O que ficar vazio **não** deve ser implementado nem roteado.

- **Laboratório** = todo item marcado vira uma rota isolada.
- **Home curada** = subconjunto (máx. 8) que também aparece em `/`, sem WebGL e com no máximo 1 seção pinada.

**Scroll**
- [ ] A1 Smooth Scroll / Lenis
- [ ] A2 Scrollytelling
- [ ] A3 Scroll-driven / Scroll-triggered
- [ ] A4 Sticky / Pinned
- [ ] A5 Kinetic Typography

**3D**
- [ ] B1 WebGL / Three / R3F
- [ ] B2 Spline 3D
- [ ] B3 Custom Shaders / GLSL
- [ ] B4 Interactive 3D Mesh / Tilt 3D

**Estética**
- [ ] C1 Bento Grid
- [ ] C2 Glassmorphism
- [ ] C3 Mesh Gradients / Aurora
- [ ] C4 Noise / Film Grain
- [ ] C5 Dark Mode + Neon Glow / Spotlight

**Micro-interações**
- [ ] D1 Magnetic Buttons
- [ ] D2 Bouncy / Spring Physics
- [ ] D3 GSAP + ScrollTrigger

**Bônus**
- [ ] E1 Reveal em cascata
- [ ] E2 Parallax de camadas
- [ ] E3 Marquee
- [ ] E4 Flip card
- [ ] E5 Count-up
- [ ] E6 Anel de progresso
- [ ] E7 Confetti
- [ ] E8 Acordeão
- [ ] E9 Pulso
- [ ] E10 Shake
- [ ] E11 Hover lift
- [ ] E12 Máscara por linha

**Home curada (subconjunto que também aparece em `/` — máx. 8, zero WebGL)**
- [x] A5 Kinetic Typography
- [x] B4 Interactive 3D Mesh / Tilt 3D
- [x] C1 Bento Grid
- [x] C3 Mesh Gradients / Aurora
- [x] D1 Magnetic Buttons
- [x] E1 Reveal em cascata
- [x] E3 Marquee
- [x] E5 Count-up

> A1 (Lenis) e D2 (springs) valem para o site inteiro e entram por padrão em qualquer combinação. Se a home passar de 8 itens, mantenha os 8 de maior impacto e explique o corte no relatório.
>
> **Regra de coerência:** todo efeito marcado na home precisa estar marcado também no laboratório, porque o link "ver demo →" aponta para `/lab/{slug}`.

**Seleção padrão do laboratório:** marque **todos** os efeitos. Como cada um vira uma rota isolada, o volume total deixa de ser um problema de peso — o custo é por página, não do site inteiro.

---

## Anexo B — Snippets de referência

### B.1 Lenis + GSAP

```tsx
"use client";
import { setLenis } from "@/lib/lenis"; // setter do singleton

export default function LenisProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const lenis = new Lenis({ duration: 1.15, easing: t => 1 - Math.pow(1 - t, 4), smoothWheel: true });
    setLenis(lenis);
    lenis.on("scroll", ScrollTrigger.update);
    const raf = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(raf);
    gsap.ticker.lagSmoothing(0);
    return () => {
      gsap.ticker.remove(raf);
      lenis.destroy();
      setLenis(null);
    };
  }, []);
  return <>{children}</>;
}
```

### B.2 Pin + troca de passo

> Trecho ilustrativo: `st`, `barRef`, `pinRef`, `rootRef` e `setActive` vêm do componente.

```tsx
useLayoutEffect(() => {
  const ctx = gsap.context(() => {
    st.current = ScrollTrigger.create({
      trigger: pinRef.current,
      start: "top top",
      end: "+=320%",
      pin: true,
      anticipatePin: 1,
      onUpdate: self => {
        barRef.current!.style.transform = `scaleY(${self.progress})`;
        setActive(Math.min(STEPS.length - 1, Math.floor(self.progress * STEPS.length)));
      },
    });
  }, rootRef);
  return () => ctx.revert();
}, []);
```

### B.3 Botão magnético

```tsx
const x = useMotionValue(0), y = useMotionValue(0);
const sx = useSpring(x, { stiffness: 220, damping: 14, mass: 0.5 });
const sy = useSpring(y, { stiffness: 220, damping: 14, mass: 0.5 });

const onMove = (e: React.MouseEvent) => {
  const r = e.currentTarget.getBoundingClientRect();
  x.set((e.clientX - (r.left + r.width / 2)) * 0.28);
  y.set((e.clientY - (r.top + r.height / 2)) * 0.35);
};
const onLeave = () => { x.set(0); y.set(0); };

<motion.button style={{ x: sx, y: sy }} onMouseMove={onMove} onMouseLeave={onLeave}
  whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }} />
```

### B.4 Tilt 3D em CSS

```tsx
<div style={{ perspective: 1200 }} onMouseMove={onMove} onMouseLeave={onLeave}>
  <motion.div style={{ rotateX, rotateY }} className="preserve-3d">
    <div style={{ transform: "translateZ(90px)" }} />
    <div style={{ transform: "translateZ(160px)" }} />
  </motion.div>
</div>
```

### B.5 Spotlight

```css
.spotlight { position: relative; background: #0b0b0c; }
.spotlight::before {
  content: "";
  position: absolute; inset: 0;
  background: radial-gradient(420px circle at var(--mx, 50%) var(--my, 50%),
              rgba(255, 90, 10, 0.20), transparent 70%);
  opacity: 0; transition: opacity .4s ease; pointer-events: none;
}
.spotlight:hover::before { opacity: 1; }
```

```ts
el.addEventListener("pointermove", e => {
  const r = el.getBoundingClientRect();
  el.style.setProperty("--mx", `${e.clientX - r.left}px`);
  el.style.setProperty("--my", `${e.clientY - r.top}px`);
});
```

### B.6 Film grain

```css
.grain {
  position: fixed; inset: 0; z-index: 50; pointer-events: none;
  opacity: .045; mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
```

### B.7 Reduced motion

```tsx
const reduce = useReducedMotion();
<motion.div animate={{ y: reduce ? 0 : [0, -14, 0] }} transition={{ duration: 5, repeat: reduce ? 0 : Infinity }} />
```

---

## Anexo C — Mapa de referência (projeto Tangerine Talk)

Use como inspiração de implementação real; não copie os textos, apenas as soluções técnicas.

> **Nota:** o projeto de referência é uma página única. Ao reaproveitar o código, distribua cada efeito para o componente de demo correspondente em `components/demos/` — não replique a estrutura de página única descrita aqui.

| Componente | Efeitos aplicados |
|---|---|
| `Hero.tsx` | A5 kinetic type, B4 tilt 3D, E2 parallax de camadas, D1, D2 (`layoutId` da pílula de idiomas) |
| `Navbar.tsx` | header sticky com sombra condicional, menu mobile com `AnimatePresence` |
| `Scrolly.tsx` | A2 scrollytelling, A3 scrub, A4 pin, E8 acordeão, troca com `AnimatePresence` |
| `Features.tsx` | E1 reveal em cascata, E11 hover lift |
| `Bento.tsx` | C1 bento grid, E6 anel de progresso, E7 confetti no clique, E9 pulso |
| `Languages.tsx` | E3 marquee com pausa no hover |
| `CtaStats.tsx` | gradiente de fundo + dot grid, E5 count-up com locale pt-BR |
| `mockups/*` | A3 (loops de estado), E4 flip, E9 pulso, E10 shake, E6 anel |
| `PillButton.tsx` | D1 magnético + parallax do ícone interno |
| `globals.css` | keyframes de marquee, `.bubble` com gradiente e sombra interna, `prefers-reduced-motion` |

---

## Anexo D — Esqueletos da estrutura multi-página

### D.1 Registro `lib/effects.ts`

```ts
export type EffectCategory = "scroll" | "3d" | "estetica" | "interacao";
export type EffectCost = "leve" | "medio" | "pesado";

export type Effect = {
  slug: string;
  code: string;
  name: string;
  category: EffectCategory;
  cost: EffectCost;
  deps: string[];
  summary: string;
  prompt: string;
  onHome?: boolean;
};

export const EFFECTS: Effect[] = [
  {
    slug: "kinetic-typography",
    code: "A5",
    name: "Kinetic Typography",
    category: "scroll",
    cost: "leve",
    deps: [],
    summary: "Palavras reveladas por máscara, com stagger e leve reação ao mouse.",
    prompt: "Crie kinetic typography no hero: palavras reveladas por máscara com stagger e leve reação ao mouse.",
    onHome: true,
  },
  // ... um item por efeito marcado no Anexo A
];

export const bySlug = (slug: string) => EFFECTS.find((e) => e.slug === slug);
export const homeEffects = () => EFFECTS.filter((e) => e.onHome);
```

### D.2 Índice `app/lab/page.tsx`

```tsx
import { EFFECTS } from "@/lib/effects";
import EffectsGrid from "@/components/lab/EffectsGrid";

export const metadata = { title: "Laboratório de efeitos" };

export default function LabPage() {
  return (
    <main className="mx-auto max-w-[1200px] px-5 py-16">
      <p className="eyebrow">Laboratório</p>
      <h1 className="h2">Efeitos que você pode pedir a qualquer LLM.</h1>
      <p className="mt-4 max-w-xl text-body">
        Cada demo abre em uma página isolada, com ficha técnica e prompt copiável.
      </p>
      <EffectsGrid effects={EFFECTS} />
    </main>
  );
}
```

### D.3 Rota `app/lab/[slug]/page.tsx`

```tsx
import { notFound } from "next/navigation";
import { EFFECTS, bySlug } from "@/lib/effects";
import DemoFrame from "@/components/lab/DemoFrame";
import CopyPrompt from "@/components/lab/CopyPrompt";

export function generateStaticParams() {
  return EFFECTS.map(({ slug }) => ({ slug }));
}

export function generateMetadata({ params }: { params: { slug: string } }) {
  const e = bySlug(params.slug);
  return e ? { title: `${e.name} — Laboratório`, description: e.summary } : {};
}

export default function EffectPage({ params }: { params: { slug: string } }) {
  const e = bySlug(params.slug);
  if (!e) notFound();

  return (
    <main className="mx-auto max-w-[1200px] px-5 py-16">
      <p className="eyebrow">
        {e.code} · {e.category} · {e.cost}
      </p>
      <h1 className="h2">{e.name}</h1>
      <p className="mt-4 max-w-xl text-body">{e.summary}</p>
      <DemoFrame slug={e.slug} />
      <CopyPrompt text={e.prompt} />
    </main>
  );
}
```

### D.4 Mapa de demos `components/demos/index.tsx`

```tsx
import dynamic from "next/dynamic";

export const DEMOS: Record<string, React.ComponentType> = {
  "kinetic-typography": dynamic(() => import("./KineticTypeDemo")),
  "lenis": dynamic(() => import("./LenisDemo"), { ssr: false }),
  "webgl": dynamic(() => import("./WebGLDemo"), {
    ssr: false,
    loading: () => <div className="h-full animate-pulse rounded-2xl bg-mist" />,
  }),
};
```

> `DemoFrame` é o único ponto que importa `DEMOS`, e ele só é usado em `/lab/[slug]`. Assim, o índice e a home nunca carregam Three.js, Spline ou qualquer demo.

---

**Fim do prompt.** Se algum item do Anexo A conflitar com performance ou acessibilidade, priorize performance e acessibilidade e explique a decisão no relatório final.