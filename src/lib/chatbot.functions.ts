import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

const MessageSchema = z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string().min(1).max(4000),
});

const ChatInput = z.object({
  message: z.string().min(1).max(4000),
  history: z.array(MessageSchema).max(50).optional().default([]),
});

export type ChatMessage = z.infer<typeof MessageSchema>;

/**
 * sendChatMessage — entry point for the chatbot.
 *
 * This server function is the connection boundary between the UI and the
 * backend that will handle the chatbot logic (e.g. Lovable AI Gateway,
 * a custom LLM, a rule-based engine, or an external API).
 *
 * To wire a real backend, replace the placeholder reply below with the
 * actual call (e.g. fetch to an internal service, AI SDK streamText, etc.).
 */
export const sendChatMessage = createServerFn({ method: "POST" })
  .inputValidator((data: unknown) => ChatInput.parse(data))
  .handler(async ({ data }) => {
    // TODO: integrar com o backend real do chatbot do CEFET/RJ.
    // Exemplo de pontos de extensão:
    //   - process.env.CHATBOT_API_URL
    //   - process.env.CHATBOT_API_KEY
    //
    // const res = await fetch(process.env.CHATBOT_API_URL!, {
    //   method: "POST",
    //   headers: {
    //     "Content-Type": "application/json",
    //     Authorization: `Bearer ${process.env.CHATBOT_API_KEY}`,
    //   },
    //   body: JSON.stringify({ message: data.message, history: data.history }),
    // });
    // const json = await res.json();
    // return { reply: json.reply as string };

    const reply =
      "Olá! 👋 Sou o Suporte Inteligente do CEFET/RJ Campus Nova Iguaçu. " +
      "O backend ainda não foi conectado, mas sua mensagem foi recebida: " +
      `"${data.message}". Em breve poderei responder com informações reais.`;

    return { reply };
  });
