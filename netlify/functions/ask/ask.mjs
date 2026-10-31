// Netlify Function: POST /api/ask -> Flare AI Intelligence Lab answer.
// The Anthropic API key lives ONLY in the Netlify environment variable ANTHROPIC_API_KEY (scope: Functions).
// It is never in the repository, in site/ or in anything the browser downloads.
import Anthropic from "@anthropic-ai/sdk";
import { getStore } from "@netlify/blobs";
import { handle } from "./core.mjs";

const client = new Anthropic(); // reads ANTHROPIC_API_KEY from the function's environment

function kvStore() {
  const s = getStore("flare-ai-lab");
  return {
    get: (k) => s.get(k, { type: "json" }),
    set: (k, v) => s.setJSON(k, v),
  };
}

export default async (req, context) => {
  if (!process.env.ANTHROPIC_API_KEY) {
    return new Response(JSON.stringify({ error: "The Lab is not configured on this deployment." }), { status: 503, headers: { "content-type": "application/json" } });
  }
  // Only the site itself may call this endpoint from a browser. URL / DEPLOY_PRIME_URL are set by Netlify.
  const allowedOrigins = [process.env.URL, process.env.DEPLOY_PRIME_URL, process.env.ALLOWED_ORIGIN].filter(Boolean);
  try {
    return await handle(req, { client, store: kvStore(), ip: context.ip, allowedOrigins });
  } catch (err) {
    // Fail closed: if the rate-limit store is unavailable, refuse rather than call the API without limits.
    return new Response(JSON.stringify({ error: "The Lab is temporarily unavailable." }), { status: 503, headers: { "content-type": "application/json" } });
  }
};

export const config = { path: "/api/ask" };
