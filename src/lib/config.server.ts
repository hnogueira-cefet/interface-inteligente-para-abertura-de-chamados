import process from "node:process";

// Server-only config. The .server.ts suffix prevents Vite from bundling
// this file into the client — values here never reach the browser.
//
// On Cloudflare Workers, env binds at REQUEST time. Module-scope reads
// (e.g. `const x = process.env.X`) resolve to undefined — always read
// process.env INSIDE a function or handler.
//
// When to use which env-access pattern:
//   - .server.ts module (this file): server-only helpers reused across
//     handlers. Wrap reads in a function so they run per-request.
//   - inline process.env inside a createServerFn handler: one-off reads
//     not reused elsewhere.
//   - import.meta.env.VITE_FOO: PUBLIC config readable from both client
//     and server (analytics IDs, public URLs). Define in .env with the
//     VITE_ prefix. Never put secrets here — they ship to the browser.

export function getServerConfig() {
  return {
    nodeEnv: process.env.NODE_ENV,
    // Configuração do backend FastAPI (Suporte Inteligente CEFET/RJ).
    // CHATBOT_API_URL deve apontar para o endpoint /chat do backend.
    // CHATBOT_API_KEY (opcional) é repassada no header X-API-Token.
    chatbotApiUrl: process.env.CHATBOT_API_URL ?? "http://localhost:8000/chat",
    chatbotApiKey: process.env.CHATBOT_API_KEY ?? "",
    chatbotTimeoutMs: Number(process.env.CHATBOT_TIMEOUT_MS ?? 30000),
  };
}
