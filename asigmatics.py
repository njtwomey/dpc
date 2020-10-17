import numpy as np
from tqdm import tqdm

from models import Awards, Bling, Challenge, Image, Comment, Member


def std(counts):
    return np.std(
        sum((count * [vote] for count, vote in zip(counts, range(1, 11))), [])
    )


def calc_asigmatic(challenge_id):
    challenge = Challenge.get(challenge_id)
    images = Image.select().where(Image.challenge == challenge)

    stds = [(image, std(image.votes)) for image in images if not image.disqualified]
    return max(stds, key=lambda img_std: img_std[1])


def backfill_asigmatic():
    asigmatic = Bling.get(Bling.slug == "asigmatic")
    niall = Member.get(Member.name == "NiallOTuama")

    challenge_ids = set(a.id for a in Challenge.select(Challenge.id))

    for challenge_id in tqdm(sorted(challenge_ids), desc="Backfilling asigmatics"):
        if (
            Awards.select(Awards.id)
            .where((Awards.challenge_id == challenge_id) & (Awards.bling == asigmatic))
            .count()
        ):
            continue

        image, std = calc_asigmatic(challenge_id)
        challenge = image.challenge

        Comment.get_or_create(
            id=challenge.id,
            commenter=niall,
            image=image,
            raw_comment="Copyrighted_Image_Reuse_Prohibited_1000203 1000203",
            comment="Copyrighted_Image_Reuse_Prohibited_1000203 1000203",
            date=challenge.voting_end,
            has_quote=False,
            made_during_challenge=False,
        )


if __name__ == "__main__":
    backfill_asigmatic()
