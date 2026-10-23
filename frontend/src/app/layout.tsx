import type { Metadata } from "next";
import { Inter } from "next/font/google";
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
  return (
    <html lang="pt-BR" className={inter.variable}>
      <body className="font-sans antialiased bg-[#080c14] text-gray-100 flex flex-col min-h-screen">
        <Header />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        
        {/* Footer */}
        <footer className="border-t border-white/[0.06] bg-[#05080e] py-8 mt-12 text-gray-400 text-xs">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-5">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg flame-gradient flex items-center justify-center text-white font-bold shadow-sm">
                <Flame className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-white text-sm">Que Promo</span>
                <p className="text-[11px] text-gray-400">quepromo.com.br • Radar de ofertas e menores preços</p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-5 text-xs text-gray-400">
              <Link href="/" className="hover:text-white transition-colors">Ofertas</Link>
              <Link href="/radar" className="hover:text-rose-400 transition-colors">Radar de Quedas</Link>
              <Link href="/busca-personalizada" className="hover:text-cyan-400 transition-colors">Busca Personalizada</Link>
              <Link href="/lojas" className="hover:text-blue-400 transition-colors">Lojas Parceiras</Link>
              <Link href="/admin" className="hover:text-emerald-400 transition-colors text-[11px] opacity-75 hover:opacity-100">Painel Afiliados</Link>
            </div>

            <div className="text-[11px] text-gray-400 text-center md:text-right">
              <p>Valores e estoques consultados em tempo real.</p>
              <p className="flex items-center justify-center md:justify-end gap-1 mt-0.5 text-gray-400">
                Feito com <Heart className="w-3 h-3 text-rose-500 fill-rose-500 inline" /> para quem busca economia real.
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
