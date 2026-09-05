/** The only JavaScript the site ships: the image viewer.
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
