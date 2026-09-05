import { Badge } from "@/components/ui/badge"
import { awardBySlug } from "@/lib/dpc"

/** An award, optionally with how many times it appears in this context. */
export function AwardBadge({ slug, count }: { slug: string; count?: number }) {
  const award = awardBySlug.get(slug)
  if (!award) return null

  return (
    <Badge variant="secondary" className="gap-1.5 py-1 pr-1.5 pl-2 font-normal">
      <img src={award.thumb} alt="" className="size-4 rounded-[3px] object-cover" />
      <span>{award.name}</span>
      {count !== undefined && (
        <span className="bg-primary text-primary-foreground rounded px-1.5 py-px text-[11px] font-medium tabular-nums">
          {count}
        </span>
      )}
    </Badge>
  )
}
