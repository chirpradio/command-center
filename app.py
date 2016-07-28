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

import mock_commands as commands
# import commands


COMMAND_PAGES = [
    # (slug, function)
    ('new-artists', commands.new_artists),
    ('update-artist-whitelist', commands.update_artist_whitelist),
    ('check-music', commands.check_music),
    ('generate-traktor', commands.generate_traktor),
    ('upload', commands.upload),
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
        handlers.extend([
            (r'/%s/' % slug, CommandPageHandler, {'slug': slug}),
            (r'/%s/start/' % slug, StartCommandHandler, {'slug': slug, 'func': func}),
            (r'/%s/stop/' % slug, StopCommandHandler, {'slug': slug}),
            (r'/%s/messages/' % slug, MessageHandler, {'slug': slug}),
        ])
    handlers.append(
        (r'/(.*)', NoCacheStaticFileHandler, {'path': str(site_path)}))

    settings = dict(debug=True)
    app = CommandCenterApplication(handlers, **settings)
    app.listen(8000)
    loop = IOLoop.current()
    loop.start()


class CommandCenterApplication(Application):
    def __init__(self, *args, **kwargs):
        super(CommandCenterApplication, self).__init__(*args, **kwargs)

        self.sockets = collections.defaultdict(set)
        self.current_task = None
        self.loop = IOLoop.current()

        def write_message(self, slug, message=None, **kwargs):
            """
            It is safe to call this method from outside the main thread that is
            running the Tornado event loop.

            """
            if not len(kwargs):
                obj = dict(type='info', value=message)
            else:
                obj = kwargs
                if message is not None:
                    kwargs['value'] = message

            data = json.dumps(obj)
            self.loop.add_callback(self._write_message, slug, data)

        def _write_message(self, slug, data):
            """
            Write the given data to all connected websockets for a particular
            slug.

            """
            for socket in self.sockets[slug]:
                socket.write_message(data)


class IndexHandler(RequestHandler):
    def get(self):
        self.write(render('index.plim', task=app.current_task))


class CommandPageHandler(RequestHandler):
    def initialize(self, slug):
        self.slug = slug

    def get(self):
        template_name = self.slug + '.plim'

        task = app.current_task
        task_is_running = task is not None and task.slug == self.slug
        self.write(render(template_name, task_is_running=task_is_running))


class StartCommandHandler(RequestHandler):
    def initialize(self, slug, func):
        self.slug = slug
        self.func = func

    def get(self):
        if app.current_task is not None:
            self.write('fail: command is still running')
            return

        task_func = get_task_func(self.func)
        task = CommandTask(self.slug, task_func)
        task.start()
        app.current_task = task
        self.write('ok')


class StopCommandHandler(RequestHandler):
    def initialize(self, slug):
        self.slug = slug

    def get(self):
        task = app.current_task
        if task is None:
            self.write('fail: no command is running')
            return
        if task.slug != self.slug:
            self.write('fail: cannot stop other command')
            return

        task.stop()
        app.current_task = None


class MessageHandler(WebSocketHandler):
    def initialize(self, slug):
        self.slug = slug

    def open(self):
        app.sockets[self.slug].add(self)

    def on_close(self):
        app.sockets[self.slug].remove(self)


class NoCacheStaticFileHandler(StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store')


class CommandTask(object):
    def __init__(self, slug, func):
        self.slug = slug
        self.func = func
        self.stop_event = threading.Event()
        self.future = None

    def stop(self):
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


def render(template_name, **kwargs):
    path = site_path / template_name
    # import ipdb; ipdb.set_trace()
    tmpl = Template(
        # filename=str(path),
        text=path.read_text(),
        lookup=template_lookup,
        preprocessor=plim.preprocessor)
    return tmpl.render(**kwargs)


def get_task_func(slug, func):
    from .printing import cprint

    write_func = functools.partial(app.write_message, slug)

    def new_func():
        with cprint.use_write_function(write_func):
            for obj in func():
                yield obj

    return new_func


if __name__ == '__main__':
    main()
