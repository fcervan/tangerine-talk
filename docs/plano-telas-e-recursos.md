# Tangerine Talk — Rascunho de telas e recursos

> Documento de produto. **Sem stack, sem arquitetura.** Objetivo: fechar o escopo de telas e recursos antes de decidir tecnologia.
> Fonte: análise da landing page (`app/`, `components/`, `components/mockups/`).
> Status: rascunho para aprovação.

---

## 1. Inventário: o que a landing promete

| Origem | Promessa literal | Vira recurso |
|---|---|---|
| Hero | "Tutor de IA que escuta, corrige e torce por você em tempo real" | Tutor conversacional + correção ao vivo |
| Hero | "Falando, ouvindo, escrevendo e brincando" | 4 pilares: Fala, Escuta, Escrita, Testes |
| Hero | 5 idiomas no seletor + "50+ idiomas" | Catálogo de idiomas / escolha do idioma-alvo |
| Hero | "Grátis para começar · Sem cartão" | Cadastro gratuito, sem cobrança em lugar nenhum |
| Features · Fala | "Parceiro de IA + feedback de pronúncia na hora" | Pronúncia com score por palavra + dica |
| Features · Escuta | "Áudio em velocidade nativa, no seu ritmo" | Player de áudio com velocidade ajustável + compreensão |
| Features · Escrita | "Monte frases peça por peça" | Exercício de montar frase com banco de palavras |
| Features · Testes | "Flashcards e quizzes inteligentes que retomam o que você esquece" | SRS (repetição espaçada) + quizzes |
| Mockup Fala | Score por palavra (98/95/72/99), média, dica "suavize o ó em cómo" | Pronúncia por palavra + feedback fonético |
| Mockup Escuta | Play/pause, 0.75×/1×, múltipla escolha, shake no erro | Compreensão auditiva |
| Mockup Escrita | Tradução PT→EN, tiles, "Verificar", "+15 XP" | Exercício de tradução + recompensa XP |
| Mockup Testes | Flip de cartão, 1/4, "Acertei"/"Revisar de novo", "Baralho concluído 4/4", **"Monte seu próprio baralho"** | Deck oficial + deck próprio + conclusão de sessão |
| Bento · Sequência | 27 dias, calendário S-T-Q-Q-S-S-D, maior sequência 41, selos 7/30/100 | Streak + calendário + selos |
| Bento · Ranking | "Liga Laranja · esta semana", 2.615 XP, posição entre outros | Ligas semanais + leaderboard |
| Bento · Conversas | "Próxima meta: 50", 36 de 50, selos 1/25/50 conversas | Metas + selos de conversa |
| Bento · Árvore | 7 nós (Básico → Saudações/Comida → Viagem/Números/Refeições/Negócios), desbloqueio por pré-requisito | Trilha/currículo com pré-requisitos |
| CTA | "Plano gratuito para sempre · Faça upgrade quando quiser" | **Conflito de produto:** não haverá cobrança. Trocar por "gratuito e open source" |
| CTA | 98% precisão, 4,9★, 1 mi+ aulas | números de marketing — suavizar ou remover antes de publicar |
| Navbar | Link "Preços" | substituir por "Provedores" ou "Open source" |

**Conclusão:** a landing promete um app **mobile-first**, centrado em **uma lição diária com 4 tipos de exercício**, um **tutor de IA com voz**, **SRS** e **streak/XP/ligas/selos**. Tudo isso exige auth, onboarding, dashboard, currículo e conteúdo — nenhum aparece na landing. O produto é **gratuito e sem cobrança**; a chave de IA é do próprio usuário.

---

## 2. Sitemap proposto

### A. Marketing (público)

| # | Tela | Objetivo |
|---|---|---|
| M1 | Landing | existente |
| M2 | **Como funciona / Provedores** | grátis, open source, traga sua chave ou rode offline |
| M3 | Termos & Privacidade | obrigatório (LGPD; voz é dado pessoal) |
| M4 | 404 / erro | — |

### B. Autenticação

| # | Tela | Objetivo |
|---|---|---|
| A1 | Cadastro | e-mail/senha (+ social, a decidir) |
| A2 | Login | — |
| A3 | Recuperar / redefinir senha | — |
| A4 | Verificar e-mail | opcional conforme provedor |

### C. Onboarding (primeiro acesso, 4–5 passos)

