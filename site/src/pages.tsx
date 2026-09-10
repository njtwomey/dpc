import type { ReactNode } from "react"
import { href } from "@/lib/base"
import { Award, ChevronRight, Trophy, Users, type LucideIcon } from "lucide-react"
import { Card } from "@/components/ui/card"
import { AwardBadge } from "@/components/AwardBadge"
import { AwardCard } from "@/components/AwardCard"
import { EverythingCard } from "@/components/EverythingCard"
import { ChallengeCard } from "@/components/ChallengeCard"
import { PageHeader } from "@/components/PageHeader"
import { PersonCard } from "@/components/PersonCard"
import { YearHeading, YearIndex, byYear } from "@/components/YearIndex"
import { Portrait } from "@/components/Portrait"
import { StaticGallery } from "@/components/gallery/StaticGallery"
import {
  awardBySlug, awarders, awards, challenges, images, memberThumbUrl, meta, recipients,
  thumbUrl, type Award as AwardT, type Challenge, type DpcImage, type Recipient,
} from "@/lib/dpc"

/** The newest awarded photographs: challenges are exported newest first, and
 *  each one's image_ids are already in award order. */
function latestImageIds(limit: number) {
  const ids: number[] = []
  for (const challenge of challenges) {
    for (const id of challenge.image_ids) {
      ids.push(id)
      if (ids.length === limit) return ids
    }
  }
  return ids
}

/** One of the three ways in. A picture fills the tile and the label sits on it,
 *  so these read as doors rather than as another row of statistics. */
function NavTile({
  path, label, count, unit, icon: Icon, children,
}: {
  path: string
  label: string
  count: number
  unit: string
  icon: LucideIcon
  children: ReactNode
}) {
  return (
    <a href={href(path)} className="group block">
      <Card className="gap-0 overflow-hidden p-0 transition-shadow hover:shadow-lg">
        <div className="relative aspect-[16/10]">
          {children}
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/45 to-black/5" />
          <div className="absolute inset-x-0 bottom-0 flex items-end justify-between gap-3 p-4 text-white">
            <div className="min-w-0">
              <p className="flex items-center gap-2 text-lg font-semibold">
                <Icon className="size-5" /> {label}
              </p>
              <p className="text-xs tabular-nums text-white/75">
                {count.toLocaleString()} {unit}
              </p>
            </div>
            <ChevronRight className="size-5 shrink-0 opacity-80 transition-transform group-hover:translate-x-1" />
          </div>
        </div>
      </Card>
    </a>
  )
}

const STATS = [
  { value: meta.num_grants, label: "awards given" },
  { value: meta.num_images, label: "photographs" },
  { value: meta.num_recipients, label: "recipients" },
  { value: meta.num_challenges, label: "challenges" },
]

