import sys
import subprocess
import os.path as op
import time

from chirp.common.printing import cprint


def new_artists():
    from chirp.library.do_dump_new_artists_in_dropbox import main_generator
    for _ in main_generator(rewrite=False):
        yield


def update_artist_whitelist():
    from chirp.library import artists
    from chirp.library.do_dump_new_artists_in_dropbox import main_generator
    for _ in main_generator(rewrite=True):
        yield

    cwd = op.dirname(artists._WHITELIST_FILE)

    # Show changes to the artist whitelist file
    cmd = ['git', 'diff', artists._WHITELIST_FILE]
    exec_and_print(cmd, cwd)

    # Commit and push.
    cmd = ['git', 'commit', artists._WHITELIST_FILE, '-m', 'Adding new artists']
    exec_and_print(cmd, cwd)
    # cmd = ['git', 'push']
    # exec_and_print(cmd, cwd)

    cprint('Changes to artist whitelist pushed to git', type='success')


def check_music():
    from chirp.library.do_periodic_import import import_albums
    for _ in import_albums(dry_run=True):
        yield


def import_music():
    from chirp.library.do_periodic_import import import_albums
    for _ in import_albums(dry_run=False):
        yield
    cprint('Finished!', type='success')


def generate_traktor():
    from chirp.library.do_generate_collection_nml import main_generator
    for _ in main_generator():
        yield


def upload():
    from chirp.library.do_push_artists_to_chirpradio import main_generator
    for _ in main_generator():
        yield

    from chirp.library.do_push_to_chirpradio import main_generator
    for _ in main_generator(start_timestamp=time.time()):
        yield


# def fake_command():
#     import time
#     for i in range(1, 11):
#         cprint('Line #%d' % i)
#         time.sleep(0.2)
#         yield
#     cprint('Success!', type='success')


def exec_and_print(cmd, cwd):
    cprint(' '.join(cmd), type='highlight')
    output = subprocess.check_output(cmd, cwd=cwd)
    cprint(output)
