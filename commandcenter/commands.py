from chirp.common.printing import cprint


def new_artists():
    from chirp.library.do_dump_new_artists_in_dropbox import main
    for _ in main(): yield


def update_artist_whitelist():
    for _ in fake_command(): yield


def check_music():
    for _ in fake_command(): yield


def generate_traktor():
    for _ in fake_command(): yield


def upload():
    for _ in fake_command(): yield


def fake_command():
    import time
    for i in range(1, 11):
        cprint('Line #%d' % i)
        time.sleep(0.2)
        yield
    cprint('Success!', type='success')
