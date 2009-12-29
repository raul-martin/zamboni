from django import test

from nose.tools import eq_

from amo import urlresolvers


class MiddlewareTest(test.TestCase):
    """
    Tests that the locale and app redirection work propperly
    """

    def test_redirection(self):
        redirections = {
        '/': '/en-US/firefox/',
        '/en-US': '/en-US/firefox/',
        '/sda/dasdas': '/en-US/firefox/sda/dasdas',
        '/sda/dasdas/': '/en-US/firefox/sda/dasdas/',
        '/sda/firefox/foo': '/en-US/firefox/foo',
        '/firefox': '/en-US/firefox/',
        '/admin': '/en-US/admin',
        }
        for path, redirection in redirections.items():
            response = self.client.get(path)
            location = response['Location'].replace('http://testserver', '', 1)

            self.assertEqual(location, redirection,
                "Expected %s to redirect to %s, but it went to %s" %
                (path, redirection, location))


class TestPrefixer:

    def setup(self):
        urlresolvers._prefixes.clear()

    def test_split_request(self):

        def split_eq(url, locale, app, path):
            prefixer = urlresolvers.Prefixer(Request(url))
            eq_(prefixer.split_request(), (locale, app, path))

        split_eq('/', '', '', '')
        split_eq('/en-US', 'en-US', '', '')
        split_eq('/en-US/firefox', 'en-US', 'firefox', '')
        split_eq('/en-US/firefox/', 'en-US', 'firefox', '')
        split_eq('/en-US/firefox/foo', 'en-US', 'firefox', 'foo')
        split_eq('/en-US/firefox/foo/', 'en-US', 'firefox', 'foo/')
        split_eq('/en-US/foo', 'en-US', '', 'foo')
        split_eq('/en-US/foo/', 'en-US', '', 'foo/')
        split_eq('/bad/firefox/foo', '', 'firefox', 'foo')
        split_eq('/bad/firefox/foo/', '', 'firefox', 'foo/')
        split_eq('/firefox/foo', '', 'firefox', 'foo')
        split_eq('/firefox/foo/', '', 'firefox', 'foo/')
        split_eq('/foo', '', '', 'foo')
        split_eq('/foo/', '', '', 'foo/')

    def test_fix(self):
        prefixer = urlresolvers.Prefixer(Request('/'))

        eq_(prefixer.fix('/'), '/en-US/firefox/')
        eq_(prefixer.fix('/foo'), '/en-US/firefox/foo')
        eq_(prefixer.fix('/foo/'), '/en-US/firefox/foo/')
        eq_(prefixer.fix('/admin'), '/en-US/admin')
        eq_(prefixer.fix('/admin/'), '/en-US/admin/')

        prefixer.locale = 'de'
        prefixer.app = 'thunderbird'

        eq_(prefixer.fix('/'), '/de/thunderbird/')
        eq_(prefixer.fix('/foo'), '/de/thunderbird/foo')
        eq_(prefixer.fix('/foo/'), '/de/thunderbird/foo/')
        eq_(prefixer.fix('/admin'), '/de/admin')
        eq_(prefixer.fix('/admin/'), '/de/admin/')

    def test_reverse(self):
        # Make sure it works outside the request.
        eq_(urlresolvers.reverse('home'), '/')

        # With a request, locale and app prefixes work.
        client = test.Client()
        client.get('/')
        eq_(urlresolvers.reverse('home'), '/en-US/firefox/')


class Request(object):

    def __init__(self, path):
        self.path = path
