# Tangerine Talk — Arquitetura e tecnologias

> Documento técnico em nível de **decisão**, não de implementação.
> Complementa `docs/plano-telas-e-recursos.md` (produto) — este cobre stack, serviços e implicações.
> Status: decisões fechadas em 2026-11; execução em andamento (Fases 0, 1, 2 e 3 concluídas).

## Decisões tomadas

| Decisão | Escolha |
|---|---|
| Natureza do projeto | **Público, gratuito e open source (MIT)**; sem cobrança de qualquer tipo |
| Front e backend separados | Sim — Next na raiz, FastAPI em `api/` |
| Containerização | Docker Compose (todos os serviços) |
| Backend | FastAPI (Python 3.12) |
| Front | Next.js 14 (stack atual) |
| Banco relacional | **MySQL 8.4** |
| Vetorial / RAG | **Qdrant** |
| Chaves de IA | **Por usuário (BYOK)**, criptografadas no banco |
| Multiusuário | **Sim** — `owner` + membros da instância, dados isolados |
| Cadastro | Convite por e-mail (SMTP opcional: sem SMTP, o owner copia o link) |
| Pagamento | **Não existe** — nenhum módulo de billing |
| Offline | **Ollama**, com degradação explícita de recursos |

---

## 1. Stack consolidada

| Camada | Escolha | Observação |
|---|---|---|
| Front | Next.js 14 (App Router) | landing + app no mesmo projeto, route groups |
| Backend | FastAPI + Python 3.12 | monolito modular |
| Banco | **MySQL 8.4 LTS** (InnoDB) | `utf8mb4` obrigatório |
| Vetorial | **Qdrant** | índice derivado, nunca fonte da verdade |
| Cache/fila | Redis | **opcional** — sem ele, fila em processo e ranking no MySQL |
| Storage | disco local (`./data/storage`) | S3 é opcional, não requisito |
| Provedores de IA | qualquer endpoint compatível com OpenAI + Anthropic | chaves por usuário |
| Proxy | Caddy / Nginx | TLS, same-origin |
| Orquestração | docker compose | sem Kubernetes nesta fase |

### Serviços no compose

```
web (Next, raiz)  ──/api──→  api (FastAPI, api/)
                                ├─→ mysql
                                ├─→ qdrant        (opcional em modo local)
                                ├─→ redis         (opcional)
                                ├─→ data/storage  (áudio local, com TTL)
                                └─→ provedores    (nuvem ou Ollama)
```

Portas no host: `3110` web, `8010` api, `127.0.0.1:3310` mysql (evita conflito com outros projetos).

---

## 2. Front-end

- **Route groups**: `app/(marketing)` (landing, legal — SSG) e `app/(app)` (autenticado, client-side).
- **Proxy same-origin**: `rewrites` de `/api/*` → FastAPI. Resolve CORS e permite cookie `httpOnly`.
- **Layout do repositório**: Next na raiz, backend em `api/`. Um único repositório, dois apps.
- **Estado**: TanStack Query (servidor) + Zustand (UI local) + react-hook-form/zod.
- **UI**: Tailwind v3 + Framer Motion (como está) + Radix UI para primitivas acessíveis.
- **Versões**: manter Next 14 e Tailwind 3 nesta fase; upgrade depois, isolado.

---

## 3. Backend (FastAPI)

| Peça | Escolha |
|---|---|
| Servidor | Uvicorn (Gunicorn+Uvicorn em prod) |
| Validação/config | Pydantic v2 + pydantic-settings |
| ORM | SQLAlchemy 2.0 **async** + **asyncmy** |
| Migrations | Alembic (`batch_alter_table` obrigatório no MySQL) |
| Auth | próprio: Argon2id + JWT curto + refresh opaco rotacionado em cookie `httpOnly` (Fase 1) |
| Filas | ARQ (Redis) |
| Rate limit | slowapi + Redis |
| Streaming LLM | SSE (`StreamingResponse`) |
| Contratos | OpenAPI → `openapi-typescript` |

