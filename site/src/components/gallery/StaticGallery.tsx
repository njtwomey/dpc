import { ImageCard } from "@/components/ImageCard"
import { awardBySlug, lookupImages } from "@/lib/dpc"
import type { AwardRef } from "@/lib/urls"

/** The server-rendered grid.
 *
 *  It embeds exactly the data its viewer needs -- these images, and only the
 *  awards they actually carry -- so the client bundle imports no dataset at
 *  all. With JavaScript off the grid still renders, each tile linking to
 *  dpchallenge.
 */
export function StaticGallery({ imageIds }: { imageIds: number[] }) {
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
      <script
        type="application/json"
        data-gallery-payload=""
        dangerouslySetInnerHTML={{ __html: JSON.stringify({ images, awards }) }}
      />
      <div className="grid grid-cols-[repeat(auto-fill,minmax(190px,1fr))] gap-4">
        {images.map((image, i) => <ImageCard key={image.id} image={image} index={i} />)}
      </div>
    </div>
  )
}
