import datetime
from dataclasses import dataclass
from typing import Optional, Union

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
    tracks: list[Union[BasicTrack, MiniTrack]]
    
@dataclass
class AlbumPlaylist(BaseAlbumPlaylist):
    user: User
    
@dataclass
class BasicAlbumPlaylist(BaseAlbumPlaylist):
    user: BasicUser