**Regra**: monolito modular (`auth/`, `users/`, `providers/`, `content/`, `learning/`, `srs/`, `tutor/`, `gamification/`, `search/`). Não microserviços. **Não existe módulo de billing.**

O FastAPI é o **único** dono da identidade — o Next apenas repassa cookies. Não usar Auth.js em paralelo.

### Identidade implementada (Fase 1)

| Peça | Implementação |
|---|---|
| Tabelas | `users`, `auth_sessions`, `invites` (migração `0001`) |
| Senha | Argon2id (`argon2-cffi`); verificação fictícia quando o e-mail não existe |
| Access token | JWT HS256, 15 min, assinado com `APP_SECRET_KEY` (epoch UTC explícito) |
| Refresh token | opaco de 48 bytes; só o SHA-256 vai ao banco; 30 dias; rotação a cada uso |
| Cookies | `tt_access` / `tt_refresh`, `httpOnly`, `SameSite=Lax`, `Secure` fora do dev |
| Convite | token de uso único, 7 dias, enviado por SMTP se configurado; senão o owner copia o link |
| Papéis | `owner` (criado por CLI, sem senha padrão) e `member` (por convite) |
| Isolamento | `GET /me` só lê o próprio usuário; endpoints de membros/convites exigem `owner` |
| Privacidade | `GET /me/export` e `DELETE /me` com confirmação de senha; logs não registram credenciais |
| Defesa extra | middleware de `Origin` para escrita; limite de 10 logins falhos por 15 min por IP+e-mail |

Testes: 28 casos, incluindo "membro não acessa `/members`", rotação/revogação de
refresh e isolamento do onboarding entre usuários.

### Idiomas e onboarding (Fase 1)

| Eixo | Campo | Regra |
|---|---|---|
| Interface | `ui_language` | BCP-47 em `VARCHAR(35)`; padrão `pt-BR`; `en-US` oferecido; aberto a novos locales |
| Estudo | `target_language` | BCP-47, nullable antes do onboarding; qualquer idioma |
| Modo | calculado | Mesma base nos dois lados ⇒ `monolingual`; senão `bilingual` |
| Preferências | `settings` | `level` (A1–C2) e `daily_goal_minutes` (5–180) |
| Estado | `onboarding_completed` | Booleano; o front redireciona para `/onboarding` enquanto for falso |

Rotas: `POST /me/onboarding` (idempotente) e `PATCH /me` (troca **só** a interface).
Migração `0002`. No front, `lib/i18n/` com dicionários `pt-BR` (referência de
tipagem) e `en-US`; resolução `exato → mesma base → pt-BR`. Nenhum fallback para
inglês. `lib/api.ts` renova o access token automaticamente ao receber 401.

O middleware do Next é apenas portão de UX (`tt_access` presente); a autoridade
continua sendo o FastAPI, que valida JWT e papéis em cada rota.

---

## 4. MySQL — implicações práticas (o que muda em relação a Postgres)

