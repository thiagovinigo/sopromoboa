import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import Header from "@/components/Header";
import Link from "next/link";
import { Flame, Shield, Heart } from "lucide-react";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Que Promo | Radar de Quedas de Preço & Ofertas Reais",
  description: "Monitore promoções que realmente baixaram de preço no Brasil. Histórico real, comparador entre lojas, alertas de desconto e links de afiliados auditados no quepromo.com.br.",
  keywords: ["promoções", "descontos", "queda de preço", "radar de ofertas", "menor preço histórico", "ofertas amazon", "mercado livre", "magalu", "quepromo"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const adsenseClientId = process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID;

  return (
    <html lang="pt-BR" className={inter.variable}>
      <head>
        <meta
          name="google-site-verification"
          content="uTn_GeyjT7ROB0RmOi0nokWQQP8ulF8kakooicAcv-Y"
        />
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8215576310884543"
          crossOrigin="anonymous"
        />
      </head>
      <body className="font-sans antialiased bg-[#080c14] text-gray-100 flex flex-col min-h-screen">
        <Header />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        
        {/* Footer Institucional & Conformidade Google AdSense */}
        <footer className="border-t border-white/[0.06] bg-[#05080e] py-10 mt-12 text-gray-400 text-xs">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
            <div className="flex flex-col md:flex-row items-center justify-between gap-5 border-b border-white/[0.06] pb-6">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg flame-gradient flex items-center justify-center text-white font-bold shadow-sm">
                  <Flame className="w-4 h-4" />
                </div>
                <div>
                  <span className="font-bold text-white text-sm">Que Promo</span>
                  <p className="text-[11px] text-gray-400">quepromo.com.br • Radar de ofertas e menores preços auditados</p>
                </div>
              </div>

              <div className="flex flex-wrap items-center justify-center gap-4 text-xs">
                <Link href="/" className="hover:text-white transition-colors">Ofertas</Link>
                <Link href="/ofertas-relampago" className="text-amber-400 hover:text-amber-300 transition-colors font-medium">⚡ Ofertas Relâmpago</Link>
                <Link href="/radar" className="hover:text-rose-400 transition-colors">Radar de Quedas</Link>
                <Link href="/busca-personalizada" className="hover:text-cyan-400 transition-colors">Busca Personalizada</Link>
                <Link href="/lojas" className="hover:text-blue-400 transition-colors">Lojas Parceiras</Link>
              </div>
            </div>

            <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-[11px] text-gray-400">
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-4">
                <Link href="/sobre-nos" className="hover:text-white transition-colors">Sobre Nós</Link>
                <Link href="/contato" className="hover:text-white transition-colors">Contato & Suporte</Link>
                <Link href="/politica-de-privacidade" className="hover:text-emerald-400 transition-colors">Política de Privacidade</Link>
                <Link href="/termos-de-uso" className="hover:text-blue-400 transition-colors">Termos de Uso</Link>
                <Link href="/admin" className="hover:text-purple-400 transition-colors opacity-75 hover:opacity-100">Painel Administrativo</Link>
              </div>

              <div className="text-center md:text-right">
                <p>© {new Date().getFullYear()} Que Promo. Todos os direitos reservados.</p>
                <p className="mt-0.5 text-gray-400">
                  Valores consultados em tempo real com auditoria de menores preços.
                </p>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
