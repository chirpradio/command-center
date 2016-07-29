import sys
import subprocess
import os.path as op

from chirp.common.printing import cprint


def new_artists():
    from chirp.library.do_dump_new_artists_in_dropbox import main
    for _ in main(): yield


def update_artist_whitelist():
    from chirp.library import artists
    from chirp.library.do_dump_new_artists_in_dropbox import main
    sys.argv = ['--rewrite']
    for _ in main(): yield
    sys.argv = None

    cwd = op.dirname(artists._WHITELIST_FILE)
    
    # Show changes to the artist whitelist file
    cmd = ['git', 'diff', artists._WHITELIST_FILE]
    exec_and_print(cmd, cwd)

    # Commit and push.
    cmd = ['git', 'commit', artists._WHITELIST_FILE, '-m', 'Adding new artists']
    exec_and_print(cmd, cwd)
    # cmd = ['git', 'push']
    # exec_and_print(cmd, cwd)


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


def exec_and_print(cmd, cwd):
    cprint(' '.join(cmd), type='highlight')
    output = subprocess.check_output(cmd, cwd=cwd)
    cprint(output)
