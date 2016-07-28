import random
import time
import functools
import threading
import json
import collections

from concurrent.futures import ThreadPoolExecutor
from pathlib2 import Path
from mako.template import Template
from mako.lookup import TemplateLookup
import plim
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler
from tornado import gen

import mock_funcs as mf


COMMAND_PAGES = [
    # (slug, function)
    ('new-artists', mf.new_artists),
    ('update-artist-whitelist', mf.update_artist_whitelist),
    ('check-music', mf.check_music),
    ('generate-traktor', mf.generate_traktor),
    ('upload', mf.upload),
]

site_path = Path(__file__).parent.absolute() / 'site'
template_lookup = TemplateLookup(
    directories=[str(site_path)], preprocessor=plim.preprocessor)
executor = ThreadPoolExecutor(1)
app = None


def main():
    global app
    handlers = [(r'/', IndexHandler)]
    for slug, func in COMMAND_PAGES:
        handlers.append(
            (r'/%s/' % slug, CommandPageHandler, {'slug': slug}))
    handlers.append(
        (r'/(.*)', NoCacheStaticFileHandler, {'path': str(site_path)}))

    settings = dict(debug=True)
    app = Application(handlers, **settings)
    app.sockets = collections.defaultdict(set)
    app.current_task = None
    app.listen(8000)
    loop = IOLoop.current()

    # Let the send() callable know about the loop and the sockets.
    # send.loop = loop
    # send.sockets = app.sockets

    loop.start()


class IndexHandler(RequestHandler):
    def get(self):
        self.write(render('index.plim', task=app.current_task))


class CommandPageHandler(RequestHandler):
    def initialize(self, slug):
        self.slug = slug

    def get(self):
        template_name = self.slug + '.plim'
        self.write(render(template_name))


class StartHandler(RequestHandler):
    def initialize(self, slug, func):
        self.slug = slug
        self.func = func

    def get(self):
        pass


class StopHandler(RequestHandler):
    def get(self):
        app = self.application
        if app.current_task:
            app.current_task.cancel()
            self.write('Stopping background task...')
            app.logger.info('Stopping background task...')


class MessageHandler(WebSocketHandler):
    def initialize(self, slug):
        self.slug = slug

    def open(self):
        self.application.sockets[self.slug].add(self)

    def on_close(self):
        self.application.sockets[self.slug].remove(self)


class NoCacheStaticFileHandler(StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store')


class CommandTask(object):
    def __init__(self, slug, func):
        self.slug = slug
        self.func = func
        self.stop_event = threading.Event()
        self.future = None

    def cancel(self):
        self.stop_event.set()

    def done(self):
        return self.stop_event.is_set()

    def start(self):
        """
        Unlike asyncio's run_in_executor(), submit() does not raise an exception
        when the function it tries to run errors out.

        """
        self.future = executor.submit(self._stoppable_run)
        self.add_done_callback(self._done_callback)

    def add_done_callback(self, callback):
        if self.future:
            self.future.add_done_callback(callback)

    def _stoppable_run(self):
        for obj in self.func():
            if self.stop_event.is_set():
                break
        self.stop_event.set()

    def _done_callback(self, future):
        # If there was an exception inside of self._stoppable_run, then it won't
        # be raised until you call future.result().
        try:
            future.result()
        except Exception as ex:
            self.log('Error: %s' % ex)



class SendCallable:
    """
    A callable object that is used to communicate with the browser.
    """

    def __init__(self):
        self.loop = None
        self.sockets = None

    def __call__(self, obj=None, **kwargs):
        """
        It is safe to call this method from outside the main thread that is
        running the Tornado event loop.
        """
        if not self.loop:
            return
        if obj is not None:
            data = json.dumps(obj)
            if kwargs:
                print('Warning: Keyword arguments to send() are ignored when '
                      'single positional argument is given')
        else:
            data = json.dumps(kwargs)
        self.loop.add_callback(self._send, data)

    def _send(self, data):
        "Write the given data to all connected websockets."
        for socket in self.sockets:
            socket.write_message(data)


send = SendCallable()

def render(template_name, **kwargs):
    path = site_path / template_name
    # import ipdb; ipdb.set_trace()
    tmpl = Template(
        # filename=str(path),
        text=path.read_text(),
        lookup=template_lookup,
        preprocessor=plim.preprocessor)
    return tmpl.render(**kwargs)


if __name__ == '__main__':
    main()
