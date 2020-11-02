from collections import Counter
from pathlib import Path

from slugify import slugify
import yaml
from tqdm import tqdm

from asigmatics import backfill_asigmatic
from models import Member, Bling, Comment, Awards, Challenge, Image


def yaml_header(**kwargs):
    data_str = yaml.dump(dict(draft=False, **kwargs)).strip()
    return f"---\n{data_str}\n---\n\n"


def awarders_index():
    return yaml_header(title=f"Awarders list", tupe="awarder", layout="list")


def awarder_index(awarder: Member):
    awarder_name = awarder.name
    awarder_slug = slugify(awarder_name)
    awarder_thumb = user_thumb(awarder.id)
    user_url = user_webpage(awarder.id)
    num_awards_given = (
        Bling.select()
        .join(Awards)
        .where((Awards.bling_id == Bling.id) & (Bling.awarder == awarder))
        .count()
    )
    description = f"Visit {awarder_name}'s [profile]({user_url}) or all of their awards [here](./all)"
    stats = f"{awarder_name} has awarded {num_awards_given}"
    return yaml_header(
        title=f"Awards given by {awarder_name}",
        name=awarder_name,
        slug=awarder_slug,
        thumb=awarder_thumb,
        description=description,
        stats=stats,
        type="awarder",
        layout="single",
    )


def award_index(bling: Bling):
    awarder = bling.awarder
    award_name = bling.name.strip()
    award_slug = slugify(award_name)

    description = bling.description.strip()

    title = f"Images awarded the {award_name} award by {awarder.name}"

    unique_challenges = (
        Awards.select(Awards.challenge).where(Awards.bling == bling).distinct().count()
    )
    unique_recipients = (
        Awards.select(Awards.user).where(Awards.bling == bling).distinct().count()
    )

    image_ids = [
        iid.image_id
        for iid in (
            Awards.select(Awards.image_id)
            .join(Comment)
            .where((Awards.comment_id == Comment.id) & (Awards.bling == bling))
            .order_by(Comment.date)
        )
    ][::-1]

    assert all(map(int, image_ids))

    stats = (
        f"The {award_name} award has been given {len(image_ids)} times to {unique_recipients} users "
        f"in {unique_challenges} distinct challenges. "
    ).strip()

    return yaml_header(
        title=title,
        name=award_name,
        slug=award_slug,
        thumb=bling.img_src,
        description=description,
        image_ids=image_ids,
        stats=stats,
        type="awarders",
        layout="gallery",
    )


def counts_to_list(counts):
    return [dict(slug=slug, count=count) for slug, count in counts.most_common()]


def challenges_index():
    challenges = Challenge.select().order_by(Challenge.voting_end.desc())
    title = "Challenge list"
    challenge_meta = [
        dict(
            name=challenge.name,
            slug=slugify(challenge.name),
            award_counts=counts_to_list(
                Counter(
                    slugify(award.bling.name)
                    for award in Awards.select().where(Awards.challenge == challenge)
                )
            ),
        )
        for challenge in tqdm(
            challenges, total=len(challenges), desc="Building challenges"
        )
    ]

    return yaml_header(
        title=title, challenges=challenge_meta, type="challenges", layout="list"
    )


def challenge_index(challenge):
    name = challenge.name.strip()
    award_counts = counts_to_list(
        Counter(
            slugify(award.bling.name)
            for award in Awards.select().where(Awards.challenge == challenge)
        )
    )

    image_ids = [
        iid.image_id
        for iid in (
            Awards.select(Awards.image_id)
            .join(Comment)
            .where(Awards.challenge == challenge)
            .order_by(Comment.date)
        )
    ][::-1]

    num_awards = Awards.select().where(Awards.challenge == challenge).count()
    stats = f"{num_awards} images received awards in this challenge."

    return yaml_header(
        title=name,
        name=name,
        slug=slugify(challenge.name),
        challenge_id=challenge.id,
        award_counts=award_counts,
        image_ids=image_ids,
        thumb=None,
        description="",
        stats=stats,
        type="challenges",
        layout="single",
    )


def recipients_index():
    user_ids = [award.user_id for award in Awards.select(Awards.user_id).distinct()]
    users = [
        dict(
            name=user.name,
            slug=slugify(user.name),
            thumb=user_thumb(user.id),
            num_awards=user.awards.count(),
            description=f"{user.awards.count()} awards received",
        ) for user in map(lambda user_id: Member.get(user_id), tqdm(user_ids))
    ]
    users = sorted(users, key=lambda uu: uu['num_awards'], reverse=True)
    return yaml_header(title="Recipients list", users=users, type="recipients", layout="list")


