// Tests the Intelligence Lab function logic with a FAKE Claude client and in-memory store (no API key, no cost).
// Run: node tests/lab_function_test.mjs
import { handle, retrieve, validate, LIMITS } from "../netlify/functions/ask/core.mjs";
import { geminiClient } from "../netlify/functions/ask/gemini.mjs";

let pass = 0, fail = 0;
const check = (name, ok, extra = "") => { ok ? pass++ : fail++; console.log((ok ? "PASS " : "FAIL ") + name + (ok ? "" : " " + extra)); };
const memStore = () => { const m = new Map(); return { get: async (k) => m.get(k) ?? null, set: async (k, v) => { m.set(k, v); }, m }; };
const ORIGIN = "https://flare.example";
const req = (q, opts = {}) => new Request("https://flare.example/api/ask", { method: opts.method || "POST",
  headers: { "content-type": "application/json", origin: opts.origin ?? ORIGIN }, body: opts.method === "GET" ? undefined : JSON.stringify({ question: q }) });
function fakeClient(reply, calls) {
  return { beta: { messages: { create: async (params) => { calls.push(params); return reply(params); } } } };
}
const answerWith = (obj) => () => ({ stop_reason: "end_turn", model: "claude-opus-5-5", content: [{ type: "text", text: JSON.stringify(obj) }] });

// retrieval
const r1 = retrieve("Which investigations tested oxygen above 30% at low pressure for a Moon base?");
check("retrieval: Moon-base question finds investigation summaries / brief", r1.some((d) => d.kind === "investigation") && r1.some((d) => d.kind === "brief"), JSON.stringify(r1.map((d) => d.id)));
const r2 = retrieve("What happened in test FLEX-114?");
check("retrieval: exact test id is ranked first", r2[0] && r2[0].id === "FLEX-114", r2[0] && r2[0].id);

// method / origin / size guards (no model call)
{
  const calls = [];
  const deps = { client: fakeClient(answerWith({}), calls), store: memStore(), ip: "1.2.3.4", allowedOrigins: [ORIGIN] };
  check("rejects GET", (await handle(req("x", { method: "GET" }), deps)).status === 405);
  check("rejects other origins", (await handle(req("Which tests used methanol droplets?", { origin: "https://evil.example" }), deps)).status === 403);
  check("rejects over-long questions", (await handle(req("a".repeat(LIMITS.maxQuestionChars + 1)), deps)).status === 400);
  check("no model call for rejected requests", calls.length === 0);
}

// a good answer: valid citations kept, invented citation dropped, grade computed by our rule, model params safe
{
  const calls = [];
  const q = "How did FLEX methanol droplet tests end?";
  const ids = retrieve(q).filter((d) => d.kind === "record").map((d) => d.id);
  const deps = { client: fakeClient(answerWith({ status: "answered", summary: "Most ended in extinction.",
    key_points: [{ text: "Test ended in extinction.", basis: "nasa_record", citations: ids.slice(0, 3) },
                 { text: "Invented claim.", basis: "interpretation", citations: ["NOT-A-REAL-ID"] }], gaps: ["Not a rate."] }), calls),
    store: memStore(), ip: "1.2.3.4", allowedOrigins: [ORIGIN] };
  const res = await handle(req(q), deps); const body = await res.json();
  check("answer: 200 and answered", res.status === 200 && body.status === "answered", JSON.stringify(body).slice(0, 200));
  check("answer: invented citation removed, point dropped", body.dropped_points === 1 && body.key_points.length === 1);
  check("answer: evidence grade from our rule (3 records -> strong)", body.grade === "strong", body.grade);
  check("answer: every citation links to a site route", body.citations.every((c) => c.route.startsWith("#/")));
  const p = calls[0];
  check("model call: claude-opus-5-5, structured output, fallbacks default", p.model === "claude-opus-5-5" && p.output_config.format.type === "json_schema" && p.fallbacks === "default" && p.betas.includes("server-side-fallback-2026-07-01"));
  check("model call: question wrapped as data, evidence included", /<visitor_question>/.test(p.messages[0].content) && /<doc id=/.test(p.messages[0].content));
  const again = await (await handle(req(q.toUpperCase() + "  "), deps)).json();
  check("cache: repeated question served from cache, no second model call", again.cached === true && calls.length === 1);
}

