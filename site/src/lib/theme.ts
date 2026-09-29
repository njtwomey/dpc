/** The theme preference, and the blocking script that applies it.
 *
 *  Pages are static HTML served straight off disk with no client-side router,
 *  so a theme applied from the client bundle would land after first paint:
 *  every single navigation would flash the light page before turning dark.
 *  The script below runs inline in <head>, before the body is parsed.
 *
 *  Both tools/prerender.tsx and vite.config.ts inline it, so dev and the build
 *  cannot drift. Keep this file free of DOM references: vite.config.ts is
 *  type-checked under tsconfig.node.json, which has no DOM lib.
 */

/** Only written once the reader has actually picked a side. While it is absent
 *  prefers-color-scheme decides, which is why there is no stored "system". */
export const THEME_KEY = "dpc-theme"

/** Reads the stored choice, falls back to the system, and marks <html>.
 *
 *  data-theme is also what tells CSS the client bundle is coming (the
 *  `scripted` variant in index.css), so it is set outside the try: storage
 *  throws outright in some privacy modes, and swallowing that must not take
 *  the toggle down with it.
 */
export const THEME_SCRIPT =
  `(function(){var d=document.documentElement,t;` +
  `try{t=localStorage.getItem(${JSON.stringify(THEME_KEY)})}catch(e){}` +
  `if(t!=="light"&&t!=="dark")t=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";` +
  `d.dataset.theme=t;d.classList.toggle("dark",t==="dark")})()`
