import { useCallback, useEffect } from "react"
import { ChevronLeft, ChevronRight, ExternalLink } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog, DialogContent, DialogDescription, DialogTitle,
} from "@/components/ui/dialog"
import {
  challengePage, imagePage, imageUrl, memberPage,
  type AwardRef, type DpcImage,
} from "@/lib/urls"

/** Marks a link that leaves for dpchallenge. */
const Out = () => <ExternalLink className="size-3 shrink-0 opacity-50" aria-hidden />

/** The image viewer: a modal over the gallery, not a page of its own.
 *
 *  A real dialog rather than a hand-rolled overlay, so focus trapping, scroll
 *  locking and the dark scrim come from Radix. That is safe here precisely
 *  because the viewer is the hydrated island -- unlike the cards, which ship no
 *  JavaScript and so cannot use components that depend on effects.
 */
export function ImageViewer({
  images, awards, index, onClose, onIndex,
}: {
  images: DpcImage[]
  awards: Record<string, AwardRef>
  index: number | null
  onClose: () => void
  onIndex: (next: number) => void
}) {
  const open = index !== null

  const step = useCallback(
    (delta: number) => {
      if (index === null) return
      onIndex((index + delta + images.length) % images.length)
    },
    [index, images.length, onIndex],
  )

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
        e.preventDefault()
        step(e.key === "ArrowRight" ? 1 : -1)
      }
      // Escape closes via Radix. preventDefault only, without stopping
      // propagation: in fullscreen the browser treats Escape as its own exit
      // shortcut, so unclaimed it leaves fullscreen instead of closing this.
      if (e.key === "Escape") e.preventDefault()
    }
    window.addEventListener("keydown", onKey, { capture: true })
    return () => window.removeEventListener("keydown", onKey, { capture: true })
  }, [open, step])

  if (index === null) return null
  const image = images[index]
  if (!image) return null

  return (
    <Dialog open={open} onOpenChange={(next) => !next && onClose()}>
      <DialogContent
        // A fixed frame, deliberately: the modal is the same size for every
        // photograph, so stepping through a challenge does not make the window
        // jump between portrait and landscape. The picture fits itself into the
        // frame instead of the other way round.
        className="flex h-[88vh] w-[min(94vw,1180px)] max-w-none flex-col gap-0 overflow-hidden p-0 sm:max-w-none"
      >
        {/* Every name is its own link out to dpchallenge, so the header needs no
            separate button and can stay one compact strip. */}
        <div className="min-w-0 border-b py-2 pr-12 pl-4">
          <DialogTitle asChild>
            <a href={imagePage(image.id)} target="_blank" rel="noreferrer"
               className="hover:text-primary flex min-w-0 items-center gap-1.5 text-sm font-semibold">
              <span className="truncate hover:underline">{image.title}</span>
              <Out />
            </a>
          </DialogTitle>
          <DialogDescription asChild>
            <p className="flex min-w-0 items-center gap-1.5 text-xs">
              <a href={memberPage(image.photographer_id)} target="_blank" rel="noreferrer"
                 className="hover:text-foreground flex min-w-0 items-center gap-1">
                <span className="truncate hover:underline">{image.photographer_name}</span>
                <Out />
              </a>
              <span aria-hidden>·</span>
              <a href={challengePage(image.challenge_id)} target="_blank" rel="noreferrer"
                 className="hover:text-foreground flex min-w-0 items-center gap-1">
                <span className="truncate hover:underline">{image.challenge_name}</span>
                <Out />
              </a>
            </p>
          </DialogDescription>
        </div>

        <div className="bg-muted/30 relative flex min-h-0 flex-1 items-center justify-center p-3">
          <Button variant="secondary" size="icon"
                  className="absolute left-3 z-10 rounded-full shadow-md"
                  onClick={() => step(-1)} aria-label="Previous">
            <ChevronLeft className="size-5" />
          </Button>
          <img
            key={image.id}
            src={imageUrl(image.challenge_id, image.id)}
            alt={image.title}
            className="max-h-full max-w-full object-contain"
          />
          <Button variant="secondary" size="icon"
                  className="absolute right-3 z-10 rounded-full shadow-md"
                  onClick={() => step(1)} aria-label="Next">
            <ChevronRight className="size-5" />
          </Button>
        </div>

        <div className="flex flex-wrap items-center gap-2 border-t px-4 py-3">
          {image.awards.map((slug) => {
            const award = awards[slug]
            return award ? (
              <Badge key={slug} variant="secondary" className="gap-1.5 py-1 pl-1.5 font-normal">
                <span className="grid size-5 place-items-center rounded-sm bg-white">
                  <img src={award.thumb} alt="" className="max-h-4 max-w-4 object-contain" />
                </span>
                {award.name}
              </Badge>
            ) : null
          })}
          <span className="text-muted-foreground ml-auto text-xs tabular-nums">
            {index + 1} / {images.length}
          </span>
        </div>
      </DialogContent>
    </Dialog>
  )
}
