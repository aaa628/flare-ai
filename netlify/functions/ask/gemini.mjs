// Google Gemini adapter for the Intelligence Lab.
// core.mjs calls `client.beta.messages.create(params)` (the Claude request shape). This adapter takes the same
// params, sends them to the Gemini API (generateContent) and returns a Claude-shaped response, so core.mjs, its
// citation checks and its limits stay exactly the same whichever provider answers.
// The key comes ONLY from the Netlify environment variable GEMINI_API_KEY (secret, Production only). It is sent in a
// request header, never in the URL, so it cannot end up in logs.

export const GEMINI_DEFAULT_MODEL = "gemini-flash-latest"; // Google's alias for the current Flash model; override with GEMINI_MODEL
const ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/";

/* Gemini's schema support is a subset of JSON Schema. Drop keywords it may reject; core.mjs validates the answer anyway. */
export function geminiSchema(s) {
  if (Array.isArray(s)) return s.map(geminiSchema);
  if (!s || typeof s !== "object") return s;
  const out = {};
  for (const [k, v] of Object.entries(s)) {
    if (k === "additionalProperties") continue;
    out[k] = typeof v === "object" ? geminiSchema(v) : v;
  }
  if (out.properties) out.properties = Object.fromEntries(Object.entries(s.properties).map(([k, v]) => [k, geminiSchema(v)]));
  return out;
}

const STOP = { STOP: "end_turn", MAX_TOKENS: "max_tokens", SAFETY: "refusal", RECITATION: "refusal", BLOCKLIST: "refusal",
  PROHIBITED_CONTENT: "refusal", SPII: "refusal", IMAGE_SAFETY: "refusal" };

// Netlify's free plan stops a function after about 10 seconds, so the whole Gemini exchange must finish well inside that.
export const GEMINI_DEADLINE_MS = 8500;

/* Request variants, fastest first. Gemini 3 models take thinkingLevel; 2.5 models take thinkingBudget. A model that rejects
   a field answers 400 at once, so the next variant is tried; the last one sends no optional fields at all. */
const VARIANTS = [
  { schema: true, thinking: { thinkingLevel: "minimal" } },
  { schema: true, thinking: { thinkingBudget: 0 } },
  { schema: true, thinking: null },
  { schema: false, thinking: null },
];

export function geminiClient({ apiKey, model = GEMINI_DEFAULT_MODEL, fetchImpl = fetch, deadlineMs = GEMINI_DEADLINE_MS }) {
  function call(params, v, signal) {
    const schema = params.output_config?.format?.schema;
    const withSchema = v.schema && schema;
    const body = {
      systemInstruction: { parts: [{ text: params.system + (!withSchema && schema ? "\nReply with JSON only, matching this JSON Schema:\n" + JSON.stringify(schema) : "") }] },
      contents: params.messages.map((m) => ({ role: m.role === "assistant" ? "model" : "user", parts: [{ text: m.content }] })),
      generationConfig: {
        maxOutputTokens: 4096, // answers are short (at most 8 points); a low cap also keeps the reply fast
        temperature: 0.2,
        responseMimeType: "application/json",
        ...(withSchema ? { responseJsonSchema: geminiSchema(schema) } : {}),
        ...(v.thinking ? { thinkingConfig: v.thinking } : {}),
      },
    };
    return fetchImpl(ENDPOINT + encodeURIComponent(model) + ":generateContent", {
      method: "POST",
      headers: { "content-type": "application/json", "x-goog-api-key": apiKey },
      body: JSON.stringify(body),
      signal,
    });
  }
  async function create(params) {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), deadlineMs);
    let res;
    try {
      for (const v of VARIANTS) {
        res = await call(params, v, ctl.signal);
        if (res.status !== 400) break;
      }
      if (!res.ok) { const e = new Error("Gemini API error " + res.status); e.status = res.status; throw e; }
      var data = await res.json();
    } catch (err) {
      if (ctl.signal.aborted) { const e = new Error("Gemini took too long"); e.status = 504; throw e; }
      throw err;
    } finally { clearTimeout(timer); }
    const used = data.modelVersion || model;
    if (data.promptFeedback?.blockReason) return { stop_reason: "refusal", model: used, content: [] };
    const cand = (data.candidates || [])[0];
    if (!cand) return { stop_reason: "refusal", model: used, content: [] };
    const text = (cand.content?.parts || []).filter((p) => typeof p.text === "string" && !p.thought).map((p) => p.text).join("")
      .trim().replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, ""); // tolerate a fenced JSON reply
    const stop = STOP[cand.finishReason] || (text ? "end_turn" : "refusal");
    return { stop_reason: stop, model: used, content: text ? [{ type: "text", text }] : [] };
  }
  return { provider: "gemini", beta: { messages: { create } } };
}
