from __future__ import annotations

import pytest

from dpc.export.urls import (
    bucket,
    challenge_page_url,
    image_page_url,
    image_thumb_url,
    image_url,
    member_page_url,
    member_thumb_url,
)


@pytest.mark.parametrize(
    ("number", "size", "expected"),
    [
        (1303, 1000, "1000-1999"),
        (1, 1000, "0-999"),
        (1000, 1000, "1000-1999"),
        (999, 1000, "0-999"),
        (50695, 5000, "50000-54999"),
        (75618, 5000, "75000-79999"),
    ],
)
def test_bucket(number, size, expected):
    assert bucket(number, size) == expected


class TestExactUrlsFromTheShippedSite:
    """Byte-for-byte against URLs in the currently published data."""

    def test_full_image(self):
        assert image_url(1303, 921974) == (
            "https://images.dpchallenge.com/images_challenge/1000-1999/1303/1200/"
            "Copyrighted_Image_Reuse_Prohibited_921974.jpg"
        )

    def test_thumbnail(self):
        assert image_thumb_url(1303, 921974) == (
            "https://images.dpchallenge.com/images_challenge/1000-1999/1303/120/"
            "Copyrighted_Image_Reuse_Prohibited_921974.jpg"
        )

    def test_member_thumbnail(self):
        assert member_thumb_url(75618) == (
            "https://images.dpchallenge.com/images_profile/75000-79999/120/75618.jpg"
        )

    def test_image_page(self):
        assert image_page_url(921974) == "https://www.dpchallenge.com/image.php?IMAGE_ID=921974"

    def test_member_page(self):
        assert member_page_url(75618) == "https://www.dpchallenge.com/profile.php?USER_ID=75618"

    def test_challenge_page(self):
        assert challenge_page_url(1303) == (
            "https://www.dpchallenge.com/challenge_results.php?CHALLENGE_ID=1303"
        )
