import datetime
from dataclasses import dataclass
from typing import Optional, Tuple, Union

from soundcloud.resource.base import BaseData
from soundcloud.resource.base_item import BaseItem
from soundcloud.resource.track import BasicTrack, MiniTrack
from soundcloud.resource.user import BasicUser, User


@dataclass
class BaseAlbumPlaylist(BaseItem):
    managed_by_feeds: bool
    set_type: str
    is_album: bool
    published_at: Optional[datetime.datetime]
    track_count: int
    tracks: Tuple[Union[BasicTrack, MiniTrack], ...]


@dataclass
class AlbumPlaylist(BaseAlbumPlaylist):
    """Playlist or album with full user info"""

    user: User


@dataclass
class BasicAlbumPlaylist(BaseAlbumPlaylist):
    """Playlist or album with partial user info"""

    user: BasicUser


@dataclass
class AlbumPlaylistNoTracks(BaseData):
    """Playlist or album with no track info"""

    artwork_url: Optional[str]
    created_at: datetime.datetime
    duration: int
    id: int
    kind: str
    last_modified: datetime.datetime
    likes_count: Optional[int]
    managed_by_feeds: bool
    permalink: str
    permalink_url: str
    public: bool
    reposts_count: Optional[int]
    secret_token: Optional[str]
    sharing: str
    title: str
    track_count: int
    uri: str
    user_id: int
    set_type: str
    is_album: bool
    published_at: Optional[datetime.datetime]
    release_date: Optional[str]
    display_date: datetime.datetime
    user: BasicUser
