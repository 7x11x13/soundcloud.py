from soundcloud import SoundCloud, User, Track, AlbumPlaylist

def test_search_all(client: SoundCloud):
    user = next(client.search("Ariana Grande"))
    assert isinstance(user, User) and user.permalink == "arianagrande"
    
def test_search_albums(client: SoundCloud):
    album = next(client.search_albums("Positions"))
    assert isinstance(album, AlbumPlaylist) and album.user.username == "Ariana Grande"

def test_search_playlists(client: SoundCloud):
    playlist = next(client.search_playlists("we do a little music"))
    assert isinstance(playlist, AlbumPlaylist) and playlist.title == "We Do A Little Music [incomplete]"
    
def test_search_tracks(client: SoundCloud):
    track = next(client.search_tracks("34+35"))
    assert isinstance(track, Track) and track.user.username == "Ariana Grande"

def test_search_users(client: SoundCloud):
    user = next(client.search_users("namasenda"))
    assert isinstance(user, User) and user.permalink == "namasenda"