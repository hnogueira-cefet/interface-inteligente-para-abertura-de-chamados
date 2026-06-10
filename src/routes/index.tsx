import { createFileRoute } from "@tanstack/react-router";
import { Clock, Sparkles, ShieldCheck } from "lucide-react";
import { ChatWidget } from "@/components/ChatWidget";
import mascot from "@/assets/mascot.png";
import cefetLogo from "@/assets/cefet-logo.png";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Suporte Inteligente — CEFET/RJ Campus Nova Iguaçu" },
      {
        name: "description",
        content:
          "O Suporte Inteligente do CEFET/RJ Campus Nova Iguaçu ajuda você com informações, serviços e orientações 24 horas.",
      },
      { property: "og:title", content: "Suporte Inteligente — CEFET/RJ Campus Nova Iguaçu" },
      {
        property: "og:description",
        content:
          "Atendimento 24h, respostas inteligentes e informações confiáveis sobre cursos, processos e serviços do CEFET/RJ.",
      },
    ],
  }),
  component: Home,
});



function Logo() {
  return (
    <img
      src={cefetLogo}
      alt="CEFET/RJ - Centro Federal de Educação Tecnológica Celso Suckow da Fonseca - Campus Nova Iguaçu"
      className="h-14 w-auto"
    />
  );
}

function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-white border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center">
          <Logo />
        </div>
      </header>

      {/* Hero */}
      <section
        className="relative overflow-hidden"
        style={{ background: "var(--gradient-hero)" }}
      >
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage:
              "radial-gradient(circle at 20% 20%, white 0%, transparent 40%), radial-gradient(circle at 80% 70%, white 0%, transparent 40%)",
          }}
        />
        <div className="relative max-w-7xl mx-auto px-6 py-12 grid gap-6 items-stretch lg:grid-cols-[35fr_32.5fr_32.5fr]">
          {/* Col 1: Card Institucional */}
          <div
            className="relative rounded-3xl border border-white/15 p-8 md:p-10 flex flex-col justify-center text-white h-[700px] max-lg:h-auto max-lg:min-h-[420px] max-sm:min-h-0 max-sm:p-6"
            style={{
              background: "linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.03))",
              backdropFilter: "blur(14px)",
              WebkitBackdropFilter: "blur(14px)",
              boxShadow: "var(--shadow-chat)",
            }}
          >
            <h1 className="font-extrabold leading-[0.95] tracking-tight">
              <span className="block text-4xl md:text-5xl lg:text-6xl">Suporte</span>
              <span className="block text-4xl md:text-5xl lg:text-6xl text-brand-blue-light">
                Inteligente
              </span>
            </h1>
            <p className="mt-6 text-white/85 text-base leading-relaxed">
              O Suporte Inteligente do CEFET/RJ Campus Nova Iguaçu está aqui para
              ajudar você com informações, serviços e orientações.
            </p>

            <div className="mt-8 flex flex-wrap gap-5">
              <Feature icon={Clock} title="Atendimento" subtitle="24 horas" />
              <Feature icon={Sparkles} title="Respostas" subtitle="Inteligentes" />
              <Feature icon={ShieldCheck} title="Informações" subtitle="Confiáveis" />
            </div>
          </div>

          {/* Col 2: Card Avatar */}
          <div
            className="relative rounded-3xl overflow-hidden flex items-center justify-center p-6 h-[700px] max-lg:h-[420px] max-sm:h-[300px] border border-white/15 w-full"
            style={{
              background: "linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.03))",
              backdropFilter: "blur(14px)",
              WebkitBackdropFilter: "blur(14px)",
              boxShadow: "var(--shadow-chat)",
            }}
          >
            <img
              src={mascot}
              alt="Mascote do Suporte Inteligente CEFET/RJ"
              className="max-h-full max-w-full w-auto h-auto object-contain drop-shadow-2xl"
            />
          </div>

          {/* Col 3: Card Chatbot */}
          <div className="h-[700px] max-sm:h-[600px] flex w-full">
            <ChatWidget />
          </div>
        </div>

      </section>
    </div>
  );
}

function Feature({
  icon: Icon,
  title,
  subtitle,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  subtitle: string;
}) {
  return (
    <div className="flex items-center gap-2.5">
      <div className="w-10 h-10 rounded-full bg-white/10 ring-1 ring-white/20 flex items-center justify-center">
        <Icon className="w-5 h-5 text-white" />
      </div>
      <div className="text-sm leading-tight">
        <div className="font-semibold">{title}</div>
        <div className="text-white/75">{subtitle}</div>
      </div>
    </div>
  );
}

