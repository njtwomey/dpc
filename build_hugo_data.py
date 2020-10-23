from collections import Counter
from pathlib import Path

from slugify import slugify
import yaml
from tqdm import tqdm

from asigmatics import backfill_asigmatic
from models import Member, Bling, Comment, Awards, Challenge, Image


def yaml_header(**kwargs):
    data_str = yaml.dump(dict(**kwargs)).strip()
    return f"---\n{data_str}\n---"


def awarders_index():
    return yaml_header(
        title=f"Awarders list", draft=False, tupe="awarder", layout="list"
    )


def awarder_index(awarder_name):
    return yaml_header(
        title=f"Awards from {awarder_name}",
        draft=False,
        awarder_slug=slugify(awarder_name),
        type="awarder",
        layout="single",
    )


def award_index(award_title, awarder_slug):
    return yaml_header(
        title=award_title,
        draft=False,
        awarder_slug=awarder_slug,
        award_slug=slugify(award_title),
        type="awarders",
        layout="gallery",
    )


def challenges_index():
    return yaml_header(
        title="Challenge list", draft=False, type="challenges", layout="list"
    )


def challenge_index(challenge):
    return yaml_header(
        title=challenge.name.strip(),
        draft=False,
        challenge_slug=slugify(challenge.name),
        challenge_id=challenge.id,
        type="challenges",
        layout="single",
    )


def recipients_index():
    return yaml_header(
        title="Recipients list", draft=False, type="recipients", layout="list",
    )


def recipient_index(user):
    return yaml_header(
        title=user.name.strip(),
        draft=False,
        recipient_slug=slugify(user.name),
        recipient_id=user.id,
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

            hugo_meta["awards"][award_dict["slug"]] = award_dict

            with open(awards_root / f"{slugify(award.name)}.yaml", "w") as fil:
                yaml.dump(award_dict, fil)

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


def build_challenge_list(data_root: Path):
    data_root = data_root / "collections" / "challenges"
    data_root.mkdir(parents=True, exist_ok=True)

    for challenge in tqdm(
        Awards.select(Awards.challenge_id).distinct(), desc="Building challenges list"
    ):
        challenge = Challenge.get(challenge.challenge_id)
        award_list = [slugify(award.bling.name) for award in challenge.awards]

        challenge_data = dict(
            challenge_id=challenge.id,
            challenge_name=challenge.name,
            challenge_slug=slugify(challenge.name),
            challenge_end=challenge.voting_end,
            challenge_url=challenge_url(challenge.id),
            num_submissions=challenge.images.count(),
            num_awards=len(award_list),
            num_distinct_awards=len(set(award_list)),
            distinct_awards=sorted(set(award_list)),
            award_counts=dict(Counter(award_list)),
            image_ids=[award.image_id for award in challenge.awards],
        )

        with open(data_root / f"{challenge.id}.yaml", "w") as fil:
            yaml.dump(challenge_data, fil)


def build_user_list(data_root: Path):
    data_root = data_root / "collections" / "users"
    data_root.mkdir(parents=True, exist_ok=True)

    for user in tqdm(
        Awards.select(Awards.user_id).distinct(), desc="Building user list"
    ):
        user = Member.get(user.user_id)

        award_slugs = [slugify(award.bling.name) for award in user.awards]
        awards = [award for award in user.awards]

        user_data = dict(
            user_id=user.id,
            user_name=user.name,
            user_slug=slugify(user.name),
            user_thumb=user_thumb(user.id),
            num_awards=len(award_slugs),
            num_distinct_awards=len(set(award_slugs)),
            distinct_awards=sorted(set(award_slugs)),
            award_counts=dict(Counter(award_slugs)),
            user_url=user_webpage(user.id),
            num_challenges=Image.select().where(Image.photographer == user).count(),
            image_ids=[
                award.image_id
                for award in sorted(
                    awards, key=lambda award: award.comment.date, reverse=True
                )
            ],
            description=f"{len(award_slugs)} awards won on {len(set(award_slugs))} distinct categories.",
        )

        with open(data_root / f"{user.id}.yaml", "w") as fil:
            yaml.dump(user_data, fil)


def build_awards_list(data_root: Path):
    data_root = data_root / "collections" / "awards"
    data_root.mkdir(exist_ok=True, parents=True)

    for bling in tqdm(Bling.select(), desc="Building awards list"):
        awards = sorted(
            [award for award in bling.awards],
            key=lambda award: award.challenge.voting_end,
            reverse=True,
        )

        with open(data_root / f"{slugify(bling.name)}.yaml", "w") as fil:
            yaml.dump([award.image_id for award in awards], fil)


def build_sorted_lists(data_root):
    data_root /= "collections"
    data_root.mkdir(exist_ok=True, parents=True)

    with open(data_root / "challenge_list.yaml", "w") as fil:
        yaml.dump(
            [
                c.id
                for c in Challenge.select().order_by(Challenge.voting_end.desc())
                if len(c.awards)
            ],
            fil,
        )

    counts = Counter([a.user_id for a in Awards.select(Awards.user_id)])
    with open(data_root / "user_list.yaml", "w") as fil:
        yaml.dump([c[0] for c in counts.most_common()], fil)


def build_awarder_content(hugo_root: Path):
    awarders_root = hugo_root / "content" / "awarders"
    awarders_root.mkdir(exist_ok=True, parents=True)

    for bling in tqdm(Bling.select(), "Generating awarder content"):
        awarder_root = awarders_root / slugify(bling.awarder.name)
        awarder_root.mkdir(exist_ok=True, parents=True)
        with open(awarder_root / "_index.html", "w") as fil:
            fil.write(awarder_index(awarder_name=bling.awarder.name))

        award_root = awarder_root / slugify(bling.name)
        award_root.mkdir(exist_ok=True, parents=True)
        with open(award_root / "_index.html", "w") as fil:
            fil.write(
                award_index(
                    award_title=bling.name, awarder_slug=slugify(bling.awarder.name),
                )
            )


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
    build_challenge_list(data_root)
    build_user_list(data_root)
    build_awards_list(data_root)

    build_sorted_lists(data_root)

    build_awarder_content(hugo_root)
    build_recipient_content(hugo_root)
    build_challenge_content(hugo_root)

    import_bling_to_db(data_root)


if __name__ == "__main__":
    main()
