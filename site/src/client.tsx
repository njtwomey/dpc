/** The only JavaScript the site ships: the image viewer, and the year index's
 *  active marker.
 *
 *  Everything else is static HTML. Each gallery embeds the data its viewer
 *  needs, so this bundle imports no dataset -- pulling in lib/dpc would drag
 *  the 1.8 MB images.json into every page.
 *
 *  With this script blocked, the tiles remain ordinary links to dpchallenge.
 */
import { useState } from "react"
import { createRoot } from "react-dom/client"
import { ImageViewer } from "@/components/gallery/ImageViewer"
import type { AwardRef, DpcImage } from "@/lib/urls"
import "./index.css"

type Payload = { images: DpcImage[]; awards: Record<string, AwardRef> }

function Viewer({ payload, bind }: { payload: Payload; bind: (open: (i: number) => void) => void }) {
  const [index, setIndex] = useState<number | null>(null)
  bind(setIndex)
  return (
    <ImageViewer images={payload.images} awards={payload.awards} index={index}
                 onClose={() => setIndex(null)} onIndex={setIndex} />
  )
}

for (const gallery of document.querySelectorAll<HTMLElement>("[data-gallery]")) {
  const raw = gallery.querySelector("[data-gallery-payload]")?.textContent
  if (!raw) continue

  const mount = document.createElement("div")
  document.body.appendChild(mount)

  let open: ((i: number) => void) | null = null
  createRoot(mount).render(
    <Viewer payload={JSON.parse(raw) as Payload} bind={(fn) => { open = fn }} />,
  )

  gallery.addEventListener("click", (event) => {
    const tile = (event.target as HTMLElement).closest<HTMLElement>("[data-image-index]")
    if (!tile || !open) return
    event.preventDefault()
    open(Number(tile.dataset.imageIndex))
  })
}

/** Mark the year you are currently scrolling through in the challenges index.
 *
 *  Progressive enhancement: without this the chips are still working anchors,
 *  they just do not light up. Read on rAF rather than with IntersectionObserver
 *  because the question is "which year has passed under the bar", not "which is
 *  visible" -- with 1,516 cards several years are on screen at once.
 */
const yearIndex = document.querySelector<HTMLElement>("[data-year-index]")
if (yearIndex) {
  const links = [...yearIndex.querySelectorAll<HTMLAnchorElement>('a[href^="#"]')]
  const sections = links.map((link) => document.getElementById(link.hash.slice(1)))

  // The reading line is where a section actually lands when you jump to it:
  // its own scroll-margin-top, which clears the header and this index. Using
  // the index's own bottom put the line about ten pixels higher, so the year
  // you clicked had not yet passed it and the previous one stayed marked.
  const first = sections.find((s): s is HTMLElement => s !== null)
  const margin = first ? Number.parseFloat(getComputedStyle(first).scrollMarginTop) : 0
  const line = (Number.isFinite(margin) ? margin : 0) + 2

  let current: HTMLAnchorElement | null = null

  const mark = (link: HTMLAnchorElement) => {
    if (link === current) return
    current?.removeAttribute("data-active")
    link.setAttribute("data-active", "")
    current = link

    // Keep the marked chip in view, but only ever scroll the strip itself --
    // scrollIntoView would move the page out from under the reader.
    if (yearIndex.scrollWidth > yearIndex.clientWidth) {
      const pad = 16
      const left = link.offsetLeft - pad
      const right = link.offsetLeft + link.offsetWidth + pad - yearIndex.clientWidth
      if (left < yearIndex.scrollLeft) yearIndex.scrollLeft = left
      else if (right > yearIndex.scrollLeft) yearIndex.scrollLeft = right
    }
  }

  // A jump pins its own year until you actually scroll away from it. On a short
  // gallery the last year or two sit too close to the bottom to ever reach the
  // line, so position alone can never mark them; what you clicked is not in
  // doubt, so intent wins over geometry until you move.
  let pinned: HTMLAnchorElement | null = null
  let pinnedAt = -1

  const positional = () => {
    const doc = document.documentElement
    if (innerHeight + scrollY >= doc.scrollHeight - 2) return links.length - 1
    let active = 0
    for (const [i, section] of sections.entries()) {
      if (!section || section.getBoundingClientRect().top > line) break
      active = i
    }
    return active
  }

  const sync = () => {
    if (pinned && Math.abs(Math.round(scrollY) - pinnedAt) < 4) {
      mark(pinned)
      return
    }
    pinned = null
    const link = links[positional()]
    if (link) mark(link)
  }

  let queued = false
  const schedule = () => {
    if (queued) return
    queued = true
    requestAnimationFrame(() => {
      queued = false
      sync()
    })
  }

  // Both callers run after the browser has already scrolled, so scrollY is the
  // anchored position and can be read straight away. Deferring it to a frame
  // meant a throttled tab never recorded it, and the pin never released.
  const pinFromHash = () => {
    const link = links.find((l) => l.hash === location.hash)
    if (!link) return
    pinned = link
    pinnedAt = Math.round(scrollY)
    mark(link)
  }

  addEventListener("scroll", schedule, { passive: true })
  // A jump that does not move the page far enough to fire a scroll event would
  // otherwise leave the marker where it was.
  addEventListener("hashchange", pinFromHash)
  for (const link of links) link.addEventListener("click", () => setTimeout(pinFromHash, 0))

  if (location.hash) pinFromHash()
  else sync()
}
