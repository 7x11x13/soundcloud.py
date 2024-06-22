import itertools
import re
from typing import Dict, Generator, List, Optional

import requests
from requests import HTTPError

from soundcloud.exceptions import ClientIDGenerationError
from soundcloud.requests import (
    CollectionRequest,
    ListRequest,
    Request,
    UserInteractionsQueryParams,
    UserInteractionsRequest,
)
from soundcloud.resource.graphql import CommentWithInteractions
from soundcloud.resource.history import HistoryItem

from .resource.aliases import Like, RepostItem, SearchItem, StreamItem
from .resource.comment import BasicComment, Comment
from .resource.conversation import Conversation
from .resource.download import OriginalDownload
from .resource.message import Message
from .resource.playlist import AlbumPlaylist, BasicAlbumPlaylist
from .resource.track import BasicTrack, Track
from .resource.user import User, UserEmail, UserStatus
from .resource.web_profile import WebProfile


class SoundCloud:
    """
    SoundCloud v2 API client
    """

    _DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"
    )
    _ASSETS_SCRIPTS_REGEX = re.compile(
        r"src=\"(https:\/\/a-v2\.sndcdn\.com/assets/[^\.]+\.js)\""
    )
    _CLIENT_ID_REGEX = re.compile(r"client_id:\"([^\"]+)\"")
    client_id: str
    """SoundCloud client ID. Needed for all requests."""
    auth_token: str
    """SoundCloud auth token. Only needed for some requests."""

    def __init__(
        self,
        client_id: str = None,
        auth_token: str = None,
        user_agent: str = _DEFAULT_USER_AGENT,
    ) -> None:

        if not client_id:
            client_id = self.generate_client_id()

        self.client_id = client_id
        self._user_agent = user_agent
        self._auth_token = None
        self._authorization = None
        self.auth_token = auth_token

        self._requests: Dict[str, Request] = {
            "me": Request[User]("/me", User),
            "me_history": CollectionRequest[HistoryItem](
                "/me/play-history/tracks", HistoryItem
            ),
            "me_stream": CollectionRequest[StreamItem]("/stream", StreamItem),
            "resolve": Request[SearchItem]("/resolve", SearchItem),
            "search": CollectionRequest[SearchItem]("/search", SearchItem),
            "search_albums": CollectionRequest[AlbumPlaylist](
                "/search/albums", AlbumPlaylist
            ),  # ?filter.genre_or_tag
            "search_playlists": CollectionRequest[AlbumPlaylist](
                "/search/playlists_without_albums", AlbumPlaylist
            ),
            "search_tracks": CollectionRequest[Track](
                "/search/tracks", Track
            ),  # ?filter.created_at&filter.duration&filter.license
            "search_users": CollectionRequest[User](
                "/search/users", User
            ),  # ?filter.place
            "tag_recent_tracks": CollectionRequest[Track](
                "/recent-tracks/{tag}", Track
            ),
            "playlist": Request[BasicAlbumPlaylist](
                "/playlists/{playlist_id}", BasicAlbumPlaylist
            ),
            "playlist_likers": CollectionRequest[User](
                "/playlists/{playlist_id}/likers", User
            ),
            "playlist_reposters": CollectionRequest[User](
                "/playlists/{playlist_id}/reposters", User
            ),
            "track": Request[BasicTrack]("/tracks/{track_id}", BasicTrack),
            "tracks": ListRequest[BasicTrack]("/tracks", BasicTrack),
            "track_albums": CollectionRequest[BasicAlbumPlaylist](
                "/tracks/{track_id}/albums", BasicAlbumPlaylist
            ),  # (can be representation=mini)
            "track_playlists": CollectionRequest[BasicAlbumPlaylist](
                "/tracks/{track_id}/playlists_without_albums", BasicAlbumPlaylist
            ),  # (can be representation=mini)
            "track_comments": CollectionRequest[BasicComment](
                "/tracks/{track_id}/comments", BasicComment
            ),
            "track_likers": CollectionRequest[User]("/tracks/{track_id}/likers", User),
            "track_related": CollectionRequest[BasicTrack](
                "/tracks/{track_id}/related", BasicTrack
            ),
            "track_reposters": CollectionRequest[User](
                "/tracks/{track_id}/reposters", User
            ),
            "track_original_download": Request[OriginalDownload](
                "/tracks/{track_id}/download", OriginalDownload
            ),
            "user": Request[User]("/users/{user_id}", User),
            "user_comments": CollectionRequest[Comment](
                "/users/{user_id}/comments", Comment
            ),
            "user_conversation_messages": CollectionRequest[Message](
                "/users/{user_id}/conversations/{conversation_id}/messages", Message
            ),
            "user_conversations": CollectionRequest[Conversation](
                "/users/{user_id}/conversations", Conversation
            ),
            "user_conversations_unread": CollectionRequest[Conversation](
                "/users/{user_id}/conversations/unread", Conversation
            ),
            "user_emails": CollectionRequest[UserEmail](
                "/users/{user_id}/emails", UserEmail
            ),
            "user_featured_profiles": CollectionRequest[User](
                "/users/{user_id}/featured-profiles", User
            ),
            "user_followers": CollectionRequest[User](
                "/users/{user_id}/followers", User
            ),
            "user_followings": CollectionRequest[User](
                "/users/{user_id}/followings", User
            ),
            "user_likes": CollectionRequest[Like]("/users/{user_id}/likes", Like),
            "user_related_artists": CollectionRequest[User](
                "/users/{user_id}/relatedartists", User
            ),
            "user_reposts": CollectionRequest[RepostItem](
                "/stream/users/{user_id}/reposts", RepostItem
            ),
            "user_stream": CollectionRequest[StreamItem](
                "/stream/users/{user_id}", StreamItem
            ),
            "user_tracks": CollectionRequest[BasicTrack](
                "/users/{user_id}/tracks", BasicTrack
            ),
            "user_toptracks": CollectionRequest[BasicTrack](
                "/users/{user_id}/toptracks", BasicTrack
            ),
            "user_albums": CollectionRequest[BasicAlbumPlaylist](
                "/users/{user_id}/albums", BasicAlbumPlaylist
            ),  # (can be representation=mini)
            "user_playlists": CollectionRequest[BasicAlbumPlaylist](
                "/users/{user_id}/playlists_without_albums", BasicAlbumPlaylist
            ),  # (can be representation=mini)
            "user_web_profiles": ListRequest[WebProfile](
                "/users/{user_urn}/web-profiles", WebProfile
            ),
        }

    @property
    def auth_token(self) -> str:
        return self._auth_token

    @auth_token.setter
    def auth_token(self, new_auth_token: Optional[str]) -> None:
        if new_auth_token is not None:
            if new_auth_token.startswith("OAuth"):
                new_auth_token = new_auth_token.split()[-1]
        self._authorization = f"OAuth {new_auth_token}" if new_auth_token else None
        self._auth_token = new_auth_token

    @auth_token.deleter
    def auth_token(self):
        self.auth_token = None

    def _get_default_headers(self) -> Dict[str, str]:
        return {"User-Agent": self._user_agent}

    def generate_client_id(self) -> str:
        """Generates a SoundCloud client ID

        Raises:
            ClientIDGenerationError: Client ID could not be generated.

        Returns:
            str: Valid client ID
        """
        r = requests.get("https://soundcloud.com")
        r.raise_for_status()
        matches = self._ASSETS_SCRIPTS_REGEX.findall(r.text)
        if not matches:
            raise ClientIDGenerationError("No asset scripts found")
        url = matches[-1]
        r = requests.get(url)
        r.raise_for_status()
        client_id = self._CLIENT_ID_REGEX.search(r.text)
        if not client_id:
            raise ClientIDGenerationError(f"Could not find client_id in script '{url}'")
        return client_id.group(1)

    def is_client_id_valid(self) -> bool:
        """
        Checks if current client_id is valid
        """
        try:
            self._requests["track"](self, track_id=1032303631, use_auth=False)
            return True
        except HTTPError as err:
            if err.response.status_code == 401:
                return False
            else:
                raise

    def is_auth_token_valid(self) -> bool:
        """
        Checks if current auth_token is valid
        """
        try:
            self._requests["me"](self)
            return True
        except HTTPError as err:
            if err.response.status_code == 401:
                return False
            else:
                raise

    def get_me(self) -> UserStatus:
        """
        Gets the user associated with client's auth token
        """
        return self._requests["me"](self)

    def get_my_history(self, **kwargs) -> Generator[HistoryItem, None, None]:
        """
        Returns the stream of recently listened tracks
        for the client's auth token
        """
        return self._requests["me_history"](self, **kwargs)

    def get_my_stream(self, **kwargs) -> Generator[StreamItem, None, None]:
        """
        Returns the stream of recent uploads/reposts
        for the client's auth token
        """
        return self._requests["me_stream"](self, **kwargs)

    def resolve(self, url: str) -> Optional[SearchItem]:
        """
        Returns the resource at the given URL if it
        exists, otherwise return None
        """
        return self._requests["resolve"](self, url=url)

    def search(self, query: str, **kwargs) -> Generator[SearchItem, None, None]:
        """
        Search for users, tracks, and playlists
        """
        return self._requests["search"](self, q=query, **kwargs)

    def search_albums(self, query: str, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Search for albums (not playlists)
        """
        return self._requests["search_albums"](self, q=query, **kwargs)

    def search_playlists(self, query: str, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Search for playlists
        """
        return self._requests["search_playlists"](self, q=query, **kwargs)

    def search_tracks(self, query: str, **kwargs) -> Generator[Track, None, None]:
        """
        Search for tracks
        """
        return self._requests["search_tracks"](self, q=query, **kwargs)

    def search_users(self, query: str, **kwargs) -> Generator[User, None, None]:
        """
        Search for users
        """
        return self._requests["search_users"](self, q=query, **kwargs)

    def get_tag_tracks_recent(self, tag: str, **kwargs) -> Generator[Track, None, None]:
        """
        Get most recent tracks for this tag
        """
        return self._requests["tag_recent_tracks"](self, tag=tag, **kwargs)

    def get_playlist(self, playlist_id: int) -> Optional[BasicAlbumPlaylist]:
        """
        Returns the playlist with the given playlist_id.
        If the ID is invalid, return None
        """
        return self._requests["playlist"](self, playlist_id=playlist_id)

    def get_playlist_likers(self, playlist_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get people who liked this playlist
        """
        return self._requests["playlist_likers"](
            self, playlist_id=playlist_id, **kwargs
        )

    def get_playlist_reposters(self, playlist_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get people who reposted this playlist
        """
        return self._requests["playlist_reposters"](
            self, playlist_id=playlist_id, **kwargs
        )

    def get_track(self, track_id: int) -> Optional[BasicTrack]:
        """
        Returns the track with the given track_id.
        If the ID is invalid, return None
        """
        return self._requests["track"](self, track_id=track_id)

    def get_tracks(self, track_ids: List[int], playlistId: int = None, playlistSecretToken: str = None, **kwargs) -> List[BasicTrack]:
        """
        Returns the tracks with the given track_ids.
        Can be used to get track info for hidden tracks in a hidden playlist.
        """
        if playlistId:
            kwargs["playlistId"] = playlistId
        if playlistSecretToken:
            kwargs["playlistSecretToken"] = playlistSecretToken
        return self._requests["tracks"](
            self, ids=",".join([str(id) for id in track_ids]), **kwargs
        )

    def get_track_albums(self, track_id: int, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Get albums that this track is in
        """
        return self._requests["track_albums"](self, track_id=track_id, **kwargs)

    def get_track_playlists(self, track_id: int, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Get playlists that this track is in
        """
        return self._requests["track_playlists"](self, track_id=track_id, **kwargs)

    def get_track_comments(
        self, track_id: int, threaded: int = 0, **kwargs
    ) -> Generator[BasicComment, None, None]:
        """
        Get comments on this track
        """
        return self._requests["track_comments"](
            self, track_id=track_id, threaded=threaded, **kwargs
        )

    def get_track_comments_with_interactions(
        self, track_id: int, threaded: int = 0, **kwargs
    ) -> Generator[CommentWithInteractions, None, None]:
        """
        Get comments on this track with interaction data. Requires authentication.
        """
        track = self.get_track(track_id)
        track_urn = track.urn
        creator_urn = track.user.urn
        comments = self.get_track_comments(track_id, threaded, **kwargs)
        while True:
            chunk = list(itertools.islice(comments, 10))
            if not chunk:
                return
            comment_urns = [comment.self.urn for comment in chunk]
            result = UserInteractionsRequest(
                self,
                UserInteractionsQueryParams(
                    creator_urn,
                    "sc:interactiontype:reaction",
                    track_urn,
                    comment_urns,
                ),
            )
            comments_with_interactions = []
            for comment, user_interactions, creator_interactions in zip(
                chunk, result.user, result.creator
            ):
                likes = list(
                    filter(
                        lambda x: x.interactionTypeValueUrn
                        == "sc:interactiontypevalue:like",
                        user_interactions.interactionCounts,
                    )
                )
                num_likes = likes[0].count if likes else 0
                comments_with_interactions.append(
                    CommentWithInteractions(
                        comment=comment,
                        likes=num_likes,
                        liked_by_creator=creator_interactions.userInteraction
                        == "sc:interactiontypevalue:like",
                        liked_by_user=user_interactions.userInteraction
                        == "sc:interactiontypevalue:like",
                    )
                )
            yield from comments_with_interactions

    def get_track_likers(self, track_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get users who liked this track
        """
        return self._requests["track_likers"](self, track_id=track_id, **kwargs)

    def get_track_related(self, track_id: int, **kwargs) -> Generator[BasicTrack, None, None]:
        """
        Get related tracks
        """
        return self._requests["track_related"](self, track_id=track_id, **kwargs)

    def get_track_reposters(self, track_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get users who reposted this track
        """
        return self._requests["track_reposters"](self, track_id=track_id, **kwargs)

    def get_track_original_download(self, track_id: int, token: str = None) -> Optional[str]:
        """
        Get track original download link. If track is private,
        requires secret token to be provided (last part of secret URL).
        Requires authentication.
        """
        if token:
            download = self._requests["track_original_download"](
                self, track_id=track_id, secret_token=token
            )
        else:
            download = self._requests["track_original_download"](
                self, track_id=track_id
            )
        if download is None:
            return None
        else:
            return download.redirectUri

    def get_user(self, user_id: int) -> Optional[User]:
        """
        Returns the user with the given user_id.
        If the ID is invalid, return None
        """
        return self._requests["user"](self, user_id=user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Returns the user with the given username.
        If the username is invalid, return None
        """
        resource = self.resolve(f"https://soundcloud.com/{username}")
        if resource and resource.kind == "user":
            return resource
        else:
            return None

    def get_user_comments(self, user_id: int, **kwargs) -> Generator[Comment, None, None]:
        """
        Get comments by this user
        """
        return self._requests["user_comments"](self, user_id=user_id, **kwargs)

    def get_conversation_messages(self, user_id: int, conversation_id: int, **kwargs) -> Generator[Message, None, None]:
        """
        Get messages in this conversation
        """
        return self._requests["user_conversation_messages"](
            self, user_id=user_id, conversation_id=conversation_id, **kwargs
        )

    def get_conversations(self, user_id: int, **kwargs) -> Generator[Conversation, None, None]:
        """
        Get conversations including this user
        """
        return self._requests["user_conversations"](self, user_id=user_id, **kwargs)

    def get_unread_conversations(self, user_id: int, **kwargs) -> Generator[Conversation, None, None]:
        """
        Get conversations unread by this user
        """
        return self._requests["user_conversations_unread"](
            self, user_id=user_id, **kwargs
        )

    def get_user_emails(self, user_id: int, **kwargs) -> Generator[UserEmail, None, None]:
        """
        Get user's email addresses. Requires authentication.
        """
        return self._requests["user_emails"](self, user_id=user_id, **kwargs)

    def get_user_featured_profiles(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get profiles featured by this user
        """
        return self._requests["user_featured_profiles"](self, user_id=user_id, **kwargs)

    def get_user_followers(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get user's followers
        """
        return self._requests["user_followers"](self, user_id=user_id, **kwargs)

    def get_user_following(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get users this user is following
        """
        return self._requests["user_followings"](self, user_id=user_id, **kwargs)

    def get_user_likes(self, user_id: int, **kwargs) -> Generator[Like, None, None]:
        """
        Get likes by this user
        """
        return self._requests["user_likes"](self, user_id=user_id, **kwargs)

    def get_user_related_artists(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get artists related to this user
        """
        return self._requests["user_related_artists"](self, user_id=user_id, **kwargs)

    def get_user_reposts(self, user_id: int, **kwargs) -> Generator[RepostItem, None, None]:
        """
        Get reposts by this user
        """
        return self._requests["user_reposts"](self, user_id=user_id, **kwargs)

    def get_user_stream(self, user_id: int, **kwargs) -> Generator[StreamItem, None, None]:
        """
        Returns generator of track uploaded by given user and
        reposts by this user
        """
        return self._requests["user_stream"](self, user_id=user_id, **kwargs)

    def get_user_tracks(self, user_id: int, **kwargs) -> Generator[BasicTrack, None, None]:
        """
        Get tracks uploaded by this user
        """
        return self._requests["user_tracks"](self, user_id=user_id, **kwargs)

    def get_user_popular_tracks(self, user_id: int, **kwargs) -> Generator[BasicTrack, None, None]:
        """
        Get popular tracks uploaded by this user
        """
        return self._requests["user_toptracks"](self, user_id=user_id, **kwargs)

    def get_user_albums(self, user_id: int, **kwargs) -> Generator[BasicAlbumPlaylist, None, None]:
        """
        Get albums uploaded by this user
        """
        return self._requests["user_albums"](self, user_id=user_id, **kwargs)

    def get_user_playlists(self, user_id: int, **kwargs) -> Generator[BasicAlbumPlaylist, None, None]:
        """
        Get playlists uploaded by this user
        """
        return self._requests["user_playlists"](self, user_id=user_id, **kwargs)

    def get_user_links(self, user_urn: str, **kwargs) -> List[WebProfile]:
        """
        Get links in this user's description
        """
        return self._requests["user_web_profiles"](self, user_urn=user_urn, **kwargs)


__all__ = ["SoundCloud"]
