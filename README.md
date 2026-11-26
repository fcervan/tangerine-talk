# Tangerine Talk

Tutor de idiomas com IA, **gratuito, open source (MIT) e auto-hospedável**.

Você usa seus próprios tokens — de provedores gratuitos ou pagos — ou roda
**100% offline com Ollama**. Cada pessoa da casa tem sua própria conta, seu
próprio progresso e sua própria chave.

> **Estado atual:** landing concluída e **Fases 1, 2 e 3 concluídas**: identidade,
> convites, papéis `owner`/`member`, onboarding, BYOK (chave por usuário,
> criptografada, com teste de conexão e fallback) e **conteúdo versionado**
> (trilha com pré-requisitos, lições, exercícios, glossas por idioma da interface
> e baralhos oficiais). Há telas de login, convite, onboarding, área inicial,
> `/curriculum` e `/providers`; o player de lições com IA entra na Fase 4.

## Por que existe

Aprender idioma custa caro justamente para quem mais precisa. O Tangerine Talk
não vende assinatura: o projeto é o software, e o custo é o que você já paga (ou
não paga) pelo provedor de IA que escolher.

## Stack

| Camada | Tecnologia |
|---|---|
| Front (landing + app) | Next.js 14 · React 18 · TypeScript · Tailwind v3 · Framer Motion · GSAP · Lenis |
| Backend | FastAPI · Python 3.12 · SQLAlchemy async · Alembic |
| Banco | MySQL 8.4 |
| Vetorial (RAG) | Qdrant (Fase 6: índice derivado, sync via outbox) |
| Cache/fila | Redis (opcional) |
| Infra | Docker Compose |

## Rodando

### Front (landing + app)

```bash
npm install
npm run dev     # http://localhost:3000
```

Rotas: `/` (landing), `/login`, `/cadastro`, `/convite/{token}`, `/onboarding`,
`/app`, `/curriculum` e `/providers`. As quatro últimas exigem sessão; o
middleware redireciona para o login.

### Backend + banco

```bash
cp .env.example .env          # preencha as senhas e APP_SECRET_KEY
docker compose up -d --build  # api em :8010, mysql em 127.0.0.1:3310
docker compose exec api alembic upgrade head
docker compose exec api python -m app.cli create-owner \
  --email voce@exemplo.com --name "Seu Nome" --generate
curl http://localhost:8010/ready
```

O `--generate` cria e mostra a senha **uma única vez**. Sem ele, o comando pede
a senha no terminal. Não existe usuário nem senha padrão.

Convites para outras pessoas da casa:

```bash
docker compose exec api python -m app.cli invite --email pessoa@exemplo.com
```

Sem SMTP configurado, o link aparece no terminal para você enviar manualmente.
Com SMTP, o owner também pode gerar convites por `POST /invites`.

### Banco: local x produção

O schema é criado **somente pelas migrações Alembic**. A aplicação nunca cria
tabelas em runtime e não exige permissões de DDL no dia a dia — apenas no
momento do `upgrade`.

- **Local:** `docker compose up -d --build` sobe o MySQL em `127.0.0.1:3310`
  com as credenciais de exemplo do `.env.example`. A API fala com `mysql:3306`
  pela rede interna do Compose.
- **Produção com MySQL existente:** defina `DATABASE_URL` no `.env` apontando
  para o seu servidor e use o override, que remove a dependência do banco local:

  ```bash
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build api
  docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api alembic upgrade head
  docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api \
    python -m app.cli create-owner --email voce@exemplo.com --name "Seu Nome" --generate
  ```

  O **banco lógico** precisa existir antes (`CREATE DATABASE tangerine CHARACTER
  SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;`). Tabelas, colunas e índices vêm das
  migrações. Não é preciso informar credenciais ao projeto — elas ficam só no
  `.env` do servidor, fora do Git.

Além do owner e dos convites, criados pela CLI, o conteúdo oficial entra por
seed versionado e **nunca automático** (ver "Conteúdo e trilha" abaixo).

### Conteúdo e trilha (Fase 3)

O conteúdo oficial é **código versionado** (`api/app/content/seed.py`), aplicado
ao MySQL por migração (`0004`) e seed explícito — nunca em runtime, nunca por
upload. O seed é idempotente: rodar de novo não duplica nada.