| Tema | Decisão / cuidado |
|---|---|
| Versão | **MySQL 8.4 LTS**, InnoDB, `utf8mb4` |
| Driver | `asyncmy` (`mysql+asyncmy://`) — mais rápido que `aiomysql` |
| IDs | **UUIDv7 em `BINARY(16)`** com `UUID_TO_BIN`/`BIN_TO_UUID`. `CHAR(36)` desperdiça índice; v7 evita fragmentação de B-tree |
| Datas | `DATETIME(6)` em **UTC** (app-side). Evitar `TIMESTAMP` (limite 2038 e conversão de fuso pelo servidor) |
| Fuso | `SET time_zone = '+00:00'` na conexão |
| Collation | default `utf8mb4_0900_ai_ci`; **colunas de resposta no idioma-alvo usam `utf8mb4_0900_as_cs`** (sensível a acento e caixa) — crítico para corrigir "cómo" vs "como" |
| DDL | **sem transação**: migration que falha deixa estado parcial → migrations pequenas, testadas em cópia, com backup antes |
| Alterações | Alembic `batch_alter_table` para mudanças de coluna/índice |
| Isolamento | considerar `READ COMMITTED` para reduzir gap locks em filas/leaderboard |
| Concorrência | `SELECT ... FOR UPDATE SKIP LOCKED` para pegar itens de SRS/lição sem travar |
| JSON | usar para payload de exercício e metadados; índices funcionais (8.0.13+) e multivalorados (8.0.17+) quando necessário; não abuse |
| Consultas | `WITH RECURSIVE` (árvore de habilidades) e window functions (`RANK()`) são suportados |
| Constraints | `CHECK` é aplicado desde 8.0.16 |
| Busca textual | `FULLTEXT` InnoDB com parser `ngram` para conteúdo CJK; para o resto, buscar via Qdrant |
| Backup | `mysqldump`/`mysqlsh` + binlog; testar restore |

**O que perdemos do Postgres** (e como cobrir): pgvector → Qdrant; `JSONB` com GIN → JSON + índices funcionais; tipos ricos/arrays → tabelas filhas ou JSON; DDL transacional → disciplina de migration.

---

## 5. Qdrant — papel e regras

**Usos no produto**
1. **Grounding do tutor**: recuperar itens/regras do currículo da lição atual para o tutor não inventar.
2. **RAG de conteúdo**: explicar gramática, dar exemplos coerentes com o nível.
3. **Busca semântica interna**: vocabulário, erros recorrentes, duplicatas.
4. **Apoio ao painel de conteúdo**: "o que já cobre este tema?".

**Não usar para**: estado de SRS, progresso, XP, ranking, sessões — tudo isso fica no MySQL.

**Regras**
- MySQL é a fonte da verdade; Qdrant é **índice derivado e reconstruível**.
- Sincronização por **outbox** (`content_outbox` no MySQL) + worker → upsert idempotente. Point ID = UUID do item.
- **Coleção por modelo de embedding** (ex.: `content_v1_bge_m3`). Trocar modelo = nova coleção + reindex em paralelo (blue/green), nunca `ALTER` destrutivo.
- Payload com filtros indexados: `language`, `level`, `course_id`, `node_id`, `item_type`, `embedding_version`.
- Distância `cosine`; HNSW com defaults no início.
- **Híbrido** (denso + esparso/BM25) via Query API quando a busca lexical importar (termos exatos, nomes próprios).
- Snapshot antes de reindexação; snapshot + dump do MySQL no mesmo job de backup.
- Em testes: Qdrant em memória ou container efêmero.

**Decisão pendente**: modelo de embedding. Recomendação — **BGE-M3** (multilíngue, denso+esparso, bom em pt-BR) self-hosted, ou `text-embedding-3-small` se priorizar simplicidade e custo previsível. A dimensão é fixada na criação da coleção.

---

## 6. IA e provedores (BYOK)

O produto é gratuito; o custo de IA é do usuário, com a chave dele. Por isso a
camada de provedores é **configuração**, não código.

### Como funciona

| Peça | Decisão | Estado |
|---|---|---|
| Transporte | **OpenAI-compatible** (Groq, Ollama Cloud, OpenRouter, Ollama); adaptador Anthropic planejado | parcial |
| Escopo da chave | **por usuário** (cada membro usa a própria); o owner não vê a chave de ninguém | feito |
| Armazenamento | Fernet/`cryptography`, chave derivada de `APP_SECRET_KEY`, `provider_credentials` (migração `0003`) | feito |
| Exposição | a API **nunca** devolve a chave nem o cifrado; só `sk-…a1b2` e metadados | feito |
| Capacidades | catálogo estático: `chat`, `stream`, `structured`, `embeddings`, `tts`, `stt` (`vision` reservado) | feito |
| Roteamento | `GET /me/providers/route?task=…` filtra por capacidade; tarefas `chat`, `feedback`, `correction`, `embedding`, `tts`, `stt` | feito |
| Fallback | cadeia fixa Groq → Ollama Cloud → OpenRouter → Ollama; **consumir** a cadeia com retry e aviso de quota é trabalho do motor de lição (Fase 4) | cadeia pronta |
| Teste | `POST /me/providers/{provider}/test` faz uma chamada mínima e devolve status estável; corpo do erro do provedor nunca vaza | feito |
| Offline | `OFFLINE_MODE=1` remove nuvens da cadeia; `OLLAMA_BASE_URL` define o endpoint local | feito |

