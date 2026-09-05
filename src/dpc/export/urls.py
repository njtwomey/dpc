"""dpchallenge URL construction.

Image and profile assets live in numbered buckets, so every URL is derivable
from an id. The exported data therefore stores ids, not URLs.
"""

from __future__ import annotations

IMAGE_BUCKET_SIZE = 1000
PROFILE_BUCKET_SIZE = 5000

THUMB_WIDTH = 120
FULL_WIDTH = 1200

_SITE = "https://www.dpchallenge.com"
_IMAGES = "https://images.dpchallenge.com"

# Every hosted image filename carries this prefix.
_IMAGE_PREFIX = "Copyrighted_Image_Reuse_Prohibited"


def bucket(number: int, size: int) -> str:
    """``(1303, 1000)`` -> ``'1000-1999'``."""
    lower = (number // size) * size
    return f"{lower}-{lower + size - 1}"


def challenge_image_root(challenge_id: int) -> str:
    return f"{_IMAGES}/images_challenge/{bucket(challenge_id, IMAGE_BUCKET_SIZE)}/{challenge_id}"


def image_url(challenge_id: int, image_id: int, width: int = FULL_WIDTH) -> str:
    root = challenge_image_root(challenge_id)
    return f"{root}/{width}/{_IMAGE_PREFIX}_{image_id}.jpg"


def image_thumb_url(challenge_id: int, image_id: int) -> str:
    return image_url(challenge_id, image_id, width=THUMB_WIDTH)


def member_thumb_url(member_id: int) -> str:
    bucketed = bucket(member_id, PROFILE_BUCKET_SIZE)
    return f"{_IMAGES}/images_profile/{bucketed}/{THUMB_WIDTH}/{member_id}.jpg"


def image_page_url(image_id: int) -> str:
    return f"{_SITE}/image.php?IMAGE_ID={image_id}"


def member_page_url(member_id: int) -> str:
    return f"{_SITE}/profile.php?USER_ID={member_id}"


def challenge_page_url(challenge_id: int) -> str:
    return f"{_SITE}/challenge_results.php?CHALLENGE_ID={challenge_id}"
