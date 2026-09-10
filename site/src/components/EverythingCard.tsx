import { ChevronRight, LayoutGrid } from "lucide-react"
import { Card } from "@/components/ui/card"
import { challengeYear, images as allImages, type Awarder } from "@/lib/dpc"
import { thumbUrl } from "@/lib/urls"

/** The way in to everything one member has given.
 *
 *  It sits above the grid of their individual awards, so it has to look like a
 *  different kind of thing rather than a bigger version of the same one: a wide
 *  band of the photographs themselves, with the gradient running sideways so
 *  the label stays legible on the left while the pictures survive on the right.
 */
export function EverythingCard({ awarder, href }: { awarder: Awarder; href: string }) {
  const preview = awarder.image_ids
    .slice(0, 10)
    .map((id) => allImages[String(id)])
    .filter(Boolean)

  const years = awarder.image_ids
    .map((id) => allImages[String(id)]?.challenge_id)
    .map((cid) => (cid === undefined ? undefined : challengeYear.get(cid)))
    .filter((y): y is string => Boolean(y))
  const span = years.length ? `${years[years.length - 1]}–${years[0]}` : ""

  return (
    <a href={href} className="group mb-6 block">
      <Card className="hover:border-primary/30 relative gap-0 overflow-hidden p-0 transition-shadow hover:shadow-md">
        <div className="relative h-20 sm:h-24">
          <div className="bg-muted absolute inset-0 grid grid-cols-5 gap-px sm:grid-cols-10">
            {preview.map((image) => (
              <img
                key={image.id}
                src={thumbUrl(image.challenge_id, image.id)}
                alt=""
                loading="lazy"
                className="size-full object-cover"
              />
            ))}
          </div>
          {/* Sideways, unlike the homepage tiles: the text sits left, so the
              right-hand photographs keep their colour. */}
          <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/55 to-black/20" />

          <div className="absolute inset-0 flex items-center justify-between gap-4 px-5 text-white">
            <div className="min-w-0">
              <p className="flex items-center gap-2 text-sm font-medium">
                <LayoutGrid className="size-4 shrink-0" />
                Everything {awarder.name} has given
              </p>
              <p className="pt-0.5 text-xs tabular-nums text-white/75">
                {awarder.num_granted.toLocaleString()} awards to{" "}
                {awarder.image_ids.length.toLocaleString()} images
                {span && ` · ${span}`}
              </p>
            </div>
            <ChevronRight className="size-5 shrink-0 opacity-70 transition-transform group-hover:translate-x-0.5" />
          </div>
        </div>
      </Card>
    </a>
  )
}
