/** Grouping a long, date-ordered list into years, and the sticky strip that
 *  navigates it.
 *
 *  Shared by the challenges list and by the galleries. The strip is plain
 *  anchors, so it works with no JavaScript; the client island adds the
 *  active-year marker on top of that.
 */

/** Split an already date-ordered list into runs of the same year.
 *
 *  Runs, not a group-by: the input is sorted, so consecutive items share a
 *  year and a year appears once. Anything whose year is unknown joins the run
 *  in progress rather than forming a phantom group.
 */
export function byYear<T>(items: T[], yearOf: (item: T) => string | undefined) {
  const years: { year: string; items: T[] }[] = []
  for (const item of items) {
    const year = yearOf(item)
    const last = years[years.length - 1]
    if (last && (year === undefined || last.year === year)) last.items.push(item)
    else if (year !== undefined) years.push({ year, items: [item] })
    else years.push({ year: "", items: [item] })
  }
  return years
}

/** The sticky strip of year links.
 *
 *  One scrolling row rather than a wrapping block: two rows of chips would eat
 *  a third of the screen on the way past. `top` clears whatever sits above it.
 */
export function YearIndex({
  years,
  className = "",
}: {
  years: { year: string; items: unknown[] }[]
  className?: string
}) {
  if (years.length < 2) return null
  return (
    <nav
      data-year-index=""
      className={`bg-background/90 sticky top-14 z-30 -mx-4 mb-8 flex gap-1.5 overflow-x-auto border-b px-4 py-2.5 backdrop-blur ${className}`}
    >
      {years.map(({ year, items }) => (
        <a
          key={year}
          href={`#${year}`}
          title={`${items.length} in ${year}`}
          className="bg-muted/60 text-muted-foreground hover:bg-accent hover:text-foreground data-[active]:bg-primary data-[active]:text-primary-foreground shrink-0 rounded-md px-2.5 py-1 text-xs font-medium tabular-nums transition-colors"
        >
          {year}
        </a>
      ))}
    </nav>
  )
}

/** The heading above each year's block. */
export function YearHeading({ year, detail }: { year: string; detail: string }) {
  return (
    <div className="mb-3 flex items-baseline gap-3 border-b pb-2">
      <h2 className="text-xl font-semibold tabular-nums">{year}</h2>
      <span className="text-muted-foreground text-xs">{detail}</span>
    </div>
  )
}
