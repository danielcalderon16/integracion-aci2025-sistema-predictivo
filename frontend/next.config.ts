import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // "standalone" es necesario para el build de Docker (docker-compose
  // local), pero rompe el build nativo de Vercel — Vercel define la
  // variable de entorno VERCEL automáticamente, así que la desactivamos ahí.
  output: process.env.VERCEL ? undefined : "standalone",
};

export default nextConfig;
