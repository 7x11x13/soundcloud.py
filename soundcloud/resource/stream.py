import datetime
from dataclasses import dataclass
from typing import Optional

from soundcloud.resource.base import BaseData
from soundcloud.resource.playlist import BasicAlbumPlaylist
from soundcloud.resource.track import BasicTrack
from soundcloud.resource.user import BasicUser


@dataclass(frozen=True)
class BaseStreamItem(BaseData):
    created_at: datetime.datetime
    type: str
    user: BasicUser
    uuid: str
    caption: Optional[str]


@dataclass(frozen=True)
class Reposted(BaseData):
    target_urn: str
    user_urn: str
    caption: Optional[str]


@dataclass(frozen=True)
class BaseStreamRepostItem(BaseStreamItem):
    reposted: Optional[Reposted]


@dataclass(frozen=True)
class TrackStreamItem(BaseStreamItem):
    """Track post in user's feed"""

    track: BasicTrack


@dataclass(frozen=True)
class TrackStreamRepostItem(BaseStreamRepostItem):
    """Track repost in user's feed"""

    track: BasicTrack


@dataclass(frozen=True)
class PlaylistStreamItem(BaseStreamItem):
    """Album or playlist post in user's feed"""

    playlist: BasicAlbumPlaylist


@dataclass(frozen=True)
class PlaylistStreamRepostItem(BaseStreamRepostItem):
    """Album or playlist repost in user's feed"""

    playlist: BasicAlbumPlaylist
