from soundcloud import SoundCloud


def test_get_comments_with_interactions(client: SoundCloud):
    comments = list(client.get_track_comments_with_interactions(1032303631))
    comments = list(filter(lambda comment: comment.comment.id == 1509855118, comments))
    assert comments
    comment = comments[0]
    assert comment.likes >= 1
    assert comment.liked_by_creator
    assert comment.liked_by_user