| # | Tela | Objetivo |
|---|---|---|
| O0 | **Idioma da aplicação** | pt-BR padrão, en-US oferecido, extensível a qualquer locale |
| O1 | Boas-vindas + **idioma-alvo** | escolha livre por código BCP-47; sem lista fechada |
| O2 | **Objetivo** (viagem, trabalho, estudos, cultura, relacionamento) | personaliza cenários e vocabulário |
| O3 | **Nivelamento** (teste curto, com "pular") | define ponto de partida na trilha |
| O4 | **Meta diária** + horário do lembrete | alimenta streak, metas e notificações |
| O5 | **Seu plano** (resumo: idioma, nível, meta, primeira unidade) | CTA "começar primeira lição" |

### D. Núcleo do app

| # | Tela | Objetivo |
|---|---|---|
| H1 | **Home/Dashboard** | streak, meta do dia, "continuar", revisões pendentes, missões, 4 atalhos |
| T1 | **Trilha** (mapa de unidades/nós) | currículo com nós, progresso, pré-requisitos |
| T2 | Detalhe da unidade | lições, itens de vocabulário, pré-requisito, status |
| L1 | **Player de lição** (shell) | progresso, sair/retomar, sequência de exercícios |
| L2 | Exercício **Fala** | frase-alvo, gravar, waveform, score por palavra, dica fonética, repetir |
| L3 | Exercício **Escuta** | áudio, 0.75×/1×, múltipla escolha, feedback de erro/acerto |
| L4 | Exercício **Escrita** | tradução + banco de tiles + verificar/corrigir |
| L5 | Exercício **Flashcards** | flip, "acertei"/"revisar de novo", progresso do baralho |
| L6 | Exercício **Quiz** (múltipla escolha, completar, associar) | "quizzes inteligentes" |
| L7 | **Resultado da lição** | XP ganho, precisão, acertos de primeira, itens novos, erros para revisar |
| L8 | **Sessão de revisão SRS** | fila do dia, por que aquele item voltou, conclusão |

### E. Tutor de IA

| # | Tela | Objetivo |
|---|---|---|
| C1 | **Conversa livre** | chat texto + voz, persona do tutor, correção inline, "traduzir", "reformular" |
| C2 | **Cenários / roleplay** | padaria, estação, hotel, restaurante (as frases da landing apontam isso), nível e objetivo |
| C3 | **Feedback de fala na conversa** | pronúncia da fala do usuário, sem sair do chat |

### F. Vocabulário e baralhos

| # | Tela | Objetivo |
|---|---|---|
| F1 | **Meus baralhos** | oficiais + criados pelo usuário, contagem, último estudo |
| F2 | Deck aberto / sessão | iniciar, editar, excluir, estatísticas do deck |
| F3 | Criar/editar deck + cartão | frente/verso, idioma, exemplo, áudio |
| F4 | Modal "salvar palavra" | a partir de lição, conversa ou revisão |
| V1 | **Meu vocabulário / caderno de erros** | palavras salvas, erros recorrentes, domínio por item |

### G. Gamificação e progresso

| # | Tela | Objetivo |
|---|---|---|
| G1 | **Sequência** (detalhe) | calendário, maior sequência, selos 7/30/100, recuperação |
| G2 | **Liga / Ranking** | semana, posição, XP, promover/rebaixar |
| G3 | **Selos / Conquistas** | galeria bloqueado/desbloqueado |
| G4 | **Metas e missões** | meta diária, missões ("36 de 50 conversas"), recompensas |
| P1 | **Progresso** | precisão e tempo por habilidade, evolução, calendário |

### H. Conta

| # | Tela | Objetivo |
|---|---|---|
| S1 | Perfil | nome, avatar, idioma(s), nível, meta, estatísticas |
| S2 | Configurações | conta/senha, idioma da interface, **voz e velocidade**, notificações, acessibilidade, privacidade |
| S3 | **Provedores de IA (BYOK)** — ✅ Fase 2 | cadastrar/testar chave, escolher modelo, capacidades, roteamento por tarefa; rota `/providers`, chave cifrada e fallback visível |
| S4 | **Trilha e baralhos** — ✅ Fase 3 | unidades com pré-requisito, lições com prévia, glossas no idioma da interface, decks oficiais; rota `/curriculum` |
| S5 | **Membros e convites** (owner) | listar membros, convidar por e-mail, revogar acesso |
| S6 | Ajuda / FAQ / suporte | + reportar problema |

**Não existe:** assinatura, plano pago, paywall ou tela de cobrança.

