import { useServerFn } from "@tanstack/react-start";
import { useEffect, useRef, useState } from "react";
import { Send, Volume2, MoreVertical, BookOpen, FileText, GraduationCap, Building2, MessageCircle } from "lucide-react";
import { sendChatMessage, type ChatMessage } from "@/lib/chatbot.functions";
import mascot from "@/assets/mascot.png";

const QUICK_ACTIONS = [
  { icon: BookOpen, label: "Informações sobre cursos" },
  { icon: FileText, label: "Processos seletivos" },
  { icon: GraduationCap, label: "Serviços acadêmicos" },
  { icon: Building2, label: "Unidades e setores" },
  { icon: MessageCircle, label: "Outros assuntos" },
];

export function ChatWidget() {
  const send = useServerFn(sendChatMessage);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Olá! 👋\nSou o Suporte Inteligente do CEFET/RJ Campus Nova Iguaçu. Como posso ajudar?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function submit(text: string) {
    const content = text.trim();
    if (!content || loading) return;
    const userMsg: ChatMessage = { role: "user", content };
    const next = [...messages, userMsg];
    setMessages(next);
    setInput("");
    setLoading(true);
    try {
      const res = await send({ data: { message: content, history: messages.slice(-20) } });
      setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Desculpe, tive um problema ao processar sua mensagem. Tente novamente." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="w-full max-w-[400px] rounded-2xl bg-white overflow-hidden flex flex-col"
      style={{ boxShadow: "var(--shadow-chat)" }}
    >
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-border bg-white">
        <div className="relative">
          <img src={mascot} alt="" className="w-10 h-10 rounded-full object-cover bg-brand-navy" />
          <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-500 ring-2 ring-white" />
        </div>
        <div className="flex-1">
          <div className="font-semibold text-foreground text-sm">Suporte Inteligente</div>
          <div className="text-xs text-emerald-600 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Online
          </div>
        </div>
        <button className="text-muted-foreground hover:text-foreground p-1" aria-label="Som">
          <Volume2 className="w-5 h-5" />
        </button>
        <button className="text-muted-foreground hover:text-foreground p-1" aria-label="Mais">
          <MoreVertical className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-3 max-h-[340px] min-h-[260px] bg-white">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={
                m.role === "user"
                  ? "max-w-[80%] rounded-2xl rounded-br-sm px-4 py-2.5 bg-brand-blue text-white text-sm whitespace-pre-line"
                  : "max-w-[85%] rounded-2xl rounded-tl-sm px-4 py-2.5 bg-brand-navy-deep text-white text-sm whitespace-pre-line"
              }
            >
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-tl-sm px-4 py-2.5 bg-brand-navy-deep/80 text-white text-sm">
              <span className="inline-flex gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-white/70 animate-bounce" />
                <span className="w-1.5 h-1.5 rounded-full bg-white/70 animate-bounce [animation-delay:120ms]" />
                <span className="w-1.5 h-1.5 rounded-full bg-white/70 animate-bounce [animation-delay:240ms]" />
              </span>
            </div>
          </div>
        )}

        {messages.length === 1 && (
          <div className="space-y-2 pt-1">
            {QUICK_ACTIONS.map((a) => (
              <button
                key={a.label}
                onClick={() => submit(a.label)}
                className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg border border-border bg-white hover:bg-secondary text-left text-sm text-foreground transition-colors"
              >
                <a.icon className="w-4 h-4 text-brand-blue" />
                {a.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit(input);
        }}
        className="border-t border-border bg-white px-3 py-3"
      >
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua mensagem..."
            className="flex-1 px-4 py-2.5 rounded-full bg-secondary text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-brand-blue/40"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="w-10 h-10 rounded-full bg-brand-blue text-white flex items-center justify-center disabled:opacity-50 hover:bg-brand-blue/90 transition-colors"
            aria-label="Enviar"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-center text-xs text-muted-foreground mt-2">
          Desenvolvido pelo CEFET/RJ <span className="text-red-500">♥</span>
        </p>
      </form>
    </div>
  );
}
