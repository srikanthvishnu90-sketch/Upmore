// delete-account: real auth-account deletion (beta 2026-09-24).
// Verifies the caller's JWT, then deletes their auth user via the GoTrue
// admin API. App-table rows cascade from auth.users (verified 2026-09-24).
// The client wipes app data first for immediacy; this removes the account
// itself so the user cannot sign back in.
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response("method not allowed", { status: 405 });
  }
  const auth = req.headers.get("Authorization") || "";
  const jwt = auth.replace(/^Bearer\s+/i, "");
  if (!jwt) return new Response("missing auth", { status: 401 });

  // Verify the JWT and resolve the user id
  const meRes = await fetch(`${SUPABASE_URL}/auth/v1/user`, {
    headers: { apikey: SERVICE_KEY, Authorization: `Bearer ${jwt}` },
  });
  if (!meRes.ok) return new Response("invalid session", { status: 401 });
  const me = await meRes.json();
  const uid = me.id;
  if (!uid) return new Response("no user", { status: 401 });

  // Optional explicit confirmation body { confirm: "DELETE" }
  let body: any = {};
  try { body = await req.json(); } catch { /* empty body ok */ }
  if (body.confirm && String(body.confirm).toUpperCase() !== "DELETE") {
    return new Response("confirmation mismatch", { status: 400 });
  }

  // Delete the auth user (cascades to profiles, threads, messages, etc.)
  const delRes = await fetch(`${SUPABASE_URL}/auth/v1/admin/users/${uid}`, {
    method: "DELETE",
    headers: { apikey: SERVICE_KEY, Authorization: `Bearer ${SERVICE_KEY}` },
  });
  if (!delRes.ok) {
    const t = await delRes.text().catch(() => "");
    return new Response(`delete failed: ${t.slice(0, 200)}`, { status: 502 });
  }
  return new Response(JSON.stringify({ deleted: true, user_id: uid }), {
    headers: { "Content-Type": "application/json" },
  });
});