// abstain cases
{
  const calls = [];
  const deps = { client: fakeClient(answerWith({ status: "answered", summary: "x", key_points: [{ text: "y", basis: "interpretation", citations: ["NOPE"] }], gaps: [] }), calls), store: memStore(), ip: "5.6.7.8", allowedOrigins: [ORIGIN] };
  const b = await (await handle(req("What is the fire probability on a Mars rover?"), deps)).json();
  check("abstains when no citation survives validation", b.status === "abstained" && b.grade === "none" && b.key_points.length === 0);
  const deps2 = { client: fakeClient(() => ({ stop_reason: "refusal", model: "claude-opus-5-5", content: [] }), []), store: memStore(), ip: "9.9.9.9", allowedOrigins: [ORIGIN] };
  const b2 = await (await handle(req("Which tests used Nomex fabric samples?"), deps2)).json();
  check("refusal stop reason -> abstained, not an error", b2.status === "abstained");
}

// rate limits
{
  const calls = [];
  const deps = { client: fakeClient(answerWith({ status: "abstained", summary: "n", key_points: [], gaps: [] }), calls), store: memStore(), ip: "7.7.7.7", allowedOrigins: [ORIGIN], now: Date.UTC(2026, 10, 14, 10) };
  let last;
  for (let i = 0; i < LIMITS.perIpPerHour + 1; i++) last = await handle(req("Question number " + i + " about BASS samples?"), deps);
  check("per-IP hourly limit returns 429", last.status === 429);
  check("no model call beyond the limit", calls.length === LIMITS.perIpPerHour);
}

