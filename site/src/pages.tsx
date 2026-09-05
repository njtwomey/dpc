import { href } from "@/lib/base"
import { Award, Trophy, Users } from "lucide-react"
import { Card } from "@/components/ui/card"
import { AwardBadge } from "@/components/AwardBadge"
import { AwardCard } from "@/components/AwardCard"
import { PageHeader } from "@/components/PageHeader"
import { PersonCard } from "@/components/PersonCard"
import { StaticGallery } from "@/components/gallery/StaticGallery"
import {
  awardBySlug, awarders, awards, challenges, memberThumbUrl, meta, recipients,
  type Award as AwardT, type Challenge, type Recipient,
} from "@/lib/dpc"

function Stat({ value, label }: { value: number; label: string }) {
  return (
    <Card className="gap-1 p-5 text-center">
      <p className="text-2xl font-semibold tabular-nums">{value.toLocaleString()}</p>
      <p className="text-muted-foreground text-xs">{label}</p>
    </Card>
  )
}

export function Home() {
  const entries = [
    { path: "/awarders/", label: "awarders", icon: Award },
    { path: "/challenges/", label: "challenges", icon: Trophy },
    { path: "/recipients/", label: "recipients", icon: Users },
  ]
  return (
    <>
      <PageHeader title="DPChallenge Award Gallery"
        description="The awards members of DPChallenge invented and gave each other, gathered from a decade of image comments." />
      <div className="mb-10 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat value={meta.num_grants} label="awards given" />
        <Stat value={meta.num_images} label="images" />
        <Stat value={meta.num_recipients} label="recipients" />
        <Stat value={meta.num_challenges} label="challenges" />
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        {entries.map(({ path, label, icon: Icon }) => (
          <a key={path} href={href(path)}>
            <Card className="hover:border-primary/30 items-center gap-2 p-8 text-center transition-colors hover:shadow-sm">
              <Icon className="text-muted-foreground size-6" />
              <p className="font-medium">Browse {label}</p>
            </Card>
          </a>
        ))}
      </div>
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
      <div className="grid grid-cols-[repeat(auto-fill,minmax(230px,1fr))] gap-4">
        {theirs.map((a) => (
          <AwardCard key={a.slug} award={a} href={href(`/awarders/${a.awarder_slug}/${a.slug}/`)} />
        ))}
      </div>
    </>
  )
}

export function AwardPage({ award }: { award: AwardT }) {
  return (
    <>
      <PageHeader title={award.name} thumb={award.thumb} description={award.description}
        stats={`Given ${award.num_granted.toLocaleString()} times to ${award.num_recipients.toLocaleString()} photographers across ${award.num_challenges.toLocaleString()} challenges`} />
      <StaticGallery imageIds={award.image_ids} />
    </>
  )
}

export function ChallengesList() {
  return (
    <>
      <PageHeader title="Challenges" stats={`${challenges.length.toLocaleString()} challenges with awards`} />
      <div className="divide-y rounded-lg border">
        {challenges.map((c) => (
          <a key={c.id} href={href(`/challenges/${c.slug}/`)}
             className="hover:bg-accent/50 flex items-center justify-between gap-4 px-4 py-3 transition-colors">
            <span className="min-w-0">
              <span className="block truncate text-sm font-medium">{c.name}</span>
              <span className="text-muted-foreground text-xs tabular-nums">
                {c.num_granted} award{c.num_granted === 1 ? "" : "s"}
              </span>
            </span>
            <span className="hidden shrink-0 flex-wrap justify-end gap-1 sm:flex">
              {c.award_counts.slice(0, 4).map((ac) => (
                <AwardBadge key={ac.slug} slug={ac.slug} count={ac.count} />
              ))}
            </span>
          </a>
        ))}
      </div>
    </>
  )
}

export function ChallengePage({ challenge }: { challenge: Challenge }) {
  return (
    <>
      <PageHeader title={challenge.name}
        stats={`${challenge.num_granted} image${challenge.num_granted === 1 ? "" : "s"} received awards`}>
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
      <StaticGallery imageIds={person.image_ids} />
    </>
  )
}

export { awardBySlug }
