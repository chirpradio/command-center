from tornado.testing import AsyncHTTPTestCase
from tornado.websocket import websocket_connect

from . import app


class TestMyApp(AsyncHTTPTestCase):
    def get_app(self):
        return app.get_app()

    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        body = response.body.decode('utf-8')

        # Check that title is there.
        self.assertIn('<h1>CHIRP Command Center</h1>', body)

        # Check that links are present.
        self.assertRegexpMatches(
            body,
            r'<a href="/new-artists/" class="[^"]+">See new artists</a>')