```bash
docker compose exec api python -m app.cli seed-content
```

O primeiro conteúdo é espanhol A1: 2 unidades, 3 lições, 10 itens, 8 exercícios
e 1 deck oficial. Unidades e lições são publicadas por `is_published`; uma
unidade só abre quando **todas** as lições da anterior foram concluídas. O XP da
lição é creditado uma vez (reconcluir não duplica) e o progresso é por usuário.

As frases ficam sempre no **idioma estudado**. As glossas são resolvidas pelo
`ui_language` na ordem: locale exato → mesma base BCP-47 → `pt-BR` → primeiro
disponível. Assim, a mesma lição atende interface em pt-BR ou en-US sem traduzir
a frase avaliada.

| Rota | O que faz |
|---|---|
| `GET /curriculum/languages` | idiomas que têm conteúdo publicado |
| `GET /curriculum?target_language=es` | unidades, lições e status (`locked`, `available`, `completed`) |
| `GET /curriculum/units/{id}` | detalhe da unidade (403 se bloqueada) |
| `GET /curriculum/lessons/{id}` | itens com glosa + exercícios (403 se bloqueada) |
| `POST /curriculum/lessons/{id}/complete` | registra conclusão e XP |
| `GET /decks?target_language=es` | baralhos oficiais do idioma |
| `GET /decks/{id}` | cartões com glosas no idioma da interface |

O progresso de lição entra em `GET /me/export` e é apagado em `DELETE /me`.
A tela `/curriculum` mostra a trilha, uma prévia da lição e os baralhos; o
player completo (fala, escuta, escrita e testes com IA) é a Fase 4.

### Onboarding (6 passos)

Na primeira entrada, o usuário passa por: (1) idioma da interface — `pt-BR` ou
`en-US`; (2) **servidor de inferência** — provedor principal (`groq`,
`ollama_cloud` ou `openrouter`), modelo e ordem de fallback; (3) idiomas que
quer estudar — seleção livre entre inglês, chinês, espanhol, italiano,
francês, alemão, coreano, japonês e português brasileiro; (4) origem do programa
— 10 temas padrão (viagem, casa com família, trabalho, saúde, compras, comida,
escola, tecnologia, lazer, emergências) ou importação de currículo (em breve);
(5) faixa de nível — `A1/A2`, `B1/B2`, `C1/C2` ou "não sei nada!"; (6) meta
diária e resumo. Tudo é gravado no MySQL e devolvido em `GET /me/export`.

A escolha do provedor define a **ordem da cadeia de fallback** usada pelo
tutor (`resolve_chain`): o provedor principal vem primeiro, depois os
fallbacks na ordem escolhida e, por último, a ordem padrão do catálogo
(`groq → ollama_cloud → openrouter → ollama`). Provedor sem credencial
cadastrada simplesmente não entra na cadeia.

### Identidade e multiusuário

