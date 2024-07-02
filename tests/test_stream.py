import itertools

from soundcloud import SoundCloud, TrackStreamItem


def test_my_history(client: SoundCloud):
    stream = client.get_my_history()
    for item in itertools.islice(stream, 3):
        assert item is not None


def test_my_stream(client: SoundCloud):
    stream = client.get_my_stream()
    for item in itertools.islice(stream, 3):
        assert item is not None


def test_user_stream(client: SoundCloud):
    user = client.get_user_by_username("one-thousand-and-one")
    assert user
    stream = client.get_user_stream(user.id)
    item = next(stream)
    assert (
        isinstance(item, TrackStreamItem) and item.track.title == "testing - test track"
    )
    item = next(stream)
    assert (
        isinstance(item, TrackStreamItem)
        and item.track.title == "Wan Bushi - Eurodance Vibes (part 1+2+3)"
    )


def test_tag_stream(client: SoundCloud):
    stream = client.get_tag_tracks_recent("Electronic")
    for track in itertools.islice(stream, 3):
        assert track is not None
