from __future__ import absolute_import

from bs4 import BeautifulSoup

import re

from models import Challenge
from parsers.challenge import get_challenge
from utils import load_or_download


def get_history(session, page_num=None):
    if page_num is None:
        href = "http://www.dpchallenge.com/challenge_history.php?show_all=1"
    else:
        href = f"https://www.dpchallenge.com/challenge_history.php?page={page_num}"

    source = load_or_download(
        session=session, href=href, force=True, save=False, filename=None
    )
    soup = BeautifulSoup(source, "html.parser")

    links = soup.find_all(
        name="a",
        attrs=dict(href=re.compile(r"/challenge_results\.php\?CHALLENGE_ID=(\d+)")),
    )

    challenge_ids = [int(link.attrs["href"].split("=")[-1]) for link in links]

    if page_num is None:
        known_challenges = set(challenge.id for challenge in Challenge.select())
        unknown_challenges = []
        for link in reversed(links):
            challenge_id = int(link.attrs["href"].split("=")[-1])
            if challenge_id not in known_challenges:
                unknown_challenges.append(challenge_id)
    else:
        unknown_challenges = sorted(challenge_ids, reverse=True)

    print(unknown_challenges)

    for challenge_id in sorted(unknown_challenges):
        get_challenge(session=session, challenge_id=challenge_id)
