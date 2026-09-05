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
  let current: HTMLAnchorElement | null = null

  const sync = () => {
    const line = yearIndex.getBoundingClientRect().bottom + 1
    let active = 0
    for (const [i, section] of sections.entries()) {
      if (!section || section.getBoundingClientRect().top > line) break
      active = i
    }

    const link = links[active]
    if (!link || link === current) return
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

  let queued = false
  addEventListener(
    "scroll",
    () => {
      if (queued) return
      queued = true
      requestAnimationFrame(() => {
        queued = false
        sync()
      })
    },
    { passive: true },
  )
  sync()
}
