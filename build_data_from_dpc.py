from os.path import join

from session import Session
from parsers import get_history

session = Session(join(".", "login_details.json"))

get_history(session=session, page_num=2)

# from models import Challenge
# from scrapers import get_challenge
# challenge_ids = sorted(set(range(1, 2490)) - set([ch.id for ch in Challenge.select()]))
# for challenge_id in challenge_ids:
#     get_challenge(
#         session=session,
#         challenge_id=challenge_id
#     )
