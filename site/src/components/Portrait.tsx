import { cn } from "cn"

/** A member or award portrait.
 *
 *  A plain <img>, deliberately not shadcn's Avatar. Radix's AvatarImage tracks
 *  load state in an effect and renders the fallback until it fires -- fine in a
 *  client app, but these pages are prerendered and ship no JavaScript for
 *  cards, so the effect never runs and every portrait would stay stuck on its
 *  initials.
 *
 *  The initials sit *behind* the image instead: visible while it loads, and
 *  left showing if the URL 404s, which some member profiles do.
 */
export function Portrait({
  src, name, className,
}: {
  src?: string | null
  name: string
  className?: string
}) {
  return (
    <span
      className={cn(
        "bg-muted text-muted-foreground relative inline-flex shrink-0 items-center justify-center overflow-hidden rounded-lg text-sm font-medium select-none",
        className,
      )}
      aria-hidden={!name}
    >
      <span aria-hidden="true">{name.slice(0, 2).toUpperCase()}</span>
      {src && (
        <img
          src={src}
          alt={name}
          loading="lazy"
          className="absolute inset-0 size-full object-cover"
        />
      )}
    </span>
  )
}
