#!/usr/bin/env python3
"""Build index fragments, the speaking page and shareable event archives from JSON.

No third-party packages are needed. Dates without a confirmed time stay date-only.
The browser applies the same Lagos date rules between static refreshes.
"""
import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://kelechiobijiaku.com"
LAGOS = ZoneInfo("Africa/Lagos")
PERSON = {
    "@type": "Person", "@id": BASE + "/#person",
    "name": "Kelechi Uzoma Obijiaku", "alternateName": "Kelechi Obijiaku",
    "jobTitle": "Lawyer and Procurement Specialist", "url": BASE + "/",
    "image": BASE + "/assets/kelechi-headshot.jpg",
    "sameAs": ["https://www.linkedin.com/in/kelechi-obijiaku/"],
    "knowsAbout": ["Public procurement", "Procurement law", "Contract management",
                   "Commercial law", "Governance", "Public-private partnerships", "Institutional reform"]
}


def esc(value):
    return html.escape(str(value), quote=True)


def structured(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def event_url(event):
    return "/events/" + event["id"] + ".html"


def phase(event, now):
    today = now.astimezone(LAGOS).date().isoformat()
    if today > event.get("endDate", event["date"]):
        return "past"
    return "live" if today >= event["date"] else "upcoming"


def countdown(event):
    return f'''<div class="event-countdown" data-event-countdown="{esc(event['id'])}">
      <p class="countdown-caption">Until {esc(event['displayDate'].split(', ', 1)[-1])} · Lagos time</p>
      <div class="countdown-values" role="timer" aria-live="off" aria-label="Countdown to the event date in Lagos">
        <span><strong data-unit="days">—</strong><small>days</small></span>
        <span><strong data-unit="hours">—</strong><small>hours</small></span>
        <span><strong data-unit="minutes">—</strong><small>minutes</small></span>
        <span><strong data-unit="seconds">—</strong><small>seconds</small></span>
      </div>
    </div>'''


def image_link(image, thumbnail=False):
    file = image.get("thumbnail", image["file"]) if thumbnail else image["file"]
    return (f'<a class="flyer-link" href="{esc(image["original"])}" data-flyer '
            f'data-caption="{esc(image.get("caption", "Personalised speaker announcement"))}" '
            f'aria-label="Enlarge {esc(image.get("caption", "personalised speaker announcement"))}">'
            f'<img src="{esc(file)}" alt="{esc(image["alt"])}" '
            f'width="{image["width"]}" height="{image["height"]}" loading="lazy" decoding="async"></a>')


def upcoming_card(event):
    return f'''<article class="event-card" data-event-card="{esc(event['id'])}">
      <figure class="event-card-visual">{image_link(event['image'], True)}</figure>
      <div class="event-card-copy">
        <div class="event-date"><time datetime="{esc(event['date'])}">{esc(event['displayDate'])}</time></div>
        <h3><a href="{event_url(event)}">{esc(event['title'])}</a></h3>
        <p class="event-card-topic">{esc(event['topic'])}</p>
        <p class="event-card-meta">{esc(event['role'])} · {esc(event['speaker'])}<br>{esc(event['designation'])}</p>
        <p class="event-card-description">{esc(event['focus'])}</p>
        <p class="event-card-meta">{esc(event['venue'])}<br>Hosted by {esc(event['host'])} · {esc(event['participation'])}</p>
        {countdown(event)}
        <div class="event-actions"><a class="btn" href="{esc(event['registrationUrl'])}" target="_blank" rel="noopener noreferrer">Register to attend</a><a class="event-text-link" href="{event_url(event)}">Event details &amp; flyers</a></div>
      </div>
    </article>'''


def past_card(event):
    return f'''<article class="past-event">
      <a href="{event_url(event)}"><img src="{esc(event['image'].get('thumbnail', event['image']['file']))}" alt="{esc(event['image']['alt'])}" width="88" height="124" loading="lazy"></a>
      <div class="event-date"><time datetime="{esc(event['date'])}">{esc(event['displayDate'])}</time></div>
      <h3><a href="{event_url(event)}">{esc(event['title'])}</a></h3>
      <p>{esc(event['role'])} · {esc(event['topic'])}</p>
      <p>{esc(event['venue'])}</p>
      <a class="event-text-link" href="{event_url(event)}">View event archive</a>
    </article>'''


EMPTY = '''<div class="event-empty"><h3>The next conversation is taking shape.</h3><p>New speaking engagements will be announced here. Explore past events or get in touch about your next conference, lecture or workshop.</p><a class="event-text-link" href="/speaking.html#invite">Invite me to speak</a></div>'''
LIGHTBOX = '''<dialog class="flyer-dialog" id="flyer-dialog" aria-labelledby="flyer-caption">
  <div class="flyer-dialog-header"><p id="flyer-caption">Event flyer</p><button type="button" data-close-flyer autofocus>Close</button></div>
  <img class="flyer-dialog-image" id="flyer-enlarged" alt="">
  <div class="flyer-dialog-footer"><a id="flyer-original" href="#" target="_blank" rel="noopener noreferrer">Open full-size original</a><div class="flyer-dialog-controls"><button type="button" data-previous-flyer>Previous</button><button type="button" data-next-flyer>Next</button></div></div>
</dialog>'''
FOOTER = '''<footer><span>© <span id="year"></span> Kelechi Uzoma Obijiaku</span><a href="/">Return to homepage</a></footer>'''
PORTFOLIO = '''<section class="portfolio-links"><h2>Explore the professional portfolio</h2><div class="contact-links"><a href="/experience.html">Professional experience</a><a href="/policy.html">Policy and institutional reform</a><a href="/publications.html">Publications and insights</a><a href="/research.html">Research</a><a href="/speaking.html">Speaking &amp; Events</a><a href="/gallery.html">Photo journal</a></div></section>'''


def header():
    return '''<a class="skip-link" href="#main-content">Skip to content</a><header class="top"><a class="logo" href="/">K<span>.</span> OBIJIAKU</a><button class="menu" aria-label="Toggle navigation" aria-expanded="false" aria-controls="nav">Menu ☰</button><nav id="nav" aria-label="Main navigation"><a href="/">Home</a><a href="/experience.html">Professional experience</a><a href="/policy.html">Policy and institutional reform</a><a href="/publications.html">Publications and insights</a><a href="/research.html">Research</a><a href="/speaking.html" aria-current="page">Speaking &amp; Events</a><a href="/gallery.html">Photo journal</a></nav></header>'''


def head(title, description, url, image, graph):
    return f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#102538"><link rel="canonical" href="{esc(url)}">
<link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/events.css">
<meta property="og:type" content="website"><meta property="og:site_name" content="Kelechi Uzoma Obijiaku">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(url)}"><meta property="og:locale" content="en_NG">
<meta property="og:image" content="{BASE + esc(image['original'])}"><meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="{image['width']}"><meta property="og:image:height" content="{image['height']}">
<meta property="og:image:alt" content="{esc(image['alt'])}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="{BASE + esc(image['original'])}">
<script type="application/ld+json">{structured({'@context':'https://schema.org','@graph':graph})}</script>'''


def schema(event, now):
    result = {
        "@type": "Event", "@id": BASE + event_url(event) + "#event",
        "name": event["title"], "url": BASE + event_url(event),
        "description": event["topic"] + ". " + event["focus"] + " " + event["description"],
        "startDate": event["date"], "endDate": event.get("endDate", event["date"]),
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/MixedEventAttendanceMode",
        "location": [
            {"@type": "Place", "name": event.get("venueName", event["venue"]),
             "address": {"@type": "PostalAddress", "addressLocality": event.get("addressLocality", ""), "addressRegion": event.get("addressRegion", ""), "addressCountry": event.get("addressCountry", "")}},
            {"@type": "VirtualLocation", "url": event["registrationUrl"]}
        ],
        "organizer": {"@type": "Organization", "name": event["host"]},
        "performer": {"@id": PERSON["@id"]},
        "image": [BASE + event["image"]["original"]] + [BASE + im["original"] for im in event.get("gallery", [])]
    }
    if phase(event, now) != "past":
        result["offers"] = {"@type": "Offer", "url": event["registrationUrl"]}
    return result


def substitute(template, values):
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    if re.search(r"\{\{[A-Z_]+\}\}", template):
        raise ValueError("Unresolved template field")
    return template


def materials(event):
    resources = event.get("resources", [])
    summary = event.get("summary", "")
    if not resources and not summary:
        return ""  # No empty, speculative downloads or recordings in the visitor's path.
    cards = []
    for item in resources:
        url = item["url"]
        if not (url.startswith("/") or url.startswith("https://")):
            raise ValueError("Resource links must be site paths or HTTPS")
        image = f'<img src="{esc(url)}" alt="{esc(item.get("alt", item["title"]))}" loading="lazy">' if item["type"] == "photo" else ""
        cards.append(f'<article class="material-card">{image}<div class="event-date">{esc(item["type"].replace("-", " "))}</div><h3><a class="event-text-link" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(item["title"])}</a></h3></article>')
    return '<section class="section tinted event-materials" id="materials"><div class="eyebrow">FROM THE EVENT</div><h2>Resources &amp; reflections</h2>' + (f'<p>{esc(summary)}</p>' if summary else '') + '<div class="material-list">' + ''.join(cards) + '</div></section>'


def build(now):
    data = json.loads((ROOT / "data/events.json").read_text())
    events = data["events"]
    ids = [event["id"] for event in events]
    if len(ids) != len(set(ids)):
        raise ValueError("Event IDs must be unique")
    for event in events:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", event["id"]):
            raise ValueError("Use a safe, permanent lowercase event ID")
        datetime.fromisoformat(event["date"])
        if event.get("endDate", event["date"]) < event["date"]:
            raise ValueError("An event cannot end before it starts")
    upcoming = sorted([e for e in events if phase(e, now) != "past"], key=lambda e: e["date"])
    past = sorted([e for e in events if phase(e, now) == "past"], key=lambda e: e["date"], reverse=True)
    root_index = ROOT / "index.html"
    homepage = root_index.read_text()
    home_section = '''<section class="section events-section" id="upcoming-events" aria-labelledby="home-events-heading"><div class="events-heading"><div><div class="eyebrow">SPEAKING &amp; PROFESSIONAL DIALOGUE</div><h2 id="home-events-heading">Upcoming Events</h2></div><a class="event-text-link" href="/speaking.html">All speaking &amp; events</a></div><div data-event-list="featured">''' + (upcoming_card(upcoming[0]) if upcoming else EMPTY) + '''</div></section>'''
    pattern = r"<!-- EVENTS:START -->.*?<!-- EVENTS:END -->"
    if not re.search(pattern, homepage, re.S):
        homepage = homepage.replace('<section class="section tinted" id="portfolio">', '<!-- EVENTS:START --><!-- EVENTS:END -->\n<section class="section tinted" id="portfolio">', 1)
    homepage = re.sub(pattern, '<!-- EVENTS:START -->\n' + home_section + '\n<!-- EVENTS:END -->', homepage, flags=re.S)
    if '/events.css' not in homepage:
        homepage = homepage.replace('</head>', '<link rel="stylesheet" href="/events.css">\n</head>')
    if '/events.js' not in homepage:
        homepage = homepage.replace('</body>', LIGHTBOX + '\n<script src="/data/events-data.js" defer></script><script src="/events.js" defer></script></body>')
    schema_pattern = r"<!-- EVENT-SCHEMA:START -->.*?<!-- EVENT-SCHEMA:END -->"
    home_schema = '<script type="application/ld+json">' + structured({'@context': 'https://schema.org', '@graph': [schema(upcoming[0], now)]}) + '</script>' if upcoming else ''
    schema_fragment = '<!-- EVENT-SCHEMA:START -->' + home_schema + '<!-- EVENT-SCHEMA:END -->'
    if re.search(schema_pattern, homepage, re.S):
        homepage = re.sub(schema_pattern, lambda _: schema_fragment, homepage, flags=re.S)
    else:
        homepage = homepage.replace('</head>', schema_fragment + '\n</head>')
    root_index.write_text(homepage)

    profile_image = {"original": "/assets/kelechi-headshot.jpg", "width": 1200, "height": 1200, "alt": "Kelechi Uzoma Obijiaku, lawyer and procurement specialist"}
    graph = [PERSON, {"@type": "CollectionPage", "@id": BASE + "/speaking.html#page", "url": BASE + "/speaking.html", "name": "Speaking & Events", "about": {"@id": PERSON["@id"]}, "hasPart": [{"@id": BASE + event_url(e) + "#event"} for e in events]}] + [schema(e, now) for e in events]
    speaking = substitute((ROOT / "templates/speaking.html").read_text(), {
        "HEAD": head("Speaking & Events | Kelechi Uzoma Obijiaku", "Explore Kelechi Obijiaku’s speaking engagements and procurement training. Invite a lawyer and procurement specialist for conferences, panels and workshops.", BASE + "/speaking.html", profile_image, graph),
        "HEADER": header(), "FOOTER": FOOTER, "LIGHTBOX": LIGHTBOX, "PORTFOLIO": PORTFOLIO,
        "UPCOMING": ''.join(upcoming_card(e) for e in upcoming) or EMPTY,
        "PAST": ''.join(past_card(e) for e in past)
    })
    (ROOT / "speaking.html").write_text(speaking)
    (ROOT / "events").mkdir(exist_ok=True)
    event_template = (ROOT / "templates/event.html").read_text()
    for event in events:
        gallery = []
        for im in event.get("gallery", []):
            caption = im["caption"]
            if im.get("expiresOn", "9999-12-31") < now.astimezone(LAGOS).date().isoformat():
                expired = datetime.fromisoformat(im["expiresOn"]).strftime("%-d %B %Y")
                caption = "Original registration flyer · offers ended " + expired
            im = {**im, "caption": caption}
            gallery.append('<figure>' + image_link(im) + f'<figcaption>{esc(caption)}</figcaption><a class="original-link" href="{esc(im["original"])}" target="_blank" rel="noopener noreferrer">Open full-size original</a></figure>')
        values = {key.upper(): esc(event[key]) for key in ["id", "role", "host", "title", "date", "topic", "speaker", "designation", "focus", "venue", "participation", "description"]}
        values.update({
            "DISPLAY_DATE": esc(event["displayDate"]), "REGISTRATION": esc(event["registrationUrl"]),
            "PHASE": phase(event, now), "STATUS": "Past engagement" if phase(event, now) == "past" else "Event day" if phase(event, now) == "live" else "Upcoming engagement",
            "HEAD": head(event["title"] + " | Kelechi Obijiaku, " + event["role"], event.get("metaDescription", event["topic"] + ". " + event["displayDate"] + ". " + event["venue"] + ". " + event["participation"] + "."), BASE + event_url(event), event["image"], [PERSON, schema(event, now)]),
            "HEADER": header(), "FOOTER": FOOTER, "LIGHTBOX": LIGHTBOX,
            "PRIMARY_IMAGE": image_link(event["image"]), "COUNTDOWN": countdown(event),
            "TAKEAWAYS": ''.join('<li>' + esc(text) + '</li>' for text in event.get("takeaways", [])),
            "GALLERY": ''.join(gallery), "MATERIALS": materials(event)
        })
        (ROOT / event_url(event).lstrip('/')).write_text(substitute(event_template, values))
    client = {"timezone": data["timezone"], "emptyHtml": EMPTY, "events": []}
    for event in events:
        client["events"].append({**event, "url": event_url(event), "upcomingHtml": upcoming_card(event), "pastHtml": past_card(event)})
    (ROOT / "data/events-data.js").write_text("// Generated by scripts/build_events.py; edit data/events.json instead.\nwindow.SPEAKING_EVENTS_DATA = " + structured(client) + ";\n")
    sitemap = (ROOT / "sitemap.xml").read_text()
    for event in events:
        url = BASE + event_url(event)
        if url not in sitemap:
            sitemap = sitemap.replace('</urlset>', '  <url><loc>' + esc(url) + '</loc></url>\n</urlset>')
    (ROOT / "sitemap.xml").write_text(sitemap)
    print(f"Built {len(events)} event page(s): {len(upcoming)} upcoming, {len(past)} archived (Africa/Lagos)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--now", help="ISO timestamp, for boundary checks in a temporary checkout")
    args = parser.parse_args()
    now = datetime.fromisoformat(args.now.replace("Z", "+00:00")) if args.now else datetime.now(LAGOS)
    if now.tzinfo is None:
        parser.error("--now requires a timezone offset")
    build(now)