### I. Interno (não é tela do aluno, mas é recurso)

Painel de conteúdo: unidades, lições, exercícios, itens de vocabulário, decks oficiais, cenários de conversa, traduções/glossas. Sem isso, o currículo não escala.

---

## 3. Detalhe das telas-chave

### H1 · Home/Dashboard — o hub que amarra tudo

- Saudação + mascote; streak com chama e dias; anel da meta diária (ex.: 12/15 min)
- Card "Continuar" → próxima lição da trilha
- Card "Revisar" → N itens vencidos no SRS (some se zero)
- 4 atalhos: Fala, Escuta, Escrita, Testes
- Missões do dia/semana + posição na liga
- **Estados:** primeiro dia (sem histórico), tudo revisado, streak em risco, meta batida (confetti)

### T1 · Trilha

- Nós verticais por unidade; nó concluído / atual / bloqueado (cadeado) / pronto para desbloquear (pulso)
- Pré-requisitos visíveis (como no Bento: Básico → Saudações/Comida → Viagem…)
- Toque no nó → T2

### L1 · Player de lição

- Barra de progresso, botão fechar (confirma perda), sequência de 8–12 exercícios mistos
- Sem navegação global durante a lição; retomada se sair

### L2 · Fala (o mais caro)

- Frase-alvo + áudio modelo; botão gravar; waveform ao vivo
- Feedback: score geral %, score **por palavra** (verde ≥90 / sublinhado ondulado <90), dica específica ("suavize o ó em cómo"), botão repetir
- **Estados:** permissão de microfone negada, silêncio, ruído, offline, sem suporte do navegador

### L3 · Escuta

- Player com waveform, play/pause, velocidade, opções; erro com shake e nova tentativa; acerto revela a frase
- Decisão: permitir "mostrar transcrição" ou só após errar

### L5 · Flashcards

- Frente no idioma estudado, verso na glossa; botões "Revisar de novo" / "Acertei"
- Tela de conclusão: "Baralho concluído! X/Y de primeira" + "Praticar de novo"
- Atalho "Monte seu próprio baralho"

### C1 · Tutor IA

- Chat com histórico da sessão, entrada por texto **e** voz, botão de microfone
- Correções inline discretas (não interrompendo o fluxo) + "explicar"
- Ações rápidas: traduzir, repetir mais devagar, dar exemplo, mudar de assunto
- **Estados:** ouvindo, transcrevendo, pensando, erro de rede, quota do provedor esgotada

### G2 · Liga

- Sem base de usuários, ranking fica vazio → precisa de decisão (ver §6)

---

## 4. Recursos por domínio

### Motor de aprendizado

- Tipos de exercício: fala, escuta, escrita/tradução, flashcards, quiz (múltipla escolha, completar, associar)
- Correção + feedback imediato; tolerância a variações de resposta
- Dificuldade adaptativa ("se adaptam a você")
- Sessão de lição mista + sessão de revisão isolada

### Fala e pronúncia

- Captura de áudio, comparação com referência, score por palavra e por frase, dica fonética
- Áudio modelo, velocidade, repetir/ouvir de novo
- (A definir: score por fonema/IPA, destaque de sílaba — mais caro)

### Escuta

- Áudio em velocidade nativa e reduzida, compreensão por múltipla escolha, replay
- (A definir: transcrição, ditado, sotaques)

### Escrita

- Banco de tiles, montagem, verificação, correção, XP
- (A definir: escrita livre com correção de IA)

### SRS

- Agendamento por item, fila diária, "revisar de novo" vs. "acertei", retenção
- Vocabulário e erros alimentam a fila automaticamente

### Tutor de IA

- ✅ **Fase 4 entregue:** chat, correção estruturada, TTS/STT com cadeia BYOK + fallback, player de lição `/lesson/{id}` com 4 habilidades (fala, escuta, escrita, testes), pronúncia via Web Speech API base
- Pendem: persona consistente, cenários/roleplay, limites por plano (mensagens/dia), feedback de fala dentro da conversa, pronúncia avançada (sílaba/fonema, IPA), provedor TTS/STT dedicado

### Currículo e conteúdo

- Idiomas-alvo (genéricos, qualquer BCP-47), níveis (A1…), unidades, nós, pré-requisitos, lições, itens e **glossas por locale** (fallback pt-BR)
- ✅ **Fase 3 entregue:** seed idempotente de espanhol A1 (2 unidades, 3 lições, 10 itens, 8 exercícios, 1 deck), pré-requisito entre unidades, progresso/XP por usuário e tela `/curriculum`
- Pendem: criação de decks pelo usuário e importação (a decidir)

