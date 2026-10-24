import { backendFetch } from "@/lib/api";

export async function POST(req: Request) {
  const body = await req.text();
  const res = await backendFetch("/prediccion", { method: "POST", body });
  const data = await res.json();
  return Response.json(data, { status: res.status });
}
