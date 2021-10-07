import string
from dataclasses import dataclass
from typing import Generator, Optional, TypeVar, Union

from requests import HTTPError

from .request import CollectionRequest, ListRequest, Request
from .resource.comment import BasicComment, Comment
from .resource.conversation import Conversation
from .resource.download import OriginalDownload
from .resource.like import PlaylistLike, TrackLike
from .resource.message import Message
from .resource.playlist import AlbumPlaylist, BasicAlbumPlaylist
from .resource.stream import (PlaylistStreamItem, PlaylistStreamRepostItem,
                              TrackStreamItem, TrackStreamRepostItem)
from .resource.track import BasicTrack, Track
from .resource.user import BasicUser, User
from .resource.web_profile import WebProfile, WebProfileUsername

T = TypeVar("T")
StreamItem = Union[TrackStreamItem, PlaylistStreamItem, TrackStreamRepostItem, PlaylistStreamRepostItem]
RepostItem = Union[TrackStreamRepostItem, PlaylistStreamRepostItem]
SearchItem = Union[User, Track, AlbumPlaylist]
        
class SoundCloud:
    
    def __init__(self, client_id: str, auth_token: str = None) -> None:
        self.client_id = client_id
        self.auth_token = None
        self.authorization = None
        self.set_auth_token(auth_token)
        
        self.requests: dict[str, Request] = {
            "me":                         Request[User](self, "/me", User),
            "me_stream":                  CollectionRequest[StreamItem](self, "/stream", StreamItem),
            "resolve":                    Request[SearchItem](self, "/resolve", SearchItem),
            "search":                     CollectionRequest[SearchItem](self, "/search", SearchItem),
            "search_albums":              CollectionRequest[AlbumPlaylist](self, "/search/albums", AlbumPlaylist), # ?filter.genre_or_tag
            "search_playlists":           CollectionRequest[AlbumPlaylist](self, "/search/playlists_without_albums", AlbumPlaylist),
            "search_tracks":              CollectionRequest[Track](self, "/search/tracks", Track), #?filter.created_at&filter.duration&filter.license
            "search_users":               CollectionRequest[User](self, "/search/users", User), #?filter.place
            "tag_recent_tracks":          CollectionRequest[Track](self, "/recent-tracks/{tag}", Track),
            "playlist":                   Request[BasicAlbumPlaylist](self, "/playlists/{playlist_id}", BasicAlbumPlaylist),
            "playlist_likers":            CollectionRequest[User](self, "/playlists/{playlist_id}/likers", User),
            "playlist_reposters":         CollectionRequest[User](self, "/playlists/{playlist_id}/reposters", User),
            "track":                      Request[BasicTrack](self, "/tracks/{track_id}", BasicTrack),
            "track_albums":               CollectionRequest[BasicAlbumPlaylist](self, "/tracks/{track_id}/albums", BasicAlbumPlaylist), # (can be representation=mini)
            "track_playlists":            CollectionRequest[BasicAlbumPlaylist](self, "/tracks/{track_id}/playlists_without_albums", BasicAlbumPlaylist), # (can be representation=mini)
            "track_comments":             CollectionRequest[BasicComment](self, "/tracks/{track_id}/comments", BasicComment),
            "track_likers":               CollectionRequest[User](self, "/tracks/{track_id}/likers", User),
            "track_reposters":            CollectionRequest[User](self, "/tracks/{track_id}/reposters", User),
            "track_original_download":    Request[OriginalDownload](self, "/tracks/{track_id}/download", OriginalDownload),
            "user":                       Request[User](self, "/users/{user_id}", User),
            "user_comments":              CollectionRequest[Comment](self, "/users/{user_id}/comments", Comment),
            "user_conversation_messages": CollectionRequest[Message](self, "/users/{user_id}/conversations/{conversation_id}/messages", Message),
            "user_conversations":         CollectionRequest[Conversation](self, "/users/{user_id}/conversations", Conversation),
            "user_conversations_unread":  CollectionRequest[Conversation](self, "/users/{user_id}/conversations/unread", Conversation),
            "user_featured_profiles":     CollectionRequest[User](self, "/users/{user_id}/featured-profiles", User),
            "user_followers":             CollectionRequest[User](self, "/users/{user_id}/followers", User),
            "user_followings":            CollectionRequest[User](self, "/users/{user_id}/followings", User),
            "user_likes":                 CollectionRequest[Union[TrackLike, PlaylistLike]](self, "/users/{user_id}/likes", Union[TrackLike, PlaylistLike]),
            "user_related_artists":       CollectionRequest[User](self, "/users/{user_id}/relatedartists", User),
            "user_reposts":               CollectionRequest[RepostItem](self, "/stream/users/{user_id}/reposts", RepostItem),
            "user_stream":                CollectionRequest[StreamItem](self, "/stream/users/{user_id}", StreamItem),
            "user_tracks":                CollectionRequest[BasicTrack](self, "/users/{user_id}/tracks", BasicTrack),
            "user_toptracks":             CollectionRequest[BasicTrack](self, "/users/{user_id}/toptracks", BasicTrack),
            "user_albums":                CollectionRequest[BasicAlbumPlaylist](self, "/users/{user_id}/albums", BasicAlbumPlaylist), # (can be representation=mini)
            "user_playlists":             CollectionRequest[BasicAlbumPlaylist](self, "/users/{user_id}/playlists_without_albums", BasicAlbumPlaylist), # (can be representation=mini)
            "user_web_profiles":          ListRequest[Union[WebProfile, WebProfileUsername]](self, "/users/{user_urn}/web-profiles", Union[WebProfile, WebProfileUsername])
        }
    
    def set_auth_token(self, auth_token: str) -> None:
        if auth_token is not None:
            if auth_token.startswith("OAuth"):
                auth_token = auth_token.split()[-1]
            self.auth_token = auth_token
            self.authorization = f"OAuth {auth_token}" if auth_token else None
    
    def is_client_id_valid(self) -> bool:
        """
        Checks if current client_id is valid
        """
        try:
            next(
                self.requests["tag_recent_tracks"](tag="electronic", limit="1", use_auth=False)
            )
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
            self.requests["me"](auth_token=self.auth_token)
            return True
        except HTTPError as err:
            if err.response.status_code == 401:
                return False
            else:
                raise
    
    def get_me(self) -> User:
        """
        Gets the user associated with client's auth token
        """
        return self.requests["me"]()
    
    def get_my_stream(self, **kwargs) -> Generator[StreamItem, None, None]:
        """
        Returns the stream of recent uploads/reposts
        for the client's auth token
        """
        return self.requests["me_stream"](**kwargs)
        
    def resolve(self, url: str) -> Optional[SearchItem]:
        """
        Returns the resource at the given URL if it
        exists, otherwise return None
        """
        return self.requests["resolve"](url=url)
    
    def search(self, query: str, **kwargs) -> Generator[SearchItem, None, None]:
        """
        Search for users, tracks, and playlists
        """
        return self.requests["search"](q=query, **kwargs)
        
    def search_albums(self, query: str, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Search for albums (not playlists)
        """
        return self.requests["search_albums"](q=query, **kwargs)
        
    def search_playlists(self, query: str, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Search for playlists
        """
        return self.requests["search_playlists"](q=query, **kwargs)
        
    def search_tracks(self, query: str, **kwargs) -> Generator[Track, None, None]:
        """
        Search for tracks
        """
        return self.requests["search_tracks"](q=query, **kwargs)
        
    def search_users(self, query: str, **kwargs) -> Generator[User, None, None]:
        """
        Search for users
        """
        return self.requests["search_users"](q=query, **kwargs)
        
    def get_tag_tracks_recent(self, tag: str, **kwargs) -> Generator[Track, None, None]:
        """
        Get most recent tracks for this tag
        """
        return self.requests["tag_recent_tracks"](tag=tag, **kwargs)
        
    def get_playlist(self, playlist_id: int) -> Optional[BasicAlbumPlaylist]:
        """
        Returns the playlist with the given playlist_id.
        If the ID is invalid, return None
        """
        return self.requests["playlist"](playlist_id=playlist_id)
        
    def get_playlist_likers(self, playlist_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get people who liked this playlist
        """
        return self.requests["playlist_likers"](playlist_id=playlist_id, **kwargs)
        
    def get_playlist_reposters(self, playlist_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get people who reposted this playlist
        """
        return self.requests["playlist_reposters"](playlist_id=playlist_id, **kwargs)
    
    def get_track(self, track_id: int) -> Optional[BasicTrack]:
        """
        Returns the track with the given track_id.
        If the ID is invalid, return None
        """
        return self.requests["track"](track_id=track_id)
    
    def get_track_albums(self, track_id: int, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Get albums that this track is in
        """
        return self.requests["track_albums"](track_id=track_id, **kwargs)
        
    def get_track_playlists(self, track_id: int, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Get playlists that this track is in
        """
        return self.requests["track_playlists"](track_id=track_id, **kwargs)
        
    def get_track_comments(self, track_id: int, threaded: int = 0, filter_replies: int = 1, **kwargs) -> Generator[BasicComment, None, None]:
        """
        Get comments on this track
        """
        return self.requests["track_comments"](track_id=track_id, 
                                               threaded=threaded,
                                               filter_replies=filter_replies,
                                               **kwargs)
        
    def get_track_likers(self, track_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get users who liked this track
        """
        return self.requests["track_likers"](track_id=track_id, **kwargs)
        
    def get_track_reposters(self, track_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get users who reposted this track
        """
        return self.requests["track_reposters"](track_id=track_id, **kwargs)
        
    def get_track_original_download(self, track_id: int) -> Optional[str]:
        """
        Get track download
        """
        download = self.requests["track_original_download"](track_id=track_id)
        if download is None:
            return None
        else:
            return download.redirectUri
            
    def get_user(self, user_id: int) -> Optional[User]:
        """
        Returns the user with the given user_id.
        If the ID is invalid, return None
        """
        return self.requests["user"](user_id=user_id)
    
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
        return self.requests["user_comments"](user_id=user_id, **kwargs)
    
    def get_conversation_messages(self, user_id: int, conversation_id: int, **kwargs) -> Generator[Message, None, None]:
        """
        Get messages in this conversation
        """
        return self.requests["user_conversation_messages"](user_id=user_id,
                                                           conversation_id=conversation_id,
                                                           **kwargs)
        
    def get_conversations(self, user_id: int, **kwargs) -> Generator[Conversation, None, None]:
        """
        Get conversations including this user
        """
        return self.requests["user_conversations"](user_id=user_id, **kwargs)
    
    def get_unread_conversations(self, user_id: int, **kwargs) -> Generator[Conversation, None, None]:
        """
        Get conversations unread by this user
        """
        return self.requests["user_conversations_unread"](user_id=user_id, **kwargs)
        
    def get_user_featured_profiles(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get profiles featured by this user
        """
        return self.requests["user_featured_profiles"](user_id=user_id, **kwargs)

    def get_user_followers(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get user's followers
        """
        return self.requests["user_followers"](user_id=user_id, **kwargs)

    def get_user_following(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get users this user is following
        """
        return self.requests["user_followings"](user_id=user_id, **kwargs)
        
    def get_user_likes(self, user_id: int, **kwargs) -> Generator[Union[TrackLike, PlaylistLike], None, None]:
        """
        Get likes by this user
        """
        return self.requests["user_likes"](user_id=user_id, **kwargs)
        
    def get_user_related_artists(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get artists related to this user
        """
        return self.requests["user_related_artists"](user_id=user_id, **kwargs)
        
    def get_user_reposts(self, user_id: int, **kwargs) -> Generator[RepostItem, None, None]:
        """
        Get reposts by this user
        """
        return self.requests["user_reposts"](user_id=user_id, **kwargs)
        
    def get_user_stream(self, user_id: int, **kwargs) -> Generator[StreamItem, None, None]:
        """
        Returns generator of track uploaded by given user and
        reposts by this user
        """
        return self.requests["user_stream"](user_id=user_id, **kwargs)
    
    def get_user_tracks(self, user_id: int, **kwargs) -> Generator[BasicTrack, None, None]:
        """
        Get tracks uploaded by this user
        """
        return self.requests["user_tracks"](user_id=user_id, **kwargs)
    
    def get_user_popular_tracks(self, user_id: int, **kwargs) -> Generator[BasicTrack, None, None]:
        """
        Get popular tracks uploaded by this user
        """
        return self.requests["user_toptracks"](user_id=user_id, **kwargs)
        
    def get_user_albums(self, user_id: int, **kwargs) -> Generator[BasicAlbumPlaylist, None, None]:
        """
        Get albums uploaded by this user
        """
        return self.requests["user_albums"](user_id=user_id, **kwargs)
        
    def get_user_playlists(self, user_id: int, **kwargs) -> Generator[BasicAlbumPlaylist, None, None]:
        """
        Get playlists uploaded by this user
        """
        return self.requests["user_playlists"](user_id=user_id, **kwargs)
    
    def get_user_links(self, user_urn: str, **kwargs) -> list[Union[WebProfile, WebProfileUsername]]:
        """
        Get links in this user's description
        """
        return self.requests["user_web_profiles"](user_urn=user_urn, **kwargs)
