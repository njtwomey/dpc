from __future__ import absolute_import

from os import makedirs
from os.path import join, exists

from bs4 import BeautifulSoup

import arrow

from models import Challenge, DoesNotExist
from parsers.image import get_image
from utils import load_or_download, clean_text


def get_challenge(session, challenge_id, root='.', follow_images=True, follow_comments=True):
    href = f'http://www.dpchallenge.com/challenge_results.php?CHALLENGE_ID={challenge_id}&show_full=1'

    fileroot = join(root, 'downloaded', 'challenge')
    filename = join(fileroot, f'{challenge_id}.html')
    if not exists(fileroot):
        makedirs(fileroot)

    source = load_or_download(session=session, href=href, filename=filename)
    soup = BeautifulSoup(source, 'html.parser')

    # Load or parse the challenge object
    try:
        challenge = Challenge.get(Challenge.id == challenge_id)

    except DoesNotExist:
        if 'Invalid CHALLENGE_ID.  Please check the URL' in source:
            return

        description = soup.find('div', {'style': 'display:block; margin-left: 22px; margin-top: -16px;'})
        description = clean_text(' '.join(description.text.strip().split()))

        dates = soup.find('div', {'style': 'margin: 2px;'})
        dates_list = list(filter(len, clean_text(dates).split('\n')))

        submission = dates_list[0].split(': ')[1].split(' - ')

        voting = dates_list[1].split(': ')[1].split(' - ')

        num_submissions = int(dates_list[2].split(': ')[1].replace(',', ''))
        num_disqualifications = int(dates_list[3].split(': ')[1].replace(',', ''))
        num_votes = int(dates_list[4].split(': ')[1].replace(',', ''))
        num_comments = int(dates_list[5].split(': ')[1].replace(',', ''))

        average_score = float(dates_list[6].split(': ')[1])
        highest_score = float(dates_list[7].split(': ')[1])
        median_score = float(dates_list[8].split(': ')[1])
        lowest_score = float(dates_list[9].split(': ')[1])

        name_preamble = 'Challenge Results for '

        challenge_name = clean_text(soup.find('tr', {'class': 'forum-heading'}))
        challenge_name = challenge_name[len(name_preamble):]

        def convert_to_date(ss):
            return arrow.get(ss, 'MMM D YYYY').date()

        challenge = Challenge(
            id=challenge_id,
            name=challenge_name,
            description=description,
            submission_start=convert_to_date(submission[0]),
            submission_end=convert_to_date(submission[1]),
            voting_start=convert_to_date(voting[0]),
            voting_end=convert_to_date(voting[1]),
            num_submissions=num_submissions,
            num_disqualifications=num_disqualifications,
            num_votes=num_votes,
            num_comments=num_comments,
            average_score=average_score,
            highest_score=highest_score,
            median_score=median_score,
            lowest_score=lowest_score
        )

        challenge.save(
            force_insert=True
        )

    # Follow each image individually (if necessary)
    if follow_images:
        link_soups = soup.find_all('a', {'class': 'i'})
        for link in link_soups:
            href = link['href']

            if '/image.php?IMAGE_ID=' in href:
                try:
                    get_image(
                        session=session,
                        challenge=challenge,
                        image_id=int(href.split('=')[1]),
                        follow_comments=follow_comments,
                        root=root,
                    )
                except IndexError:
                    print(f"Failed with {link=}")
