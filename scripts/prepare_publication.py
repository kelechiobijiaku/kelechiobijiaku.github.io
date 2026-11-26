#!/usr/bin/env python3
"""Export one approved master article for LinkedIn's own publishing editor."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from build_procure2save import ROOT, esc, load_data, local_file


def prepare(article_id, output=None):
    data, articles = load_data(include_approved_drafts=True)
    article = next((a for a in articles if a['id'] == article_id), None)
    if article is None:
        raise ValueError('Choose an existing article with approved: true.')
    destination = Path(output) if output else ROOT / '.publishing' / article_id
    destination.mkdir(parents=True, exist_ok=True)
    image = local_file(article['coverImage'])
    cover_name = 'cover' + image.suffix
    shutil.copyfile(image, destination / cover_name)
    (destination / 'title.txt').write_text(article['title'] + '\n')
    (destination / 'article.html').write_text(article['body'])
    manifest = {
        'id': article['id'], 'title': article['title'], 'publicationDate': article['date'],
        'websiteUrl': 'https://kelechiobijiaku.com' + article['url'],
        'linkedinUrl': article.get('linkedinUrl'),
        'contentSha256': hashlib.sha256(article['body'].encode()).hexdigest(),
        'coverSha256': hashlib.sha256(image.read_bytes()).hexdigest(),
        'coverFile': cover_name, 'newsletterUrl': data['publication']['newsletterUrl'],
        'approved': True,
    }
    (destination / 'publication.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    title_json = json.dumps(article['title'], ensure_ascii=False).replace('<', '\\u003c')
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Procure2save publishing kit</title><style>
    *{box-sizing:border-box}body{font:18px/1.8 system-ui,sans-serif;color:#172b39;background:#f3f5f6;margin:0}main{max-width:900px;margin:0 auto;padding:35px 6%;background:#fff}h1{font:36px/1.3 Georgia,serif}h2,h3{line-height:1.4}button,.button{display:inline-block;border:0;background:#102538;color:#fff;padding:12px 18px;font:600 16px/1.5 system-ui;margin:0 12px 12px 0;cursor:pointer;text-decoration:none}a{color:#76551e}img{max-width:100%;height:auto}.instructions{padding:20px;border:1px solid #cad2d7;background:#f7f8f9;margin-bottom:32px}.status{font-size:16px}article{border-top:1px solid #cad2d7;padding-top:24px}button:focus-visible,a:focus-visible{outline:3px solid #8a692f;outline-offset:3px}</style></head><body><main><p>PROCURE2SAVE · APPROVED PUBLICATION KIT</p>
    <h1>TITLE</h1><div class="instructions"><p>This kit uses the same approved article and original cover as the website.</p><button id="copy-title" type="button">Copy title</button><button id="copy-body" type="button">Copy formatted article</button><a class="button" href="COVER" download>Download cover image</a><a href="NEWSLETTER" target="_blank" rel="noopener noreferrer">Open Procure2save on LinkedIn</a><p>In LinkedIn, choose “Create new edition”, paste the title and article, upload this cover, review the edition and publish on the website publication day. Save the resulting LinkedIn URL in the article metadata.</p><p class="status" id="status" role="status"></p></div>
    <img src="COVER" alt="Original approved article cover"><article id="approved-body">BODY</article>
    <script>const approvedTitle=TITLE_JSON;const status=document.getElementById('status');document.getElementById('copy-title').onclick=async()=>{try{await navigator.clipboard.writeText(approvedTitle);status.textContent='Title copied.';}catch{status.textContent='Select the heading above and copy it manually.';}};document.getElementById('copy-body').onclick=async()=>{const body=document.getElementById('approved-body');try{await navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([body.innerHTML],{type:'text/html'}),'text/plain':new Blob([body.innerText],{type:'text/plain'})})]);status.textContent='Formatted article copied. Paste it into the newsletter body.';}catch{const range=document.createRange();range.selectNodeContents(body);const selection=getSelection();selection.removeAllRanges();selection.addRange(range);const copied=document.execCommand('copy');status.textContent=copied?'Formatted article copied.':'Article selected. Press Ctrl+C or Command+C to copy.';}};</script></main></body></html>'''
    replacements = {'TITLE': esc(article['title']), 'COVER': esc(cover_name), 'NEWSLETTER': esc(data['publication']['newsletterUrl']), 'BODY': article['body'], 'TITLE_JSON': title_json}
    # Substitute longest tokens first without interpreting the approved content.
    import re
    page = re.sub(r'TITLE_JSON|NEWSLETTER|TITLE|COVER|BODY', lambda m: replacements[m[0]], page)
    (destination / 'index.html').write_text(page)
    print(f'Approved publication kit: {destination / "index.html"}')
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('article_id')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    prepare(args.article_id, args.output)
