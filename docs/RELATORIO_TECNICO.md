# Relatório Técnico — Entrega do Chatbot CEFET/RJ

Documento da **Etapa 4** descrevendo arquivos modificados, criados, dependências
adicionadas e o fluxo de funcionamento da integração do Suporte Inteligente
CEFET/RJ ao repositório `interface-inteligente-para-abertura-de-chamados`.

---

## 1. Visão Geral

A solução adiciona um **backend FastAPI** (Python 3.12) responsável pela
inteligência do chatbot — conversando com o modelo **Llama** hospedado na **Groq** —
e conecta-o ao frontend **TanStack Start** já existente, sem reescrever a UI ou
quebrar a identidade visual do portal.

O frontend chama uma **server function** (`sendChatMessage`) que age como
proxy seguro entre o navegador e o backend Python. O conteúdo do usuário é
sanitizado, o histórico é mantido por sessão e a resposta volta ao
`ChatWidget` já presente em `src/components/`.

---

## 2. Arquivos Modificados

| Arquivo | Mudança |
| --- | --- |
| `src/lib/chatbot.functions.ts` | Substituiu-se o *placeholder* por um proxy `fetch` ao backend FastAPI. Agora valida `session_id`, propaga `X-API-Token`, trata 429/erros e devolve um `reply` consistente. |
| `src/lib/config.server.ts` | Acrescentadas as variáveis `chatbotApiUrl`, `chatbotApiKey` e `chatbotTimeoutMs`, todas server-only (lidas em runtime no Node/Workers). |
| `src/components/ChatWidget.tsx` | Persistência de `session_id` em `localStorage` (UUID), mensagem inicial conforme prompt institucional, envio de `session_id` ao backend e `maxLength` no input. |
| `.gitignore` | Adicionados padrões Python (`__pycache__/`, `.venv/`, `backend/.env`) e proteção a arquivos `.env`. |

A UI, os tokens CSS, o `__root.tsx`, o `index.tsx` e os componentes shadcn/ui
**não** foram alterados.

---

## 3. Arquivos Criados

### Backend (FastAPI)

```
backend/
├── __init__.py                    # __version__
├── main.py                        # bootstrap FastAPI + middlewares
├── requirements.txt               # dependências Python pinadas
├── Dockerfile                     # imagem do backend
├── api/
│   ├── __init__.py
│   ├── chat.py                    # POST /chat (com Depends + rate-limit)
│   ├── health.py                  # GET /health
│   └── security.py                # autenticação opcional + identificação
├── config/
│   ├── __init__.py
│   └── settings.py                # pydantic-settings, lê .env
├── models/
│   ├── __init__.py
│   └── schemas.py                 # Pydantic: ChatRequest / ChatResponse / etc.
├── prompts/
│   ├── __init__.py
│   └── system_prompt.py           # prompt institucional CEFET/RJ
├── services/
│   ├── __init__.py
│   ├── audit_logger.py            # structlog (JSON / console)
│   ├── groq_client.py             # SDK Groq + Llama
│   ├── rate_limiter.py            # slowapi
│   ├── sanitizer.py               # anti-injection + sanitização
│   └── session_store.py           # store em memória (thread-safe)
└── tests/
    ├── __init__.py
    └── test_sanitizer.py
```

### Infraestrutura e raiz

```
docker/
└── Dockerfile.frontend            # build do TanStack Start (Bun + Node)
docker-compose.yml                 # orquestra backend + frontend
.env.example                       # template de variáveis
README.md                          # documentação completa do projeto
docs/
├── ANALISE_INICIAL.md             # relatório da Etapa 1
└── RELATORIO_TECNICO.md           # este documento
```

Total: **22 arquivos novos** (1 README, 2 docs, 19 do backend/infra).

---

## 4. Dependências Adicionadas

### Backend — `backend/requirements.txt`

