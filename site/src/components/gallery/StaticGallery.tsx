import { ImageCard } from "@/components/ImageCard"
import { YearHeading, YearIndex, byYear } from "@/components/YearIndex"
import { awardBySlug, challengeYear, lookupImages } from "@/lib/dpc"
import type { AwardRef, DpcImage } from "@/lib/urls"

/** The server-rendered grid.
 *
 *  It embeds exactly the data its viewer needs -- these images, and only the
 *  awards they actually carry -- so the client bundle imports no dataset at
 *  all. With JavaScript off the grid still renders, each tile linking to
 *  dpchallenge.
 */
export function StaticGallery({
  imageIds,
  grouped = false,
}: {
  imageIds: number[]
  /** Break the grid into years. Purely presentational -- see below. */
  grouped?: boolean
}) {
  const images = lookupImages(imageIds)
  if (!images.length) {
    return <p className="text-muted-foreground py-12 text-center text-sm">No images.</p>
  }

  const awards: Record<string, AwardRef> = {}
  for (const image of images) {
    for (const slug of image.awards) {
      const award = awardBySlug.get(slug)
      if (award && !awards[slug]) {
        awards[slug] = {
          slug, name: award.name, thumb: award.thumb, awarder_slug: award.awarder_slug,
        }
      }
    }
  }

  return (
    <div data-gallery="">
      {/* One flat list, whatever the grid looks like. The viewer steps through
          this array, so grouping must never reach it -- otherwise the arrows
          would stop at the end of a year instead of carrying on into the next. */}
      <script
        type="application/json"
        data-gallery-payload=""
        dangerouslySetInnerHTML={{ __html: JSON.stringify({ images, awards }) }}
      />
      {grouped ? <GroupedGrid images={images} /> : <Grid images={images} from={0} />}
    </div>
  )
}

const GRID = "grid grid-cols-[repeat(auto-fill,minmax(225px,1fr))] gap-4"

/** ``from`` is the offset of these images within the flat payload, so every
 *  tile carries its global index no matter which year it is rendered under. */
function Grid({ images, from }: { images: DpcImage[]; from: number }) {
  return (
    <div className={GRID}>
      {images.map((image, i) => (
        <ImageCard key={image.id} image={image} index={from + i} />
      ))}
    </div>
  )
}

function GroupedGrid({ images }: { images: DpcImage[] }) {
  const years = byYear(images, (image) => challengeYear.get(image.challenge_id))
  if (years.length < 2) return <Grid images={images} from={0} />

  // Each year's offset into the flat payload. Quadratic, over at most a couple
  // of dozen years, and it keeps the render free of a mutable accumulator.
  const sections = years.map((group, i) => ({
    ...group,
    from: years.slice(0, i).reduce((n, g) => n + g.items.length, 0),
  }))

  return (
    <>
      <YearIndex years={years} />
      {sections.map(({ year, items, from }) => (
        // scroll-mt clears both sticky bars: the site header and this index.
        <section key={year} id={year} className="mb-10 scroll-mt-28">
          <YearHeading
            year={year}
            detail={`${items.length} image${items.length === 1 ? "" : "s"}`}
          />
          <Grid images={items} from={from} />
        </section>
      ))}
    </>
  )
}
