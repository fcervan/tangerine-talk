# AGENTS.md — Tangerine Talk

> Contexto para agentes de código (OpenCode e outros) que forem continuar este projeto.
> **Idioma de trabalho: português do Brasil.** Responda sempre em pt-BR.
> Todos os caminhos aqui são **relativos à raiz do projeto** — ele pode ser movido de pasta sem quebrar nada.

---

## 1. O que é este projeto

Tutor de idiomas com IA **gratuito, open source (MIT) e auto-hospedável**. A landing
está pronta (copy hardcoded em **pt-BR**) e o backend já tem identidade e multiusuário.

**Fase atual:** Fases 1, 2, 3, 4 e 5 concluídas — FastAPI, MySQL, migração, login por cookie
`httpOnly`, refresh rotacionado, convites, papéis `owner`/`member`, perfil, exportação
e exclusão de conta; **BYOK** com chave por usuário cifrada (Fernet), teste de conexão,
cadeia de fallback e modo offline; **conteúdo versionado** com trilha, lições,
exercícios, glossas por `ui_language`, decks oficiais e progresso por usuário;
**tutor de IA** com chat, correção, TTS/STT, player de lição com 4 habilidades e
fallback automático entre provedores; **gamificação** com XP, streak, SRS (SM-2),
selos, ligas semanais e missões diárias.
57 testes passam (incluindo isolamento entre usuários).
**Próximas fases:** conteúdo expandido, Qdrant, qualidade. Ver seção 10.

---

## 2. Stack e versões

Versões **instaladas** (verificadas em `node_modules`):

| Camada | Tecnologia | Versão |
|---|---|---|
| Framework | Next.js (App Router) | 14.2.15 |
| UI | React / React DOM | 18.3.1 |
| Linguagem | TypeScript (strict) | 5.9.3 |
| Estilo | Tailwind CSS (v3) | 3.4.19 |
| Animações de UI | Framer Motion | 11.18.2 |
| Animações de scroll | GSAP + ScrollTrigger | 3.15.1 |
| Scroll suave | Lenis | 1.3.27 |
| Build | PostCSS / Autoprefixer | 8.5.32 / 10.6.2 |

Ambiente usado: Node v20.18.2, npm 10.8.2.

**Não há:** ESLint, Prettier, Jest/Vitest/Playwright, Tailwind plugins, biblioteca de estado, i18n.

---

## 3. Comandos

```bash
npm install        # instalar dependências
npm run dev        # dev server em http://localhost:3000
npm run build      # build de produção
npm start          # servir o build

npx tsc --noEmit                              # front

cd api
uv sync                                        # instala o backend
uv run pytest -q                               # 57 testes
uv run ruff check . && uv run mypy app
uv run alembic upgrade head                    # aplica migrações no MySQL
uv run python -m app.cli create-owner --help   # bootstrap do owner
```

### ⚠️ Armadilha crítica: `build` e `dev` ao mesmo tempo

**Nunca rode `npm run build` com o `npm run dev` ativo no mesmo diretório.** Os dois compartilham `.next`; o build apaga o CSS do dev e o site passa a carregar **sem estilo** (o HTML pede `/_next/static/css/app/layout.css` e recebe **404**). Isso já aconteceu neste projeto e pareceu "layout quebrado".

Se acontecer:

```bash
# 1. pare o dev server
# 2. remova o .next contaminado
rm -rf .next
# 3. suba o dev novamente
npm run dev
# 4. no navegador: Ctrl+Shift+R
```

Para testar produção, pare o dev antes (ou use outra worktree/cópia).

### Retomando o projeto em outro path

```bash
# 1. copie a pasta (node_modules e .next podem ficar de fora)
rsync -a --exclude node_modules --exclude .next tangerine-talk/ /novo/caminho/

# 2. instale e suba
cd /novo/caminho
npm install
npm run dev
```

- **Nenhum caminho absoluto está no código**: o alias `@/*` e o `paths` do `tsconfig.json` são relativos à raiz. Mover a pasta não quebra imports.
- `.next/` é regenerado no primeiro `dev` ou `build`.
- Se for para **outra máquina**, copie também `package-lock.json` (garante as mesmas versões) e o arquivo de referência citado na seção 12.
- Se a sessão do agente for nova, ele deve ler este `AGENTS.md` antes de qualquer alteração.

