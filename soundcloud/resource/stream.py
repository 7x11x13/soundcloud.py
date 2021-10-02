import datetime
from dataclasses import dataclass
from typing import Optional

from dacite import from_dict, Config

from soundcloud.resource.base import BaseData
from soundcloud.resource.track import BasicTrack
from soundcloud.resource.playlist import BasicAlbumPlaylist
from soundcloud.resource.user import BasicUser

@dataclass
class BaseStreamItem(BaseData):
    created_at: datetime.datetime
    type: str
    user: BasicUser
    uuid: str
    caption: Optional[str]

@dataclass
class Reposted(BaseData):
    target_urn: str
    user_urn: str
    caption: Optional[str]

@dataclass
class BaseStreamRepostItem(BaseStreamItem):
    reposted: Optional[Reposted]

@dataclass
class TrackStreamItem(BaseStreamItem):
    track: BasicTrack
    
@dataclass
class TrackStreamRepostItem(BaseStreamRepostItem):
    track: BasicTrack
    
@dataclass
class PlaylistStreamItem(BaseStreamItem):
    playlist: BasicAlbumPlaylist
    
@dataclass
class PlaylistStreamRepostItem(BaseStreamRepostItem):
    playlist: BasicAlbumPlaylist
