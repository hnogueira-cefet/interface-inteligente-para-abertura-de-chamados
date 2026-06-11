# Suporte Inteligente CEFET/RJ

Interface inteligente para abertura de chamados acadêmicos e administrativos do
CEFET/RJ. Combina um **frontend TanStack Start** (React 19 + Vite) com um
**backend FastAPI** que conversa com o modelo **Llama** hospedado na **Groq**.

> 🟦 O projeto foi gerado originalmente pelo Lovable. O chatbot foi acoplado
> **sobre** a arquitetura existente: nada da identidade visual, paleta ou
> componentes shadcn/ui foi reescrito.

---

## Sumário

- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Configuração da API Groq](#configuração-da-api-groq)
- [Execução local (dev)](#execução-local-dev)
- [Execução via Docker Compose](#execução-via-docker-compose)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Endpoints do backend](#endpoints-do-backend)
- [Deploy](#deploy)
- [Segurança](#segurança)
- [Estrutura de diretórios](#estrutura-de-diretórios)
- [Documentação adicional](#documentação-adicional)

---

## Arquitetura

```
┌──────────────┐   useServerFn   ┌────────────────────┐  fetch+API key   ┌──────────────────┐
│  ChatWidget  │ ───────────────▶│ sendChatMessage    │ ────────────────▶│  FastAPI /chat   │
│  (browser)   │                 │ (TanStack server   │                  │  (Python + Groq) │
│              │◀─────────────── │  function — proxy) │◀──────────────── │                  │
└──────────────┘   { reply }     └────────────────────┘   { reply }      └──────────────────┘
```

- O navegador chama uma **server function** do TanStack Start (`sendChatMessage`),
  que age como **proxy** seguro.
- O proxy injeta o token (`X-API-Token`) e encaminha a chamada ao backend Python.
- O FastAPI sanitiza a entrada, aplica *rate limiting*, mescla o histórico da
  sessão, monta o *prompt* institucional e consulta a Groq.
- A resposta percorre o caminho inverso e é exibida no `ChatWidget`.

Detalhes técnicos completos: [`docs/ANALISE_INICIAL.md`](docs/ANALISE_INICIAL.md)
e [`docs/RELATORIO_TECNICO.md`](docs/RELATORIO_TECNICO.md).

---

## Pré-requisitos

| Dependência | Versão | Onde |
| --- | --- | --- |
| Bun | 1.2+ | frontend (também aceita `npm`) |
| Node.js | 22+ | runtime de produção do frontend |
| Python | 3.12+ | backend FastAPI |
| Docker + Docker Compose | 24+ | execução containerizada (opcional) |
| Conta na Groq | — | [console.groq.com](https://console.groq.com) |

---

## Configuração da API Groq

1. Acesse <https://console.groq.com/keys>.
2. Crie uma chave (`gsk_...`).
3. Copie `.env.example` para `.env` na raiz do projeto.
4. Cole a chave em `GROQ_API_KEY`.
5. (Opcional) Ajuste `GROQ_MODEL` — o default é `llama-3.3-70b-versatile`.

```bash
cp .env.example .env
$EDITOR .env
```

---

## Execução local (dev)

### 1) Backend FastAPI

```bash
# da raiz do repositório
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# garanta que o .env está preenchido (pelo menos GROQ_API_KEY)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Verifique: <http://localhost:8000/health> e a documentação interativa em
<http://localhost:8000/docs>.

### 2) Frontend TanStack Start

```bash
# em outro terminal, na raiz do repositório
bun install            # ou: npm install
bun run dev            # ou: npm run dev
```

A página abre em <http://localhost:3000> (ou em outra porta conforme o
runtime). O `ChatWidget` da home já está conectado ao backend.

> 💡 As variáveis `CHATBOT_API_URL` e `CHATBOT_API_KEY` são lidas pelo Node
> em *runtime*. Sem prefixo `VITE_`, elas **não** chegam ao navegador.

---

## Execução via Docker Compose

```bash
cp .env.example .env
# preencha GROQ_API_KEY (e, em produção, API_TOKEN)

docker compose up --build
```

- Backend → <http://localhost:8000>
- Frontend → <http://localhost:3000>

Para parar: `docker compose down`. Para rebuild forçado: `docker compose build --no-cache`.

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `APP_NAME` | `Suporte Inteligente CEFET/RJ` | Nome exibido em logs/docs |
| `APP_ENV` | `development` | `development \| staging \| production` |
| `APP_HOST` | `0.0.0.0` | Host do Uvicorn |
| `APP_PORT` | `8000` | Porta do backend |
| `APP_DEBUG` | `false` | Habilita reload do Uvicorn |
| `GROQ_API_KEY` | _(vazio)_ | **Obrigatório** — chave Groq |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Modelo Llama na Groq |
| `GROQ_TEMPERATURE` | `0.3` | Criatividade do modelo |
| `GROQ_MAX_TOKENS` | `1024` | Limite de tokens por resposta |
| `GROQ_TIMEOUT_SECONDS` | `30` | Timeout da requisição à Groq |
| `SESSION_TTL_SECONDS` | `7200` | TTL da sessão em memória (2h) |
| `SESSION_MAX_MESSAGES` | `40` | Máx. de mensagens preservadas por sessão |
| `API_TOKEN` | _(vazio)_ | Token compartilhado `X-API-Token`. Vazio = sem auth (dev) |
| `RATE_LIMIT_PER_MINUTE` | `20` | Limite por IP/minuto |
| `RATE_LIMIT_PER_HOUR` | `200` | Limite por IP/hora |
| `MAX_MESSAGE_LENGTH` | `2000` | Tamanho máximo de cada mensagem |
| `MAX_HISTORY_MESSAGES` | `20` | Mensagens enviadas ao modelo |
| `ALLOWED_ORIGINS` | `localhost:3000,5173,8080` | Lista CORS separada por vírgula |
| `LOG_LEVEL` | `INFO` | `DEBUG \| INFO \| WARNING \| ERROR` |
| `LOG_FORMAT` | `json` | `json` (prod) ou `console` (dev) |
| `CHATBOT_API_URL` | `http://localhost:8000/chat` | Endpoint chamado pela server function |
| `CHATBOT_API_KEY` | _(vazio)_ | Valor enviado em `X-API-Token` |
| `CHATBOT_TIMEOUT_MS` | `30000` | Timeout do proxy server-side |

---

## Endpoints do backend

### `POST /chat`

Request:
```json
{
  "session_id": "a8b3f0c1-7d2e-4b9c-8e5f-1a2b3c4d5e6f",
  "message": "Preciso solicitar histórico",
  "history": [
    { "role": "user", "content": "Olá" },
    { "role": "assistant", "content": "Olá! Como posso ajudar?" }
  ]
}
```

Response:
```json
{
  "response": "Claro! Você é aluno da Pós-Graduação Stricto Sensu ou Lato Sensu?",
  "reply":    "Claro! Você é aluno da Pós-Graduação Stricto Sensu ou Lato Sensu?",
  "session_id": "a8b3f0c1-7d2e-4b9c-8e5f-1a2b3c4d5e6f",
  "model": "llama-3.3-70b-versatile"
}
```

Cabeçalhos:
- `X-API-Token: <API_TOKEN>` — obrigatório quando `API_TOKEN` está definido.
- `Content-Type: application/json`.

### `GET /health`

Devolve `200 OK` com status do serviço, versão e modelo configurado. Usado pelo
`HEALTHCHECK` do Docker.

### `GET /docs` e `GET /redoc`

Swagger / ReDoc — disponíveis exceto quando `APP_ENV=production`.

---

## Deploy

### Backend (FastAPI)

- **Container** (recomendado): use a imagem produzida por `backend/Dockerfile`
  em qualquer plataforma (k8s, Fly.io, Render, ECS, Cloud Run...).
- Configure os segredos (`GROQ_API_KEY`, `API_TOKEN`) em um cofre — nunca no
  repositório.
- Atrás de um proxy reverso, encaminhe `X-Forwarded-For` para que o *rate limit*
  use o IP real do cliente.

### Frontend (TanStack Start)

- O `vite.config.ts` usa o preset `@lovable.dev/vite-tanstack-config`, que por
  default empacota para **Cloudflare Workers** via Nitro.
- Para deploy em Node, use a saída em `.output/server/index.mjs` (veja
  `docker/Dockerfile.frontend`).
- Defina `CHATBOT_API_URL` apontando para o backend público (ex.:
  `https://api.cefet-suporte.example/chat`) e `CHATBOT_API_KEY` com o token.

### TLS / Domínio

- Coloque ambos os serviços atrás de um proxy reverso com TLS terminado (Caddy,
  Nginx, Traefik, Cloudflare).
- Garanta que `ALLOWED_ORIGINS` reflita o domínio público do frontend.

---

## Segurança

| Camada | Mitigação |
| --- | --- |
| **CORS** | `ALLOWED_ORIGINS` restringe domínios permitidos no backend |
| **Auth backend ⇄ proxy** | Header `X-API-Token` (`API_TOKEN`) |
| **Rate limiting** | `slowapi` em janelas de 1 min e 1 h, por IP |
| **Sanitização de entrada** | Normalização Unicode + remoção de control chars |
| **Prompt injection** | Detecção heurística + envelope `<<< ... >>>` + system prompt blindado |
| **Validação dupla** | Zod no frontend + Pydantic no backend |
| **Logs de auditoria** | `structlog` (JSON em produção) com `session_id` e `client_id` |
| **Controle de sessão** | UUID em `localStorage`, TTL configurável no backend |
| **Segredos** | Apenas em `.env` (gitignored); chave Groq não chega ao browser |
| **Limite de tamanho** | Mensagens e histórico têm tamanho máximo configurável |
| **Anti-spam** | Rate limit + identificação por IP + token; pode evoluir para captcha |

---

## Estrutura de diretórios

```
.
├── backend/                       # FastAPI + Groq/Llama
│   ├── api/                       # routers REST
│   │   ├── chat.py                # POST /chat
│   │   ├── health.py              # GET /health
│   │   └── security.py            # auth + identificação do cliente
│   ├── config/                    # pydantic-settings
│   ├── models/                    # schemas Pydantic
│   ├── prompts/                   # system prompt institucional
│   ├── services/                  # groq, sessões, sanitização, logs, rate-limit
│   ├── tests/                     # testes pytest
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
│
├── src/                           # Frontend TanStack Start (já existente)
│   ├── assets/                    # logo + mascote CEFET
│   ├── components/
│   │   ├── ChatWidget.tsx         # widget do chatbot (atualizado)
│   │   └── ui/                    # shadcn/ui
│   ├── hooks/
│   ├── lib/
│   │   ├── chatbot.functions.ts   # server function proxy (atualizado)
│   │   ├── config.server.ts       # leitura de env server-only (atualizado)
│   │   └── …
│   ├── routes/
│   ├── server.ts
│   ├── start.ts
│   └── styles.css
│
├── docker/
│   └── Dockerfile.frontend
│
├── docs/
│   ├── ANALISE_INICIAL.md         # relatório da Etapa 1
│   └── RELATORIO_TECNICO.md       # entrega da Etapa 4
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── package.json                   # (intacto) — scripts Bun/Vite
├── README.md                      # este arquivo
└── … (arquivos originais do Lovable)
```

---

## Documentação adicional

- [`docs/ANALISE_INICIAL.md`](docs/ANALISE_INICIAL.md) — análise inicial,
  arquitetura recomendada, pontos de integração.
- [`docs/RELATORIO_TECNICO.md`](docs/RELATORIO_TECNICO.md) — relatório final
  de entrega (arquivos modificados, criados, fluxo de funcionamento).

---

## Licença / Créditos

Projeto interno do **CEFET/RJ — Campus Nova Iguaçu**. Base visual gerada pelo
Lovable; integração de IA implementada pelo time de desenvolvimento.
