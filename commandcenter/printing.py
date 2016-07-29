import contextlib


class CustomPrint(object):
    def __init__(self):
        self.write = self.default_write

    def __call__(self, message, **kwargs):
        self.write(message, **kwargs)

    def default_write(self, message, **kwargs):
        if message:
            print(message)

    @contextlib.contextmanager
    def use_write_function(self, func):
        self.write = func
        yield
        self.write = self.default_write


cprint = CustomPrint()
