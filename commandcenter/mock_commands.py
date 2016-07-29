import time

from printing import cprint


def new_artists():
    for i in range(1, 31):
        cprint('Artist #%d' % i)
        time.sleep(0.2)
        yield

    cprint('Found 30 new artists!', type='success')


def update_artist_whitelist():
    for i in range(1, 31):
        cprint('Artist #%d' % i)
        time.sleep(0.2)
        if i == 11:
            raise Exception('Oh no random unexpected error!')
        yield

    cprint('Added 30 new artists!', type='success')


check_music = new_artists
generate_traktor = new_artists
upload = new_artists
