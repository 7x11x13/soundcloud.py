from typing import Union

from soundcloud.resource.like import PlaylistLike, TrackLike
from soundcloud.resource.playlist import AlbumPlaylist
from soundcloud.resource.stream import (
    PlaylistStreamItem,
    PlaylistStreamRepostItem,
    TrackStreamItem,
    TrackStreamRepostItem,
)
from soundcloud.resource.track import Track
from soundcloud.resource.user import User

Like = Union[TrackLike, PlaylistLike]
"""Generic like"""

RepostItem = Union[TrackStreamRepostItem, PlaylistStreamRepostItem]
"""Generic repost"""

SearchItem = Union[User, Track, AlbumPlaylist]
"""Generic search result"""

StreamItem = Union[
    TrackStreamItem, PlaylistStreamItem, TrackStreamRepostItem, PlaylistStreamRepostItem
]
"""Generic feed item"""
