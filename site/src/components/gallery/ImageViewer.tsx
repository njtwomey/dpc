import { useCallback, useEffect } from "react"
import { ChevronLeft, ChevronRight, ExternalLink, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  challengePage, imagePage, imageUrl, memberPage,
  type AwardRef, type DpcImage,
} from "@/lib/urls"

/** Full-screen viewer, and the only component that ships to the browser.
 *
 *  It takes its awards as a prop rather than importing the catalogue, so the
 *  client bundle never pulls in the 1.8 MB image dataset.
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
  const step = useCallback(
    (delta: number) => {
      if (index === null) return
      onIndex((index + delta + images.length) % images.length)
    },
    [index, images.length, onIndex],
  )

  useEffect(() => {
    if (index === null) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose()
      if (e.key === "ArrowRight") step(1)
      if (e.key === "ArrowLeft") step(-1)
    }
    window.addEventListener("keydown", onKey)
    document.body.style.overflow = "hidden"
    return () => {
      window.removeEventListener("keydown", onKey)
      document.body.style.overflow = ""
    }
  }, [index, onClose, step])

  if (index === null) return null
  const image = images[index]
  if (!image) return null

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-white/98 backdrop-blur-sm"
         role="dialog" aria-modal="true" aria-label={image.title}>
      <div className="flex items-start justify-between gap-4 border-b px-4 py-3">
        <div className="min-w-0">
          <h2 className="truncate text-base font-semibold">{image.title}</h2>
          <p className="text-muted-foreground truncate text-sm">
            <a href={memberPage(image.photographer_id)} target="_blank" rel="noreferrer"
               className="hover:text-foreground hover:underline">{image.photographer_name}</a>
            {" · "}
            <a href={challengePage(image.challenge_id)} target="_blank" rel="noreferrer"
               className="hover:text-foreground hover:underline">{image.challenge_name}</a>
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-1">
          <Button variant="ghost" size="sm" asChild>
            <a href={imagePage(image.id)} target="_blank" rel="noreferrer">
              <ExternalLink className="size-4" /> DPChallenge
            </a>
          </Button>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close">
            <X className="size-4" />
          </Button>
        </div>
      </div>

      <div className="relative flex min-h-0 flex-1 items-center justify-center p-4">
        <Button variant="outline" size="icon" className="absolute left-4 z-10 rounded-full shadow-sm"
                onClick={() => step(-1)} aria-label="Previous">
          <ChevronLeft className="size-5" />
        </Button>
        <img key={image.id} src={imageUrl(image.challenge_id, image.id)} alt={image.title}
             className="max-h-full max-w-full object-contain shadow-lg" />
        <Button variant="outline" size="icon" className="absolute right-4 z-10 rounded-full shadow-sm"
                onClick={() => step(1)} aria-label="Next">
          <ChevronRight className="size-5" />
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-2 border-t px-4 py-3">
        {image.awards.map((slug) => {
          const award = awards[slug]
          return award ? (
            <Badge key={slug} variant="secondary" className="gap-1.5 py-1 pl-2 font-normal">
              <img src={award.thumb} alt="" className="size-4 rounded-[3px] object-cover" />
              {award.name}
            </Badge>
          ) : null
        })}
        <span className="text-muted-foreground ml-auto text-xs tabular-nums">
          {index + 1} / {images.length}
        </span>
      </div>
    </div>
  )
}
