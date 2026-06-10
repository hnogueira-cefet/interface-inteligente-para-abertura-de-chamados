import { createFileRoute } from "@tanstack/react-router";
import { Clock, Sparkles, ShieldCheck, Landmark, Users, GraduationCap } from "lucide-react";
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
    <div className="flex items-center gap-3">
      <div className="w-11 h-11 rounded-md bg-gradient-to-br from-brand-blue to-brand-navy flex items-center justify-center text-white font-bold text-lg shadow-sm">
        TE
      </div>
      <div className="leading-tight">
        <div className="font-bold text-brand-navy-deep text-base">CEFET/RJ</div>
        <div className="text-[10px] text-muted-foreground max-w-[180px]">
          Centro Federal de Educação Tecnológica
          <br />
          Celso Suckow da Fonseca
          <br />
          Campus Nova Iguaçu
        </div>
      </div>
    </div>
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
        <div className="relative max-w-7xl mx-auto px-6 py-12 grid lg:grid-cols-[1fr_auto] gap-8 items-center">
          {/* Left content + mascot */}
          <div className="relative grid md:grid-cols-2 gap-6 items-end min-h-[520px]">
            <div className="text-white z-10">
              <h1 className="font-extrabold leading-[0.95] tracking-tight">
                <span className="block text-6xl md:text-7xl">Suporte</span>
                <span className="block text-6xl md:text-7xl text-brand-blue-light">
                  Inteligente
                </span>
              </h1>
              <p className="mt-6 text-white/85 text-base max-w-md leading-relaxed">
                O Suporte Inteligente do CEFET/RJ Campus Nova Iguaçu está aqui para
                ajudar você com informações, serviços e orientações.
              </p>

              <div className="mt-8 flex flex-wrap gap-6">
                <Feature icon={Clock} title="Atendimento" subtitle="24 horas" />
                <Feature icon={Sparkles} title="Respostas" subtitle="Inteligentes" />
                <Feature icon={ShieldCheck} title="Informações" subtitle="Confiáveis" />
              </div>

            </div>

            <div className="relative hidden md:block">
              <img
                src={mascot}
                alt="Mascote do Suporte Inteligente CEFET/RJ"
                width={896}
                height={1216}
                className="relative z-10 w-full max-w-md mx-auto drop-shadow-2xl"
              />
            </div>
          </div>

          {/* Chat */}
          <div className="lg:w-[400px] w-full mx-auto">
            <ChatWidget />
          </div>
        </div>

        {/* Stats strip */}
        <div className="relative bg-brand-navy-deep/60 backdrop-blur border-t border-white/10">
          <div className="max-w-7xl mx-auto px-6 py-4 flex flex-wrap gap-8 text-white">
            <Stat icon={Landmark} value="+110" label="Anos de história" />
            <Stat icon={Users} value="+50.000" label="Estudantes formados" />
            <Stat icon={GraduationCap} value="Educação pública" label="de qualidade" />
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

function Stat({
  icon: Icon,
  value,
  label,
}: {
  icon: React.ComponentType<{ className?: string }>;
  value: string;
  label: string;
}) {
  return (
    <div className="flex items-center gap-3">
      <Icon className="w-6 h-6 text-brand-blue-light" />
      <div className="leading-tight">
        <div className="font-bold">{value}</div>
        <div className="text-xs text-white/75">{label}</div>
      </div>
    </div>
  );
}
