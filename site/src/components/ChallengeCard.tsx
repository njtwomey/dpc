import { AwardStamps } from "@/components/AwardStamps"
import { Card } from "@/components/ui/card"
import { images, type Challenge } from "@/lib/dpc"
import { thumbUrl } from "@/lib/urls"

/** One challenge, shown through the photographs that won awards in it.
 *
 *  Same shape as ImageCard: the pictures carry nothing on top of them, and the
 *  name, the count and the awards sit in the footer underneath. A challenge
 *  with one winner gets one wide thumbnail rather than a third of a strip and
 *  two empty cells.
 */
export function ChallengeCard({ challenge, href }: { challenge: Challenge; href: string }) {
  const preview = challenge.image_ids
    .slice(0, 3)
    .map((id) => images[String(id)])
    .filter(Boolean)

  return (
    <a href={href} className="group block">
      <Card className="hover:border-primary/30 gap-0 overflow-hidden p-0 transition-shadow hover:shadow-md">
        {/* The strip is absolutely positioned inside the ratio box: as a plain
            flex child its min-height:auto would let a single wide thumbnail
            outgrow the 3:2 frame and drag the whole grid row taller. */}
        <div className="bg-muted relative aspect-[3/2] overflow-hidden">
          <div
            className="absolute inset-0 grid gap-px"
            style={{ gridTemplateColumns: `repeat(${Math.max(preview.length, 1)}, 1fr)` }}
          >
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
        </div>

        <div className="min-w-0 space-y-1 px-3 py-2.5">
          <p className="group-hover:text-primary truncate text-sm font-medium" title={challenge.name}>
            {challenge.name}
          </p>
          <div className="flex min-w-0 items-center justify-between gap-2">
            <span className="text-muted-foreground truncate text-xs tabular-nums">
              {challenge.num_granted} award{challenge.num_granted === 1 ? "" : "s"}
            </span>
            <AwardStamps slugs={challenge.award_counts.map((c) => c.slug)} />
          </div>
        </div>
      </Card>
    </a>
  )
}
