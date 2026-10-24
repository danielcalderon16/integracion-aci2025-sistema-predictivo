import { backendFetch } from "@/lib/api";

export async function GET() {
  const res = await backendFetch("/usuarios");
  const data = await res.json();
  return Response.json(data, { status: res.status });
}
