import datetime
from dataclasses import dataclass
from typing import Optional

from dacite import from_dict

from soundcloud.resource.base import BaseData
from soundcloud.resource.playlist import AlbumPlaylistNoTracks
from soundcloud.resource.track import BasicTrack

@dataclass
class BaseLike(BaseData):
    created_at: datetime.datetime
    kind: str     

@dataclass
class TrackLike(BaseLike):
    track: BasicTrack

@dataclass
class PlaylistLike(BaseLike):
    playlist: AlbumPlaylistNoTracks