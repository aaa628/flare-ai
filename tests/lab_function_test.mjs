// Tests the Intelligence Lab function logic with a FAKE Claude client and in-memory store (no API key, no cost).
// Run: node tests/lab_function_test.mjs
import { handle, retrieve, validate, LIMITS } from "../netlify/functions/ask/core.mjs";

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

// validate(): grade rule edge cases
check("grade: single citation -> thin", validate({ status: "answered", summary: "", key_points: [{ text: "t", basis: "brief", citations: ["brief-moon"] }], gaps: [] }, [{ id: "brief-moon", kind: "brief", title: "b", route: "#/", source: "s" }]).grade === "thin");

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
