import itertools
import sys
import re
from typing import Dict, Generator, List, Optional

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal

import requests
from requests import HTTPError

from soundcloud.exceptions import ClientIDGenerationError
from soundcloud.requests import (
    MeHistoryRequest,
    MeRequest,
    MeStreamRequest,
    PlaylistLikersRequest,
    PlaylistRepostersRequest,
    PlaylistRequest,
    PostPlaylistRequest,
    DeletePlaylistRequest,
    ResolveRequest,
    SearchAlbumsRequest,
    SearchPlaylistsRequest,
    SearchRequest,
    SearchTracksRequest,
    SearchUsersRequest,
    TagRecentTracksRequest,
    TrackAlbumsRequest,
    TrackCommentsRequest,
    TrackLikersRequest,
    TrackOriginalDownloadRequest,
    TrackPlaylistsRequest,
    TrackRelatedRequest,
    TrackRepostersRequest,
    TrackRequest,
    TracksRequest,
    UserAlbumsRequest,
    UserCommentsRequest,
    UserConversationMessagesRequest,
    UserConversationsRequest,
    UserConversationsUnreadRequest,
    UserEmailsRequest,
    UserFeaturedProfilesRequest,
    UserFollowersRequest,
    UserFollowingsRequest,
    UserInteractionsQueryParams,
    UserInteractionsRequest,
    UserLikesRequest,
    UserPlaylistsRequest,
    UserRelatedArtistsRequest,
    UserRepostsRequest,
    UserRequest,
    UserStreamRequest,
    UserToptracksRequest,
    UserTracksRequest,
    UserWebProfilesRequest,
)
from soundcloud.resource.graphql import CommentWithInteractions
from soundcloud.resource.history import HistoryItem

from .resource.aliases import Like, RepostItem, SearchItem, StreamItem
from .resource.comment import BasicComment, Comment
from .resource.conversation import Conversation
from .resource.message import Message
from .resource.playlist import AlbumPlaylist, BasicAlbumPlaylist
from .resource.track import BasicTrack, Track
from .resource.user import User, UserEmail
from .resource.web_profile import WebProfile
from .resource.response import NoContentResponse


