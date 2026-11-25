# Kelechi Obijiaku professional website — version 2

## Preview
Open index.html in your browser. The photo chooser previews images locally but does not upload them to a server.

## Publish with GitHub Pages
1. Create a public repository named YOURUSERNAME.github.io.
2. Upload the **contents of this folder** to the repository root (index.html must be at root).
3. Settings → Pages → Deploy from branch → main / root.
4. Your website will appear at https://YOURUSERNAME.github.io.

## Add more permanent gallery photos
1. Put JPEG/PNG/WebP images in assets/gallery/.
2. Edit gallery.json, for example:
[
  {"file":"assets/gallery/conference.jpg","caption":"Speaking at a professional conference"},
  {"file":"assets/gallery/workshop.jpg","caption":"Procurement policy workshop"}
]
3. Commit/upload the new photos and gallery.json to GitHub. They will then appear in the Gallery section.
Note: the browser file chooser only previews files locally; GitHub Pages cannot directly receive uploads from public visitors.

## Contact information
Only the email and LinkedIn profile are published. Telephone numbers are intentionally excluded.

## Prepublication checks
- Confirm award year for the Business of Law recognition (CVs differ between 2023 and 2024).
- Leadership is attributed to law, regulations and gender-responsive procurement policy; technical-team membership to the manual, emergency procurement, asset-disposal, sustainability and Vision 2036 work. Verify project confidentiality and exact publication URLs.
- PhD, Master in International Management and CIPS are explicitly shown as IN PROGRESS; do not present MCIPS as awarded.
- Replace the relative image URL in structured data with the full public URL once deployed.
- Add a sitemap.xml with your real domain after publishing.
- Check professional biography and permission to publish any third-party conference photographs.

## Free hosting
GitHub Pages hosts static files without a paid server. There is no persistent admin upload feature in a purely static website. To add photos, upload them to your GitHub repository.

Version 5: Added substantive Ministry of Justice commercial-law and PPP experience, appointments, NBA conference speaking, training, and corrected singular Procurement Manual. Contact remains email and LinkedIn only.

## Speaking & Events

The event source is `data/events.json`. The HTML is generated in advance for search engines and visitors without JavaScript; `events.js` keeps listings and countdowns current in the browser. All dates use **Africa/Lagos**, regardless of the visitor's timezone. An event remains current through its `endDate` and enters the archive at the next Lagos midnight. With no confirmed session time, the countdown targets the event date; the day itself displays “Event day”.

The `Refresh speaking and event pages` GitHub Actions workflow checks daily at 00:07 Lagos time, rebuilds changed static pages and requests a branch-based GitHub Pages build. GitHub may delay scheduled jobs; browser archiving does not depend on that schedule. This workflow does not change the Pages source, custom domain or DNS. GitHub can disable schedules after prolonged repository inactivity; runtime date handling remains active.

### Add an event

1. Copy an entry in `data/events.json`, choose a unique permanent `id`, and fill in its confirmed details, dates, venue, presentation and registration URL. IDs determine the permanent `/events/<id>.html` URL; keep past IDs unchanged.
2. Add original flyers to `assets/events/<id>/`. Use optimised WebP versions for display and preserve the original JPEG/PNG files for enlargement and social previews. Set `image` to the personalised speaker flyer; `gallery` holds supplementary artwork. Use `expiresOn` on time-limited promotional artwork.
3. Run `python scripts/build_events.py` and `node --test tests/events.test.cjs`.
4. Commit the source, images and generated pages. The workflow also builds on event-source changes and can be run manually from GitHub Actions.

Only the nearest current event is featured on the homepage; the speaking page lists all current and archived events. Past event pages and images remain available at their original URLs. Existing speaking and training history is in `templates/speaking.html`.

For an older engagement with no confirmed exact date, use `archived: true`, an integer `year`, and a descriptive `displayDate` instead of inventing a day. These entries use `templates/archive.html`, stay in the past list and have no countdown or registration promotion. Include `representation` and `invitedSpeaker` when participation was on behalf of another speaker or institution. The NBA 2026 entry records Kelechi Obijiaku's representation of invited speaker Fatai Idowu Onafowote and LSPPA.

An event can also have a `videos` array with `title`, `description`, `file` (MP4), `poster`, `duration` (ISO 8601) and `uploadDate`. Optional `videoHeading` and `videoIntro` describe the collection. Players preserve sound, use standard H.264/AAC, load on demand and provide native controls and downloads.

### Add post-event materials

Add a plain-text `summary` to the event entry and/or add items to its `resources` array, then rebuild. Resources appear only when populated. Examples:

```json
[
  {"type":"slides","title":"Presentation slides","url":"/assets/events/<id>/presentation.pdf"},
  {"type":"photo","title":"At the conference","url":"/assets/events/<id>/conference-photo.jpg","alt":"Describe the actual photograph"},
  {"type":"video","title":"Session recording","url":"https://example.org/actual-recording"},
  {"type":"event-summary","title":"Event reflections","url":"/actual-summary.html"}
]
```

Use real uploaded files or published URLs. Do not publish placeholder resource links. The original four Consulting Business Conference flyers are preserved without edits; WebP display copies reduce loading time.