A chave mestra é estável em produção e obrigatória. Se `APP_SECRET_KEY` mudar, as
credenciais cadastradas ficam ilegíveis e o usuário as cadastra novamente — o
erro é explícito e não contém segredo. Em dev sem `.env`, a chave é efêmera e o
mesmo comportamento acontece a cada reinício da API.

### Matriz de capacidades (referência)

| Provedor | chat | embeddings | tts | stt | pronúncia |
|---|---|---|---|---|---|
| OpenAI | ✓ | ✓ | ✓ | ✓ | — |
| Anthropic | ✓ | — | — | — | — |
| DeepSeek | ✓ | — | — | — | — |
| GLM (Zhipu) | ✓ | ✓ | ✓ | ✓ | — |
| Qwen (DashScope) | ✓ | ✓ | ✓ | ✓ | — |
| Groq | ✓ | — | — | ✓ | — |
| OpenRouter | ✓ (agrega) | ✓ | — | — | — |
| Ollama | ✓ | ✓ | parcial | parcial | — |
| Azure Speech | — | — | ✓ | ✓ | **✓** |

### Áudio

| Função | Nuvem | Offline |
|---|---|---|
| TTS | Azure Neural / OpenAI TTS | Piper / Kokoro |
| ASR | Deepgram / Whisper API | `faster-whisper` |
| Pronúncia por palavra | **Azure Pronunciation Assessment** | **sem equivalente confiável** |

**Degradação offline da Fala:** vira "ouça o modelo → grave → ouça você → repita",
sem nota. Alinhamento forçado local (wav2vec2) fica como opção futura, não como requisito.

**MVP é push-to-talk** (grava → envia → transcreve → responde). Full-duplex (WebRTC/LiveKit) fica para v2.

**Alerta de escopo**: a cobertura de pronúncia é bem menor que "50+ idiomas". Os idiomas de lançamento são limitados por ASR + PA + TTS.

---

## 7. Lógica de domínio

- **SRS**: **FSRS** (`py-fsrs`), estado por item em `user_item_state`.
- **XP/streak**: eventos append-only (`xp_events`, `practice_days`), agregados derivados.
- **Leaderboard**: Redis sorted sets por semana + job de fechamento; MySQL com `RANK()` como fallback/histórico.
- **Liga com base pequena**: bots/ligas simuladas até haver massa crítica (decisão de produto).
- **Áudio**: processar e descartar por padrão (`AUDIO_RETENTION_DAYS=0`); guardar só com opt-in.
- **Uso**: limite por usuário configurável para não queimar a cota de uma chave compartilhada.

---

## 8. Docker

**Dev**: `mysql` e `api` sobem por padrão; `web` fica no profile `web` para não conflitar com o `npm run dev` local; `qdrant`, `redis` e `ollama` entram quando a fase exigir.

**Prod**: imagens multi-stage, `caddy` com TLS, sem bind mounts, migrations como job separado.

Ordem: `mysql` saudável → `api` (migrate) → `web` → `caddy`. Seed de conteúdo explícito, nunca automático.

---

## 9. Qualidade

- **Backend**: pytest + pytest-asyncio; testes de FSRS, XP, streak, autorização e sincronização com Qdrant.
- **Front**: Vitest + Testing Library; Playwright nos fluxos críticos.
- **Observabilidade**: Sentry (front+back), OpenTelemetry, Langfuse.
- **CI**: ruff + mypy (api), eslint + tsc (web), testes, build das imagens.

