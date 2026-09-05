/** The path the site is served from.
 *
 *  Pages serves this project at /dpc/, not at the domain root, so every
 *  internal link needs that prefix. Vite substitutes __SITE_BASE__ at build
 *  time for the browser; the prerenderer sets the same global before importing
 *  any component. Getting this wrong 404s every link on the deployed site.
 */
declare const __SITE_BASE__: string | undefined

const raw =
  typeof __SITE_BASE__ !== "undefined"
    ? __SITE_BASE__
    : ((globalThis as { __SITE_BASE__?: string }).__SITE_BASE__ ?? "/")

/** Always exactly one trailing slash, never a doubled one. */
export const BASE = `/${raw.replace(/^\/+|\/+$/g, "")}/`.replace("//", "/")

/** `href("/awarders/")` -> `/dpc/awarders/` */
export const href = (path: string) => `${BASE}${path.replace(/^\/+/, "")}`
