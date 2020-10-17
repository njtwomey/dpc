from bs4 import Tag
from requests import ConnectionError

from os.path import exists


def clean_text(text):
    if isinstance(text, Tag):
        text = text.text
    return text.replace("\xa0", "").strip()


def load_or_download(session, href, filename, force=False, save=True, n_restarts=10):
    if "CHALLENGE_ID" in href:
        print(href)

    if force or not exists(filename):
        for ii in range(n_restarts):
            try:
                source = session.get(href)
                if save:
                    with open(filename, "w") as fil:
                        fil.write(source)
                return source
            except ConnectionError:
                print("Request connection error timed out.")

        raise ConnectionError

    else:
        with open(filename, "r") as fil:
            source = "\n".join(fil.readlines())

    return source
