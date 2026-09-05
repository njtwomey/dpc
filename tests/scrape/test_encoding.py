from __future__ import annotations

from dpc.parse.challenge import parse_challenge
from dpc.scrape.encoding import decode_html


def test_windows_1252_em_dash_survives(html_bytes):
    # 0x97 is an em dash in windows-1252. Decoding it as latin-1 is what put
    # "Hidden Gem VI \x97 Mid-Term Quiz" into the published site.
    text = decode_html(html_bytes("encoding/cp1252.html"))
    assert "—" in text
    assert "\x97" not in text


def test_decoded_bytes_parse_into_a_clean_challenge_name(html_bytes):
    page = decode_html(html_bytes("encoding/cp1252.html")) + (
        '<div style="margin: 2px;">'
        "Submission Dates: Jan 1 2004 - Jan 7 2004\n"
        "Voting Dates: Jan 8 2004 - Jan 14 2004\n"
        "Submissions: 1\nDisqualifications: 0\nVotes: 2\nComments: 3\n"
        "Average Score: 5.0\nHighest Score: 6.0\nMedian Score: 5.0\nLowest Score: 4.0\n"
        "</div>"
    )
    challenge = parse_challenge(page, challenge_id=2512)
    assert challenge.name == "Hidden Gem VI — Mid-Term Quiz"


def test_real_utf8_is_left_alone():
    assert decode_html("café — ok".encode()) == "café — ok"


def test_declared_encoding_is_honoured():
    assert decode_html("café".encode("cp1252"), "cp1252") == "café"


def test_useless_iso_8859_1_default_is_ignored_in_favour_of_sniffing():
    # Servers default-declare ISO-8859-1 constantly; trusting it reintroduces
    # the exact mojibake this function exists to prevent.
    assert decode_html(b"Hidden Gem \x97 Quiz", "ISO-8859-1") == "Hidden Gem — Quiz"


def test_undecodable_bytes_do_not_raise():
    assert decode_html(b"\xff\xfe\x00bad") != ""
