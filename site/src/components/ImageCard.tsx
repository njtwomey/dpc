import { ExternalLink } from "lucide-react"
import { Card } from "@/components/ui/card"
import { AwardStamps } from "@/components/AwardStamps"
import { imagePage, memberPage, thumbUrl, type DpcImage } from "@/lib/dpc"

/** One awarded photograph.
 *
 *  The tile is an anchor to dpchallenge, so it works with JavaScript off; the
 *  client island intercepts the click and opens the viewer instead, and
 *  data-index is how it knows which image this is.
 *
 *  The photograph carries nothing on top of it. Title, photographer and awards
 *  all live in the footer, in that order.
 */
export function ImageCard({ image, index }: { image: DpcImage; index: number }) {
  return (
    <Card className="group gap-0 overflow-hidden p-0 transition-shadow hover:shadow-md">
      <a
        href={imagePage(image.id)}
        data-image-index={index}
        aria-label={image.title}
        className="focus-visible:ring-ring block aspect-[3/2] overflow-hidden focus-visible:ring-2 focus-visible:outline-none"
      >
        <img
          src={thumbUrl(image.challenge_id, image.id)}
          alt={image.title}
          loading="lazy"
          className="size-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
        />
      </a>

      <div className="min-w-0 space-y-1 px-3 py-2.5">
        <a
          href={imagePage(image.id)}
          target="_blank"
          rel="noreferrer"
          title={image.title}
          className="hover:text-primary block truncate text-sm font-medium hover:underline"
        >
          {image.title}
        </a>
        <div className="flex min-w-0 items-center justify-between gap-2">
          <a
            href={memberPage(image.photographer_id)}
            target="_blank"
            rel="noreferrer"
            className="text-muted-foreground hover:text-foreground inline-flex min-w-0 items-center gap-1 truncate text-xs hover:underline"
          >
            <span className="truncate">{image.photographer_name}</span>
            <ExternalLink className="size-3 shrink-0" />
          </a>
          <AwardStamps slugs={image.awards} />
        </div>
      </div>
    </Card>
  )
}
