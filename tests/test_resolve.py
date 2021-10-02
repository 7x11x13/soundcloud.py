from soundcloud import SoundCloud, Track, AlbumPlaylist, User

def test_resolve_track(client: SoundCloud):
    track = client.resolve("https://soundcloud.com/7x11x13/wan-bushi-eurodance-vibes-part-123")
    assert isinstance(track, Track) and track.id == 1032303631
    
def test_resolve_playlist(client: SoundCloud):
    playlist = client.resolve("https://soundcloud.com/one-thousand-and-one/sets/playlist1")
    assert isinstance(playlist, AlbumPlaylist) and playlist.id == 1326192094

def test_resolve_user(client: SoundCloud):
    user = client.resolve("https://soundcloud.com/7x11x13")
    assert isinstance(user, User) and user.id == 790976431

def test_resolve_invalid_resource(client: SoundCloud):
    assert client.resolve("https://soundcloud.com/7x11x13/invalid") is None
    
def test_resolve_invalid_url(client: SoundCloud):
    assert client.resolve("https://google.com/") is None