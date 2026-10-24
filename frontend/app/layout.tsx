import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { getCurrentUser } from "@/lib/api";
import NavBar from "@/components/NavBar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Plataforma ACI 2025 + Predicción IA",
  description: "Calculadora de diseño de mezcla ACI 2025 integrada con predicción de resistencia por IA",
};

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const usuario = await getCurrentUser();

  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900">
        <NavBar usuario={usuario} />
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
