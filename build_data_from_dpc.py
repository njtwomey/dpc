from os.path import join

from tqdm import tqdm

from session import Session
from parsers import get_history
from parsers import get_challenge
from models import Challenge

session = Session(join(".", "login_details.json"))

# Failed with link=<a class="i" href="/image.php?IMAGE_ID=1267496">Portrait of a Titmouse</a>

# for page_num in reversed(range(21)):
#     get_history(session=session, page_num=page_num)

challenge_ids = sorted(set(range(1, 3900)) - set([ch.id for ch in Challenge.select()]))
pbar = tqdm(challenge_ids)
for challenge_id in pbar :
    pbar.set_description(f"{challenge_id=}")
    get_challenge(
        session=session,
        challenge_id=challenge_id
    )
