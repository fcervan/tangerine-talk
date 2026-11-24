# Referências de Engenharia de IA — o que aproveitar no Tangerine Talk

> Inventário curado dos projetos de estudo locais (Scoras Academy — Engenharia de IA),
> com o que **reaproveitar**, o que **evitar** e como cada padrão se encaixa no produto.
> Complementa `docs/plano-telas-e-recursos.md` (produto) e `docs/arquitetura-e-tecnologias.md` (stack).
> Atualizado em 2026-11-24.

---

## 1. Mapa dos repositórios

| Repositório | Stack / conteúdo | O que ensina | Relevância |
|---|---|---|---|
| `projetos/assistente-suporte` | FastAPI + React/Vite + Qdrant + DuckDB + LangGraph + Docker | arquitetura completa de app com RAG, auth, SSE, testes | ★★★ |
| `projetos/avaliador-vendas` | Python + LangGraph + LLM-as-judge + CI | rubrica, score ponderado, early-exit, 100% coverage | ★★★ |
| `projetos/reforco-langgraph` | LangGraph + Groq | padrões de grafo, gotchas de modelo, testes offline | ★★★ |
| `RAG-Tecnicas-Avancadas` | notebooks + CRAG + GraphRAG + prompt caching | RAG avançado, reranking, híbrido, custo | ★★★ |
| `Curso_Introdutorio_de_Langgraph` | notebooks | base conceitual de grafos, memória, HITL, subgrafos | ★★★ |
| `projetos/docling-service` | FastAPI + Docling + Docker | ingestão de documentos como serviço isolado | ★★ |
| `projetos/dbscope` | MCP + MySQL + segurança | acesso read-only a MySQL, invariantes de segurança | ★★ |
| `SLM` | transformers + peft + limpeza de texto | normalização multilíngue, LoRA/QLoRA, modelos locais | ★★ |
| `Projetos_Praticos_de_IA` | LangGraph + DuckDB + reportlab | NL2SQL, relatórios PDF, observabilidade (AgentOps) | ★★ |
| `Python_Para_Iniciantes_em_IA` | ML clássico + NLP + CUDA | base de ML/NLP | ★ |
| `Fundamentos_de_LLMs`, `Introducao_Aos_LLMs` | notebooks teóricos | transformers, atenção, alucinação | ☆ |
| `questionarios` | quizzes | formato de quiz | ☆ |
| `projetos/efeitos-landing-page` | Next + Framer/GSAP | laboratório de efeitos (mesmo padrão da landing) | ★ |

---

## 2. Padrões reaproveitáveis

### 2.1 LLM com fallback (Groq → Ollama Cloud → OpenRouter)

**Referência:** `projetos/assistente-suporte/api/src/llm_client.py` · `projetos/avaliador-vendas/src/llm_client.py`

- Tenta Groq (latência), depois Ollama Cloud, depois OpenRouter; erro claro se não houver chave.
- Modelos configuráveis por env (`GROQ_MODEL`, etc.), sem hardcode.
- Para o Tangerine: manter a **ordem** e adicionar roteamento por tarefa — modelo rápido para feedback de lição, modelo forte para o tutor.

### 2.2 LLM-as-judge com rubrica + pesos + early-exit

**Referência:** `projetos/avaliador-vendas/src/{rubrics,evaluators,graph}.py`

- Uma rubrica por critério, nota 0–10, **média ponderada**, veredito e feedback textual.
- `early-exit`: se a base falha, não gasta avaliação nas etapas seguintes (economia real de tokens).

**Uso direto no Tangerine:** correção de **escrita livre**, avaliação de **conversa no tutor** e feedback de **lição composta**. É o padrão que a landing já sugere ("corrige e torce por você").

### 2.3 RAG híbrido (denso + BM25 + RRF)

**Referência:** `projetos/assistente-suporte/api/src/{vector_qdrant,embeddings}.py`

- Busca densa ampla (`top_k * 5`) → BM25 sobre o pool → fusão **RRF**.
- Normalização de texto + stemming PT para o lado lexical.
- Expansão de query por glossário do domínio.

**Uso no Tangerine:** grounding do tutor no currículo da lição atual; busca interna de vocabulário.

**Ressalva:** o BM25 ali é em memória, sobre o pool denso — serve para corpus pequeno. Para conteúdo grande, usar **vetores esparsos nativos do Qdrant** (hybrid query) ou `FULLTEXT` do MySQL.

### 2.4 Qdrant: padrão de coleção e payload

**Referência:** `projetos/assistente-suporte/api/src/vector_qdrant.py`

- `VectorParams(size=dim, distance=Distance.COSINE)`, payload com `texto`, `fonte`, `pagina`, `secao`, `doc_id`, `versao_chunk`.
- `collection_exists` antes de criar; função de wipe explícita.