export function Home() {
  const medals = [...awards].sort((a, b) => b.num_granted - a.num_granted).slice(0, 15)
  const faces = recipients.slice(0, 6)

  // One winner from each of the newest challenges, skipping anything the strip
  // at the bottom of the page already shows: the same thumbnail twice on one
  // screen reads as a mistake.
  const latest = latestImageIds(100)
  const taken = new Set(latest)
  const recent: DpcImage[] = []
  for (const challenge of challenges) {
    const id = challenge.image_ids.find((i) => !taken.has(i))
    const image = id === undefined ? undefined : images[String(id)]
    if (!image) continue
    recent.push(image)
    taken.add(image.id)
    if (recent.length === 3) break
  }

  return (
    <>
      <header className="mb-8 space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight text-balance">
          DPChallenge Award Gallery
        </h1>
        <p className="max-w-prose text-sm leading-relaxed text-muted-foreground">
          The awards members of DPChallenge invented and gave each other, gathered from a
          decade of image comments.
        </p>
      </header>

      <div className="mb-10 grid gap-4 sm:grid-cols-3">
        <NavTile path="/awarders/" label="Awarders" icon={Award}
                 count={meta.num_awarders} unit="members give awards">
          {/* The awards themselves: an awarder is known by the medal they made.
              Packed tight and edge to edge -- spaced out on white cells they
              read as a form, not as a collage. */}
          <div className="bg-muted absolute inset-0 grid grid-cols-5 gap-px">
            {medals.map((award) => (
              <img key={award.slug} src={award.thumb} alt="" loading="lazy"
                   className="size-full bg-white object-cover" />
            ))}
          </div>
        </NavTile>

        <NavTile path="/challenges/" label="Challenges" icon={Trophy}
                 count={meta.num_challenges} unit="challenges with awards">
          <div className="bg-muted absolute inset-0 grid grid-cols-3 gap-px">
            {recent.map((image) => (
              <img key={image.id} src={thumbUrl(image.challenge_id, image.id)} alt=""
                   loading="lazy" className="size-full object-cover" />
            ))}
          </div>
        </NavTile>

        <NavTile path="/recipients/" label="Recipients" icon={Users}
                 count={meta.num_recipients} unit="photographers have won one">
          <div className="bg-muted absolute inset-0 grid grid-cols-3 gap-px">
            {faces.map((person) => (
              <Portrait key={person.id} src={memberThumbUrl(person.id)} name={person.name}
                        className="size-full rounded-none" />
            ))}
          </div>
        </NavTile>
      </div>

      {/* Numbers, not cards: they are context for the tiles above, not a fourth
          thing to click. */}
      <dl className="mb-12 grid grid-cols-2 gap-x-8 gap-y-5 border-y py-5 sm:grid-cols-4">
        {STATS.map(({ value, label }) => (
          <div key={label}>
            <dt className="text-muted-foreground text-xs">{label}</dt>
            <dd className="text-2xl font-semibold tabular-nums">{value.toLocaleString()}</dd>
          </div>
        ))}
      </dl>

      <section>
        <div className="mb-4 flex items-baseline justify-between gap-4 border-b pb-2">
          <h2 className="text-xl font-semibold">Latest awards</h2>
          <a href={href("/challenges/")}
             className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-xs font-medium">
            All challenges <ChevronRight className="size-3.5" />
          </a>
        </div>
        <StaticGallery imageIds={latest} />
      </section>
    </>
  )
}

export function AwardersList() {
  return (
    <>
      <PageHeader title="Awarders" stats={`${awarders.length} members give awards`} />
      <div className="grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-4">
        {awarders.map((a) => (
          <PersonCard key={a.id} href={href(`/awarders/${a.slug}/`)} name={a.name}
                      thumb={a.thumb ?? ""} stat={a.num_granted} statLabel="given" />
        ))}
      </div>
    </>
  )
}

export function AwarderPage({ slug }: { slug: string }) {
  const awarder = awarders.find((a) => a.slug === slug)!
  const theirs = awards.filter((a) => a.awarder_slug === slug)
  return (
    <>
      <PageHeader title={`Awards given by ${awarder.name}`} thumb={awarder.thumb ?? undefined}
        stats={`${awarder.num_granted.toLocaleString()} awards across ${theirs.length} kinds`} />
      <EverythingCard awarder={awarder} href={href(`/awarders/${slug}/all/`)} />
      <div className="grid grid-cols-[repeat(auto-fill,minmax(230px,1fr))] gap-4">
        {theirs.map((a) => (
          <AwardCard key={a.slug} award={a} href={href(`/awarders/${a.awarder_slug}/${a.slug}/`)} />
        ))}
      </div>
    </>
  )
}

/** Every image a member has ever awarded anything to, in one gallery.
 *
 *  The per-award pages answer "who won this bling"; this answers "what has
 *  this person been marking out", which is a different question and the one
 *  you want when a member gives several related awards. */
export function AwarderGalleryPage({ slug }: { slug: string }) {
  const awarder = awarders.find((a) => a.slug === slug)!
  const theirs = awards.filter((a) => a.awarder_slug === slug)
  return (
    <>
      <PageHeader title={`Everything given by ${awarder.name}`} thumb={awarder.thumb ?? undefined}
        stats={`${awarder.num_granted.toLocaleString()} awards to ${awarder.image_ids.length.toLocaleString()} images`}>
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          {theirs.map((a) => <AwardBadge key={a.slug} slug={a.slug} count={a.num_granted} />)}
        </div>
        <p className="pt-1 text-xs">
          <a href={href(`/awarders/${slug}/`)}
             className="text-muted-foreground hover:text-foreground hover:underline">
            Back to {awarder.name}'s awards
          </a>
        </p>
      </PageHeader>
      <StaticGallery imageIds={awarder.image_ids} grouped />
    </>
  )
}

