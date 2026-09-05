/** Types and URL helpers for the exported DPC dataset.
 *
 * The export deliberately ships ids rather than URLs -- every dpchallenge asset
 * URL is derivable from an id, and spelling them out multiplied the old export
 * to 38 MB. These mirror src/dpc/export/urls.py exactly.
 */
import awardersJson from "@data/awarders.json"
import awardsJson from "@data/awards.json"
import challengesJson from "@data/challenges.json"
import imagesJson from "@data/images.json"
import metaJson from "@data/meta.json"
import recipientsJson from "@data/recipients.json"

export type { Count, DpcImage, AwardRef } from "@/lib/urls"
export {
  imageUrl, thumbUrl, memberThumbUrl, imagePage, memberPage, challengePage,
} from "@/lib/urls"
import type { DpcImage } from "@/lib/urls"

export type Awarder = {
  id: number; name: string; slug: string
  thumb: string | null; num_granted: number; award_slugs: string[]
}
export type Award = {
  slug: string; name: string; description: string; thumb: string
  awarder_id: number; awarder_slug: string; awarder_name: string
  num_granted: number; num_recipients: number; num_challenges: number
  image_ids: number[]
}
export type Challenge = {
  id: number; name: string; slug: string
  num_granted: number; award_counts: { slug: string; count: number }[]; image_ids: number[]
}
export type Recipient = {
  id: number; name: string; slug: string
  num_granted: number; num_awards: number; num_challenges: number
  award_counts: { slug: string; count: number }[]; image_ids: number[]
}

export const awarders = awardersJson as Awarder[]
export const awards = awardsJson as Award[]
export const challenges = challengesJson as Challenge[]
export const recipients = recipientsJson as Recipient[]
export const images = imagesJson as Record<string, DpcImage>
export const meta = metaJson as {
  num_awarders: number; num_awards: number; num_challenges: number
  num_grants: number; num_images: number; num_recipients: number
}

export const awardBySlug = new Map(awards.map((a) => [a.slug, a]))

export const lookupImages = (ids: number[]) =>
  ids.map((id) => images[String(id)]).filter(Boolean)
