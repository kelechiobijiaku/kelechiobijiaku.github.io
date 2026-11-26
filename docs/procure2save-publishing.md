# Publishing Procure2save

The publication lives at **https://kelechiobijiaku.com/procure2save/**. The website and LinkedIn use one approved article and the same original cover. Website updates deploy through the existing GitHub Pages setup.

## The simplest ongoing workflow

1. Finalise the title, full article and cover together. Approve that version once, with the intended publication date in **Africa/Lagos**.
2. Ask ChatGPT: **“Publish this approved Procure2save edition on my website and as a new edition of my LinkedIn newsletter today. Use the identical title, complete article and cover. Update the archive, RSS feed and sitemap, and record both published URLs.”** If LinkedIn requires a manual action or sign-in, finish that step in its own publishing editor. Website publishing does not depend on LinkedIn integration access.
3. Check both live pages, including the beginning and end of the article and any headings, links or lists. Record the new LinkedIn edition URL in `linkedinUrl`, then rebuild. A source link can be added after the website has already gone live.

This supports publication on the same day. It does not promise a single simultaneous transaction across the two services. Do not create another LinkedIn edition when the article already has a published `linkedinUrl`.

## Source structure

| Location | Purpose |
| --- | --- |
| `data/procure2save.json` | Publication identity, author, topics and article metadata |
| `content/procure2save/<permanent-id>.html` | Complete approved article body, with its original formatting |
| `assets/procure2save/<permanent-id>.<png/jpg>` | Original approved cover; the downloaded LinkedIn covers are retained byte for byte |
| `templates/procure2save/` | Hub, reading and topic page templates |
| `scripts/build_procure2save.py` | Static page, search index, related articles, RSS and sitemap generation |
| `scripts/prepare_publication.py` | Local kit for copying approved content into LinkedIn's editor |
| `procure2save/feed.xml` | Full-content RSS feed, with original dates, author, cover images and permanent article URLs |

All public article pages contain complete text in the HTML. JavaScript enhances archive search, category, year and ordering controls. Topic pages and the full archive remain browsable without JavaScript. Search runs locally in the visitor's browser; no search queries are sent to another service.

## Add an edition through GitHub

Keep the permanent ID and URL unchanged after first publication. A custom existing article URL can be retained in `url`; do not create a second copy under a new path. The builder rejects duplicate IDs, permanent URLs and LinkedIn source URLs, and refuses to overwrite unrelated existing HTML files.

1. Add the approved body to `content/procure2save/your-permanent-id.html` and the cover to `assets/procure2save/`. Use body markup such as paragraphs, headings, emphasis, lists and links; omit a surrounding HTML document and title heading. Store any inline article images locally under `/assets/`. Do not include scripts, embeds, tracking attributes or event handlers.
2. Add a record to `articles` in `data/procure2save.json`. Use an existing category ID from `categories`. For example:

```json
{
  "id": "your-permanent-id",
  "url": "/procure2save/your-permanent-id/",
  "title": "The exact approved title",
  "date": "2026-11-26",
  "websitePublished": "2026-11-26",
  "status": "draft",
  "approved": true,
  "contentFile": "content/procure2save/your-permanent-id.html",
  "coverImage": "/assets/procure2save/your-permanent-id.jpg",
  "coverAlt": "An accurate description of the approved cover",
  "coverWidth": 1280,
  "coverHeight": 720,
  "categories": ["public-procurement", "contract-management"],
  "featured": false
}
```

3. Set `publication.updated` to the actual update date. Use the real original publication date in `date` for imported articles. Add `modified` only when the approved content actually changes; it is not the import date. Set the true image dimensions. `related` optionally accepts up to three existing article IDs; otherwise related articles are selected by topic overlap and recency.
4. Prepare the kit while the approved edition is still a draft:

```sh
python scripts/prepare_publication.py your-permanent-id
```

Open `.publishing/your-permanent-id/index.html` locally. It provides **Copy title**, **Copy formatted article** and **Download cover image**. Its `article.html` is identical to the website body source. Its `publication.json` records SHA-256 hashes of the approved content and cover so a later edit is detectable. The kit does not sign in or send anything to LinkedIn.

