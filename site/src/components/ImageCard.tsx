import { ExternalLink } from "lucide-react"
import { Card } from "@/components/ui/card"
import { awardBySlug, imagePage, memberPage, thumbUrl, type DpcImage } from "@/lib/dpc"

/** One awarded photograph.
 *
 *  The tile is an anchor to dpchallenge, so it works with JavaScript off; the
 *  client island intercepts the click and opens the viewer instead. data-index
 *  is how the island knows which image it is.
 */
export function ImageCard({ image, index }: { image: DpcImage; index: number }) {
  return (
    <Card className="group gap-0 overflow-hidden p-0 transition-shadow hover:shadow-md">
      <a
        href={imagePage(image.id)}
        data-image-index={index}
        className="focus-visible:ring-ring relative block aspect-[3/2] overflow-hidden focus-visible:ring-2 focus-visible:outline-none"
      >
        <img
          src={thumbUrl(image.challenge_id, image.id)}
          alt={image.title}
          loading="lazy"
          className="size-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
        />
        <span className="pointer-events-none absolute inset-x-0 bottom-0 flex flex-wrap gap-1 bg-gradient-to-t from-black/70 to-transparent p-2 pt-6">
          {image.awards.slice(0, 3).map((slug) => {
            const award = awardBySlug.get(slug)
            return award ? (
              <img key={slug} src={award.thumb} alt={award.name} title={award.name}
                   className="size-5 rounded-[3px] ring-1 ring-white/60" />
            ) : null
          })}
          {image.awards.length > 3 && (
            <span className="rounded bg-white/85 px-1 text-[11px] leading-5 font-medium">
              +{image.awards.length - 3}
            </span>
          )}
        </span>
      </a>

      <div className="flex min-w-0 items-center justify-between gap-2 px-3 py-2">
        <p className="truncate text-sm font-medium" title={image.title}>{image.title}</p>
        <a href={memberPage(image.photographer_id)} target="_blank" rel="noreferrer"
           className="text-muted-foreground hover:text-foreground inline-flex shrink-0 items-center gap-1 text-xs">
          {image.photographer_name}
          <ExternalLink className="size-3" />
        </a>
      </div>
    </Card>
  )
}
