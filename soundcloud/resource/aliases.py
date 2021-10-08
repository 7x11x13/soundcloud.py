from typing import Union

from soundcloud.resource.like import PlaylistLike, TrackLike
from soundcloud.resource.playlist import AlbumPlaylist
from soundcloud.resource.stream import (PlaylistStreamItem,
                                        PlaylistStreamRepostItem,
                                        TrackStreamItem, TrackStreamRepostItem)
from soundcloud.resource.track import Track
from soundcloud.resource.user import User

Like = Union[TrackLike, PlaylistLike]
RepostItem = Union[TrackStreamRepostItem, PlaylistStreamRepostItem]
SearchItem = Union[User, Track, AlbumPlaylist]
StreamItem = Union[TrackStreamItem, PlaylistStreamItem, TrackStreamRepostItem, PlaylistStreamRepostItem]
