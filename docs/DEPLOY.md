# Running and deploying Flare AI

The website is plain files in `site/` (HTML, CSS, JavaScript, and the generated `site/data/data.js`).
`site/index.html` loads everything with **relative links** (`css/style.css`, `data/data.js`, `js/app.js`),
so the same folder works offline and on any static host. There is no build step on the host.

## 1. Offline (no internet, no install)

Double-click `site/index.html`. The page opens from `file://` and works fully offline:
the data is a `.js` file (not JSON), because browsers block `fetch()` on `file://` pages.

## 2. Local web server (closest to the real host)

```bash
python3 -m http.server 8000 --directory site
```
Open http://localhost:8000.

## 3. The demo host: Netlify (free, works with a private repo)

Recommended for judges: one stable HTTPS link that always shows the latest `main`.

**Option A, quickest (no account link to GitHub):** go to https://app.netlify.com/drop and drag the `site/` folder
onto the page. You get a URL in seconds. Repeat the drag after each update.

**Option B, automatic (redeploys on every push to `main`):**
1. https://app.netlify.com -> Add new site -> Import an existing project -> GitHub -> pick `aaa628/flare-ai`.
2. Netlify reads `netlify.toml` from the repo root: publish directory `site`, no build command. Click Deploy.
3. Optional: Site settings -> Change site name, e.g. `flare-ai-628` -> https://flare-ai-628.netlify.app

`netlify.toml` also sets security headers (a Content-Security-Policy: scripts and data only from the site itself, nothing from other domains; inline style attributes are allowed because the charts use them).

**Alternatives** with the same settings (publish directory `site`, no build): Cloudflare Pages, Vercel.
GitHub Pages also works but needs a public repo on the free plan.

## Updating the data

Data changes are made locally, then committed:
```bash
pip install openpyxl            # once
python scripts/build_site_data.py
```
Commit `site/data/data.js` together with the CSV changes; the host serves the committed file.

## Why not raw.githubusercontent.com?

`raw.githubusercontent.com` serves repository files as plain text with `X-Content-Type-Options: nosniff`,
so browsers refuse to run them as CSS or JavaScript, private repos return 404 there, and files are cached for minutes.
It is a file server, not a website host. An earlier version pointed `index.html` at it so a hosted HTML previewer
could load the assets; that broke offline use and is replaced by the Netlify link above. In-app links never rely on
`<base>` resolution (`tests/previewer_nav_test.py` still guards that), so the page also behaves inside previewers
that inject a `<base>` tag pointing at a real web host.

## Intelligence Lab (Claude): secure setup

The Lab's AI answers come from one Netlify Function, `netlify/functions/ask/` (served at `/api/ask`). The browser sends only
the visitor's question; the function retrieves Flare AI documents, calls Claude (`claude-opus-5-5`) with them, checks every
citation and returns the answer. **The API key never leaves Netlify's server side.**

### Where the key lives (and where it must never be)
- **Only** in Netlify: Site configuration -> Environment variables -> Add a variable -> Key `ANTHROPIC_API_KEY`,
  Scopes: **Functions** only, tick **"Contains secret values"**. Netlify then hides it in the UI and logs.
- **Never** in the repository, `site/`, `netlify.toml`, a commit message, a screenshot or a chat. `.env` is git-ignored.
  If a key is ever exposed, delete it in the Anthropic Console immediately and create a new one.
- Use a **dedicated key** for this site (Anthropic Console -> API keys), ideally in its own workspace, so it can be
  revoked without affecting anything else.

### Spend protection (do all of these)
1. **Anthropic Console spend limit:** set a monthly limit on the workspace that owns the key (e.g. a few dollars for
   the hackathon). This is the hard ceiling: even a bot cannot spend past it.
2. **Built-in limits in the function** (`netlify/functions/ask/core.mjs`, `LIMITS`): 300-character questions, 8 questions per
   visitor per hour, 25 per day, 400 per day across all visitors, 24-hour answer cache (repeat questions cost nothing).
   Limits are stored in Netlify Blobs; if that store is unavailable the function refuses (fails closed).
3. **Origin check:** browsers on other websites cannot call `/api/ask` (only the site's own Netlify URLs are allowed).
4. **No free proxy:** the function ignores everything except `question`, uses its own fixed instructions and its own
   retrieved documents, and caps the answer length, so it cannot be repurposed as a general chatbot.

### Model and cost
`claude-opus-5-5` at effort `low`, with Anthropic's server-side refusal fallback (`fallbacks: "default"`). A typical question
sends about 12 documents. To trade quality for cost you can change `MODEL` in `core.mjs` (for example to `claude-haiku-5-5`);
that is a team decision.

### Turning it off
Delete the `ANTHROPIC_API_KEY` variable (the Lab then shows "not configured" and falls back to keyword search), or delete the
key in the Anthropic Console. The rest of the site keeps working; offline (double-click) use always uses keyword search.

### Testing without a key
`npm install` then `node tests/lab_function_test.mjs` runs the function logic with a fake Claude client (limits, origin check,
citation checking, abstaining). `python tests/lab_ui_test.py` tests the Lab page with a simulated server reply.
