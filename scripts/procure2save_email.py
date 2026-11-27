"""Render approved Procure2save editions and submit them once, after site publication."""
import argparse
import json
import os
import re
import time
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from build_procure2save import ORIGIN, esc, load_data, local_file


def render(article, author, preview=False):
    website = ORIGIN + article["url"]
    def absolute(match):
        key, quote, value = match.groups()
        return f'{key}={quote}{esc(urljoin(website, unescape(value)))}{quote}'
    body = re.sub(r"""\b(href|src)=(["'])(.*?)\2""", absolute, article["body"])
    unsubscribe = ('<span>Unsubscribe (personal link appears in the delivered email)</span>'
                   if preview else '<a href="{{ unsubscribe }}">Unsubscribe</a>')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(article["title"])}</title></head>
<body style="margin:0;background:#f4f6f5;color:#162a28;font:17px/1.65 Georgia,serif"><main style="max-width:640px;margin:auto;background:white;padding:24px">
<p style="color:#126354;font:bold 18px Arial,sans-serif">Procure2save</p>
<h1 style="line-height:1.16">{esc(article["title"])}</h1><p>By {esc(author)}</p>
<img width="640" style="width:100%;height:auto" src="{esc(ORIGIN+article["coverImage"])}" alt="{esc(article["coverAlt"])}">
{body}
<hr><p><a href="{esc(website)}">Read on my website</a> · <a href="{esc(article["linkedinUrl"])}">Read the original on LinkedIn</a></p>
<p style="font:14px/1.5 Arial,sans-serif">You received this edition because you subscribed to Procure2save. {unsubscribe}</p></main></body></html>'''


def api(url, headers, payload=None):
    request = Request(url, headers={"Content-Type": "application/json", **headers},
                      data=None if payload is None else json.dumps(payload).encode())
    with urlopen(request, timeout=30) as response:
        data = response.read()
    return json.loads(data) if data else {}


def wait_for_publication(article):
    cover = local_file(article["coverImage"]).read_bytes()
    for attempt in range(25):
        try:
            with urlopen(ORIGIN + article["url"], timeout=20) as response:
                page = response.read().decode()
            with urlopen(ORIGIN + article["coverImage"], timeout=20) as response:
                live_cover = response.read()
            if (article["body"] in page and esc(article["linkedinUrl"]) in page
                    and esc(article["title"]) in page and live_cover == cover):
                return
        except (URLError, TimeoutError):
            pass
        if attempt < 24:
            time.sleep(25)
    raise RuntimeError("Live website has not yet published the approved edition. Rerun after deployment.")


def deliver(article, author):
    repo = 'https://api.github.com/repos/' + os.environ['GITHUB_REPOSITORY'] + '/git'
    github = {"Authorization": "Bearer " + os.environ["GH_TOKEN"]}
    tag = 'procure2save-email/' + article["id"]
    try:
        api(repo + '/ref/tags/' + tag, github)
        print('Already claimed:', article["id"])
        return
    except HTTPError as error:
        if error.code != 404:
            raise
    brevo = {"api-key": os.environ["BREVO_API_KEY"]}
    payload = {"name": "Procure2save / " + article["id"], "subject": article["title"],
               "sender": {"email": os.environ["BREVO_SENDER"], "name": author},
               "recipients": {"listIds": [int(os.environ["BREVO_LIST_ID"])]},
               "htmlContent": render(article, author)}
    if not brevo["api-key"] or not payload["sender"]["email"]:
        raise ValueError("Configure the verified sender and API key first.")
    wait_for_publication(article)
    # The provider creates an unsent draft. Only the atomic tag winner may send it.
    endpoint = "https://api.brevo.com/v3/emailCampaigns"
    campaign = api(endpoint, brevo, payload)["id"]
    print("Brevo draft", campaign, "for", article["id"], flush=True)
    api(repo + '/refs', github, {"ref": "refs/tags/" + tag, "sha": os.environ["GITHUB_SHA"]})
    api(f"{endpoint}/{campaign}/sendNow", brevo, {})
    print("Submitted campaign", campaign)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", metavar="ARTICLE_ID")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data, articles = load_data()
    author = data["publication"]["author"]["name"]
    if args.preview:
        article = next(a for a in articles if a["id"] == args.preview and a.get("linkedinUrl"))
        args.output.write_text(render(article, author, preview=True))
    else:
        for article in reversed(articles):
            if article.get("emailApproved") is True and article.get("linkedinUrl"):
                deliver(article, author)
