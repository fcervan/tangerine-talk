# Tangerine Talk

Tutor de idiomas com IA, **gratuito, open source (MIT) e auto-hospedável**.

Você usa seus próprios tokens — de provedores gratuitos ou pagos — ou roda
**100% offline com Ollama**. Cada pessoa da casa tem sua própria conta, seu
próprio progresso e sua própria chave.

> **Estado atual:** landing concluída e **Fase 1 (identidade e multiusuário)
> concluída**: API com login, convites, papéis `owner`/`member`, perfis e
> migração no MySQL. O app já tem telas de login, convite, onboarding e uma
> área inicial; o motor de lições ainda está em construção.

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

Rotas: `/` (landing), `/login`, `/convite/{token}`, `/onboarding` e `/app`.
As duas últimas exigem sessão; o middleware redireciona para o login.

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

Hoje o único "dado necessário" criado à mão é o owner e os convites, pela CLI.
O currículo e os decks oficiais entram na Fase 3, também por migração/seed
versionado.

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
cd api && uv run pytest -q            # backend (28 testes)
cd api && uv run ruff check . && uv run mypy app
```

## Estrutura

```
app/
  (marketing)/    landing
  (auth)/         login e convite
  (app)/          onboarding e área autenticada (/app)
  layout.tsx      locale vindo do cookie + LocaleProvider
middleware.ts     portão de UX para /app e /onboarding
components/       landing + formulários, LocaleSwitcher e wizard
lib/i18n/         dicionários pt-BR/en-US e resolução com fallback
lib/api.ts        fetch same-origin com refresh automático
api/
  app/auth/       login, refresh, logout, convites, cookies e dependências
  app/users/      perfil, onboarding, membros, convites, export e exclusão
  app/i18n.py     normalização BCP-47 e modo monolingual/bilingual
  app/models/     usuário, sessão e convite (UUIDv7 em BINARY(16))
  app/security/   Argon2id, JWT/refresh e limite de tentativas
  alembic/        0001 identidade · 0002 idiomas e onboarding
  tests/          28 testes, incluindo isolamento entre usuários
docs/             produto, arquitetura, referências, catálogo de efeitos
public/           mascote
docker-compose.yml
web.Dockerfile
```

## Provedores de IA

As chaves são **por usuário** e ficam criptografadas no banco — nunca em `.env`,
nunca no Git, nunca em log. O app aceita qualquer endpoint compatível com OpenAI
(OpenAI, DeepSeek, GLM, Qwen/DashScope, Groq, OpenRouter, Ollama) e tem adaptador
para Anthropic.

Modo offline (`OFFLINE_MODE=1`) força Ollama e desliga o que depende de nuvem.

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
