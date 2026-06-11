# Relatório de Análise Inicial — Suporte Inteligente CEFET/RJ

> Documento gerado antes de qualquer alteração no código, conforme exigido na
> **Etapa 1** da especificação. Serve de referência para a estratégia de
> integração do chatbot ao projeto já existente.

---

## 1. Identificação do Projeto

| Item | Valor |
| --- | --- |
| Repositório | `git@github.com:hnogueira-cefet/interface-inteligente-para-abertura-de-chamados.git` |
| Origem | Projeto gerado via **Lovable.dev** (`@lovable.dev/vite-tanstack-config`) |
| Linguagem principal | TypeScript (ES2022, strict mode) |
| Framework full-stack | **TanStack Start** (Vite + React 19 + Nitro) |
| Roteador | TanStack Router (file-based em `src/routes/`) |
| Estado de dados | TanStack React Query |
| Estilos | Tailwind CSS v4 + `tw-animate-css` |
| Componentes | **shadcn/ui** (estilo *new-york*) + Radix UI |
| Ícones | `lucide-react` |
| Package manager | Bun (`bun.lock`, `bunfig.toml`) — compatível com npm |
| SSR / build | Nitro 3 (deploy default em Cloudflare Workers) |
| Lint / format | ESLint 9 + Prettier 3 |
| Validação | Zod |

---

## 2. Estrutura Atual do Repositório

```
.
├── bun.lock / bunfig.toml         # Bun
├── package.json                   # deps + scripts (dev/build/preview/lint)
├── vite.config.ts                 # presets Lovable + Cloudflare
├── tsconfig.json                  # paths: "@/*" → "./src/*"
├── components.json                # config shadcn/ui
├── eslint.config.js
├── .prettierrc / .prettierignore
└── src/
    ├── assets/
    │   ├── cefet-logo.png
    │   └── mascot.png             # mascote oficial do agente
    ├── components/
    │   ├── ChatWidget.tsx         # ⭐ chatbot UI já existente
    │   └── ui/                    # ~45 componentes shadcn
    ├── hooks/
    │   └── use-mobile.tsx
    ├── lib/
    │   ├── api/example.functions.ts
    │   ├── chatbot.functions.ts   # ⭐ server function placeholder (TODO)
    │   ├── config.server.ts       # leitura de env server-only
    │   ├── error-capture.ts
    │   ├── error-page.ts
    │   ├── lovable-error-reporting.ts
    │   └── utils.ts               # cn()
    ├── routes/
    │   ├── __root.tsx             # shell, QueryClientProvider, error boundaries
    │   ├── index.tsx              # ⭐ Home com Hero + ChatWidget
    │   └── README.md
    ├── routeTree.gen.ts           # gerado automaticamente
    ├── router.tsx
    ├── server.ts                  # entrypoint SSR (Nitro/Cloudflare/Node)
    ├── start.ts                   # middlewares globais
    └── styles.css                 # tokens de tema CEFET/RJ
```

### 2.1 Identidade visual já consolidada

O `src/styles.css` define a paleta institucional via *CSS custom properties*:

- `--brand-navy-deep`, `--brand-navy` — azuis institucionais
- `--brand-blue`, `--brand-blue-light` — azuis de destaque
- `--gradient-hero` — degradê do hero
- `--shadow-chat` — sombra do widget

Essas variáveis **não devem ser alteradas** — toda nova UI deve consumi-las.

### 2.2 Componentes-chave existentes

- **`ChatWidget.tsx`** — UI completa do chatbot (header com mascote, balões de
  conversa, ações rápidas, input com botão de envio). Já consome a server
  function `sendChatMessage` via `useServerFn` do TanStack Start.
- **`chatbot.functions.ts`** — server function (`POST`) com validação Zod e um
  *TODO* explícito para conectar o backend real. Aceita `{ message, history }`
  e retorna `{ reply }`.
- **`config.server.ts`** — *helper* para leitura segura de variáveis de ambiente
  em tempo de requisição (compatível com Cloudflare Workers).

### 2.3 Rotas existentes

| Rota | Arquivo | Função |
| --- | --- | --- |
| `/` | `src/routes/index.tsx` | Home com Hero + `ChatWidget` embutido |
| `__root` | `src/routes/__root.tsx` | Shell global (QueryClient, error boundaries, 404) |

### 2.4 Autenticação

**Não há sistema de autenticação no projeto.** O chatbot atual é público.
Pode-se introduzir um `session_id` opaco (UUID) para rastrear conversas sem
exigir login.

### 2.5 Deploy

- Build via `vite build` → Nitro empacota para **Cloudflare Workers** (default).
- Arquivos do Wrangler/Cloudflare já ignorados no `.gitignore`.
- Não há `Dockerfile` nem `docker-compose.yml` no repositório.

---

## 3. Pontos de Integração para o Chatbot

A UI **já está totalmente integrada na home**. O que falta é a inteligência
real por trás dela. Os pontos de extensão naturais são:

1. **`src/lib/chatbot.functions.ts`** — substituir o placeholder por uma chamada
   ao backend FastAPI (proxy server-side, mantendo a chave Groq fora do
   navegador).
2. **`src/components/ChatWidget.tsx`** — acrescentar `session_id` persistido no
   `localStorage` e atualizar a mensagem inicial para o texto institucional.
3. **`src/lib/config.server.ts`** — adicionar `chatbotApiUrl` e `chatbotApiKey`
   ao bloco de config server-only.

