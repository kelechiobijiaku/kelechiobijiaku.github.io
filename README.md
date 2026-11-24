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
