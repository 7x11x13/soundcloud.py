import datetime
from dataclasses import dataclass

from soundcloud.resource.base import BaseData
from soundcloud.resource.playlist import AlbumPlaylistNoTracks
from soundcloud.resource.track import BasicTrack


@dataclass(frozen=True)
class BaseLike(BaseData):
    created_at: datetime.datetime
    kind: str


@dataclass(frozen=True)
class TrackLike(BaseLike):
    """Like on a track"""

    track: BasicTrack


@dataclass(frozen=True)
class PlaylistLike(BaseLike):
    """Like on a playlist"""

    playlist: AlbumPlaylistNoTracks