---

## 4. Estrutura

```
app/
  layout.tsx            # locale do cookie, metadata i18n, Poppins, globals.css
  (marketing)/page.tsx  # landing (LenisProvider > Navbar > sections > Footer)
  (auth)/               # login e convite/[token]
  (app)/                # onboarding, app, curriculum e providers (área autenticada)
  globals.css           # tokens utilitários, keyframes, .bubble, .dot-grid, .marquee, reduced motion
middleware.ts           # portão de UX: /app, /onboarding, /curriculum e /providers
components/
  Navbar.tsx            # header sticky, menu mobile animado
  Hero.tsx              # headline com máscara, tilt 3D, seletor de idiomas
  Features.tsx          # 4 cards (Fala, Escuta, Escrita, Testes)
  Scrolly.tsx           # scrollytelling com pin do GSAP + mockups
  Bento.tsx             # gamificação: sequência, ranking, metas, skill tree
  Languages.tsx         # marquee de idiomas
  CtaStats.tsx          # CTA final + stats com count-up
  Footer.tsx
  PillButton.tsx        # CTA com efeito magnético
  Logo.tsx, icons.tsx
  LenisProvider.tsx     # provider de smooth scroll
  LocaleProvider.tsx    # useI18n(): locale, t(), setLocale()
  LocaleSwitcher.tsx    # seletor pt-BR/en-US
  LoginForm.tsx, InviteForm.tsx, OnboardingWizard.tsx, AppDashboard.tsx
  ProvidersPanel.tsx, CurriculumPanel.tsx, LessonPlayer.tsx
  mockups/              # Speaking, Listening, Writing, Testing, Waveform
lib/
  i18n/                 # locales/pt-BR.ts (tipa), en-US.ts, fallback pt-BR
  api.ts                # fetch /api/* com refresh automático
  lenis.ts              # singleton + scrollToId
  gsap.ts               # registro do ScrollTrigger
  ease.ts               # curvas compartilhadas
  confetti.ts           # burst via Web Animations API
public/
  mascot.png            # mascote (usado no Hero e no Logo)
  logo-full.jpg         # NÃO usado atualmente
api/
  app/auth/             # login, refresh, logout, cookies, deps e convites
  app/users/            # perfil, onboarding, membros, convites, export e exclusão
  app/i18n.py           # BCP-47, base do idioma, modo monolingual/bilingual
  app/models/           # User, AuthSession, Invite, ProviderCredential, conteúdo — UUIDv7 em BINARY(16)
  app/providers/        # catálogo, cadeia de fallback, teste de conexão e rotas BYOK
  app/content/          # seed versionado, esquemas e rotas de currículo/decks
  app/tutor/            # chat, correção, TTS/STT, player de lição com 4 habilidades
  app/security/         # Argon2id, JWT/refresh, limite de login, Fernet
  alembic/versions/     # 0001 identidade · 0002 idiomas · 0003 BYOK · 0004 conteúdo
  tests/                # SQLite em memória + httpx assíncrono
docker-compose.yml      # mysql :3310, api :8010, web (profile) :3110
next.config.mjs         # rewrite /api/* → FastAPI
```

Versionado no Git (`main`); `.gitignore` cobre `node_modules/`, `.next/`, `*.tsbuildinfo`, `.env`, dumps, áudios e volumes. `.next/` e `node_modules/` são descartáveis e não devem ser versionados.

---

## 5. Convenções de código

- **Server components por padrão.** `"use client"` só onde há hooks, eventos ou animação (21 arquivos hoje).
- Conteúdo de listas (features, passos, cards, decks) fica em **arrays no topo do arquivo**, nunca hardcoded no JSX.
- TypeScript `strict`; sem `any` injustificado. Alias `@/*` → raiz.
- Tailwind **v3** com tokens em `tailwind.config.ts` (`theme.extend`). Sem CSS-in-JS.
- Ícones são SVGs próprios em `components/icons.tsx`. Não adicionar biblioteca de ícones.
- Imagens usam `<img>` puro (não há `next/image` no projeto).
- Animações: **apenas `transform` e `opacity`** em loops; `will-change` com parcimônia.
- `prefers-reduced-motion` é obrigatório em tudo que se move (CSS + `useReducedMotion` + `gsap.matchMedia`).
- Cleanup obrigatório: remover listeners, cancelar RAF, `ctx.revert()` em todo `gsap.context`.
- Scroll suave centralizado: use `scrollToId()` de `lib/lenis.ts`; não duplique lógica.
- Não adicione dependências sem necessidade real. O bundle atual da home é ~191 kB de First Load JS.

