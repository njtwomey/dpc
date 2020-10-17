from __future__ import absolute_import

from os.path import join, exists
from os import makedirs

from arrow.parser import ParserMatchError
from bs4 import BeautifulSoup

import arrow

from models import Member, DoesNotExist
from utils import load_or_download, clean_text


def get_member(session, member_id, name="", root="."):
    try:
        member = Member.get(Member.id == member_id)

    except DoesNotExist:
        href = "http://www.dpchallenge.com/profile.php?USER_ID={member_id}".format(
            member_id=member_id
        )

        fileroot = join(root, "downloaded", "member")
        filename = join(fileroot, "{}.html".format(member_id))
        if not exists(fileroot):
            makedirs(fileroot)

        source = load_or_download(session=session, href=href, filename=filename)
        soup = BeautifulSoup(source, "html.parser")

        if soup.find("font", {"color": "red"}):
            # HAS THE MEMBER CANCELLED THEIR MEMBERSHIP?
            member = Member(id=member_id, name=name, join_date=arrow.now().date())

        else:
            # NORMAL MEMBERSHIP
            member = (
                soup.find(
                    name="table",
                    attrs=dict(cellspacing="5", cellpadding="0", width="100%"),
                )
                .find(name="table")
                .find_all(name="td")
            )

            join_ind = -1
            member_ind = -1

            for ui, uu in enumerate(member):
                key = ascii(uu.text)

                if "Registered:" in key:
                    join_ind = ui + 1

                elif "Username:" in key:
                    member_ind = ui + 1

            assert join_ind > 0 and member_ind > 0
            name = clean_text(member[member_ind]).split()[0]

            date = clean_text(member[join_ind])
            date = date.split()
            date[1] = date[1][:-2]
            try:
                date = arrow.get(" ".join(date), "MMM\\. D YYYY")
            except ParserMatchError:
                date = arrow.get(" ".join(date), "MMM. D YYYY")

            member = Member(id=member_id, name=name, join_date=date.date())

        member.save(force_insert=True)

    return member