---

## 10. Riscos técnicos

1. **Pronúncia por palavra** — protótipo com Azure antes das telas; offline degrada.
2. **Latência do tutor** — streaming real de tokens + modelo rápido.
3. **Quota do provedor do usuário** — erro de quota precisa ser tratado, não mascarado.
4. **Conteúdo** — maior esforço contínuo; painel interno cedo.
5. **Migrations no MySQL** — sem DDL transacional; disciplina obrigatória.
6. **Sincronização MySQL → Qdrant** — projetar reindexação idempotente desde o início.
7. **Vazamento de chave** — criptografia, mascaramento e testes dedicados.

---

## 11. Fora de escopo agora

Kubernetes · microserviços · GraphQL · app nativo · Kafka · feature flags SaaS · CDN própria.

---

## 12. Repositório público e privacidade

Tudo que entra no Git é público. Regras:

- `.env`, chaves, dumps, áudios e volumes **fora** do repositório (ver `.gitignore`).
- `gitleaks` no CI, sobre o histórico completo.
- Chaves de provedor criptografadas em repouso; nunca em log, resposta ou backup em claro.
- Áudio descartado por padrão; retenção só com opt-in explícito.
- Sem telemetria por padrão.
- Fixtures, seeds e testes com dados **sintéticos**.
- Excluir conta apaga dados, áudios e registros; exportação sob demanda.
- O `owner` **não** lê conversas dos membros — apenas agregados.

## 13. Decisões pendentes

1. **Voz**: push-to-talk no MVP (recomendado) ou full-duplex já?
2. ~~Idiomas de lançamento~~ **Fechado:** interface pt-BR + en-US (extensível); idioma-alvo qualquer um por BCP-47. Currículo oficial entra aos poucos.
3. **Embedding**: BGE-M3 self-hosted ou `text-embedding-3-small`?
4. **Offline na Fala**: aceitar sem score (recomendado) ou investir em alinhamento local?
5. **Landing**: trocar "Preços/upgrade" por "gratuito e open source" antes de publicar?
6. ~~BYOK~~ **Fechado e implementado na Fase 2:** chave por usuário cifrada com
   Fernet, catálogo com quatro provedores, cadeia fixa de fallback, teste de
   conexão e modo offline. Motor de lição consome a cadeia com retry e aviso
   de quota (Fase 4).
7. ~~Conteúdo~~ **Fechado e implementado na Fase 3:** MySQL é a fonte da verdade;
   seed versionado e idempotente (nunca em runtime), unidade só abre após todas
   as lições anteriores, XP creditado uma vez, glossas por `ui_language` com
   fallback pt-BR e frase sempre no idioma alvo. Qdrant segue como índice
   derivado, sem uso no MVP. Pendem decks próprios e importação.
8. ~~Motor de lição~~ **Fechado e implementado na Fase 4:** player de lição com
   4 habilidades (fala, escuta, escrita, testes), tutor de IA server-side
   (chat, correção, TTS/STT) com cadeia BYOK + fallback, pronúncia via Web
   Speech API base. Pendem: provedor TTS/STT dedicado, avaliação de pronúncia
   comparada a referência, full-duplex.
9. ~~Gamificação~~ **Fechado e implementado na Fase 5:** XP, streak (SM-2 + selos
   7/30/100), SRS (SM-2), ligas semanais (Bronze→Silver→Gold→Diamond com
   promoção/rebaixamento), missões diárias (7 tipos). Endpoints completos:
   `/gamification`, `/streak`, `/badges`, `/srs/due`, `/srs/review`, `/missions`,
   `/league/current`, `/league/history`, `/leaderboard`. Selos: first_lesson,
   first_deck, streak_7/30/100, conversations_1/25/50, week_league_win.
