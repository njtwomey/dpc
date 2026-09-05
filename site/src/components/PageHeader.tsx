import type { ReactNode } from "react"
import { Portrait } from "@/components/Portrait"

/** The banner at the top of every gallery: portrait, title, one line of
 *  numbers, and whatever context the page wants underneath. */
export function PageHeader({
  title, thumb, stats, description, children,
}: {
  title: string
  thumb?: string
  stats?: string
  description?: string
  children?: ReactNode
}) {
  return (
    <header className="mb-8 flex flex-col gap-4 border-b pb-6 sm:flex-row sm:items-start">
      {thumb && <Portrait src={thumb} name={title} className="size-16" />}
      <div className="min-w-0 flex-1 space-y-2">
        <h1 className="text-2xl font-semibold tracking-tight text-balance">{title}</h1>
        {stats && <p className="text-muted-foreground text-sm tabular-nums">{stats}</p>}
        {description && <p className="max-w-prose text-sm leading-relaxed">{description}</p>}
        {children}
      </div>
    </header>
  )
}
