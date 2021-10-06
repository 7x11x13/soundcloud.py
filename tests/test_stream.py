from soundcloud import SoundCloud, TrackStreamItem

def test_my_stream(client: SoundCloud):
    item = next(client.get_my_stream())
    assert item is not None

def test_user_stream(client: SoundCloud):
    user = client.get_user_by_username("one-thousand-and-one")
    stream = client.get_user_stream(user.id)
    recent = next(stream)
    assert isinstance(recent, TrackStreamItem) and recent.track.title == "Wan Bushi - Eurodance Vibes (part 1+2+3)"