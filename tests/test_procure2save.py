"""Publication preservation and build lifecycle checks; no network or dependencies."""
import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_procure2save as publication
import prepare_publication as kit


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links, self.meta, self.scripts = [], {}, []
        self.canonical, self.h1 = None, ''
        self.script, self.in_h1 = None, False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical = a['href']
        if tag == 'meta':
            self.meta[a.get('name') or a.get('property')] = a.get('content')
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.script = ''
        if tag == 'h1':
            self.in_h1 = True

    def handle_data(self, data):
        if self.in_h1:
            self.h1 += data
        if self.script is not None:
            self.script += data

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_h1 = False
        if tag == 'script' and self.script is not None:
            self.scripts.append(json.loads(self.script))
            self.script = None


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.articles = publication.load_data()

    def test_imported_article_text_and_original_cover_bytes_match_their_source_fingerprints(self):
        imported = [a for a in self.articles if a.get('source', {}).get('platform') == 'LinkedIn']
        self.assertGreaterEqual(len(imported), 5)
        for a in imported:
            self.assertEqual(publication.text_hash(a['body']), a['source']['textSha256'])
            self.assertEqual(hashlib.sha256(publication.local_file(a['coverImage']).read_bytes()).hexdigest(), a['source']['coverSha256'])
            page = (ROOT / a['url'].lstrip('/') / 'index.html').read_text()
            marker = '<div class="p2-article-body" id="article-body">'
            rendered = page.split(marker, 1)[1].split('</div>', 1)[0]
            self.assertEqual(publication.text_hash(rendered), a['source']['textSha256'])

    def test_every_article_has_original_title_date_source_link_author_and_self_canonical(self):
        for a in self.articles:
            p = Page((ROOT / a['url'].lstrip('/') / 'index.html').read_text())
            self.assertEqual(p.h1, a['title'])
            self.assertEqual(p.canonical, publication.ORIGIN + a['url'])
            self.assertEqual(p.meta['og:type'], 'article')
            self.assertEqual(p.meta['og:image'], publication.ORIGIN + a['coverImage'])
            self.assertEqual(p.meta['article:published_time'], a['date'])
            schema = p.scripts[0]
            self.assertEqual(schema['headline'], a['title'])
            self.assertEqual(schema['articleBody'], a['text'])
            self.assertEqual(schema['datePublished'], a['date'])
            self.assertEqual(schema['author']['name'], self.data['publication']['author']['name'])
            if a.get('linkedinUrl'):
                self.assertIn(a['linkedinUrl'], p.links)
                self.assertEqual(schema['isBasedOn' if a.get('source', {}).get('platform') == 'LinkedIn' else 'sameAs'], a['linkedinUrl'])
            related = publication.related_articles(a, self.articles)
            self.assertNotIn(a['id'], [r['id'] for r in related])
            self.assertEqual(len({r['id'] for r in related}), len(related))

    def test_rss_is_valid_and_contains_every_full_article_with_original_dates_and_absolute_images(self):
        feed = ET.parse(ROOT / 'procure2save/feed.xml')
        items = feed.findall('channel/item')
        self.assertEqual(len(items), len(self.articles))
        for a, item in zip(self.articles, items):
            self.assertEqual(item.findtext('title'), a['title'])
            self.assertEqual(item.findtext('guid'), publication.ORIGIN + a['url'])
            full = item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded')
            # Ignore the leading cover, retaining the entire original body.
            body = full.split('</p>', 1)[1]
            self.assertEqual(publication.text_hash(body), publication.text_hash(a['body']))
            self.assertIn(publication.ORIGIN + a['coverImage'], full)
            self.assertNotIn('src="/assets/', full)
            self.assertTrue(item.findtext('pubDate'))

    def test_sitemap_preserves_portfolio_and_speaking_urls_and_has_no_duplicates(self):
        tree = ET.parse(ROOT / 'sitemap.xml')
        urls = [el.text for el in tree.iter() if el.tag.endswith('}loc')]
        self.assertEqual(len(urls), len(set(urls)))
        for path in ['/', '/experience.html', '/research.html', '/publications.html', '/speaking.html', '/gallery.html', '/policy.html', '/events/consulting-business-conference-2026.html', '/events/nba-annual-general-conference-2026.html', '/procure2save/']:
            self.assertIn(publication.ORIGIN + path, urls)
        for a in self.articles:
            self.assertIn(publication.ORIGIN + a['url'], urls)

    def test_all_generated_reading_and_topic_page_links_resolve_to_real_local_pages(self):
        for path in (ROOT / 'procure2save').rglob('index.html'):
            for url in Page(path.read_text()).links:
                if not url.startswith('/') or url.startswith('//'):
                    continue
                url = url.split('#')[0].split('?')[0]
                target = ROOT / url.lstrip('/')
                if url.endswith('/'):
                    target /= 'index.html'
                self.assertTrue(target.is_file(), (path, url))

    def test_search_index_contains_complete_text_and_dates_for_all_published_articles(self):
        index = json.loads((ROOT / 'data/procure2save-search.json').read_text())
        by_id = {a['id']: a for a in index}
        self.assertEqual(set(by_id), {a['id'] for a in self.articles})
        for a in self.articles:
            self.assertEqual(by_id[a['id']]['text'], a['text'])
            self.assertEqual(by_id[a['id']]['date'], a['date'])

    def test_publishing_kit_uses_the_exact_same_approved_body_and_cover(self):
        a = self.articles[0]
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            output = kit.prepare(a['id'], Path(temp))
            manifest = json.loads((output / 'publication.json').read_text())
            self.assertEqual((output / 'article.html').read_text(), a['body'])
            self.assertEqual((output / 'title.txt').read_text().rstrip('\n'), a['title'])
            self.assertEqual(manifest['contentSha256'], hashlib.sha256(a['body'].encode()).hexdigest())
            self.assertEqual(hashlib.sha256((output / manifest['coverFile']).read_bytes()).hexdigest(), manifest['coverSha256'])
            page = Page((output / 'index.html').read_text())
            self.assertEqual(page.h1, a['title'])

    def test_adding_a_future_edition_updates_outputs_without_exposing_an_unapproved_draft(self):
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(temp)
            for path in ['templates/procure2save', 'content/procure2save', 'assets/procure2save']:
                shutil.copytree(ROOT / path, root / path)
            (root / 'data').mkdir()
            for name in ['index.html', 'publications.html', 'sitemap.xml']:
                shutil.copyfile(ROOT / name, root / name)
            data = json.loads(json.dumps(self.data))
            future = dict(data['articles'][0])
            future.update(id='test-future-edition', url='/procure2save/test-future-edition/', title='Approved future edition', contentFile='content/procure2save/test-future-edition.html', featured=False)
            future.pop('source', None)
            future.pop('linkedinUrl', None)
            data['articles'].append(future)
            (root / future['contentFile']).write_text('<p>One approved master article for both destinations.</p>')
            unapproved = dict(future, id='unapproved-draft', url='/procure2save/unapproved-draft/', approved=False, status='draft')
            data['articles'].append(unapproved)
            (root / 'data/procure2save.json').write_text(json.dumps(data))
            with patch.object(publication, 'ROOT', root):
                publication.build()
                page = root / 'procure2save/test-future-edition/index.html'
                self.assertTrue(page.exists())
                self.assertFalse((root / 'procure2save/unapproved-draft').exists())
                self.assertIn('Approved future edition', (root / 'procure2save/feed.xml').read_text())
                self.assertNotIn('unapproved-draft', (root / 'data/procure2save-search.json').read_text())
                self.assertIn('/procure2save/test-future-edition/', (root / 'sitemap.xml').read_text())
                first = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                publication.build()
                self.assertEqual(first, {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()})
                data['articles'][-1]['status'] = 'published'
                (root / 'data/procure2save.json').write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, 'approved content'):
                    publication.load_data()

    def test_duplicate_source_urls_and_modified_imports_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            data = json.loads(json.dumps(self.data))
            linked = [a for a in data['articles'] if a.get('linkedinUrl')]
            linked[1]['linkedinUrl'] = linked[0]['linkedinUrl']
            config = Path(temp) / 'data.json'
            config.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'already registered'):
                publication.load_data(config)
            data = json.loads(json.dumps(self.data))
            data['articles'][0]['source']['textSha256'] = '0' * 64
            config.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'changed'):
                publication.load_data(config)


if __name__ == '__main__':
    unittest.main()
