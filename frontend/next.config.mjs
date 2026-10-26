/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**" },
      { protocol: "http", hostname: "**" }
    ],
  },
  // Ofertas Relâmpago desligadas por enquanto: redirecionamento temporário (307)
  async redirects() {
    return [{ source: "/ofertas-relampago", destination: "/", permanent: false }];
  },
};

export default nextConfig;
