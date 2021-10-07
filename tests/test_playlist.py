from soundcloud import SoundCloud, BasicAlbumPlaylist

def test_get_playlist(client: SoundCloud):
    playlist = client.get_playlist(1326192094)
    assert isinstance(playlist, BasicAlbumPlaylist) and playlist.user.username == "7x11x13-testing"
    
def test_playlist_likers(client: SoundCloud):
    likers = client.get_playlist_likers(1326192094)
    found = False
    for liker in likers:
        if liker.username == "7x11x13":
            found = True
            break
    assert found

def test_playlist_reposters(client: SoundCloud):
    reposters = client.get_playlist_reposters(1326720835)
    found = False
    for reposter in reposters:
        if reposter.username == "7x11x13":
            found = True
            break
    assert found