import { Card } from "@/components/ui/card"
import { images, type Award } from "@/lib/dpc"
import { thumbUrl } from "@/lib/urls"

/** An award, shown through the photographs that won it.
 *
 *  A bare badge on an empty tile says very little: the graphics are small and
 *  most of the card ends up as padding. Backing it with recent winners gives
 *  the card something to look at and previews what is behind the link.
 */
export function AwardCard({ award, href }: { award: Award; href: string }) {
  const preview = award.image_ids
    .slice(0, 3)
    .map((id) => images[String(id)])
    .filter(Boolean)

  return (
    <a href={href} className="group block">
      <Card className="hover:border-primary/30 gap-0 overflow-hidden p-0 transition-shadow hover:shadow-md">
        <div className="bg-muted relative aspect-[3/2]">
          <div className="absolute inset-0 grid grid-cols-3">
            {preview.map((image) => (
              <img
                key={image.id}
                src={thumbUrl(image.challenge_id, image.id)}
                alt=""
                loading="lazy"
                className="size-full object-cover transition-transform duration-300 group-hover:scale-[1.04]"
              />
            ))}
          </div>
          {/* Dimmed so the badge stays legible over any photograph. The scrim
              takes the page's own background rather than white: a white veil
              inside a dark card reads as a blown-out panel. */}
          <div className="bg-background/55 group-hover:bg-background/45 absolute inset-0 transition-colors" />
          {/* A quarter of the award graphics are GIF/PNG with transparent
              backgrounds, drawn for a white page. The scrim used to be their
              backing; now that it goes dark they need their own. */}
          <img
            src={award.thumb}
            alt=""
            className="ring-border absolute top-1/2 left-1/2 max-h-[62%] max-w-[52%] -translate-x-1/2 -translate-y-1/2 rounded-md object-contain shadow-md ring-1 dark:bg-white/85"
          />
        </div>

        <div className="min-w-0 space-y-0.5 px-3 py-2.5">
          <p className="truncate text-sm font-medium" title={award.name}>{award.name}</p>
          <p className="text-muted-foreground text-xs tabular-nums">
            {award.num_granted.toLocaleString()} given
            {" · "}
            {award.num_recipients.toLocaleString()} photographers
          </p>
        </div>
      </Card>
    </a>
  )
}