export function AwardPage({ award }: { award: AwardT }) {
  return (
    <>
      <PageHeader title={award.name} thumb={award.thumb} description={award.description}
        stats={`Given ${award.num_granted.toLocaleString()} times to ${award.num_recipients.toLocaleString()} photographers across ${award.num_challenges.toLocaleString()} challenges`} />
      <StaticGallery imageIds={award.image_ids} grouped />
    </>
  )
}

/** Challenges grouped into the year their voting closed.
 *
 *  1,516 rows of text is a wall, and the export is already in date order, so
 *  the years were sitting there unused. Splitting on them turns the page into
 *  something you can navigate -- and the cards show what was actually won. */
export function ChallengesList() {
  const years = byYear(challenges, (c) => c.ended.slice(0, 4))

  return (
    <>
      <PageHeader title="Challenges"
        stats={`${challenges.length.toLocaleString()} challenges with awards, ${years[years.length - 1]!.year}–${years[0]!.year}`} />

      <YearIndex years={years} />

      {years.map(({ year, items }) => (
        // scroll-mt clears both sticky bars: the h-14 site header and the year index.
        <section key={year} id={year} className="mb-10 scroll-mt-28">
          <YearHeading
            year={year}
            detail={`${items.length} challenge${items.length === 1 ? "" : "s"} \u00b7 ${items
              .reduce((n, c) => n + c.num_granted, 0)
              .toLocaleString()} awards`}
          />
          <div className="grid grid-cols-[repeat(auto-fill,minmax(215px,1fr))] gap-4">
            {items.map((c) => (
              <ChallengeCard key={c.id} challenge={c} href={href(`/challenges/${c.slug}/`)} />
            ))}
          </div>
        </section>
      ))}
    </>
  )
}

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
]

/** "14 January 2013". Formatted by hand rather than through toLocaleDateString,
 *  so the prerendered HTML does not depend on the build machine's locale. */
function longDate(iso: string) {
  const [year, month, day] = iso.split("-")
  return `${Number(day)} ${MONTHS[Number(month) - 1]} ${year}`
}

export function ChallengePage({ challenge }: { challenge: Challenge }) {
  return (
    <>
      <PageHeader title={challenge.name}
        stats={`Voting closed ${longDate(challenge.ended)} \u00b7 ${challenge.num_granted} image${challenge.num_granted === 1 ? "" : "s"} received awards`}>
        <div className="flex flex-wrap gap-1.5 pt-1">
          {challenge.award_counts.map((ac) => <AwardBadge key={ac.slug} slug={ac.slug} count={ac.count} />)}
        </div>
      </PageHeader>
      <StaticGallery imageIds={challenge.image_ids} />
    </>
  )
}

export function RecipientsList() {
  return (
    <>
      <PageHeader title="Recipients" stats={`${recipients.length.toLocaleString()} photographers have won an award`} />
      <div className="grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-4">
        {recipients.map((r) => (
          <PersonCard key={r.id} href={href(`/recipients/${r.slug}/`)} name={r.name}
                      thumb={memberThumbUrl(r.id)} stat={r.num_granted} statLabel="awards" />
        ))}
      </div>
    </>
  )
}

export function RecipientPage({ person }: { person: Recipient }) {
  return (
    <>
      <PageHeader title={person.name} thumb={memberThumbUrl(person.id)}
        stats={`${person.num_granted} awards (${person.num_awards} distinct) across ${person.num_challenges} challenges`}>
        <div className="flex flex-wrap gap-1.5 pt-1">
          {person.award_counts.map((ac) => <AwardBadge key={ac.slug} slug={ac.slug} count={ac.count} />)}
        </div>
      </PageHeader>
      <StaticGallery imageIds={person.image_ids} grouped />
    </>
  )
}

export { awardBySlug }
