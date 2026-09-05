/** dpchallenge URL construction and shared types.
 *
 *  Deliberately imports no JSON: the client island pulls this in, and anything
 *  it touches ends up in the browser bundle. Mirrors src/dpc/export/urls.py.
 */
export type Count = { slug: string; count: number }

export type DpcImage = {
  id: number; title: string
  challenge_id: number; challenge_name: string; challenge_slug: string
  photographer_id: number; photographer_name: string; photographer_slug: string
  awards: string[]
}

export type AwardRef = { slug: string; name: string; thumb: string; awarder_slug: string }

const bucket = (n: number, size: number) => {
  const lower = Math.floor(n / size) * size
  return `${lower}-${lower + size - 1}`
}

export const imageUrl = (challengeId: number, imageId: number, width = 1200) =>
  `https://images.dpchallenge.com/images_challenge/${bucket(challengeId, 1000)}` +
  `/${challengeId}/${width}/Copyrighted_Image_Reuse_Prohibited_${imageId}.jpg`

export const thumbUrl = (challengeId: number, imageId: number) =>
  imageUrl(challengeId, imageId, 120)

export const memberThumbUrl = (memberId: number) =>
  `https://images.dpchallenge.com/images_profile/${bucket(memberId, 5000)}/120/${memberId}.jpg`

export const imagePage = (id: number) => `https://www.dpchallenge.com/image.php?IMAGE_ID=${id}`
export const memberPage = (id: number) => `https://www.dpchallenge.com/profile.php?USER_ID=${id}`
export const challengePage = (id: number) =>
  `https://www.dpchallenge.com/challenge_results.php?CHALLENGE_ID=${id}`