// Gemini adapter (FAKE fetch: no key, no network). core.mjs is unchanged, so the same citation checks apply.
{
  const sent = [];
  const gReply = (obj, extra = {}) => ({ candidates: [{ content: { role: "model", parts: [{ text: JSON.stringify(obj) }] }, finishReason: "STOP" }], modelVersion: "gemini-test-flash", ...extra });
  const fakeFetch = (replies) => async (url, init) => { sent.push({ url, init, body: JSON.parse(init.body) });
    const r = replies.shift(); return new Response(typeof r.body === "string" ? r.body : JSON.stringify(r.body), { status: r.status || 200 }); };
  const q = "How did FLEX methanol droplet tests end?";
  const ids = retrieve(q).filter((d) => d.kind === "record").map((d) => d.id);
  const good = { status: "answered", summary: "Most ended in extinction.", key_points: [{ text: "Ended in extinction.", basis: "nasa_record", citations: ids.slice(0, 3) },
    { text: "Invented.", basis: "interpretation", citations: ["FAKE-1"] }], gaps: [] };
  const g = geminiClient({ apiKey: "test-key-not-real", model: "gemini-test-flash", fetchImpl: fakeFetch([{ body: gReply(good) }]) });
  const res = await handle(req(q), { client: g, store: memStore(), ip: "2.2.2.2", allowedOrigins: [ORIGIN] }); const b = await res.json();
  check("gemini: answered, invented citation dropped, grade by our rule", res.status === 200 && b.status === "answered" && b.dropped_points === 1 && b.grade === "strong", JSON.stringify(b).slice(0, 200));
  check("gemini: answer names the model that wrote it", b.model === "gemini-test-flash");
  const s0 = sent[0];
  check("gemini: key sent in a header, never in the URL", s0.init.headers["x-goog-api-key"] === "test-key-not-real" && !s0.url.includes("test-key-not-real") && s0.url.endsWith("/models/gemini-test-flash:generateContent"));
  check("gemini: same fixed instructions, question wrapped as data, JSON schema requested",
    /Answer ONLY from the numbered evidence/.test(s0.body.systemInstruction.parts[0].text) && /<visitor_question>/.test(s0.body.contents[0].parts[0].text)
    && s0.body.generationConfig.responseMimeType === "application/json" && s0.body.generationConfig.responseJsonSchema.required.includes("key_points")
    && !JSON.stringify(s0.body.generationConfig.responseJsonSchema).includes("additionalProperties"));

  sent.length = 0;
  const g2 = geminiClient({ apiKey: "k", fetchImpl: fakeFetch([{ status: 400, body: {} }, { status: 400, body: {} }, { status: 400, body: { error: { message: "schema" } } }, { body: { candidates: [{ content: { parts: [{ text: "```json\n" + JSON.stringify(good) + "\n```" }] }, finishReason: "STOP" }] } }]) });
  const b2 = await (await handle(req(q), { client: g2, store: memStore(), ip: "3.3.3.3", allowedOrigins: [ORIGIN] })).json();
  check("gemini: fast settings first (minimal thinking), fields a model rejects are dropped step by step",
    sent.length === 4 && sent[0].body.generationConfig.thinkingConfig.thinkingLevel === "minimal" && sent[1].body.generationConfig.thinkingConfig.thinkingBudget === 0
    && !sent[2].body.generationConfig.thinkingConfig && sent[2].body.generationConfig.responseJsonSchema
    && !sent[3].body.generationConfig.responseJsonSchema && /JSON Schema/.test(sent[3].body.systemInstruction.parts[0].text) && b2.status === "answered");
  const slow = async (url, init) => new Promise((_, rej) => init.signal.addEventListener("abort", () => rej(new DOMException("aborted", "AbortError"))));
  const g6 = geminiClient({ apiKey: "k", fetchImpl: slow, deadlineMs: 50 });
  const r6 = await handle(req("Which tests used Nomex fabric samples?"), { client: g6, store: memStore(), ip: "4.4.4.7", allowedOrigins: [ORIGIN] });
  check("gemini: too slow -> stopped before Netlify's 10 s limit, clean error (page shows keyword matches)", r6.status === 502 && (await r6.json()).detail === "upstream 504");

  const g3 = geminiClient({ apiKey: "k", fetchImpl: fakeFetch([{ body: { candidates: [{ content: { parts: [] }, finishReason: "SAFETY" }] } }]) });
  const b3 = await (await handle(req("Which tests used Nomex fabric samples?"), { client: g3, store: memStore(), ip: "4.4.4.4", allowedOrigins: [ORIGIN] })).json();
  check("gemini: safety block -> abstained, not an error", b3.status === "abstained");
  const g4 = geminiClient({ apiKey: "k", fetchImpl: fakeFetch([{ status: 429, body: { error: { message: "quota" } } }]) });
  const r4 = await handle(req("Which tests used Nomex fabric samples?"), { client: g4, store: memStore(), ip: "4.4.4.5", allowedOrigins: [ORIGIN] });
  check("gemini: quota exhausted -> 502 error (page falls back to keyword search)", r4.status === 502 && (await r4.json()).detail === "upstream 429");
  const g5 = geminiClient({ apiKey: "k", fetchImpl: fakeFetch([{ body: { candidates: [{ content: { parts: [{ text: "{\"status\":" }] }, finishReason: "MAX_TOKENS" }] } }]) });
  check("gemini: cut-off answer -> 502, never a half answer", (await handle(req("Which tests used Nomex fabric samples?"), { client: g5, store: memStore(), ip: "4.4.4.6", allowedOrigins: [ORIGIN] })).status === 502);
}

// validate(): grade rule edge cases
check("grade: single citation -> thin", validate({ status: "answered", summary: "", key_points: [{ text: "t", basis: "brief", citations: ["brief-moon"] }], gaps: [] }, [{ id: "brief-moon", kind: "brief", title: "b", route: "#/", source: "s" }]).grade === "thin");

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