---

## 6. Design system

Tokens em `tailwind.config.ts`:

```ts
tangerine: { DEFAULT: "#FF5A0A", light: "#FF7A33", dark: "#E64A00", tint: "#FFE9DC", soft: "#FFF5EE" }
ink: "#111111"   body: "#5C5C5C"   mist: "#F7F7F8"   line: "#EDEDED"

fontFamily: Poppins, system-ui, sans-serif
borderRadius: pill = 999px
boxShadow: card, lift, cta
```

Classes utilitárias em `app/globals.css`:

| Classe | Uso |
|---|---|
| `.eyebrow` | rótulo pequeno em maiúsculas |
| `.h2` | título de seção (34px → 44px) |
| `.hl` | destaque em laranja dentro do título |
| `.card` | card branco com sombra |
| `.bubble` | balão de fala com gradiente e sombra interna |
| `.dot-grid` | fundo pontilhado |
| `.marquee` | faixa infinita (pausa no hover) |
| `.preserve-3d` / `.backface-hidden` | utilidades 3D |

Tipografia: Poppins 400–800 via `<link>` do Google Fonts (não é `next/font`).

---

## 7. Idiomas e decisões editoriais

**Dois eixos independentes — nunca misturar:**

| Eixo | Campo | Quem define | Exemplo |
|---|---|---|---|
| Idioma da **interface** | `ui_language` | usuário (padrão `pt-BR`) | textos da home, enunciados, instruções, glossas, feedback, datas e números |
| Idioma **estudado** | `target_language` | usuário no onboarding | a frase avaliada, que permanece no idioma alvo |

A interface nasce com **pt-BR como principal** e **en-US como segundo idioma oferecido**, mas o sistema é aberto: qualquer código BCP-47 pode ser cadastrado depois (adicione um dicionário em `lib/i18n/locales/`). **Fallback técnico é sempre pt-BR**, nunca inglês. Textos em `lib/i18n/locales/*.ts`; sem texto hardcoded novo.

Se `ui_language` e `target_language` tiverem a mesma base, o exercício é **monolingual** (leitura, gramática e pronúncia, sem tradução). A direção de toda tradução é `ui_language → target_language` — nunca um par fixo.

Regras que continuam valendo:

- **Marca não se traduz:** "Tangerine Talk".
- **Glossário pt-BR:** sequência (streak), selos (badges), baralho (deck), flashcards (mantido). Em en-US: streak, badges, deck, flashcards.
- **Frases de exemplo permanecem no idioma estudado:** `Buenos días`, `こんにちは`, `¿Dónde está la estación?`. O que se traduz são as **glossas/explicações** e os rótulos de idioma — sempre no idioma da interface.
- Os pares "espanhol → português" e "português → inglês" dos mockups da landing são **exemplos de marketing**, não regra do motor de lição.
- **Números/datas:** `Intl` com o locale ativo; pt-BR como padrão (2.615, 4,9).

---

## 8. Mapa das seções

| Seção | Arquivo | Efeitos |
|---|---|---|
| Navbar | `components/Navbar.tsx` | header sticky com sombra após scroll, menu mobile com `AnimatePresence` |
| Hero | `components/Hero.tsx` | headline com máscara (kinetic type), tilt 3D com perspective/translateZ, parallax de camadas, pílula com `layoutId` |
| Recursos | `components/Features.tsx` | reveal em cascata (`whileInView`) |
| Como funciona | `components/Scrolly.tsx` | ScrollTrigger com `pin`, barra de progresso, troca de mockups, passos clicáveis |
| Gamificação | `components/Bento.tsx` | bento grid, anel SVG (`pathLength`), confetti no clique, skill tree interativa |
| Idiomas | `components/Languages.tsx` | marquee CSS |
| CTA + stats | `components/CtaStats.tsx` | count-up com GSAP e locale pt-BR |
| Footer | `components/Footer.tsx` | — |

