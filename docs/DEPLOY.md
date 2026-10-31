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
