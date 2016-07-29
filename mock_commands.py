import time

from printing import cprint


def new_artists():
    for i in range(1, 31):
        cprint('Artist #%d' % i)
        time.sleep(0.2)
        if i == 11:
            raise Exception('Oh no random unexpected error!')
        yield

    cprint('Found 30 new artists!', type='success')


update_artist_whitelist = new_artists
check_music = new_artists
generate_traktor = new_artists
upload = new_artists
