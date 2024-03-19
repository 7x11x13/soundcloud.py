import re
import string
from dataclasses import dataclass
from typing import Dict, Generator, Generic, List, Optional, TypeVar, Union

try:
    from typing import get_args, get_origin
except ImportError:
    # get_args and get_origin shim for version < 3.8
    def get_args(tp):
        return getattr(tp, "__args__", ())
    
    def get_origin(tp):
        return getattr(tp, "__origin__", None)
    
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from requests import HTTPError

from .resource.aliases import Like, RepostItem, SearchItem, StreamItem
from .resource.comment import BasicComment, Comment
from .resource.conversation import Conversation
from .resource.download import OriginalDownload
from .resource.like import PlaylistLike, TrackLike
from .resource.message import Message
from .resource.playlist import AlbumPlaylist, BasicAlbumPlaylist
from .resource.track import BasicTrack, Track
from .resource.user import User, UserStatus
from .resource.web_profile import WebProfile

T = TypeVar("T")


class ClientIDGenerationError(Exception):
    pass

        
class SoundCloud:
    
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"
    ASSETS_SCRIPTS_REGEX = re.compile(r"src=\"(https:\/\/a-v2\.sndcdn\.com/assets/[^\.]+\.js)\"")
    CLIENT_ID_REGEX = re.compile(r"client_id:\"([^\"]+)\"")
    
    def __init__(self, client_id: str = None, auth_token: str = None, user_agent: str = DEFAULT_USER_AGENT) -> None:
        
        if not client_id:
            client_id = self.generate_client_id()
        
        self.client_id = client_id
        self.auth_token = None
        self.authorization = None
        self.user_agent = user_agent
        self.set_auth_token(auth_token)
        
        self.requests: Dict[str, Request] = {
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
            "tracks":                     ListRequest[BasicTrack](self, "/tracks", BasicTrack),
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
            "user_likes":                 CollectionRequest[Like](self, "/users/{user_id}/likes", Like),
            "user_related_artists":       CollectionRequest[User](self, "/users/{user_id}/relatedartists", User),
            "user_reposts":               CollectionRequest[RepostItem](self, "/stream/users/{user_id}/reposts", RepostItem),
            "user_stream":                CollectionRequest[StreamItem](self, "/stream/users/{user_id}", StreamItem),
            "user_tracks":                CollectionRequest[BasicTrack](self, "/users/{user_id}/tracks", BasicTrack),
            "user_toptracks":             CollectionRequest[BasicTrack](self, "/users/{user_id}/toptracks", BasicTrack),
            "user_albums":                CollectionRequest[BasicAlbumPlaylist](self, "/users/{user_id}/albums", BasicAlbumPlaylist), # (can be representation=mini)
            "user_playlists":             CollectionRequest[BasicAlbumPlaylist](self, "/users/{user_id}/playlists_without_albums", BasicAlbumPlaylist), # (can be representation=mini)
            "user_web_profiles":          ListRequest[WebProfile](self, "/users/{user_urn}/web-profiles", WebProfile)
        }
    
    def set_auth_token(self, auth_token: str) -> None:
        if auth_token is not None:
            if auth_token.startswith("OAuth"):
                auth_token = auth_token.split()[-1]
            self.auth_token = auth_token
            self.authorization = f"OAuth {auth_token}" if auth_token else None
    
    def get_default_headers(self) -> Dict[str, str]:
        return {"User-Agent": self.user_agent}
    
    def generate_client_id(self) -> str:
        r = requests.get("https://soundcloud.com")
        r.raise_for_status()
        matches = self.ASSETS_SCRIPTS_REGEX.findall(r.text)
        if not matches:
            raise ClientIDGenerationError("No asset scripts found")
        url = matches[-1]
        r = requests.get(url)
        r.raise_for_status()
        client_id = self.CLIENT_ID_REGEX.search(r.text)
        if not client_id:
            raise ClientIDGenerationError(f"Could not find client_id in script '{url}'")
        return client_id.group(1)
    
    def is_client_id_valid(self) -> bool:
        """
        Checks if current client_id is valid
        """
        try:
            self.requests["track"](track_id=1032303631, use_auth=False)
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
            self.requests["me"]()
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
        Get most recent tracks for this tag. Might be obsolete?
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
    
    def get_tracks(self, track_ids: List[int], playlistId: int = None, playlistSecretToken: str = None, **kwargs) -> List[BasicTrack]:
        """
        Returns the tracks with the given track_ids.
        Can be used to get track info for hidden tracks in a hidden playlist.
        """
        if playlistId:
            kwargs["playlistId"] = playlistId
        if playlistSecretToken:
            kwargs["playlistSecretToken"] = playlistSecretToken
        return self.requests["tracks"](ids=",".join([str(id) for id in track_ids]), **kwargs)
    
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
        
    def get_track_original_download(self, track_id: int, token: str = None) -> Optional[str]:
        """
        Get track original download link. If track is private,
        requires secret token to be provided (last part of secret URL)
        """
        if token:
            download = self.requests["track_original_download"](track_id=track_id, secret_token=token)
        else:
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
        
    def get_user_likes(self, user_id: int, **kwargs) -> Generator[Like, None, None]:
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
    
    def get_user_links(self, user_urn: str, **kwargs) -> List[WebProfile]:
        """
        Get links in this user's description
        """
        return self.requests["user_web_profiles"](user_urn=user_urn, **kwargs)