Âncoras: `#top`, `#features`, `#how-it-works`, `#gamification`, `#languages`, `#pricing`.
**Gap conhecido:** `#pricing` aponta para a seção de CTA (`CtaStats`), não existe página/tabela de preços.

---

## 9. Armadilhas conhecidas

1. **`build` com `dev` ativo corrompe o CSS** — ver seção 3.
2. **`.next` é descartável.** Se algo estranho acontecer, pare o dev, `rm -rf .next` e suba de novo.
3. **Framer Motion renderiza `opacity: 0` no SSR** para elementos com `initial`. Com JS desligado ou falha de hidratação, esses blocos ficam invisíveis. Não coloque conteúdo crítico de SEO dependente de `animate` sem fallback.
4. **ScrollTrigger + pin** cria um `pin-spacer`; chame `ScrollTrigger.refresh()` depois de fontes/imagens e sempre reverta com `ctx.revert()`.
5. **Strict Mode** roda efeitos duas vezes em dev — sem cleanup, triggers e listeners duplicam.
6. **Screenshot headless com `--virtual-time-budget` não reproduz animações corretamente** (pode parecer que o hero está vazio). Valide com Chrome real via CDP ou no navegador.
7. **Overflow:** a palavra "naturalmente." na headline a 44px cabe em 360px, mas fica no limite em 320px. Se a headline mudar, teste em 320/390px.
8. `tsconfig.tsbuildinfo` é artefato de build; pode ser apagado.

---

## 10. Próxima fase: a aplicação

A landing sugere o produto. Escopo de telas/recursos em `docs/plano-telas-e-recursos.md`; stack e decisões em `docs/arquitetura-e-tecnologias.md`.

**Stack já decidida (2026-11):** front Next.js separado do backend **FastAPI**, tudo em **Docker**; banco **MySQL**; vetorial **Qdrant**; cache/fila **Redis**; LLM com fallback Groq → Ollama Cloud → OpenRouter.

Status: **Fases 0, 1, 2 e 3 concluídas**. O app tem onboarding, login, convite,
i18n com pt-BR padrão/en-US secundário, BYOK por usuário (chave cifrada, teste
de conexão, fallback e modo offline) e conteúdo versionado no MySQL (unidades,
lições, exercícios, glossas por locale, decks oficiais e progresso por usuário)
com a tela `/curriculum` e o **player de lição `/lesson/{id}` com 4 habilidades**.
Gamificação completa: XP, streak, SRS (SM-2), selos, ligas semanais e missões.

Roadmap **sugerido** — o que ainda não está fechado:

1. ✅ **Higiene do repositório** — licença MIT, SECURITY/CONTRIBUTING/CODE_OF_CONDUCT, `.gitignore`, gitleaks no CI
2. ✅ **Fundação do app** — i18n em `lib/i18n` (pt-BR padrão, en-US, extensível), `lib/api.ts` com refresh automático, middleware protegendo `/app`, `/onboarding`, `/curriculum` e `/providers`
3. ✅ **Auth e multiusuário** — backend + telas de login, convite e onboarding (idioma da interface, idioma alvo, nível, meta diária)
   - pendente: migrar a copy da landing para os dicionários (visual inalterado)
4. ✅ **Núcleo de aprendizado — Fase 4 entregue**
   - player de lição com as 4 habilidades (fala, escuta, escrita, testes), consumindo o conteúdo da Fase 3
   - tutor de IA (chat, correção, TTS/STT, server-side, chave nunca no cliente), com retry e aviso de quota na cadeia BYOK
   - pronúncia via Web Speech API (base; provedor TTS/STT pendente)
5. ✅ **Gamificação — Fase 5 entregue**
   - XP, streak (com selos 7/30/100), SRS (SM-2), ligas semanais (Bronze→Diamond), missões diárias
   - endpoints: `/gamification`, `/streak`, `/badges`, `/srs/due`, `/srs/review`, `/missions`, `/league/*`, `/leaderboard`
   - selos: first_lesson, first_deck, streak_7/30/100, conversations_1/25/50, week_league_win
