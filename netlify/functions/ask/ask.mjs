// Netlify Function: POST /api/ask -> Flare AI Intelligence Lab answer.
// The provider key lives ONLY in a Netlify environment variable (secret, Production only):
//   GEMINI_API_KEY    -> Google Gemini answers (model: GEMINI_MODEL, default in gemini.mjs)
//   ANTHROPIC_API_KEY -> Claude answers (used only if no Gemini key is set)
// Keys are never in the repository, in site/ or in anything the browser downloads.
import { getStore } from "@netlify/blobs";
import { handle } from "./core.mjs";
import { geminiClient } from "./gemini.mjs";

let client = null;
async function getClient() {
  if (client) return client;
  if (process.env.GEMINI_API_KEY) {
    client = geminiClient({ apiKey: process.env.GEMINI_API_KEY, model: process.env.GEMINI_MODEL || undefined });
  } else if (process.env.ANTHROPIC_API_KEY) {
    const { default: Anthropic } = await import("@anthropic-ai/sdk");
    client = new Anthropic(); // reads ANTHROPIC_API_KEY from the function's environment
  }
  return client;
}

function kvStore() {
  const s = getStore("flare-ai-lab");
  return {
    get: (k) => s.get(k, { type: "json" }),
    set: (k, v) => s.setJSON(k, v),
  };
}

export default async (req, context) => {
  const c = await getClient();
  if (!c) {
    return new Response(JSON.stringify({ error: "The Lab is not configured on this deployment." }), { status: 503, headers: { "content-type": "application/json" } });
  }
  // Only the site itself may call this endpoint from a browser. URL / DEPLOY_PRIME_URL are set by Netlify.
  const allowedOrigins = [process.env.URL, process.env.DEPLOY_PRIME_URL, process.env.ALLOWED_ORIGIN].filter(Boolean);
  try {
    return await handle(req, { client: c, store: kvStore(), ip: context.ip, allowedOrigins });
  } catch (err) {
    // Fail closed: if the rate-limit store is unavailable, refuse rather than call the API without limits.
    return new Response(JSON.stringify({ error: "The Lab is temporarily unavailable." }), { status: 503, headers: { "content-type": "application/json" } });
  }
};

export const config = { path: "/api/ask" };
