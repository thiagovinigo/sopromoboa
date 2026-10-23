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
      <body className="font-sans antialiased bg-[#0b0f19] text-gray-100 flex flex-col min-h-screen">
        <Header />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        
        {/* Footer */}
        <footer className="border-t border-gray-800 bg-[#080c14] py-10 mt-16 text-gray-400 text-xs">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg flame-gradient flex items-center justify-center text-white font-bold">
                <Flame className="w-5 h-5" />
              </div>
              <div>
                <span className="font-bold text-white text-sm">Que Promo</span>
                <p className="text-[11px] text-gray-400">quepromo.com.br • O radar oficial de ofertas e preços baixos.</p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-6 text-xs text-gray-400">
              <Link href="/" className="hover:text-white transition-colors">Todas as Ofertas</Link>
              <Link href="/radar" className="hover:text-rose-400 transition-colors">Radar de Quedas</Link>
              <Link href="/afiliados" className="hover:text-emerald-400 transition-colors">Gestão de Afiliados</Link>
              <Link href="/busca-personalizada" className="hover:text-cyan-400 transition-colors">Busca Personalizada</Link>
            </div>

            <div className="text-[11px] text-gray-400 text-center md:text-right">
              <p>Os preços e estoques podem variar conforme as lojas de origem.</p>
              <p className="flex items-center justify-center md:justify-end gap-1 mt-1 text-gray-400">
                Feito com <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500 inline" /> para quem busca economia real.
              </p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