| Pacote | Versão | Finalidade |
| --- | --- | --- |
| `fastapi` | 0.115.6 | Framework web |
| `uvicorn[standard]` | 0.34.0 | Servidor ASGI |
| `pydantic` | 2.10.3 | Validação de schemas |
| `pydantic-settings` | 2.7.0 | Leitura tipada do `.env` |
| `groq` | 0.13.1 | SDK oficial da Groq |
| `slowapi` | 0.1.9 | Rate limiting |
| `python-multipart` | 0.0.20 | Forms / multipart (futuro) |
| `structlog` | 24.4.0 | Logs estruturados |
| `httpx` | 0.28.1 | Cliente HTTP (utilitário) |
| `python-dotenv` | 1.0.1 | Compat com loaders externos |

### Frontend

**Nenhuma dependência nova** foi adicionada ao `package.json`. A integração
reaproveita 100% das libs que já estavam instaladas (`@tanstack/react-start`,
`zod`, `react`, `lucide-react`, etc.).

---

## 5. Fluxo de Funcionamento

```
┌──────────────────────────┐
│  1. Usuário digita        │
│     no ChatWidget         │
└────────────┬──────────────┘
             │ {session_id, message, history}
             ▼
┌──────────────────────────┐
│  2. sendChatMessage       │
│     (TanStack server fn)  │  ← roda em Node/Workers
│     valida com Zod        │
│     adiciona X-API-Token  │
└────────────┬──────────────┘
             │ POST /chat
             ▼
┌──────────────────────────┐
│  3. FastAPI               │
│     - autenticação        │
│     - rate-limit (slowapi)│
│     - sanitização         │
│     - merge histórico     │
└────────────┬──────────────┘
             │ messages = [system_prompt, ...history, user]
             ▼
┌──────────────────────────┐
│  4. Groq (Llama)          │
│     llama-3.3-70b         │
│     temperature=0.3       │
└────────────┬──────────────┘
             │ completion.choices[0].message.content
             ▼
┌──────────────────────────┐
│  5. Backend persiste a    │
│     conversa na sessão e  │
│     loga (structlog)      │
└────────────┬──────────────┘
             │ {response, reply, session_id, model}
             ▼
┌──────────────────────────┐
│  6. Server function       │
│     repassa { reply }     │
└────────────┬──────────────┘
             │
             ▼
┌──────────────────────────┐
│  7. ChatWidget exibe a    │
│     resposta              │
└──────────────────────────┘
```

### Detalhes por etapa

1. **UI** — `ChatWidget.tsx` chama `useServerFn(sendChatMessage)` passando o
   `session_id` (obtido/gerado no `localStorage`), a mensagem digitada e as
   últimas 20 mensagens.
2. **Server function** — valida com Zod, garante que a chave Groq não vaze e
   propaga o `X-API-Token` definido em `CHATBOT_API_KEY`.
3. **FastAPI `/chat`** — verifica token, aplica rate limit (`20/min`,
   `200/h` por IP), sanitiza a entrada (remove control chars, normaliza
   Unicode, detecta padrões de *prompt injection*) e funde o histórico
   armazenado em `InMemorySessionStore` com o histórico opcional do cliente.
4. **Groq client** — monta `[system, ...history, user]`, chama
   `chat.completions.create(...)` com timeout configurável.
5. **Persistência** — a mensagem do usuário e a resposta vão para o store
   (TTL 2 h, máximo 40 mensagens) e um log JSON é emitido.
6. **Proxy** — a server function devolve `{ reply }` (campo que o `ChatWidget`
   já espera).
7. **UI** — a mensagem aparece no histórico do chat.

---

## 6. Segurança Implementada

