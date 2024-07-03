import datetime
from dataclasses import dataclass

from soundcloud.resource.base import BaseData
from soundcloud.resource.track import CommentTrack
from soundcloud.resource.user import BasicUser


@dataclass(frozen=True)
class CommentSelf(BaseData):
    urn: str


@dataclass(frozen=True)
class BasicComment(BaseData):
    """Comment without a specified track"""

    kind: str
    id: int
    body: str
    created_at: datetime.datetime
    timestamp: int
    track_id: int
    user_id: int
    self: CommentSelf
    user: BasicUser


@dataclass(frozen=True)
class Comment(BasicComment):
    """Comment with a specified track"""

    track: CommentTrack
