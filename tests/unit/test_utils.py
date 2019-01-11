# -*- coding: utf-8 -*-
import mock
from unittest import TestCase
from searx import utils


class TestUtils(TestCase):

    def test_gen_useragent(self):
        self.assertIsInstance(utils.gen_useragent(), str)
        self.assertIsNotNone(utils.gen_useragent())
        self.assertTrue(utils.gen_useragent().startswith('Mozilla'))

    def test_searx_useragent(self):
        self.assertIsInstance(utils.searx_useragent(), str)
        self.assertIsNotNone(utils.searx_useragent())
        self.assertTrue(utils.searx_useragent().startswith('searx'))

    def test_highlight_content(self):
        self.assertEqual(utils.highlight_content(0, None), None)
        self.assertEqual(utils.highlight_content(None, None), None)
        self.assertEqual(utils.highlight_content('', None), None)
        self.assertEqual(utils.highlight_content(False, None), None)

        contents = [
            '<html></html>'
            'not<'
        ]
        for content in contents:
            self.assertEqual(utils.highlight_content(content, None), content)

        content = 'a'
        query = 'test'
        self.assertEqual(utils.highlight_content(content, query), content)
        query = 'a test'
        self.assertEqual(utils.highlight_content(content, query), content)

    def test_html_to_text(self):
        html = """
        <a href="/testlink" class="link_access_account">
            <span class="toto">
                <span>
                    <img src="test.jpg" />
                </span>
            </span>
            <span class="titi">
                            Test text
            </span>
        </a>
        """
        self.assertIsInstance(utils.html_to_text(html), str)
        self.assertIsNotNone(utils.html_to_text(html))
        self.assertEqual(utils.html_to_text(html), "Test text")

    def test_prettify_url(self):
        data = (('https://searx.me/', 'https://searx.me/'),
                ('https://searx.me/ű', 'https://searx.me/ű'),
                ('https://searx.me/' + (100 * 'a'), 'https://searx.me/[...]aaaaaaaaaaaaaaaaa'),
                ('https://searx.me/' + (100 * 'ű'), 'https://searx.me/[...]űűűűűűűűűűűűűűűűű'))

        for test_url, expected in data:
            self.assertEqual(utils.prettify_url(test_url, max_length=32), expected)

    def test_match_language(self):
        self.assertEqual(utils.match_language('es', ['es']), 'es')
        self.assertEqual(utils.match_language('es', [], fallback='fallback'), 'fallback')
        self.assertEqual(utils.match_language('ja', ['jp'], {'ja': 'jp'}), 'jp')

        aliases = {'en-GB': 'en-UK', 'he': 'iw'}

        # guess country
        self.assertEqual(utils.match_language('de-DE', ['de']), 'de')
        self.assertEqual(utils.match_language('de', ['de-DE']), 'de-DE')
        self.assertEqual(utils.match_language('es-CO', ['es-AR', 'es-ES', 'es-MX']), 'es-ES')
        self.assertEqual(utils.match_language('es-CO', ['es-MX']), 'es-MX')
        self.assertEqual(utils.match_language('en-UK', ['en-AU', 'en-GB', 'en-US']), 'en-GB')
        self.assertEqual(utils.match_language('en-GB', ['en-AU', 'en-UK', 'en-US'], aliases), 'en-UK')

        # language aliases
        self.assertEqual(utils.match_language('iw', ['he']), 'he')
        self.assertEqual(utils.match_language('he', ['iw'], aliases), 'iw')
        self.assertEqual(utils.match_language('iw-IL', ['he']), 'he')
        self.assertEqual(utils.match_language('he-IL', ['iw'], aliases), 'iw')
        self.assertEqual(utils.match_language('iw', ['he-IL']), 'he-IL')
        self.assertEqual(utils.match_language('he', ['iw-IL'], aliases), 'iw-IL')
        self.assertEqual(utils.match_language('iw-IL', ['he-IL']), 'he-IL')
        self.assertEqual(utils.match_language('he-IL', ['iw-IL'], aliases), 'iw-IL')


class TestHTMLTextExtractor(TestCase):

    def setUp(self):
        self.html_text_extractor = utils.HTMLTextExtractor()

    def test__init__(self):
        self.assertEqual(self.html_text_extractor.result, [])

    def test_handle_charref(self):
        self.html_text_extractor.handle_charref('xF')
        self.assertIn('\x0f', self.html_text_extractor.result)
        self.html_text_extractor.handle_charref('XF')
        self.assertIn('\x0f', self.html_text_extractor.result)

        self.html_text_extractor.handle_charref('97')
        self.assertIn('a', self.html_text_extractor.result)

    def test_handle_entityref(self):
        entity = 'test'
        self.html_text_extractor.handle_entityref(entity)
        self.assertIn(entity, self.html_text_extractor.result)


class TestUnicodeWriter(TestCase):

    def setUp(self):
        self.unicode_writer = utils.UnicodeWriter(mock.MagicMock())

    def test_write_row(self):
        row = [1, 2, 3]
        self.assertEqual(self.unicode_writer.writerow(row), None)

    def test_write_rows(self):
        self.unicode_writer.writerow = mock.MagicMock()
        rows = [1, 2, 3]
        self.unicode_writer.writerows(rows)
        self.assertEqual(self.unicode_writer.writerow.call_count, len(rows))