**Melhorias obrigatórias no Tangerine:**
- Point ID **determinístico** (= UUID do item), não `uuid4()` por chunk → permite upsert idempotente.
- Coleção versionada por modelo de embedding (`content_v1_<modelo>`).

### 2.5 Streaming SSE

**Referência:** `projetos/assistente-suporte/api/src/main.py` (`POST /chat/stream`)

- `StreamingResponse(..., media_type="text/event-stream")` com `data:` + `[DONE]`.

**Ressalva importante:** a implementação atual **não faz streaming real** — calcula a resposta inteira e fatia por linha. Para o tutor do Tangerine, usar `astream`/`astream_events` do LangGraph para emitir **tokens** desde o primeiro caractere; é o que sustenta a sensação de "tempo real" prometida no hero.

### 2.6 Auth JWT + papéis

**Referência:** `projetos/assistente-suporte/api/src/auth.py`

- `passlib[bcrypt]` para hash, `python-jose` para JWT, dependências `atual` e `admin`.

**Melhorias no Tangerine:** access token curto + **refresh em cookie `httpOnly`** (não Bearer em localStorage), `pydantic-settings` em vez de `os.getenv` espalhado, e rate limit no login.

### 2.7 Docker Compose multi-serviço

**Referência:** `projetos/assistente-suporte/docker-compose.yml` · `projetos/docling-service/docker-compose.yml`

- Serviços com `container_name`, volume nomeado para estado, `depends_on`, `env_file`, `restart`.
- `profiles` para serviço pesado opcional (docling), publicado só em `127.0.0.1`.
- Limites de memória/CPU (`mem_limit`, `cpus`) no serviço pesado.

**Uso no Tangerine:** mesma estrutura, trocando `duckdb` por `mysql` e adicionando `redis`.

### 2.8 Docling como serviço de ingestão

**Referência:** `projetos/docling-service` (FastAPI, API key SHA-256, rate limit, OCR sob demanda, unload ocioso)

**Uso potencial:** importar material de currículo (PDF/apostila) para o painel de conteúdo. É pesado (~2,7 GB, CPU) — rodar isolado, fora do caminho crítico do app.

### 2.9 dbscope no desenvolvimento

**Referência:** `projetos/dbscope`

MCP read-only para MySQL com invariantes fortes: role de banco read-only + `START TRANSACTION READ ONLY`, parser SQL, redação de credenciais, limites de linhas/bytes, auditoria.

**Uso direto:** como o Tangerine usará MySQL, o dbscope vira a forma segura de o agente inspecionar o banco em dev — sem receber host/senha.

### 2.10 LangGraph: o que já está dominado

**Referência:** `Curso_Introdutorio_de_Langgraph` + `projetos/reforco-langgraph`

Padrões já praticados que servem ao tutor:
- `StateGraph` + `TypedDict` + reducers (`add_messages`, `operator.add`)
- roteadores/condicionais, subgrafos, `Send` map-reduce
- memória (`MemorySaver`), `trim_messages`, resumo de thread (`gerar_resumo` no assistente-suporte)
- **HITL** (`interrupt`, breakpoints, time-travel) → útil para revisão de conteúdo no painel interno
- `astream_events` → token streaming no tutor

### 2.11 Testes e qualidade

**Referência:** `projetos/avaliador-vendas` (CI + 100% cobertura) e `projetos/dbscope` (ruff + `mypy --strict`)

- Testes **mockados** (nenhuma chamada real de API no CI).
- Fallback `FakeMessagesListChatModel` quando não há chave — o projeto nunca "morre" sem credencial.
- `pytest`, `ruff`, `mypy`, GitHub Actions.

**Uso no Tangerine:** adotar os mesmos gates no backend; no front, Vitest + Playwright.

### 2.12 RAG avançado — quando o básico não bastar

**Referência:** `RAG-Tecnicas-Avancadas`

| Técnica | Aplicação no Tangerine |
|---|---|
| **Prompt caching** | cachear o *system prompt* do tutor + currículo da lição → menos custo e latência |
| **Re-ranking** | melhorar os trechos recuperados antes de mandar ao tutor |
| **CRAG (corretivo)** | se a recuperação é fraca, admitir "não sei" / pedir reformulação em vez de alucinar |
| **GraphRAG** | relações entre vocabulário, unidades e erros do aluno (fase futura) |
| **Híbrido denso+esparso** | termos exatos do idioma-alvo (nomes, conjugações) |

### 2.13 Normalização de texto multilíngue (SLM)

**Referência:** `SLM/4.1-*` (unidecode, ftfy, emoji, nltk/spacy)