5. Open the [Procure2save newsletter](https://www.linkedin.com/newsletters/procure2save-7061017714391228416/) in the authenticated account and choose **Create new edition**. Confirm that the selected publication is Procure2Save. Paste the title and formatted body and upload the original cover from the kit. Preview the entire article, including the final paragraph. Use LinkedIn's native controls to publish on the agreed day. If a clipboard permission is unavailable, select and copy from the kit manually.
6. On that same day, set `status` to `published`, retain `approved: true`, and add the resulting published `linkedinUrl` when available. Commit the metadata, body and image to `main`. The **Refresh speaking and event pages** workflow builds the hub, article pages, categories, related reading, search, RSS and sitemap, checks them, commits generated changes and requests the existing GitHub Pages build. Its daily event refresh remains in place. Do not change Pages source, CNAME, DNS or Search Console settings.
7. Verify the live website article and the LinkedIn edition. A GitHub Actions run completing its build is not a substitute for checking the live URLs.

You can also generate and commit all outputs yourself:

```sh
python scripts/build_procure2save.py
python -m unittest discover -s tests -p 'test_procure2save.py'
node --test tests/events.test.cjs
```

The existing event builder and publication builder both preserve other sitemap entries. Website canonical URLs point to the permanent website article; the original LinkedIn URL is recorded separately in the reading page, RSS and structured data. This is a deliberate cross-publication choice: it gives the website its own indexable edition without claiming that the LinkedIn version has been redirected.

## LinkedIn automation investigation — 26 November 2026

No authorised newsletter-edition publishing integration was available in the connected tools or found in LinkedIn's public API documentation during implementation. The documented **Posts API** supports social posts, including an “article” link card with a source URL, title, thumbnail and description. That is a different operation from creating a full long-form edition inside an existing LinkedIn newsletter, and it does not establish support for newsletter subscriber notifications. Do not treat an ordinary feed-post integration as a newsletter publisher.

Use LinkedIn's authenticated native newsletter editor for the final newsletter publication. A future approved provider can replace this manual step only after its actual newsletter-edition capability and granted permissions have been verified. The website does not store LinkedIn passwords, browser cookies or access tokens; no private LinkedIn endpoints, session replay, background scraping or restriction bypass is installed.

Official references checked:

- [LinkedIn Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-10), particularly “Article Post Creation Sample Request”.
- [LinkedIn Newsletters](https://www.linkedin.com/help/linkedin/answer/a522525), explaining publishing through LinkedIn's article and newsletter editor.
- [Newsletters on LinkedIn FAQ](https://www.linkedin.com/help/linkedin/answer/a521735), including subscription and newsletter-page behaviour.

## Imported editions and preservation

The five most recent editions visible in the authenticated newsletter archive were imported on 26 November 2026:

| Original title | Original publication date |
| --- | --- |
| Whose Economy Are We Building? Rethinking Preference in Nigerian Public Procurement | 20 November 2026 |
| When a Company Gets Blacklisted: The Hidden Cost of Procurement Misconduct | 15 November 2026 |
| THE CHEAPEST BID CAN BECOME THE MOST EXPENSIVE CONTRACT | 6 November 2026 |
| WHEN GOVERNMENTS SAY “BUY LOCAL”, WHO REALLY WINS? | 30 October 2026 |
| LOCAL CONTENT AND THE COST QUESTION IN NIGERIA | 3 May 2026 |

Their visible article text, case, punctuation, emphasis, paragraphs and headings were preserved. LinkedIn-specific tracking markup and empty comments were removed. The metadata records fingerprints of the original visible text and original cover bytes; builds fail if these change. This protects against accidental rewrites or image replacement. A deliberate correction requires checking the revised approved source and updating the fingerprints accordingly.

There were no existing full article pages in the repository at implementation time. Existing selected article mentions in Publications & Insights and the homepage now link to the imported editions; all other writing and research references remain.

Older editions remain available through the newsletter's original archive link. They have not been represented as fully imported. Import another edition only after its full body, original date and cover can be retrieved; do not reconstruct it from snippets or memory.

The repository is public. Keep confidential drafts outside it. `draft` prevents generation into the publication hub, feed and sitemap; it is not an access-control mechanism for files committed to a public repository. Local publishing kits are excluded by `.gitignore`.
