import itertools

from soundcloud import SoundCloud, User
from soundcloud.resource.like import TrackLike
from soundcloud.resource.stream import TrackStreamRepostItem


def test_valid_user_id(client: SoundCloud):
    user = client.get_user(790976431)
    assert isinstance(user, User) and user.permalink == "7x11x13"


def test_invalid_user_id(client: SoundCloud):
    user = client.get_user(0)
    assert user is None


def test_valid_username(client: SoundCloud):
    user = client.get_user_by_username("7x11x13")
    assert isinstance(user, User) and user.permalink == "7x11x13"


def test_invalid_username(client: SoundCloud):
    user = client.get_user_by_username("")
    assert user is None


def test_user_comments(client: SoundCloud):
    comment = next(client.get_user_comments(992430331))
    assert comment.body == "hi"


def test_user_conversation_messages(client: SoundCloud):
    message = next(client.get_conversation_messages(790976431, 992430331))
    assert message.content == "bye"


def test_user_conversations(client: SoundCloud):
    found = False
    for conversation in client.get_conversations(790976431):
        if conversation.last_message.content == "bye":
            found = True
    assert found


def test_user_followers(client: SoundCloud):
    found = False
    for follower in client.get_user_followers(992430331):
        if follower.permalink == "7x11x13":
            found = True
            break
    assert found


def test_user_followings(client: SoundCloud):
    following = next(client.get_user_following(992430331))
    assert following.permalink == "7x11x13"


def test_user_likes(client: SoundCloud):
    like = next(client.get_user_likes(992430331))
    assert isinstance(like, TrackLike)
    assert like.track.title == "Wan Bushi - Eurodance Vibes (part 1+2+3)"


def test_user_likes_2(client: SoundCloud):
    for like in itertools.islice(client.get_user_likes(790976431), 10):
        assert like is not None


def test_user_reposts(client: SoundCloud):
    repost = next(client.get_user_reposts(992430331))
    assert isinstance(repost, TrackStreamRepostItem)
    assert repost.track.title == "Wan Bushi - Eurodance Vibes (part 1+2+3)"


def test_user_tracks(client: SoundCloud):
    tracks = list(client.get_user_tracks(790976431))
    assert tracks[-1].title == "Wan Bushi - Eurodance Vibes (part 1+2+3)"


def test_user_toptracks(client: SoundCloud):
    tracks = list(client.get_user_popular_tracks(790976431))
    assert tracks[0].title == "Wan Bushi - Eurodance Vibes (part 1+2+3)"


def test_user_albums(client: SoundCloud):
    found = False
    for album in client.get_user_albums(211111464):
        if album.title == "Positions":
            found = True
            break
    assert found


def test_user_playlists(client: SoundCloud):
    assert next(client.get_user_playlists(992430331)).title == "playlist1"


def test_user_links(client: SoundCloud):
    user = client.get_user(992430331)
    assert user
    profiles = client.get_user_links(user.urn)
    assert profiles[0].title == "test"


def test_user_emails(client: SoundCloud):
    email = next(client.get_user_emails(790976431))
    assert email.address.endswith("gmail.com")