@dataclass
class Request(Generic[T]):
    
    base = "https://api-v2.soundcloud.com"
    client: SoundCloud
    format_url: str
    return_type: T
    
    def format_url_and_remove_params(self, kwargs):
        format_args = {tup[1] for tup in string.Formatter().parse(self.format_url) if tup[1] is not None}
        args = {}
        for k in list(kwargs.keys()):
            if k in format_args:
                args[k] = kwargs.pop(k)     
        return self.base + self.format_url.format(**args)
    
    def convert_dict(self, d):
        union = get_origin(self.return_type) is Union
        if union:
            for t in get_args(self.return_type):
                try:
                    return t.from_dict(d)
                except:
                    pass
        else:
            return self.return_type.from_dict(d)
        raise ValueError(f"Could not convert {d} to type {self.return_type}")
    
    def __call__(self, use_auth=True, **kwargs) -> Optional[T]:
        """
        Requests the resource at the given url with
        parameters given by kwargs. Converts the resource
        to type T and returns it. If the
        resource does not exist, returns None
        """
        resource_url = self.format_url_and_remove_params(kwargs)
        params = kwargs
        params["client_id"] = self.client.client_id
        headers = self.client.get_default_headers()
        if use_auth and self.client.authorization is not None:
            headers["Authorization"] = self.client.authorization
        with requests.get(resource_url, params=params, headers=headers) as r:
            if r.status_code in (400, 404, 500):
                return None
            r.raise_for_status()
            return self.convert_dict(r.json())


@dataclass
class CollectionRequest(Request, Generic[T]):
    
    def __call__(self, use_auth=True, offset: str = None, limit: int = None, **kwargs) -> Generator[T, None, None]:
        """
        Yields resources from the given url with
        parameters given by kwargs. Converts the resources
        to type T before yielding
        """
        resource_url = self.format_url_and_remove_params(kwargs)
        params = kwargs
        params["client_id"] = self.client.client_id
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit
        headers = self.client.get_default_headers()
        if use_auth and self.client.authorization is not None:
            headers["Authorization"] = self.client.authorization
        while resource_url:
            with requests.get(resource_url, params=params, headers=headers) as r:
                if r.status_code in (400, 404, 500):
                    return
                r.raise_for_status()
                data = r.json()
                for resource in data["collection"]:
                    yield self.convert_dict(resource)
                resource_url = data.get("next_href", None)
                parsed = urlparse(resource_url)
                params = parse_qs(parsed.query)
                params["client_id"] = self.client.client_id # next_href doesn't contain client_id
                resource_url = urljoin(resource_url, parsed.path)
        
                
@dataclass
class ListRequest(Request, Generic[T]):
    """
    Requests the resource list at the given url with
    parameters given by kwargs. Converts the resources
    to type T and returns them.
    """
    def __call__(self, use_auth=True, **kwargs) -> List[T]:
        resource_url = self.format_url_and_remove_params(kwargs)
        params = kwargs
        params["client_id"] = self.client.client_id
        headers = self.client.get_default_headers()
        if use_auth and self.client.authorization is not None:
            headers["Authorization"] = self.client.authorization
        resources = []
        with requests.get(resource_url, params=params, headers=headers) as r:
            if r.status_code in (400, 404, 500):
                return []
            r.raise_for_status()
            for resource in r.json():
                resources.append(self.convert_dict(resource))
        return resources
