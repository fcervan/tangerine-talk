# Tangerine Talk

Tutor de idiomas com IA, **gratuito, open source (MIT) e auto-hospedável**.

Você usa seus próprios tokens — de provedores gratuitos ou pagos — ou roda
**100% offline com Ollama**. Cada pessoa da casa tem sua própria conta, seu
próprio progresso e sua própria chave.

> **Estado atual:** landing page concluída. O aplicativo está em construção,
> começando pelo backend (`api/`) e pela infraestrutura.

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

### Front (landing)

```bash
npm install
npm run dev     # http://localhost:3000
```

### Backend + banco

```bash
cp .env.example .env          # preencha as senhas e APP_SECRET_KEY
docker compose up -d --build  # api em :8010, mysql em 127.0.0.1:3310
curl http://localhost:8010/health
```

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
cd api && uv run pytest -q            # backend
cd api && uv run ruff check . && uv run mypy app
```

## Estrutura

```
app/              rotas Next (landing)
components/       componentes da landing
lib/              utilitários do front
api/              backend FastAPI (app/, tests/)
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