**Cuidado que vira regra de produto:** remover acento serve para **busca** (BM25), **nunca** para **corrigir resposta**. No Tangerine, "cómo" ≠ "como" na avaliação. Isso conversa direto com a decisão de collation `utf8mb4_0900_as_cs` no MySQL.

### 2.14 Relatórios e observabilidade

- **PDF de progresso** (reportlab, em `Projetos_Praticos_de_IA`) → tela/histórico exportável.
- **AgentOps / tracing** (notebook `AgentOps Com LangGraph`) → trocar por Langfuse no produto.

---

## 3. O que **não** reaproveitar (armadilhas já pagas)

| Item | Por quê |
|---|---|
| **DuckDB com writer único** (`threading.Lock`) | explícito no AGENTS como limitação v1; app multiusuário precisa de MySQL |
| **SSE que fatiа resposta pronta** | não é streaming real; para o tutor precisa de tokens |
| **`uuid4()` como point ID no Qdrant** | reingestão duplica pontos; usar ID determinístico |
| **BM25 em memória sobre o pool** | não escala; usar sparse vectors ou FULLTEXT |
| **JWT em Bearer/localStorage** | XSS; usar cookie `httpOnly` no app |
| **`passlib` + `bcrypt>=4.1`** | quebra o hash; pinar `bcrypt==4.0.1` (ou migrar para `pwdlib`/`argon2`) |
| **`docling` puxando torch CUDA** | instalar torch CPU do índice `whl/cpu` antes do requirements |
| **Groq `gpt-oss` sem `reasoning_effort="low"`** | consome orçamento, `finish_reason: length`, `content` vazio |
| **Chaves em `.env` versionado** | nunca; `.env.example` só com placeholders |
| **MiniLM 384d como embedding padrão** | multilíngue fraco para 50 idiomas; avaliar BGE-M3 |
| **Tokens/cores do `tokens.css` do suporte** | identidade visual é outra; não transplantar |

---

## 4. Lacunas — o que ainda não existe nos estudos

Nenhum projeto cobre, e o Tangerine vai precisar:

1. **Áudio**: ASR, TTS, pronúncia por palavra (Azure/Deepgram), upload e storage.
2. **SRS/FSRS**: agendamento e retenção.
3. **MySQL assíncrono**: SQLAlchemy async + Alembic (dbscope usa PyMySQL síncrono).
4. **Auth no Next**: cookies, middleware, SSR autenticado.
5. **BYOK e privacidade de chaves**: criptografia em repouso, mascaramento, roteamento por provedor.
6. **Multiusuário**: isolamento de dados, convites por e-mail, papéis.
7. **i18n**: conteúdo multilíngue (a landing é pt-BR hardcoded).
8. **Notificações**: e-mail/push.
9. **Gamificação persistida**: XP/streak/ligas além do mock.

---

## 5. Mapa módulo → referência

| Módulo do Tangerine | Base principal | O que copiar |
|---|---|---|
| `auth/` | assistente-suporte `auth.py` | JWT + papéis; evoluir para cookies/refresh |
| `tutor/` | assistente-suporte `graph.py` + reforco-langgraph | grafo, memória, resumo, streaming |
| `tutor/` (grounding) | `vector_qdrant.py` + RAG avançado | híbrido, rerank, CRAG, prompt caching |
| `learning/` (correção) | avaliador-vendas | rubrica + pesos + early-exit |
| `content/` (ingestão) | docling-service | conversão de documentos isolada |
| `search/` | Qdrant + SLM (normalização) | coleção versionada, filtros, normalização |
| `gamification/` | — | sem referência; desenhar do zero |
| `srs/` | — | sem referência; usar `py-fsrs` |
| `providers/` | — | sem referência; desenhar BYOK do zero |
| Infra | assistente-suporte + docling-service | compose, profiles, healthchecks, limites |
| Dev tooling | dbscope | inspeção read-only do MySQL |
| Qualidade | avaliador-vendas + dbscope | CI, ruff, mypy, testes mockados, cobertura |

---

## 6. Spikes recomendados antes de codar o app

1. **Pronúncia**: Azure Pronunciation Assessment com 1 frase pt-BR→es e 1 pt-BR→ja; medir score por palavra.
2. **Tutor streaming**: grafo mínimo emitindo tokens via SSE até o Next.
3. **RAG do currículo**: 20 itens no Qdrant com filtro por idioma/nível; medir precisão.
4. **Correção com rubrica**: avaliador-vendas adaptado para "resposta de escrita" com 5 casos.
5. **MySQL async**: uma tabela + Alembic + teste de concorrência com `SKIP LOCKED`.
6. **Qdrant idempotente**: reindexar duas vezes e provar que não duplica pontos.

Cada spike é pequeno, descartável e responde a um risco do documento de arquitetura.
