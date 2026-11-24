# Segurança

Tangerine Talk é um projeto público e auto-hospedável. Ele lida com dois tipos
de dado sensível: **chaves de API dos provedores de IA** (configuradas por cada
usuário) e **áudio de voz** (quando o recurso de fala é usado).

## Como reportar uma vulnerabilidade

**Não abra issue pública.** Use o canal privado:

1. GitHub → aba **Security** → **Report a vulnerability** (Security Advisories), ou
2. e-mail para o mantenedor indicado no `README.md`.

Inclua: versão, passos para reproduzir, impacto e, se possível, uma sugestão de
correção. Você receberá confirmação em até 7 dias.

## Escopo

Dentro do escopo:

- vazamento de chave de provedor (log, resposta de API, banco, backup);
- acesso a dados de outro usuário da mesma instância;
- execução remota, injeção, SSRF em URL de provedor configurável;
- bypass de autenticação ou de autorização;
- exposição de áudio ou histórico de conversa.

Fora do escopo:

- má configuração da sua própria instância (senha fraca, banco exposto à internet);
- custo gerado pelo uso da sua própria chave;
- conteúdo gerado pelo modelo.

## Regras do projeto

- Nenhuma chave, token ou `.env` é versionado. `.env.example` só tem placeholders.
- Chaves de provedor são criptografadas em repouso e nunca retornadas pela API.
- Logs não registram chaves, tokens nem conteúdo de conversa por padrão.
- Áudio é processado e descartado por padrão (`AUDIO_RETENTION_DAYS=0`).
- Fixtures, testes e seeds usam dados sintéticos — nunca dados reais.
- O histórico do Git é verificado com `gitleaks` no CI.
