import datetime
from dataclasses import dataclass
from typing import List, Optional, Union

from dacite import from_dict

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
    tracks: List[Union[BasicTrack, MiniTrack]]
    
@dataclass
class AlbumPlaylist(BaseAlbumPlaylist):
    user: User
    
@dataclass
class BasicAlbumPlaylist(BaseAlbumPlaylist):
    user: BasicUser

@dataclass
class AlbumPlaylistNoTracks(BaseData):
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