- `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `POST /auth/register`
- `POST /auth/register-public` — cadastro aberto (nome, e-mail e senha)
- `GET /me`, `PATCH /me`, `POST /me/password`, `GET /me/export`, `DELETE /me`
- `POST /me/onboarding` — idioma da interface, idiomas estudados, faixa de nível,
  origem do programa (currículo ou temas), meta diária e escolha do provedor
  de inferência (principal, modelo e fallbacks)
- `GET /members`, `POST /invites`, `GET /invites`, `DELETE /invites/{id}` (só owner)

AccessToken JWT curto (15 min) e refresh opaco (30 dias), ambos em cookies
`httpOnly` + `SameSite=Lax` + `Secure` fora do dev. O refresh é **rotacionado** a
cada uso e revogado no logout. Trocar a senha encerra todas as sessões.

A senha tem **mínimo de 12 caracteres** (validado no front e no back). O
cadastro aberto (`/cadastro` → `POST /auth/register-public`) cria a conta e já
inicia a sessão; o fluxo por convite continua existindo em `/convite/{token}`.

O front encaminha `/api/*` para a API (`next.config.mjs`), então o navegador
fala sempre com a mesma origem — sem CORS e sem token em `localStorage`.

### Idiomas

A aplicação tem **dois eixos independentes**:

- `ui_language` — idioma da interface (textos, instruções, glossas, feedback).
  Nasce em `pt-BR`, oferece `en-US` e aceita qualquer código BCP-47 adicionado
  depois. Fallback técnico: sempre `pt-BR`.
- `target_language` — idioma estudado, escolhido no onboarding. Qualquer um:
  japonês, alemão, coreano etc. A frase avaliada permanece nesse idioma.
- `study_languages` — lista de idiomas que o usuário quer estudar (multi-seleção
  no onboarding: inglês, chinês, espanhol, italiano, francês, alemão, coreano,
  japonês e português brasileiro). `target_language` guarda o primeiro da lista
  e continua sendo o idioma usado nas trilhas.
- `level_band` — faixa de nível escolhida: `A1_A2`, `B1_B2`, `C1_C2` ou `NONE`
  ("não sei nada!").
- `program_source` / `program_topics` — como o programa foi montado: `topics`
  (temas padrão selecionados) ou `curriculum` (currículo importado).
- `inference_provider` / `inference_fallbacks` — provedor principal e ordem de
  fallback escolhidos no onboarding (`groq`, `ollama_cloud`, `openrouter`).
  O modelo escolhido fica em `settings.inference_model`.

Se as bases forem iguais (ex.: interface `en-US` estudando `en-GB`), o exercício
é **monolingual** — sem tradução, foco em leitura, gramática e pronúncia.

Para adicionar um idioma à interface, crie `lib/i18n/locales/<locale>.ts` com as
mesmas chaves de `pt-BR.ts` e registre-o em `AVAILABLE_LOCALES` (`lib/i18n/index.ts`).

### Front em container

```bash
docker compose --profile web up -d --build   # http://localhost:3110
```

> ⚠️ **Não rode `npm run build` com o `npm run dev` ativo.** Os dois escrevem em
> `.next` e o build apaga o CSS do dev (o site carrega sem estilo). Se acontecer:
> pare o dev, `rm -rf .next`, `npm run dev`, `Ctrl+Shift+R`.

### Verificações

```bash
npx tsc --noEmit                      # front
cd api && uv run pytest -q            # backend (57 testes)
cd api && uv run ruff check . && uv run mypy app
```

## Estrutura

```
app/
  (marketing)/    landing
  (auth)/         login, cadastro e convite
  (app)/          onboarding, /app, /curriculum e /providers
  layout.tsx      locale vindo do cookie + LocaleProvider
middleware.ts     portão de UX para /app, /onboarding, /curriculum e /providers
components/       landing, formulários, LocaleSwitcher, wizard, Provider/CurriculumPanel
lib/i18n/         dicionários pt-BR/en-US e resolução com fallback
lib/api.ts        fetch same-origin com refresh automático
api/
  app/auth/       login, refresh, logout, convites, cookies e dependências
  app/users/      perfil, onboarding, membros, convites, export e exclusão
  app/i18n.py     normalização BCP-47 e modo monolingual/bilingual
  app/providers/  catálogo, criptografia de chave, fallback e rotas BYOK
  app/content/    seed versionado, esquemas e rotas de trilha/decks
  app/tutor/      chat, correção, TTS/STT com cadeia BYOK e fallback
  app/models/     usuário, sessão, convite, credencial, conteúdo (UUIDv7 em BINARY(16))
  app/security/   Argon2id, JWT/refresh, limite de tentativas e Fernet
  alembic/        0001 identidade · 0002 idiomas · 0003 BYOK · 0004 conteúdo ·
                  0005 gamificação · 0006 decks/outbox · 0007 onboarding v2 ·
                  0008 escolha de provedor de inferência
  tests/          57 testes, incluindo isolamento entre usuários
docs/             produto, arquitetura, referências, catálogo de efeitos
public/           mascote
docker-compose.yml
web.Dockerfile
```

## Provedores de IA (BYOK)

Cada membro cadastra **a própria** chave em `/providers`. Ela é cifrada em repouso
com Fernet (chave derivada de `APP_SECRET_KEY`) e descriptografada só no momento
da chamada, no servidor. A API devolve apenas `key_hint` (`sk-…a1b2`) e metadados:
nem a chave, nem o cifrado aparecem em resposta, log, exportação ou mensagem de erro.

Provedores disponíveis agora (todos com transporte OpenAI-compatible):

| Slug | Chave | Uso |
|---|---|---|
| `groq` | sim | chat/stream, correção estruturada e STT — primeiro da cadeia |
| `ollama_cloud` | sim | chat/stream/correção, TTS, STT — segundo da cadeia |
| `openrouter` | sim | chat/stream/correção, embeddings, TTS, STT — terceiro da cadeia |
| `ollama` | não | local, sem nuvem; última opção da cadeia |

Endpoints (todos exigem sessão e filtram por `user_id`):

| Rota | O que faz |
|---|---|
| `GET /me/providers` | credenciais + catálogo + ordem de fallback |
| `POST /me/providers` | cadastra (uma credencial por provedor) |
| `PATCH /me/providers/{provider}` | troca chave/modelo/URL ou ativa/desativa |
| `DELETE /me/providers/{provider}` | remove |
| `POST /me/providers/{provider}/test` | chamada mínima de chat; status `ok`, `invalid_key`, `quota`, `provider_error` ou `network` |
| `GET /me/providers/route?task=chat` | mostra a cadeia planejada para a tarefa, sem chaves |

A rota por tarefa (`chat`, `feedback`, `correction`, `embedding`, `tts`, `stt`) filtra
por capacidade. `OFFLINE_MODE=1` remove os provedores em nuvem da cadeia e deixa
somente o Ollama local; `OLLAMA_BASE_URL` define o endpoint dele (o sufixo `/v1` é
acrescentado se faltar). A ordem `Groq → Ollama Cloud → OpenRouter → Ollama` é fixa
no catálogo, não vem do cliente.

> Em **dev sem `.env`**, `APP_SECRET_KEY` é efêmera: ao reiniciar a API, as chaves
> salvas ficam ilegíveis e precisam ser cadastradas de novo. Em produção a chave é
> obrigatória e estável. Trocar a chave mestra também invalida as credenciais.

### Tutor de IA (Fase 4)

A chave nunca sai do servidor: a cadeia BYOK é resolvida e chamada aqui.
Em caso de falha de todos os provedores, devolvemos status/aviso para a UI.

Endpoints (exigem sessão):

| Rota | O que faz |
|---|---|
| `POST /tutor/chat` | chat livre com tutor (task: chat/feedback/correction) |
| `POST /tutor/correct` | corrige resposta do aluno vs esperada (JSON `{correct, feedback}`) |
| `POST /tutor/tts` | síntese de fala → base64 audio |
| `POST /tutor/stt` | transcrição de áudio (base64) |
| `POST /tutor/stt/upload` | transcrição via upload multipart |

O player de lição (`/lesson/{id}`) consome essas rotas para exercícios de
fala, escuta, escrita e testes, com fallback automático entre provedores.

### Gamificação (Fase 5)

XP, streak, SRS, selos, ligas semanais e missões diárias.

Endpoints (exigem sessão):

| Rota | O que faz |
|---|---|
| `GET /gamification` | resumo completo (XP, level, streak, badges, liga, missões) |
| `GET /gamification/streak` | histórico de streak (últimos N dias) |
| `GET /gamification/badges` | selos conquistados |
| `GET /gamification/srs/due` | itens vencidos para revisão (SRS) |
| `POST /gamification/srs/review` | registra revisão de item (qualidade 0-5) |
| `GET /gamification/missions` | missões do dia |
| `GET /gamification/league/current` | status da liga semanal atual |
| `GET /gamification/league/history` | histórico de ligas |
| `GET /gamification/leaderboard` | ranking da liga (top 50) |

Selos: `first_lesson`, `first_deck`, `streak_7/30/100`, `conversations_1/25/50`, `week_league_win`.
SRS usa algoritmo SM-2 simplificado. Liga semanal: Bronze → Silver → Gold → Diamond, com promoção/rebaixamento automático.

### Qdrant — Índice Vetorial (Fase 6)

MySQL é a fonte da verdade; Qdrant é índice derivado e reconstruível via outbox.

| Rota | O que faz |
|---|---|
| `POST /search` | busca híbrida (denso + esparso) com filtros por idioma/nível |
| `POST /search/reindex` | reindexação completa (blue/green) — admin |

Coleção: `content_v1_bge_m3` (BGE-M3, 1024 dims, cosine). Payload indexado: `target_language`, `level`, `item_type`, `item_id`, `deck_id`, `user_id`.
Sincronização: tabela `content_outbox` no MySQL + worker assíncrono → upsert idempotente no Qdrant.
Uso no tutor: grounding de lições (busca itens/regras da lição atual antes de chamar LLM).

## Documentos

| Arquivo | Conteúdo |
|---|---|
| `AGENTS.md` | contexto, convenções e armadilhas do projeto |
| `docs/plano-telas-e-recursos.md` | telas, recursos e priorização do produto |
| `docs/arquitetura-e-tecnologias.md` | stack, serviços, MySQL, Qdrant, provedores e riscos |
| `docs/referencias-engenharia-ia.md` | o que aproveitar dos projetos de estudo |
| `docs/prompt-landing-page-efeitos-premium.md` | catálogo de efeitos (laboratório `/lab`) |

## Segurança e privacidade

Leia o [`SECURITY.md`](./SECURITY.md). Em resumo: nenhum segredo no repositório,
chaves criptografadas em repouso, áudio descartado por padrão, sem telemetria e
verificação de segredos no CI.

## Próximos passos (TODO / Fases 9+)

| Fase | Item | Status | Prioridade |
|------|------|--------|------------|
| 9 | **Performance & Core Web Vitals** | ⬜ TODO | P0 |
| 9 | LCP < 2.5s, CLS < 0.1, INP < 200ms | ⬜ TODO | P0 |
| 9 | Bundle optimization, lazy loading, caching | ⬜ TODO | P1 |
| 9 | **Analytics opt-in** (LGPD-compliant) | ⬜ TODO | P1 |
| 9 | **Testes E2E** (Playwright/Cypress) fluxos críticos | ⬜ TODO | P0 |
| 9 | Login → onboarding → lição → progresso → gamificação | ⬜ TODO | P0 |
| 9 | **Testes unitários** lógica SRS/XP/streak/gamificação | ⬜ TODO | P1 |
| 9 | **Migração copy landing → i18n** (pt-BR/en-US) | ⬜ TODO | P1 |
| 10 | **Conteúdo expandido** | ⬜ TODO | P1 |
| 10 | Mais idiomas/níveis no seed (FR, DE, JA, KO, ZH A1-B2) | ⬜ TODO | P1 |
| 10 | Painel admin de conteúdo (owner) | ⬜ TODO | P1 |
| 10 | Importação de decks (CSV/JSON/Anki) | ⬜ TODO | P2 |
| 10 | Decks próprios do usuário (CRUD) | ⬜ TODO | P1 |
| 11 | **Qdrant** (integração completa) | ⬜ TODO | P1 |
| 11 | Worker outbox sync MySQL → Qdrant | ⬜ TODO | P1 |
| 11 | Grounding do tutor via Qdrant | ⬜ TODO | P1 |
| 11 | Busca híbrida (denso + esparso/BM25) | ⬜ TODO | P1 |
| 11 | Reindexação blue/green | ⬜ TODO | P1 |
| 12 | **TTS/STT dedicado** (Azure/Speechace) | ⬜ TODO | P2 |
| 12 | Pronúncia avançada (sílaba/fonema, IPA) | ⬜ TODO | P2 |
| 12 | Push-to-talk vs full-duplex | ⬜ TODO | P2 |
| 12 | Feedback de fala dentro da conversa | ⬜ TODO | P2 |
| 13 | **Cenários/Roleplay** | ⬜ TODO | P1 |
| 13 | Nivelamento (placement test) | ⬜ TODO | P1 |
| 13 | Caderno de erros/vocabulário | ⬜ TODO | P1 |
| 13 | Progresso detalhado (precisão/tempo por habilidade) | ⬜ TODO | P1 |
| 14 | **Notificações push** (lembrete de prática) | ⬜ TODO | P2 |
| 14 | Compartilhar conquistas | ⬜ TODO | P2 |
| 14 | Ligas com temporadas/recompensas | ⬜ TODO | P2 |
| 15 | **Certificados** | ⬜ TODO | P2 |
| 15 | Múltiplos idiomas simultâneos | ⬜ TODO | P2 |

> **Legenda**: ⬜ TODO = não iniciado | 🟡 WIP = em progresso | ✅ DONE = concluído

---

## Segurança e privacidade
