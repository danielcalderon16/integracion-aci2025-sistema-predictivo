import { cookies } from "next/headers";
import { COOKIE_NAME } from "@/lib/constants";

const BACKEND_URL =
  process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getToken(): Promise<string | null> {
  const store = await cookies();
  return store.get(COOKIE_NAME)?.value ?? null;
}

/** Llama al backend FastAPI adjuntando el token del usuario (si existe). Uso server-side únicamente. */
export async function backendFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const token = await getToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");

  return fetch(`${BACKEND_URL}${path}`, { ...init, headers, cache: "no-store" });
}

export async function getCurrentUser() {
  const res = await backendFetch("/auth/me");
  if (!res.ok) return null;
  return res.json();
}
