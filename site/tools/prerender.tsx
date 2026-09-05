/** Render every route to static HTML.
 *
 *  The React equivalent of `hugo`: no server, no client-side routing, one HTML
 *  file per URL. Run after `vite build`, which produces the CSS and the island
 *  bundle this stitches in.
 */
import { mkdir, readdir, writeFile } from "node:fs/promises"
import { dirname, join } from "node:path"
import { renderToStaticMarkup } from "react-dom/server"
// Set before importing anything that renders, so lib/base picks it up.
;(globalThis as { __SITE_BASE__?: string }).__SITE_BASE__ = process.env.SITE_BASE ?? "/"

const { routes } = await import("./routes")

const OUT = join(import.meta.dirname, "..", "dist")

/** Vite hashes its filenames, so find them rather than hardcoding. Asset URLs
 *  need the same base prefix the links do, or they 404 once deployed. */
async function assets(base: string) {
  const files = await readdir(join(OUT, "assets"))
  const url = (f: string) => `${base}assets/${f}`
  return {
    css: files.filter((f) => f.endsWith(".css")).map(url),
    js: files.filter((f) => f.endsWith(".js")).map(url),
  }
}

const escape = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;")

function document(title: string, body: string, css: string[], js: string[]) {
  return `<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escape(title)} | DPChallenge Award Gallery</title>
${css.map((h) => `<link rel="stylesheet" href="${h}">`).join("\n")}
</head>
<body>
<div id="root">${body}</div>
${js.map((s) => `<script type="module" src="${s}"></script>`).join("\n")}
</body>
</html>
`
}

const started = performance.now()
const { BASE } = await import("../src/lib/base")
const { css, js } = await assets(BASE)
const all = routes()

let bytes = 0
await Promise.all(
  all.map(async (route) => {
    const file = join(OUT, route.path, "index.html")
    await mkdir(dirname(file), { recursive: true })
    const html = document(route.title, renderToStaticMarkup(route.element), css, js)
    bytes += Buffer.byteLength(html)
    await writeFile(file, html, "utf8")
  }),
)

const seconds = (performance.now() - started) / 1000
console.log(
  `prerendered ${all.length.toLocaleString()} pages in ${seconds.toFixed(2)}s ` +
    `(${(bytes / 1024 / 1024).toFixed(1)} MB of HTML)`,
)
