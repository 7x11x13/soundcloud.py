import datetime
from dataclasses import dataclass
from typing import Optional

from soundcloud.resource.base import BaseData
from soundcloud.resource.track import CommentTrack
from soundcloud.resource.user import BasicUser


@dataclass
class CommentSelf(BaseData):
    urn: str


@dataclass
class BasicComment(BaseData):
    """Comment without a specified track"""

    kind: str
    id: int
    body: str
    created_at: datetime.datetime
    timestamp: Optional[int]
    track_id: int
    user_id: int
    self: CommentSelf
    user: BasicUser


@dataclass
class Comment(BasicComment):
    """Comment with a specified track"""

    track: CommentTrack
