import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

import { getServerConfig } from "./config.server";

const MessageSchema = z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string().min(1).max(4000),
});

const ChatInput = z.object({
  session_id: z
    .string()
    .min(8)
    .max(128)
    .regex(/^[A-Za-z0-9_-]+$/u, "session_id contém caracteres inválidos"),
  message: z.string().min(1).max(4000),
  history: z.array(MessageSchema).max(50).optional().default([]),
});

export type ChatMessage = z.infer<typeof MessageSchema>;
export type ChatInputData = z.infer<typeof ChatInput>;

/**
 * sendChatMessage — entry point for the chatbot.
 *
 * Atua como **proxy server-side** entre o navegador e o backend FastAPI do
 * Suporte Inteligente CEFET/RJ.
 *
 * Por que server function?
 *   - A chave da API (X-API-Token) NUNCA chega ao navegador.
 *   - Permite acrescentar middlewares (rate limit, logging) no edge.
 *   - Mantém a UI desacoplada do endpoint real (apenas troca de URL).
 *
 * Endpoint chamado: POST {CHATBOT_API_URL}
 * Body enviado:    { session_id, message, history }
 * Resposta:        { response, reply, session_id, model }
 */
export const sendChatMessage = createServerFn({ method: "POST" })
  .inputValidator(ChatInput)
  .handler(async ({ data }) => {
    const config = getServerConfig();

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), config.chatbotTimeoutMs);

    try {
      const res = await fetch(config.chatbotApiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(config.chatbotApiKey ? { "X-API-Token": config.chatbotApiKey } : {}),
        },
        body: JSON.stringify({
          session_id: data.session_id,
          message: data.message,
          history: data.history,
        }),
        signal: controller.signal,
      });

      if (!res.ok) {
        if (res.status === 429) {
          return {
            reply:
              "Você enviou muitas mensagens em pouco tempo. Aguarde alguns instantes e tente novamente.",
          };
        }
        const text = await res.text().catch(() => "");
        console.error("[chatbot] backend returned non-2xx", res.status, text);
        return {
          reply:
            "Desculpe, o serviço está temporariamente indisponível. Tente novamente em instantes.",
        };
      }

      const json = (await res.json()) as { response?: string; reply?: string };
      const reply = json.response ?? json.reply ?? "";
      if (!reply) {
        return {
          reply:
            "Não consegui gerar uma resposta agora. Pode tentar reformular sua mensagem?",
        };
      }
      return { reply };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.error("[chatbot] proxy error", message);
      return {
        reply:
          "Tive um problema ao falar com o serviço de atendimento. Tente novamente em instantes.",
      };
    } finally {
      clearTimeout(timeout);
    }
  });