class SoundCloud:
    """
    SoundCloud v2 API client
    """

    _DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"
    )
    _ASSETS_SCRIPTS_REGEX = re.compile(
        r"src=\"(https:\/\/a-v2\.sndcdn\.com/assets/0-[^\.]+\.js)\""
    )
    _CLIENT_ID_REGEX = re.compile(r"client_id:\"([^\"]+)\"")
    client_id: str
    """SoundCloud client ID. Needed for all requests."""
    _user_agent: str
    _auth_token: Optional[str]
    _authorization: Optional[str]

    def __init__(
        self,
        client_id: Optional[str] = None,
        auth_token: Optional[str] = None,
        user_agent: str = _DEFAULT_USER_AGENT,
    ) -> None:
        if not client_id:
            client_id = self.generate_client_id()

        self.client_id = client_id
        self._user_agent = user_agent
        self._auth_token = None
        self._authorization = None
        self.auth_token = auth_token

    @property
    def auth_token(self) -> Optional[str]:
        """SoundCloud auth token. Only needed for some requests."""
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

    @classmethod
    def generate_client_id(cls) -> str:
        """Generates a SoundCloud client ID

        Raises:
            ClientIDGenerationError: Client ID could not be generated.

        Returns:
            str: Valid client ID
        """
        r = requests.get("https://soundcloud.com")
        r.raise_for_status()
        matches = cls._ASSETS_SCRIPTS_REGEX.findall(r.text)
        if not matches:
            raise ClientIDGenerationError("No asset scripts found")
        url = matches[0]
        r = requests.get(url)
        r.raise_for_status()
        client_id = cls._CLIENT_ID_REGEX.search(r.text)
        if not client_id:
            raise ClientIDGenerationError(f"Could not find client_id in script '{url}'")
        return client_id.group(1)

    def is_client_id_valid(self) -> bool:
        """
        Checks if current client_id is valid
        """
        try:
            TrackRequest(self, track_id=1032303631, use_auth=False)
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
            MeRequest(self)
            return True
        except HTTPError as err:
            if err.response.status_code == 401:
                return False
            else:
                raise

    def get_me(self) -> Optional[User]:
        """
        Gets the user associated with client's auth token
        """
        return MeRequest(self)

    def get_my_history(self, **kwargs) -> Generator[HistoryItem, None, None]:
        """
        Returns the stream of recently listened tracks
        for the client's auth token
        """
        return MeHistoryRequest(self, **kwargs)

    def get_my_stream(self, **kwargs) -> Generator[StreamItem, None, None]:
        """
        Returns the stream of recent uploads/reposts
        for the client's auth token
        """
        return MeStreamRequest(self, **kwargs)

    def resolve(self, url: str) -> Optional[SearchItem]:
        """
        Returns the resource at the given URL if it
        exists, otherwise return None
        """
        return ResolveRequest(self, url=url)

    def search(self, query: str, **kwargs) -> Generator[SearchItem, None, None]:
        """
        Search for users, tracks, and playlists
        """
        return SearchRequest(self, q=query, **kwargs)

    def search_albums(
        self, query: str, **kwargs
    ) -> Generator[AlbumPlaylist, None, None]:
        """
        Search for albums (not playlists)
        """
        return SearchAlbumsRequest(self, q=query, **kwargs)

    def search_playlists(
        self, query: str, **kwargs
    ) -> Generator[AlbumPlaylist, None, None]:
        """
        Search for playlists
        """
        return SearchPlaylistsRequest(self, q=query, **kwargs)

    def search_tracks(self, query: str, **kwargs) -> Generator[Track, None, None]:
        """
        Search for tracks
        """
        return SearchTracksRequest(self, q=query, **kwargs)

    def search_users(self, query: str, **kwargs) -> Generator[User, None, None]:
        """
        Search for users
        """
        return SearchUsersRequest(self, q=query, **kwargs)

    def get_tag_tracks_recent(self, tag: str, **kwargs) -> Generator[Track, None, None]:
        """
        Get most recent tracks for this tag
        """
        return TagRecentTracksRequest(self, tag=tag, **kwargs)

    def get_playlist(self, playlist_id: int) -> Optional[BasicAlbumPlaylist]:
        """
        Returns the playlist with the given playlist_id.
        If the ID is invalid, return None
        """
        return PlaylistRequest(self, playlist_id=playlist_id)

    def post_playlist(
        self, sharing: Literal["private", "public"], title: str, tracks: List[int]
    ) -> Optional[BasicAlbumPlaylist]:
        """
        Create a new playlist
        """
        body = {"playlist": {"sharing": sharing, "title": title, "tracks": tracks}}
        return PostPlaylistRequest(self, body=body)

    def delete_playlist(self, playlist_id: int) -> Optional[NoContentResponse]:
        """
        Delete a playlist
        """
        return DeletePlaylistRequest(self, playlist_id=playlist_id)

    def get_playlist_likers(
        self, playlist_id: int, **kwargs
    ) -> Generator[User, None, None]:
        """
        Get people who liked this playlist
        """
        return PlaylistLikersRequest(self, playlist_id=playlist_id, **kwargs)

    def get_playlist_reposters(
        self, playlist_id: int, **kwargs
    ) -> Generator[User, None, None]:
        """
        Get people who reposted this playlist
        """
        return PlaylistRepostersRequest(self, playlist_id=playlist_id, **kwargs)

    def get_track(self, track_id: int) -> Optional[BasicTrack]:
        """
        Returns the track with the given track_id.
        If the ID is invalid, return None
        """
        return TrackRequest(self, track_id=track_id)

    def get_tracks(
        self,
        track_ids: List[int],
        playlistId: Optional[int] = None,
        playlistSecretToken: Optional[str] = None,
        **kwargs,
    ) -> List[BasicTrack]:
        """
        Returns the tracks with the given track_ids.
        Can be used to get track info for hidden tracks in a hidden playlist.
        """
        if playlistId is not None:
            kwargs["playlistId"] = playlistId
        if playlistSecretToken is not None:
            kwargs["playlistSecretToken"] = playlistSecretToken
        return TracksRequest(
            self, ids=",".join([str(id) for id in track_ids]), **kwargs
        )

    def get_track_albums(
        self, track_id: int, **kwargs
    ) -> Generator[BasicAlbumPlaylist, None, None]:
        """
        Get albums that this track is in
        """
        return TrackAlbumsRequest(self, track_id=track_id, **kwargs)

    def get_track_playlists(
        self, track_id: int, **kwargs
    ) -> Generator[BasicAlbumPlaylist, None, None]:
        """
        Get playlists that this track is in
        """
        return TrackPlaylistsRequest(self, track_id=track_id, **kwargs)

    def get_track_comments(
        self, track_id: int, threaded: int = 0, **kwargs
    ) -> Generator[BasicComment, None, None]:
        """
        Get comments on this track
        """
        return TrackCommentsRequest(
            self, track_id=track_id, threaded=threaded, **kwargs
        )

    def get_track_comments_with_interactions(
        self, track_id: int, threaded: int = 0, **kwargs
    ) -> Generator[CommentWithInteractions, None, None]:
        """
        Get comments on this track with interaction data. Requires authentication.
        """
        track = self.get_track(track_id)
        if not track:
            return
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
            if not result:
                return
            comments_with_interactions = []
            for comment, user_interactions, creator_interactions in zip(
                chunk, result.user, result.creator
            ):
                assert user_interactions.interactionCounts is not None
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
                        likes=num_likes or 0,
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
        return TrackLikersRequest(self, track_id=track_id, **kwargs)

    def get_track_related(
        self, track_id: int, **kwargs
    ) -> Generator[BasicTrack, None, None]:
        """
        Get related tracks
        """
        return TrackRelatedRequest(self, track_id=track_id, **kwargs)

    def get_track_reposters(
        self, track_id: int, **kwargs
    ) -> Generator[User, None, None]:
        """
        Get users who reposted this track
        """
        return TrackRepostersRequest(self, track_id=track_id, **kwargs)

    def get_track_original_download(
        self, track_id: int, token: Optional[str] = None
    ) -> Optional[str]:
        """
        Get track original download link. If track is private,
        requires secret token to be provided (last part of secret URL).
        Requires authentication.
        """
        if token is not None:
            download = TrackOriginalDownloadRequest(
                self, track_id=track_id, secret_token=token
            )
        else:
            download = TrackOriginalDownloadRequest(self, track_id=track_id)
        if download is None:
            return None
        else:
            return download.redirectUri

    def get_user(self, user_id: int) -> Optional[User]:
        """
        Returns the user with the given user_id.
        If the ID is invalid, return None
        """
        return UserRequest(self, user_id=user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Returns the user with the given username.
        If the username is invalid, return None
        """
        resource = self.resolve(f"https://soundcloud.com/{username}")
        if resource and isinstance(resource, User):
            return resource
        else:
            return None

    def get_user_comments(
        self, user_id: int, **kwargs
    ) -> Generator[Comment, None, None]:
        """
        Get comments by this user
        """
        return UserCommentsRequest(self, user_id=user_id, **kwargs)

    def get_conversation_messages(
        self, user_id: int, conversation_id: int, **kwargs
    ) -> Generator[Message, None, None]:
        """
        Get messages in this conversation
        """
        return UserConversationMessagesRequest(
            self, user_id=user_id, conversation_id=conversation_id, **kwargs
        )

    def get_conversations(
        self, user_id: int, **kwargs
    ) -> Generator[Conversation, None, None]:
        """
        Get conversations including this user
        """
        return UserConversationsRequest(self, user_id=user_id, **kwargs)

    def get_unread_conversations(
        self, user_id: int, **kwargs
    ) -> Generator[Conversation, None, None]:
        """
        Get conversations unread by this user
        """
        return UserConversationsUnreadRequest(self, user_id=user_id, **kwargs)

    def get_user_emails(
        self, user_id: int, **kwargs
    ) -> Generator[UserEmail, None, None]:
        """
        Get user's email addresses. Requires authentication.
        """
        return UserEmailsRequest(self, user_id=user_id, **kwargs)

    def get_user_featured_profiles(
        self, user_id: int, **kwargs
    ) -> Generator[User, None, None]:
        """
        Get profiles featured by this user
        """
        return UserFeaturedProfilesRequest(self, user_id=user_id, **kwargs)

    def get_user_followers(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get user's followers
        """
        return UserFollowersRequest(self, user_id=user_id, **kwargs)

    def get_user_following(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get users this user is following
        """
        return UserFollowingsRequest(self, user_id=user_id, **kwargs)

    def get_user_likes(self, user_id: int, **kwargs) -> Generator[Like, None, None]:
        """
        Get likes by this user
        """
        return UserLikesRequest(self, user_id=user_id, **kwargs)

    def get_user_related_artists(
        self, user_id: int, **kwargs
    ) -> Generator[User, None, None]:
        """
        Get artists related to this user
        """
        return UserRelatedArtistsRequest(self, user_id=user_id, **kwargs)

    def get_user_reposts(
        self, user_id: int, **kwargs
    ) -> Generator[RepostItem, None, None]:
        """
        Get reposts by this user
        """
        return UserRepostsRequest(self, user_id=user_id, **kwargs)

    def get_user_stream(
        self, user_id: int, **kwargs
    ) -> Generator[StreamItem, None, None]:
        """
        Returns generator of track uploaded by given user and
        reposts by this user
        """
        return UserStreamRequest(self, user_id=user_id, **kwargs)

    def get_user_tracks(
        self, user_id: int, **kwargs
    ) -> Generator[BasicTrack, None, None]:
        """
        Get tracks uploaded by this user
        """
        return UserTracksRequest(self, user_id=user_id, **kwargs)

    def get_user_popular_tracks(
        self, user_id: int, **kwargs
    ) -> Generator[BasicTrack, None, None]:
        """
        Get popular tracks uploaded by this user
        """
        return UserToptracksRequest(self, user_id=user_id, **kwargs)

    def get_user_albums(
        self, user_id: int, **kwargs
    ) -> Generator[BasicAlbumPlaylist, None, None]:
        """
        Get albums uploaded by this user
        """
        return UserAlbumsRequest(self, user_id=user_id, **kwargs)

    def get_user_playlists(
        self, user_id: int, **kwargs
    ) -> Generator[BasicAlbumPlaylist, None, None]:
        """
        Get playlists uploaded by this user
        """
        return UserPlaylistsRequest(self, user_id=user_id, **kwargs)

    def get_user_links(self, user_urn: str, **kwargs) -> List[WebProfile]:
        """
        Get links in this user's description
        """
        return UserWebProfilesRequest(self, user_urn=user_urn, **kwargs)


__all__ = ["SoundCloud"]
