import { cookies } from "next/headers";
import { COOKIE_NAME } from "@/lib/constants";

const BACKEND_URL =
  process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function POST(req: Request) {
  const body = await req.json();

  const backendRes = await fetch(`${BACKEND_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });

  if (!backendRes.ok) {
    const error = await backendRes.json().catch(() => ({ detail: "No se pudo iniciar sesión" }));
    return Response.json(error, { status: backendRes.status });
  }

  const data = await backendRes.json();
  const store = await cookies();
  store.set(COOKIE_NAME, data.access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24,
  });

  return Response.json({ ok: true });
}
