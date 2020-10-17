from __future__ import absolute_import

from os import makedirs
from os.path import join, exists

from bs4 import BeautifulSoup

import arrow

import re

from models import Comment, Image, DoesNotExist
from parsers.member import get_member
from utils import load_or_download, clean_text


def parse_comments(session, image_id, source, soup, image):
    comment_soup = soup.find(
        "table",
        {"width": "90%", "cellspacing": "1", "cellpadding": "2", "align": "center"},
    )

    if comment_soup is None:
        return

    comments = []

    rows = comment_soup.find_all("td")

    comment_ids = Comment.select(Comment.id).where(Comment.image == image).tuples()
    comment_ids_set = set([c[0] for c in comment_ids])

    during_challenge = False

    row_iter = iter(rows)
    for row in row_iter:
        if row.text.strip() == "Comments Made During the Challenge":
            during_challenge = True

        link = row.find("a")
        if link and "name" in link.attrs:
            comment_id = int(link.attrs["name"])
            if comment_id not in comment_ids_set:
                member_link = row.find_all("a")[2]
                member_name = member_link.text
                member_id = int(member_link.attrs["href"].split("=")[-1])
                commenter = get_member(
                    session=session, member_id=member_id, name=member_name
                )

                reporting = next(row_iter)
                date = arrow.get(
                    reporting.text.strip(), "MM/DD/YYYY HH:mm:ss A"
                ).datetime

                comment_info = next(row_iter)
                comment_str = comment_info.text
                comment_strs = comment_str.split("Message edited by author ")
                edited = None
                if len(comment_strs) > 1:
                    edited = arrow.get(
                        comment_strs[-1].strip()[:19], "YYYY-MM-DD HH:mm:ss"
                    ).datetime
                    comment_str = " ".join(comment_strs[:-1])

                # Quotes
                has_quote = False

                # quotes = table.find_all('table', {'width': '95%',
                #                                   'align': 'center'})
                # if quotes:
                #     has_quote = True
                #     for quote in quotes:
                #         quote.extract()

                comments.append(
                    {
                        "id": comment_id,
                        "commenter": commenter,
                        "image": image,
                        "raw_comment": comment_info.find("td"),
                        "comment": comment_str,
                        "date": date,
                        "has_quote": has_quote,
                        "made_during_challenge": during_challenge,
                        "edited": edited,
                    }
                )

    if len(comments) > 0:
        Comment.insert_many(comments).execute()


def parse_image_stats(source, soup):
    source = source.split('<td>Voting Breakdown <span style="font-weight: normal;">')[
        1
    ].split('<td valign="top" width="450" class="textsm">')[0]

    breakdown_soup = soup.findAll(
        "div", {"class": lambda el: el == "breakdown_vote_count"}
    )

    def dq():
        return (
            "Avg (all users)"
            not in source
            # or
            # ('<div align="center"><b>This image has been locked for further commenting.</b></div>' in source)
        )

    def split_parse(key, ty):
        if key not in source:
            return None

        search = re.search(r"([\d\.]+)", source.split(key)[1])

        if not search:
            return None

        return ty(search.group(1))

    def finishing_place():
        return split_parse("<b>Place:</b> ", float)

    def average_all():
        return split_parse("<b>Avg (all users):</b> ", float)

    def average_commenters():
        return split_parse("<b>Avg (commenters):</b> ", float)

    def average_participants():
        return split_parse("<b>Avg (participants):</b> ", float)

    def average_non_participants():
        return split_parse("<b>Avg (non-participants):</b> ", float)

    def num_views():
        return split_parse("<b>Views since voting:</b> ", float)

    def num_votes():
        return split_parse("<b>Votes:</b> ", float)

    def breakdown():
        return [int(el.text) for el in breakdown_soup]

    is_disqualified = dq()
    if is_disqualified:
        return dict(
            position=None,
            average_all=None,
            average_comments=None,
            average_participants=None,
            average_non_participants=None,
            num_views=num_views(),
            num_votes=None,
            breakdown=breakdown(),
            disqualified=is_disqualified,
        )

    else:
        return dict(
            position=finishing_place(),
            average_all=average_all(),
            average_comments=average_commenters(),
            average_participants=average_participants(),
            average_non_participants=average_non_participants(),
            num_views=num_views(),
            num_votes=num_votes(),
            breakdown=breakdown(),
            disqualified=is_disqualified,
        )


def get_image(session, challenge, image_id, root=".", follow_comments=True):
    href = "http://www.dpchallenge.com/image.php?IMAGE_ID={image_id}".format(
        image_id=image_id
    )
    fileroot = join(root, "downloaded", "image", "{}".format(challenge.id))
    filename = join(fileroot, "{}.html".format(image_id))
    if not exists(fileroot):
        makedirs(fileroot)

    source = load_or_download(session=session, href=href, filename=filename)
    soup = BeautifulSoup(source, "html.parser")

    try:
        image = Image.get(Image.id == image_id)

    except DoesNotExist:
        image_title = clean_text(soup.find("div", {"class": "imagetitle"}))
        member_id = int(
            soup.find_all("a", {"class": "u"})[1]["href"].split("=")[1].split("&")[0]
        )

        photographer = get_member(session=session, member_id=member_id, root=root)

        stats = parse_image_stats(source=source, soup=soup)

        image = Image(
            id=image_id,
            challenge=challenge,
            photographer=photographer,
            name=image_title,
            votes=stats["breakdown"],
            average_all=stats["average_all"],
            average_comments=stats["average_comments"],
            average_participants=stats["average_participants"],
            average_non_participants=stats["average_non_participants"],
            num_views=stats["num_views"],
            num_votes=stats["num_votes"],
            disqualified=stats["disqualified"],
        )

        image.save(force_insert=True)

    if follow_comments:
        parse_comments(
            session=session, image_id=image_id, source=source, soup=soup, image=image
        )

    return image
