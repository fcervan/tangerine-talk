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
| Vetorial (RAG) | Qdrant |
| Cache/fila | Redis (opcional) |
| Infra | Docker Compose |

## Rodando

### Front (landing + app)

```bash
npm install
npm run dev     # http://localhost:3000
```

Rotas: `/` (landing), `/login`, `/convite/{token}`, `/onboarding`, `/app`,
`/curriculum` e `/providers`. As quatro últimas exigem sessão; o middleware
redireciona para o login.

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

### Identidade e multiusuário

- `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `POST /auth/register`
- `GET /me`, `PATCH /me`, `POST /me/password`, `GET /me/export`, `DELETE /me`
- `POST /me/onboarding` — idioma da interface, idioma estudado, nível e meta
- `GET /members`, `POST /invites`, `GET /invites`, `DELETE /invites/{id}` (só owner)

AccessToken JWT curto (15 min) e refresh opaco (30 dias), ambos em cookies
`httpOnly` + `SameSite=Lax` + `Secure` fora do dev. O refresh é **rotacionado** a
cada uso e revogado no logout. Trocar a senha encerra todas as sessões.

O front encaminha `/api/*` para a API (`next.config.mjs`), então o navegador
fala sempre com a mesma origem — sem CORS e sem token em `localStorage`.

### Idiomas

A aplicação tem **dois eixos independentes**:

- `ui_language` — idioma da interface (textos, instruções, glossas, feedback).
  Nasce em `pt-BR`, oferece `en-US` e aceita qualquer código BCP-47 adicionado
  depois. Fallback técnico: sempre `pt-BR`.
- `target_language` — idioma estudado, escolhido no onboarding. Qualquer um:
  japonês, alemão, coreano etc. A frase avaliada permanece nesse idioma.

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
  (auth)/         login e convite
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
  alembic/        0001 identidade · 0002 idiomas · 0003 BYOK · 0004 conteúdo
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

## Contribuindo

Veja o [`CONTRIBUTING.md`](./CONTRIBUTING.md). Projeto licenciado sob [MIT](./LICENSE).