---

## 4. Estratégia Recomendada

A especificação solicita **backend FastAPI + Groq/Llama** e, ao mesmo tempo,
exige *não recriar o site* e *manter a arquitetura existente*. A abordagem
adotada concilia ambos:

### 4.1 Arquitetura híbrida em duas camadas

```
┌──────────────┐   useServerFn   ┌────────────────────┐  fetch+API key   ┌──────────────────┐
│  ChatWidget  │ ───────────────▶│ sendChatMessage    │ ────────────────▶│  FastAPI /chat   │
│  (browser)   │                 │ (TanStack server   │                  │  (Python + Groq) │
│              │◀─────────────── │  function — proxy) │◀──────────────── │                  │
└──────────────┘   { reply }     └────────────────────┘   { reply }      └──────────────────┘
```

**Vantagens:**

- A UI não muda de protocolo — continua chamando `sendChatMessage` (zero
  reescrita de componentes).
- A chave da Groq **nunca** chega ao browser; fica apenas na camada Python e
  numa variável server-only do TanStack Start.
- O backend Python concentra a lógica de IA, prompts, sessões, *rate limiting*,
  auditoria — e pode ser deployado independentemente (Docker, VM, k8s).
- Preserva a possibilidade de deploy em Cloudflare Workers (a server function
  só faz `fetch` para o backend Python).

### 4.2 Estrutura adicional proposta

```
backend/
├── api/
│   └── chat.py                # POST /chat
├── services/
│   ├── groq_client.py         # SDK Groq + Llama
│   ├── session_store.py       # histórico de conversa (in-memory, Redis-ready)
│   ├── rate_limiter.py        # limite por IP/sessão (slowapi)
│   ├── sanitizer.py           # validação + proteção a prompt injection
│   └── audit_logger.py        # logs estruturados
├── prompts/
│   └── system_prompt.py       # prompt institucional CEFET/RJ
├── models/
│   └── schemas.py             # Pydantic
├── config/
│   └── settings.py            # pydantic-settings (.env)
├── main.py                    # FastAPI app + CORS + middlewares
├── requirements.txt
└── Dockerfile

docker/
└── Dockerfile.frontend        # build do TanStack Start

docker-compose.yml             # orquestra backend + frontend
.env.example
README.md (atualizado)
docs/
├── ANALISE_INICIAL.md         # este arquivo
└── RELATORIO_TECNICO.md       # entregue na Etapa 4
```

### 4.3 Boas práticas adotadas

- **SOLID / Clean Code**: cada serviço Python com uma única responsabilidade,
  injetado via FastAPI `Depends()`.
- **Configuração externa**: `pydantic-settings` lê `.env` — zero segredo no
  código.
- **Validação dupla**: Zod no frontend + Pydantic no backend.
- **Sessões opacas**: UUID gerado e armazenado no `localStorage`.
- **Persistência plugável**: store em memória por padrão, com interface
  preparada para Redis.
- **Logs estruturados** com `structlog` para auditoria.
- **Identidade visual**: nenhum token CSS, asset ou componente shadcn é
  alterado — apenas reutilizados.

---

## 5. Arquivos que serão **modificados**

| Arquivo | Motivo |
| --- | --- |
| `src/lib/chatbot.functions.ts` | Substituir placeholder por proxy ao backend FastAPI |
| `src/lib/config.server.ts` | Adicionar variáveis `CHATBOT_API_URL` e `CHATBOT_API_KEY` |
| `src/components/ChatWidget.tsx` | Persistir `session_id` no `localStorage` e ajustar mensagem inicial |
| `src/routes/__root.tsx` | (Opcional) atualizar `<title>` para *Suporte Inteligente CEFET/RJ* |
| `package.json` | (Opcional) script `dev:full` para subir front+back |
| `.gitignore` | Adicionar `__pycache__/`, `.venv/`, `backend/.env` |
| `README.md` | Reescrito com instruções completas |

## 6. Arquivos que serão **criados**

- `backend/` — todo o backend FastAPI (ver §4.2).
- `docker/Dockerfile.frontend` — build do TanStack Start em container.
- `docker-compose.yml` — orquestração.
- `.env.example` — *template* das variáveis (sem segredos).
- `docs/ANALISE_INICIAL.md` — este arquivo.
- `docs/RELATORIO_TECNICO.md` — entrega final.

---

## 7. Compatibilidade e Riscos

| Risco | Mitigação |
| --- | --- |
| Deploy do TanStack Start em Cloudflare Workers não suporta libs Node nativas | Manter a camada Python isolada; a server function só faz `fetch` |
| Variáveis de ambiente em Workers ligam por request | Já tratado pelo `getServerConfig()` existente |
| Quebra da identidade visual | Nenhum token CSS é alterado; apenas reuso |
| Rate-limit afetar usuários legítimos | Limites configuráveis via `.env`, padrão generoso |
| Vazamento de chave Groq | Chave mora apenas no backend Python; frontend nunca a vê |

---

## 8. Próximas Etapas

1. **Etapa 2** — Reaproveitamento dos componentes visuais existentes
   (`ChatWidget`, mascote, paleta) sem duplicação.
2. **Etapa 3** — Implementação do backend FastAPI + integração Groq/Llama com
   prompt institucional, sessões, segurança e auditoria.
3. **Etapa 4** — Geração do `RELATORIO_TECNICO.md` e do README definitivo.

A análise está concluída. Pode-se prosseguir com as alterações.