| Mecanismo | Local | Como funciona |
| --- | --- | --- |
| **CORS** | `backend/main.py` | `CORSMiddleware` com `ALLOWED_ORIGINS` (variável de ambiente). |
| **Validação de origem** | `backend/api/chat.py` | Dependência `authenticate_request` exige `X-API-Token` quando `API_TOKEN` está configurado. |
| **Rate limiting** | `backend/services/rate_limiter.py` | `slowapi` com janelas de minuto e hora, identificação via `X-Forwarded-For` ou IP. |
| **Proteção contra Prompt Injection** | `backend/services/sanitizer.py` + `backend/prompts/system_prompt.py` | Detecta padrões clássicos, envelopa a mensagem como dado e o system prompt obriga o modelo a ignorar instruções dentro do conteúdo do usuário. |
| **Sanitização de entrada** | `backend/services/sanitizer.py` | Remove control chars, normaliza Unicode, trunca tamanho, valida vazio. |
| **Logs de auditoria** | `backend/services/audit_logger.py` | `structlog` JSON com `session_id`, `client_id`, tamanho, padrões suspeitos. |
| **Controle de sessão** | `backend/services/session_store.py` + `ChatWidget.tsx` | UUID no `localStorage`, TTL e teto de mensagens no servidor. |
| **Proteção contra spam** | combinação de rate limit + token + identificação por IP | Pode evoluir para captcha em caso de necessidade. |
| **Validação dupla** | Zod no frontend + Pydantic no backend | Reduz ataques de payload malformado. |

---

## 7. Endpoint REST

### `POST /chat`

Request:
```json
{
  "session_id": "a8b3f0c1-7d2e-4b9c-8e5f-1a2b3c4d5e6f",
  "message": "Preciso solicitar histórico"
}
```

Response (200):
```json
{
  "response": "Claro! Você é aluno da Pós-Graduação Stricto Sensu ou Lato Sensu?",
  "reply":    "Claro! Você é aluno da Pós-Graduação Stricto Sensu ou Lato Sensu?",
  "session_id": "a8b3f0c1-7d2e-4b9c-8e5f-1a2b3c4d5e6f",
  "model": "llama-3.3-70b-versatile"
}
```

Erros padronizados:
- `400` — payload inválido (mensagem vazia, session_id inválido).
- `401` — token ausente/incorreto (quando `API_TOKEN` configurado).
- `422` — schema Pydantic falhou.
- `429` — rate limit excedido.
- `502` — falha ao consultar a Groq.

---

## 8. Decisões Arquiteturais

- **Backend separado em FastAPI**: atende ao requisito explícito da
  especificação e permite deploy independente do frontend (Cloudflare
  Workers / Node).
- **Server function como proxy**: a chave da Groq e o `API_TOKEN` ficam
  exclusivamente no servidor — nunca no `bundle` do cliente.
- **Store em memória abstraído via interface**: trocar por Redis
  (multi-instância) requer apenas uma nova classe `SessionStore`.
- **Prompt blindado**: o `system prompt` instrui o modelo a ignorar tentativas
  de mudança de papel e o `InputSanitizer` envelopa o conteúdo do usuário
  como dado.
- **Estrutura Python por camadas (api → services → models)**: respeita SOLID
  (cada serviço com uma responsabilidade, injetados via `Depends`).
- **Identidade visual preservada**: nenhum token CSS, asset, layout ou
  componente shadcn foi alterado.

---

## 9. Como Executar (resumo)

```bash
# 1. variáveis
cp .env.example .env
# preencha GROQ_API_KEY

# 2. tudo via docker-compose
docker compose up --build
# → frontend: http://localhost:3000
# → backend:  http://localhost:8000  (docs em /docs)

# 3. ou em modo dev
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload &      # em um terminal
bun install && bun run dev                # em outro
```

---

## 10. Próximos Passos (sugestões)

1. **Redis** para sessões multi-instância.
2. **Telemetria** via OpenTelemetry exportando para Datadog/Grafana.
3. **Streaming SSE** para respostas em tempo real (o `groq` SDK suporta).
4. **Integração com o sistema oficial de chamados** (criar chamado direto da
   conversa quando o aluno confirmar).
5. **Captcha** após N falhas de rate-limit.
6. **Testes E2E** com Playwright cobrindo o fluxo completo.

---

Entrega encerrada. Consulte o [`README.md`](../README.md) para o passo-a-passo
completo de instalação, configuração e deploy.