### Gamificação

- XP, streak + calendário + maior sequência, selos (7/30/100 dias; 1/25/50 conversas), ligas semanais, metas diárias, missões
- Proteção de sequência / congelamento (não prometido — decisão)
- Níveis/patamares de XP (não prometido — decisão)

### Conta e plataforma

- Auth, onboarding (idioma da interface + idioma-alvo + nível + meta), perfil, preferências (voz, velocidade, notificações, acessibilidade)
- **Provedores:** chave por usuário (BYOK), criptografada, com teste de conexão e roteamento por tarefa
- **Multiusuário:** `owner` + membros, convite por e-mail, isolamento total de dados
- **Sem cobrança:** nenhum fluxo de assinatura, paywall ou checkout
- Notificações de lembrete de prática
- Progresso/histórico pessoal
- Acessibilidade AA (foco, ARIA, reduced motion), LGPD (consentimento de áudio, exclusão de conta), suporte

---

## 5. Priorização sugerida

### P0 — MVP (a landing só "fecha" com isso)

Cadastro por convite · onboarding (idioma + meta) · Home · Trilha + 1 unidade real · ✅ **Player com Fala, Escuta, Escrita, Flashcards** · ✅ **Resultado de lição** · ✅ **Tutor de IA (chat, correção, TTS/STT, fallback BYOK)** · SRS básico · streak + XP + selos 7/30/100 · Perfil/Configurações · **Provedores de IA (BYOK)** · **Membros e convites**.

### P1 — v1 (completa a promessa visual)

Nivelamento · cenários/roleplay · feedback de fala dentro da conversa · baralhos próprios (F1–F4) · caderno de erros/vocabulário · progresso detalhado (P1) · metas e missões (G4) · ligas (G2 com decisão).

### P2 — v2 (encantamento e retenção)

Liga com temporadas e recompensas · notificações push · compartilhar conquistas · pronúncia avançada (sílaba/fonema, IPA) · múltiplos idiomas simultâneos · certificados.

---

## 6. Lacunas e decisões que precisam do usuário

1. ~~Idiomas no lançamento~~ **Fechado:** a interface nasce em pt-BR + en-US (extensível); o idioma-alvo é genérico. O currículo oficial entra aos poucos, sem travar o app.
2. ~~Base do curso~~ **Fechado:** a direção é `ui_language → target_language`. Se as bases coincidirem, o deck é monolingual.
3. **Tutor:** voz em tempo real ou texto primeiro com voz depois? Isso muda peso, custo e latência.
4. **Precisão de pronúncia:** score por palavra (como o mockup) ou fonema/sílaba? O "98%" é marketing ou meta?
5. **Liga:** ranking com usuários reais (vazio no início) ou com bots/ligas simuladas até ter base?
6. **Nivelamento:** teste de 5–10 min, autoavaliação ou só "pular"? (vale só na v1?)
7. **Limite de uso:** haverá limite por usuário/dia para proteger a chave (que é dele)? Sugiro padrão alto e configurável.
8. **Streak:** permite congelar/proteger dia perdido? Existe meta semanal além da diária?
9. **Níveis/XP:** só XP acumulado ou também níveis e patamares?
10. **Escrita livre com IA** entra no MVP ou fica para depois?
11. **Lembretes de prática:** e-mail, push ou nenhum no lançamento? (convite por e-mail já está decidido)
12. **Deck próprio:** criar do zero, importar (CSV) ou só salvar palavras durante as lições?
13. **Offline na Fala:** aceitar "sem nota" (recomendado) ou investir em alinhamento local?

---

## 7. Fora de escopo (não prometido na landing)

Chat social entre alunos · professores humanos · videoaulas · certificação oficial · modo dark · app nativo de loja · gamificação social (amigos/duelos). Se algum entrar, é decisão nova — não é dívida da landing.

---

## 8. Resumo

A landing promete **uma rotina diária de 4 habilidades com tutor de IA por voz, currículo em trilha, SRS e gamificação de streak/liga/selos** — e para isso precisamos de ~35 telas, das quais **11 são P0** e sustentam a promessa sozinhas. O produto é **gratuito e open source**: cada usuário traz a própria chave de IA ou roda offline.

**Próximo passo:** aprovar escopo deste documento e seguir para arquitetura + recursos técnicos.
