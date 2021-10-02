from dataclasses import dataclass
from typing import Generator, Optional, TypeVar, Union, get_origin, get_args
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from requests import HTTPError

from .resource.comment import BasicComment, Comment
from .resource.conversation import Conversation
from .resource.like import TrackLike, PlaylistLike
from .resource.message import Message
from .resource.playlist import BasicAlbumPlaylist, AlbumPlaylist
from .resource.stream import TrackStreamItem, PlaylistStreamItem, TrackStreamRepostItem, PlaylistStreamRepostItem
from .resource.track import BasicTrack, Track
from .resource.user import BasicUser, User
from .resource.web_profile import WebProfile

T = TypeVar("T")

@dataclass
class Request:
    
    base = "https://api-v2.soundcloud.com"
    
    format_url: str
    return_type: type
    
    def new(self, *args, **kwargs):
        return (
            self.base + self.format_url.format(*args, **kwargs),
            self.return_type
        )
        
    def __iter__(self):
        return iter((self.format_url, self.return_type))

class SoundCloud:
    
    requests: dict[str, Request] = {
        "me":                         Request("/me", User),
        "me_stream":                  Request("/stream", Union[TrackStreamItem, PlaylistStreamItem, TrackStreamRepostItem, PlaylistStreamRepostItem]),
        "resolve":                    Request("/resolve", Union[User, Track, AlbumPlaylist]),
        "search":                     Request("/search", Union[User, Track, AlbumPlaylist]),
        "search_albums":              Request("/search/albums", AlbumPlaylist), # ?filter.genre_or_tag
        "search_playlists":           Request("/search/playlists_without_albums", AlbumPlaylist),
        "search_tracks":              Request("/search/tracks", Track), #?filter.created_at&filter.duration&filter.license
        "search_users":               Request("/search/users", User), #?filter.place
        "tag_recent_tracks":          Request("/recent-tracks/{tag}", Track),
        "playlist":                   Request("/playlists/{playlist_id}", BasicAlbumPlaylist),
        "playlist_likers":            Request("/playlists/{playlist_id}/likers", User),
        "playlist_reposters":         Request("/playlists/{playlist_id}/reposters", User),
        "track":                      Request("/tracks/{track_id}", BasicTrack),
        "track_albums":               Request("/tracks/{track_id}/albums", BasicAlbumPlaylist), # (can be representation=mini)
        "track_playlists":            Request("/tracks/{track_id}/playlists_without_albums", BasicAlbumPlaylist), # (can be representation=mini)
        "track_comments":             Request("/tracks/{track_id}/comments", BasicComment),
        "track_likers":               Request("/tracks/{track_id}/likers", User),
        "track_reposters":            Request("/tracks/{track_id}/reposters", User),
        "user":                       Request("/users/{user_id}", User),
        "user_comments":              Request("/users/{user_id}/comments", Comment),
        "user_conversation_messages": Request("/users/{user_id}/conversations/{conversation_id}/messages", Message),
        "user_conversations":         Request("/users/{user_id}/conversations", Conversation),
        "user_conversations_unread":  Request("/users/{user_id}/conversations/unread", Conversation),
        "user_featured_profiles":     Request("/users/{user_id}/featured-profiles", User),
        "user_followers":             Request("/users/{user_id}/followers", User),
        "user_followings":            Request("/users/{user_id}/followings", User),
        "user_likes":                 Request("/users/{user_id}/likes", Union[TrackLike, PlaylistLike]),
        "user_related_artists":       Request("/users/{user_id}/relatedartists", User),
        "user_reposts":               Request("/stream/users/{user_id}/reposts", Union[TrackStreamRepostItem, PlaylistStreamRepostItem]),
        "user_stream":                Request("/stream/users/{user_id}", Union[TrackStreamItem, PlaylistStreamItem, TrackStreamRepostItem, PlaylistStreamRepostItem]),
        "user_tracks":                Request("/users/{user_id}/tracks", BasicTrack),
        "user_toptracks":             Request("/users/{user_id}/toptracks", BasicTrack),
        "user_albums":                Request("/users/{user_id}/albums", BasicAlbumPlaylist), # (can be representation=mini)
        "user_playlists":             Request("/users/{user_id}/playlists_without_albums", BasicAlbumPlaylist), # (can be representation=mini)
        "user_web_profiles":          Request("/users/{user_urn}/web-profiles", WebProfile),
    }
    
    def __init__(self, client_id: str, auth_token: str = None) -> None:
        self.client_id = client_id
        self.auth_token = None
        self.authorization = None
        self.set_auth_token(auth_token)
    
    def set_auth_token(self, auth_token: str) -> None:
        if auth_token is not None:
            if auth_token.startswith("OAuth"):
                auth_token = auth_token.split()[-1]
            self.auth_token = auth_token
            self.authorization = f"OAuth {auth_token}" if auth_token else None
        
    def resource(self, resource_url: str, resource_type: T, use_auth: bool = True, **kwargs) -> Optional[T]:
        """
        Requests the resource at the given url with
        parameters given by kwargs. Converts the resource
        to type resource_type and returns it. If the
        resource does not exist, returns None
        """
        union = get_origin(resource_type) is Union
        params = kwargs
        params["client_id"] = self.client_id
        headers = {}
        if use_auth and self.authorization is not None:
            headers["Authorization"] = self.authorization
        with requests.get(resource_url, params=params, headers=headers) as r:
            if r.status_code in (400, 404, 500):
                return None
            r.raise_for_status()
            if union:
                for t in get_args(resource_type):
                    try:
                        return t.from_dict(r.json())
                    except:
                        pass
            else:
                return resource_type.from_dict(r.json())
            raise ValueError(f"Could not convert {r.json()} to type {resource_type}")
    
    def collection(self, url: str, resource_type: T, offset: str = None, limit: str = None, use_auth: bool = True, **kwargs) -> Generator[T, None, None]:
        """
        Yields resources from the given url with
        parameters given by kwargs. Converts the resources
        to type resource_type before yielding
        """
        union = get_origin(resource_type) is Union
        params = kwargs
        params["client_id"] = self.client_id
        headers = {}
        if use_auth and self.authorization is not None:
            headers["Authorization"] = self.authorization
        while url:
            with requests.get(url, params=params, headers=headers) as r:
                if r.status_code in (400, 404, 500):
                    return
                r.raise_for_status()
                data = r.json()
                for resource in data["collection"]:
                    if union:
                        converted = False
                        for t in get_args(resource_type):
                            try:
                                yield t.from_dict(resource)
                                converted = True
                                break
                            except:
                                pass
                        if not converted:
                            raise ValueError(f"Could not convert resource to type {resource_type}")
                    else:
                        yield resource_type.from_dict(resource)
                url = data.get("next_href", None)
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                params["client_id"] = self.client_id # next_href doesn't contain client_id
                url = urljoin(url, parsed.path)
    
    def is_client_id_valid(self) -> bool:
        """
        Checks if current client_id is valid
        """
        try:
            next(self.collection(
                *self.requests["tag_recent_tracks"].new(tag="electronic"), limit="1", use_auth=False)
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
            self.resource(*self.requests["me"].new(auth_token=self.auth_token))
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
        return self.resource(
            *self.requests["me"].new()
        )
    
    def get_my_stream(self, **kwargs) -> Generator[Union[TrackStreamItem, PlaylistStreamItem, TrackStreamRepostItem, PlaylistStreamRepostItem], None, None]:
        """
        Returns the stream of recent uploads/reposts
        for the client's auth token
        """
        return self.collection(
            *self.requests["me_stream"].new(), **kwargs
        )
        
    def resolve(self, url: str) -> Union[AlbumPlaylist, User, Track, None]:
        """
        Returns the resource at the given URL if it
        exists, otherwise return None
        """
        return self.resource(
            *self.requests["resolve"].new(), url=url
        )
    
    def search(self, query: str, **kwargs) -> Generator[Union[User, Track, AlbumPlaylist], None, None]:
        """
        Search for users, tracks, and playlists
        """
        return self.collection(
            *self.requests["search"].new(), q=query, **kwargs
        )
        
    def search_albums(self, query: str, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Search for albums (not playlists)
        """
        return self.collection(
            *self.requests["search_albums"].new(), q=query, **kwargs
        )
        
    def search_playlists(self, query: str, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Search for playlists
        """
        return self.collection(
            *self.requests["search_playlists"].new(), q=query, **kwargs
        )
        
    def search_tracks(self, query: str, **kwargs) -> Generator[Track, None, None]:
        """
        Search for tracks
        """
        return self.collection(
            *self.requests["search_tracks"].new(), q=query, **kwargs
        )
        
    def search_users(self, query: str, **kwargs) -> Generator[User, None, None]:
        """
        Search for users
        """
        return self.collection(
            *self.requests["search_users"].new(), q=query, **kwargs
        )
        
    def get_tag_tracks_recent(self, tag: str, **kwargs) -> Generator[Track, None, None]:
        """
        Get most recent tracks for this tag
        """
        return self.collection(
            *self.requests["tag_recent_tracks"].new(tag=tag), **kwargs
        )
        
    def get_playlist(self, playlist_id: int) -> Optional[BasicAlbumPlaylist]:
        """
        Returns the playlist with the given playlist_id.
        If the ID is invalid, return None
        """
        return self.resource(
            *self.requests["playlist"].new(playlist_id=playlist_id)
        )
        
    def get_playlist_likers(self, playlist_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get people who liked this playlist
        """
        return self.collection(
            *self.requests["playlist_likers"].new(playlist_id=playlist_id),
            **kwargs
        )
        
    def get_playlist_reposters(self, playlist_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get people who reposted this playlist
        """
        return self.collection(
            *self.requests["playlist_reposters"].new(playlist_id=playlist_id),
            **kwargs
        )
    
    def get_track(self, track_id: int) -> Optional[BasicTrack]:
        """
        Returns the track with the given track_id.
        If the ID is invalid, return None
        """
        return self.resource(
            *self.requests["track"].new(track_id=track_id)
        )
    
    def get_track_albums(self, track_id: int, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Get albums that this track is in
        """
        return self.collection(
            *self.requests["track_albums"].new(track_id=track_id),
            **kwargs
        )
        
    def get_track_playlists(self, track_id: int, **kwargs) -> Generator[AlbumPlaylist, None, None]:
        """
        Get playlists that this track is in
        """
        return self.collection(
            *self.requests["track_playlists"].new(track_id=track_id),
            **kwargs
        )
        
    def get_track_comments(self, track_id: int, threaded: int = 0, filter_replies: int = 1, **kwargs) -> Generator[BasicComment, None, None]:
        """
        Get comments on this track
        """
        return self.collection(
            *self.requests["track_comments"].new(track_id=track_id),
            threaded=threaded,
            filter_replies=filter_replies,
            **kwargs
        )
        
    def get_track_likers(self, track_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get users who liked this track
        """
        return self.collection(
            *self.requests["track_likers"].new(track_id=track_id),
            **kwargs
        )
        
    def get_track_reposters(self, track_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get users who reposted this track
        """
        return self.collection(
            *self.requests["track_reposters"].new(track_id=track_id), **kwargs
        )
            
    def get_user(self, user_id: int) -> Optional[User]:
        """
        Returns the user with the given user_id.
        If the ID is invalid, return None
        """
        return self.resource(
            *self.requests["user"].new(user_id=user_id)
        )
    
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
        return self.collection(
            *self.requests["user_comments"].new(user_id=user_id), **kwargs
        )
    
    def get_conversation_messages(self, user_id: int, conversation_id: int, **kwargs) -> Generator[Message, None, None]:
        """
        Get messages in this conversation
        """
        return self.collection(
            *self.requests["user_conversation_messages"].new(user_id=user_id,
                                                             conversation_id=conversation_id),
            **kwargs
        )
        
    def get_conversations(self, user_id: int, **kwargs) -> Generator[Conversation, None, None]:
        """
        Get conversations including this user
        """
        return self.collection(
            *self.requests["user_conversations"].new(user_id=user_id),
            **kwargs
        )
    
    def get_unread_conversations(self, user_id: int, **kwargs) -> Generator[Conversation, None, None]:
        """
        Get conversations unread by this user
        """
        return self.collection(
            *self.requests["user_conversations_unread"].new(user_id=user_id),
            **kwargs
        )
        
    def get_user_featured_profiles(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get profiles featured by this user
        """
        return self.collection(
            *self.requests["user_featured_profiles"].new(user_id=user_id),
            **kwargs
        )

    def get_user_followers(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get user's followers
        """
        return self.collection(
            *self.requests["user_followers"].new(user_id=user_id),
            **kwargs
        )

    def get_user_following(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get users this user is following
        """
        return self.collection(
            *self.requests["user_followings"].new(user_id=user_id),
            **kwargs
        )
        
    def get_user_likes(self, user_id: int, **kwargs) -> Generator[Union[TrackLike, PlaylistLike], None, None]:
        """
        Get likes by this user
        """
        return self.collection(
            *self.requests["user_likes"].new(user_id=user_id),
            **kwargs
        )
        
    def get_user_related_artists(self, user_id: int, **kwargs) -> Generator[User, None, None]:
        """
        Get artists related to this user
        """
        return self.collection(
            *self.requests["user_related_artists"].new(user_id=user_id),
            **kwargs
        )
        
    def get_user_reposts(self, user_id: int, **kwargs) -> Generator[Union[TrackStreamRepostItem, PlaylistStreamRepostItem], None, None]:
        """
        Get reposts by this user
        """
        return self.collection(
            *self.requests["user_reposts"].new(user_id=user_id),
            **kwargs
        )
        
    def get_user_stream(self, user_id: int, **kwargs) -> Generator[Union[TrackStreamItem, PlaylistStreamItem, TrackStreamRepostItem, PlaylistStreamRepostItem], None, None]:
        """
        Returns generator of track uploaded by given user and
        reposts by this user
        """
        return self.collection(
            *self.requests["user_stream"].new(user_id=user_id), **kwargs
        )
    
    def get_user_tracks(self, user_id: int, **kwargs) -> Generator[BasicTrack, None, None]:
        """
        Get tracks uploaded by this user
        """
        return self.collection(
            *self.requests["user_tracks"].new(user_id=user_id), **kwargs
        )
    
    def get_user_popular_tracks(self, user_id: int, **kwargs) -> Generator[BasicTrack, None, None]:
        """
        Get popular tracks uploaded by this user
        """
        return self.collection(
            *self.requests["user_toptracks"].new(user_id=user_id), **kwargs
        )
        
    def get_user_albums(self, user_id: int, **kwargs) -> Generator[BasicAlbumPlaylist, None, None]:
        """
        Get albums uploaded by this user
        """
        return self.collection(
            *self.requests["user_albums"].new(user_id=user_id), **kwargs
        )
        
    def get_user_playlists(self, user_id: int, **kwargs) -> Generator[BasicAlbumPlaylist, None, None]:
        """
        Get playlists uploaded by this user
        """
        return self.collection(
            *self.requests["user_playlists"].new(user_id=user_id), **kwargs
        )
    
    def get_user_links(self, user_urn: str, **kwargs) -> Generator[WebProfile, None, None]:
        """
        Get links in this user's description
        """
        return self.collection(
            *self.requests["user_web_profiles"].new(user_urn=user_urn), **kwargs
        )