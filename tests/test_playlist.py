from soundcloud import BasicAlbumPlaylist, SoundCloud, NoContentResponse


def test_get_playlist(client: SoundCloud):
    playlist = client.get_playlist(1326192094)
    assert (
        isinstance(playlist, BasicAlbumPlaylist)
        and playlist.user.username == "7x11x13-testing"
    )


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


def test_post_and_delete_playlist(client: SoundCloud):
    # POST
    playlist = client.post_playlist("private", "Playlist Test", [1032303631])
    assert (
        isinstance(playlist, BasicAlbumPlaylist)
        and playlist.title == "Playlist Test"
        and playlist.tracks[0].id == 1032303631
    )

    # DELETE
    response = client.delete_playlist(playlist.id)
    assert isinstance(response, NoContentResponse) and response.status_code == 204
