import datetime
from dataclasses import dataclass

from soundcloud.resource.base import BaseData
from soundcloud.resource.track import CommentTrack
from soundcloud.resource.user import BasicUser

@dataclass
class CommentSelf(BaseData):
    urn: str

@dataclass
class BasicComment(BaseData):
    kind: str
    id: int
    body: str
    created_at: datetime.datetime
    timestamp: int
    track_id: int
    user_id: int
    self: CommentSelf
    user: BasicUser
    
@dataclass
class Comment(BasicComment):
    track: CommentTrack