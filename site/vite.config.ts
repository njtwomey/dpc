import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import { renderToStaticMarkup } from "react-dom/server"

const root = import.meta.dirname

/** Render pages during `vite dev` exactly as the build does.
 *
 *  Without this the dev server serves index.html, which carries only the viewer
 *  island and so renders nothing -- the pages exist only as prerendered HTML.
 *  This makes development and production the same code path.
 */
function devSsr() {
  return {
    name: "dpc-dev-ssr",
    configureServer(server: any) {
      return () => {
        server.middlewares.use(async (req: any, res: any, next: any) => {
          const url = (req.originalUrl || req.url || "/").split("?")[0]
          if (url.startsWith("/@") || url.startsWith("/src/") || url.includes(".")) return next()

          try {
            const { routes } = await server.ssrLoadModule("/tools/routes.tsx")
            const path = url.endsWith("/") ? url : `${url}/`
            const route = routes().find((r: any) => r.path === path)
            if (!route) return next()

            const html = await server.transformIndexHtml(
              url,
              `<!doctype html><html lang="en-GB"><head><meta charset="utf-8">` +
                `<meta name="viewport" content="width=device-width, initial-scale=1">` +
                `<title>${route.title} | DPChallenge Award Gallery</title>` +
                // A real stylesheet link, so dev blocks on CSS the way the
                // build does. Without it the styles arrive inside the JS
                // module and every page flashes unstyled first.
                `<link rel="stylesheet" href="/src/index.css?direct">` +
                `</head><body>` +
                `<div id="root">${renderToStaticMarkup(route.element)}</div>` +
                `<script type="module" src="/src/client.tsx"></script></body></html>`,
            )
            res.setHeader("Content-Type", "text/html")
            res.end(html)
          } catch (error) {
            next(error)
          }
        })
      }
    },
  }
}

const base = process.env.SITE_BASE ?? "/"

export default defineConfig({
  base,
  define: { __SITE_BASE__: JSON.stringify(base) },
  plugins: [react(), tailwindcss(), devSsr()],
  build: { outDir: "dist" },
  resolve: {
    alias: {
      "@": `${root}/src`,
      // shadcn emits `import { cn } from "cn"`, so cn is its own alias.
      cn: `${root}/src/lib/utils.ts`,
      // The site builds from the same JSON `dpc export` writes.
      "@data": `${root}/data/dpc`,
    },
  },
})