def recipient_index(user):
    user_id = user.id
    user_slug = slugify(user.name)
    user_name = user.name

    image_ids = [
        iid.image_id
        for iid in Awards.select().where(Awards.user == user).order_by(Awards.image_id)
    ][::-1]

    description = ""

    num_awards = Awards.select().where(Awards.user == user).count()
    num_blings = (
        Awards.select(Awards.bling).where(Awards.user == user).distinct().count()
    )
    num_challenges = (
        Awards.select(Awards.challenge).where(Awards.user == user).distinct().count()
    )
    award_counts = Counter(
        slugify(award.bling.name)
        for award in Awards.select().where(Awards.user == user)
    )

    stats = f"{num_awards} total awards ({num_blings} distinct) received over {num_challenges} challenges"

    return yaml_header(
        title=f"{user_name}'s personal gallery",
        user_id=user_id,
        name=user_name,
        slug=user_slug,
        thumb=user_thumb(user_id),
        description=description,
        stats=stats,
        image_ids=image_ids,
        award_counts=counts_to_list(award_counts),
        type="recipients",
        layout="single",
    )


def bucketer(number, denominator):
    lower = (number // denominator) * denominator
    upper = lower + denominator - 1
    return f"{lower}-{upper}"


def challenge_url(challenge_id):
    return f"https://images.dpchallenge.com/images_challenge/{bucketer(challenge_id, 1000)}/{challenge_id}"


def image_thumb_url(challenge_id, image_id):
    return f"{challenge_url(challenge_id)}/120/Copyrighted_Image_Reuse_Prohibited_{image_id}.jpg"


def image_url(challenge_id, image_id):
    return f"{challenge_url(challenge_id)}/1200/Copyrighted_Image_Reuse_Prohibited_{image_id}.jpg"


def user_thumb(user_id):
    return f"https://images.dpchallenge.com/images_profile/{bucketer(user_id, 5000)}/120/{user_id}.jpg"


def image_webpage(image_id):
    return f"https://www.dpchallenge.com/image.php?IMAGE_ID={image_id}"


def user_webpage(user_id):
    return f"https://www.dpchallenge.com/profile.php?USER_ID={user_id}"


def challenge_webpage(challenge_id):
    return (
        f"https://www.dpchallenge.com/challenge_results.php?CHALLENGE_ID={challenge_id}"
    )


def import_bling_to_db(data_root: Path):
    awards_root = data_root / "collections" / "awards_meta"
    awards_root.mkdir(exist_ok=True, parents=True)

    awarders_root = data_root / "collections" / "awarders_meta"
    awarders_root.mkdir(exist_ok=True, parents=True)

    with open("meta.yaml", "r") as fil:
        awards_meta = yaml.safe_load(fil)

    for awarder_meta in tqdm(awards_meta, desc="Loading blings"):
        awarder = Member.get(Member.id == awarder_meta["user_id"])

        hugo_meta = dict(
            id=awarder.id,
            name=awarder.name,
            slug=slugify(awarder.name),
            url=user_webpage(awarder.id),
            thumb=awarder_meta.get("thumb", user_thumb(awarder.id)),
            awards=dict(),
        )

        num_awarded = 0

        for award_meta in awarder_meta["awards"]:
            kwargs = dict(
                awarder=awarder,
                name=award_meta["name"],
                slug=slugify(award_meta["name"]),
                description=award_meta["description"],
                img_src=award_meta["image"],
                regex=list(map(str, award_meta["urls"])),
            )

            try:
                award = Bling.get(slug=slugify(award_meta["name"]))
                award.update(**kwargs)

            except:
                award = Bling.create(**kwargs)

            award_dict = dict(
                name=award.name,
                slug=slugify(award.name),
                description=award.description.strip(),
                thumb=award.img_src,
                urls=award.regex,
                awarder_id=awarder.id,
                awarder_slug=slugify(awarder.name),
                num_awarded=(Awards.select().where(Awards.bling == award).count()),
                num_distinct_recipients=(
                    Awards.select(Awards.user)
                    .where(Awards.bling == award)
                    .distinct()
                    .count()
                ),
                num_distinct_challenges=(
                    Awards.select(Awards.challenge)
                    .where(Awards.bling == award)
                    .distinct()
                    .count()
                ),
            )

            num_awarded += award_dict["num_awarded"]

            hugo_meta["awards"][award_dict["slug"]] = award_dict

            with open(awards_root / f"{slugify(award.name)}.yaml", "w") as fil:
                yaml.dump(award_dict, fil)

        hugo_meta["num_awarded"] = num_awarded

        with open(awarders_root / f"{slugify(awarder.name)}.yaml", "w") as fil:
            yaml.dump(hugo_meta, fil)


def find_awards():
    for bling in tqdm(Bling.select(), desc="Finding awarded images"):
        awarded_images = [a.image_id for a in bling.awards]

        for url in bling.regex:
            for comment in Comment.select().where(
                (Comment.commenter == bling.awarder)
                & (Comment.raw_comment.contains(url))
                & (Comment.image.not_in(awarded_images))
            ):
                Awards.get_or_create(
                    bling=bling,
                    user=comment.image.photographer,
                    comment=comment,
                    image=comment.image,
                    challenge=comment.image.challenge,
                )


def build_image_list(data_root: Path):
    data_root = data_root / "collections" / "images"
    data_root.mkdir(parents=True, exist_ok=True)

    for image in tqdm(
        Awards.select(Awards.image_id).distinct(), desc="Building images list"
    ):
        image = Image.get(image.image_id)
        user = image.photographer
        challenge = image.challenge

        image_data = dict(
            image_id=image.id,
            image_url=image_url(challenge.id, image.id),
            image_thumb_url=image_thumb_url(challenge.id, image.id),
            image_webpage=image_webpage(image.id),
            image_title=image.name,
            user_id=image.photographer_id,
            user_name=user.name,
            user_slug=slugify(user.name),
            user_thumb=user_thumb(user.id),
            user_webpage=user_webpage(image.photographer_id),
            challenge_id=challenge.id,
            challenge_name=challenge.name,
            challenge_slug=slugify(challenge.name),
            challenge_webpage=challenge_webpage(challenge.id),
            awards=[slugify(award.bling.name) for award in image.awards],
        )

        with open(data_root / f"{image.id}.yaml", "w") as fil:
            yaml.dump(image_data, fil)


def build_awarder_content(hugo_root: Path):
    awarders_root = hugo_root / "content" / "awarders"
    awarders_root.mkdir(exist_ok=True, parents=True)

    with open(awarders_root / "_index.html", "w") as fil:
        fil.write(awarders_index())

    for bling in tqdm(Bling.select(), "Generating awarder content"):
        awarder_root = awarders_root / slugify(bling.awarder.name)
        awarder_root.mkdir(exist_ok=True, parents=True)
        with open(awarder_root / "_index.html", "w") as fil:
            fil.write(awarder_index(awarder=bling.awarder))

        award_root = awarder_root / slugify(bling.name)
        award_root.mkdir(exist_ok=True, parents=True)
        with open(award_root / "_index.html", "w") as fil:
            fil.write(award_index(bling))


def build_recipient_content(hugo_root):
    recipient_root = hugo_root / "content" / "recipients"
    recipient_root.mkdir(parents=True, exist_ok=True)

    with open(recipient_root / f"_index.html", "w") as fil:
        fil.write(recipients_index())

    user_ids = {a.user_id for a in Awards.select()}
    for user_id in tqdm(user_ids, desc="Building recipient content"):
        user = Member.get(user_id)
        if not len(user.name):
            continue
        with open(recipient_root / f"{slugify(user.name)}.html", "w") as fil:
            fil.write(recipient_index(user))


def build_challenge_content(hugo_root: Path):
    challenges_root = hugo_root / "content" / "challenges"
    challenges_root.mkdir(exist_ok=True, parents=True)

    with open(challenges_root / "_index.html", "w") as fil:
        fil.write(challenges_index())

    for challenge in tqdm(
        Awards.select(Awards.challenge_id).distinct(), desc="Building challenge content"
    ):
        challenge = Challenge.get(challenge.challenge_id)
        with open(challenges_root / f"{slugify(challenge.name)}.html", "w") as fil:
            fil.write(challenge_index(challenge=challenge))


def main():
    hugo_root = Path("./hugo-website")
    data_root = hugo_root / "data"

    import_bling_to_db(data_root)

    backfill_asigmatic()

    find_awards()

    build_image_list(data_root)

    build_awarder_content(hugo_root)
    build_recipient_content(hugo_root)
    build_challenge_content(hugo_root)

    import_bling_to_db(data_root)


if __name__ == "__main__":
    main()
