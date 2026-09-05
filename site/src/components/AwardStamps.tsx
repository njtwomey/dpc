import { awardBySlug } from "@/lib/dpc"

const SHOWN = 5

/** The awards an image won, as a row of small stamps.
 *
 *  Each graphic is *contained* on its own chip rather than cropped: they are
 *  arbitrary images with different shapes and backgrounds, and cropping them to
 *  squares turns a row into visual noise. Uniform chips make them read as a set
 *  of medals.
 */
export function AwardStamps({ slugs }: { slugs: string[] }) {
  if (!slugs.length) return null
  const shown = slugs.slice(0, SHOWN)
  const extra = slugs.length - shown.length

  return (
    <span className="flex shrink-0 items-center gap-1">
      {shown.map((slug) => {
        const award = awardBySlug.get(slug)
        if (!award) return null
        return (
          <span
            key={slug}
            title={`${award.name} — ${award.awarder_name}`}
            className="bg-muted/60 grid size-6 place-items-center rounded ring-1 ring-black/5"
          >
            <img
              src={award.thumb}
              alt={award.name}
              loading="lazy"
              className="max-h-[18px] max-w-[18px] object-contain"
            />
          </span>
        )
      })}
      {extra > 0 && (
        <span className="text-muted-foreground text-[11px] font-medium tabular-nums">
          +{extra}
        </span>
      )}
    </span>
  )
}
