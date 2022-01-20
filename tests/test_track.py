from soundcloud import BasicTrack, SoundCloud


def test_get_track_by_id(client: SoundCloud):
    track = client.get_track(1032303631)
    assert isinstance(track, BasicTrack) and track.title == "Wan Bushi - Eurodance Vibes (part 1+2+3)"
    
def test_get_tracks(client: SoundCloud):
    tracks = client.get_tracks([1032303631, 919105681])
    ids = {track.id for track in tracks}
    assert 1032303631 in ids and 919105681 in ids

def test_track_albums(client: SoundCloud):
    album = next(client.get_track_albums(919105681))
    assert album.user.username == "Ariana Grande"
    
def test_track_playlists(client: SoundCloud):
    found = False
    for playlist in client.get_track_playlists(1032303631):
        if playlist.user.permalink == "one-thousand-and-one":
            found = True
            break
    assert found

def test_track_comments(client: SoundCloud):
    found = False
    for comment in client.get_track_comments(1032303631):
        if comment.user.username == "7x11x13-testing" and comment.body == "hi":
            found = True
            break
    assert found

def test_track_reposters(client: SoundCloud):
    track = client.get_track(1032303631)
    found = False
    for user in client.get_track_reposters(track.id):
        if user.permalink == "one-thousand-and-one":
            found = True
            break
    assert found

def test_track_likers(client: SoundCloud):
    track = client.get_track(1032303631)
    found = False
    for user in client.get_track_likers(track.id):
        if user.permalink == "one-thousand-and-one":
            found = True
            break
    assert found

def test_track_tags(client: SoundCloud):
    track = client.get_track(1032303631)
    tags = track.get_all_tags()
    assert "Wan Bushi" in tags and "Electronic" in tags

def test_track_original_download(client: SoundCloud):
    download = client.get_track_original_download(1032303631)
    assert download.startswith("http")