6. ✅ **Conteúdo e trilha** — Fase 3 entregue
   - seed idempotente de espanhol A1: 2 unidades, 3 lições, 10 itens, 8 exercícios e 1 deck oficial
   - pré-requisito entre unidades, glossas resolvidas pelo `ui_language`, progresso por usuário em export/exclusão
   - tela `/curriculum` com prévia da lição e baralhos; pendente: painel para criar decks próprios e importação
7. ✅ **Provedores de IA e multiusuário** — Fase 2 entregue
   - BYOK por usuário (Fernet), teste de conexão, cadeia `Groq → Ollama Cloud → OpenRouter → Ollama` e modo offline
   - convites por e-mail e isolamento entre membros
   - motor de lição consome a cadeia com retry e aviso de quota (Fase 4)
8. **Qualidade**
   - acessibilidade AA, performance (Core Web Vitals), analytics
   - testes: unitários para lógica de SRS/XP e E2E dos fluxos críticos

**Decisões ainda abertas:** provedor de áudio/pronúncia (Azure vs. Speechace), push-to-talk vs. full-duplex, modelo de embedding (BGE-M3 vs. OpenAI) e tratamento da Fala offline (sem nota vs. alinhamento local). **Fechadas:** idiomas da interface (pt-BR + en-US, extensível), idioma alvo genérico, par igual = deck monolingual. Detalhes em `docs/arquitetura-e-tecnologias.md` §13.

---

## 11. Regras para agentes

- Responda em **pt-BR**; nomes de código em inglês.
- Antes de reescrever copy, leia a seção 7 (decisões editoriais).
- Não remova animações, degradês ou o mascote sem pedido explícito.
- Ao mexer em layout: valide 390px e 1440px e confirme `scrollWidth === clientWidth`.
- Rode `npx tsc --noEmit` após mudanças de código.
- **Não rode `npm run build` com o dev ativo.**
- Mantenha `prefers-reduced-motion`, foco visível e labels ARIA.
- Se adicionar dependência, justifique e verifique o impacto no First Load JS.

---

## 12. Referências

- `docs/plano-telas-e-recursos.md` — rascunho de produto: inventário de promessas da landing, sitemap (~35 telas), recursos por domínio, priorização P0/P1/P2 e decisões pendentes.
- `docs/arquitetura-e-tecnologias.md` — stack decidida (Next + FastAPI + MySQL + Qdrant + Redis + Docker), implicações do MySQL, regras do Qdrant, IA/voz, riscos e decisões abertas.
- `docs/referencias-engenharia-ia.md` — o que aproveitar e o que evitar dos repositórios de estudo locais (assistente-suporte, avaliador-vendas, docling-service, dbscope, RAG avançado, LangGraph, SLM), com mapa módulo → referência e spikes recomendados.
- `docs/prompt-landing-page-efeitos-premium.md` — prompt/catálogo de efeitos de movimento, 3D e estética, com a arquitetura **índice (`/lab`) + uma página por efeito (`/lab/[slug]`)**, fichas técnicas e critérios de performance. Útil para evoluir a landing ou criar o laboratório de efeitos.

---

## 13. Repositório e ambiente

**Repositório público.** Tudo que entra no Git é visível para o mundo — trate cada commit como publicação.

- Layout: front (Next.js) na raiz e backend em `api/`; infraestrutura em `docker-compose.yml`.
- Para conferir o estado: `git status`, `git log --oneline -5`, `npm run dev`.
- **Nunca** versione `node_modules/`, `.next/`, `*.tsbuildinfo`, `.env`, dumps, áudios ou volumes (já cobertos pelo `.gitignore`).
- Configuração pessoal fica **fora** do repositório (`.env`, chaves SSH, arquivos de segredo).
- Antes de publicar, rode a verificação de segredos no histórico (ver `.github/workflows/ci.yml`).
- Não faça `git add/commit/push` sem confirmação explícita do mantenedor.
- **Tarefa final do projeto (ao concluir todas as fases):** apagar o repositório no
  GitHub, recriá-lo vazio e subir o histórico limpo — os SHAs antigos
  (`6be6a19`, `a93360a`) ainda são servidos por URL direta mesmo após o
  force-push. Lembrar ao usuário na hora e pedir confirmação antes de apagar.
