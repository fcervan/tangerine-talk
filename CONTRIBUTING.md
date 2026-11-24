# Contribuindo

Obrigado pelo interesse! Este projeto é gratuito, open source (MIT) e feito para
ser auto-hospedado.

## Antes de abrir um PR

1. Leia o `README.md` e o `AGENTS.md` (convenções e armadilhas conhecidas).
2. Rode os testes e o lint do que você alterou.
3. **Nunca** inclua chave, token, `.env`, dump de banco, áudio ou dado pessoal.
4. Use dados sintéticos em testes, exemplos e seeds.

## Ambiente

```bash
# front (landing + app)
npm install
npm run dev

# backend
cd api
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## Regras de código

- Front: TypeScript estrito, server components por padrão, `"use client"` só quando necessário.
- Backend: Python 3.12, `from __future__ import annotations`, tipos em funções públicas.
- Mensagens de interface e erros em **português**; identificadores em inglês.
- Não adicione dependência sem justificar (impacto em bundle e superfície de ataque).
- Toda mudança de comportamento atualiza o `README.md`.

## Adicionando um provedor de IA

Provedores novos entram por **configuração**, não por código novo, sempre que
expõem API compatível com OpenAI (`base_url` + `model`). Se o provedor tiver
particularidades, veja a matriz de capacidades em `docs/arquitetura-e-tecnologias.md`.

## Commits

- Mensagens curtas, no imperativo, em português: `adiciona teste de isolamento`.
- Um assunto por commit.
- Sem `Co-authored-by` de ferramentas, a menos que você queira.

## Licença

Ao contribuir, você concorda que sua contribuição é licenciada sob MIT.
