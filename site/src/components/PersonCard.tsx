import { Card } from "@/components/ui/card"
import { Portrait } from "@/components/Portrait"

/** An awarder or a recipient.
 *
 *  The portrait is the card: full-bleed and square, with the name and count on
 *  a strip underneath. These are photographers, so their picture should carry
 *  the tile rather than sit in it as a token.
 */
export function PersonCard({
  href, name, thumb, stat, statLabel,
}: {
  href: string; name: string; thumb: string; stat: number; statLabel: string
}) {
  return (
    <a href={href} className="group block">
      <Card className="hover:border-primary/30 gap-0 overflow-hidden p-0 transition-shadow hover:shadow-md">
        <Portrait
          src={thumb}
          name={name}
          className="aspect-square w-full rounded-none text-2xl [&>img]:transition-transform [&>img]:duration-300 group-hover:[&>img]:scale-[1.04]"
        />
        <div className="min-w-0 px-3 py-2.5 text-center">
          <p className="truncate text-sm font-medium" title={name}>{name}</p>
          <p className="text-muted-foreground text-xs tabular-nums">
            {stat.toLocaleString()} {statLabel}
          </p>
        </div>
      </Card>
    </a>
  )
}
