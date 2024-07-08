from dataclasses import dataclass
from typing import Optional, Tuple

from soundcloud.resource.base import BaseData
from soundcloud.resource.comment import BasicComment

InteractionTypeValue = str


@dataclass
class InteractionCount(BaseData):
    count: Optional[int]
    interactionTypeValueUrn: Optional[InteractionTypeValue]


@dataclass
class UserInteraction(BaseData):
    targetUrn: Optional[str]
    userInteraction: Optional[InteractionTypeValue]
    interactionCounts: Optional[Tuple[InteractionCount, ...]]
    interactionTypeUrn: Optional[str]


@dataclass
class CommentWithInteractions(BaseData):
    comment: BasicComment
    likes: int
    """Number of likes on comment"""

    liked_by_creator: bool
    """Whether comment was liked by the track creator"""

    liked_by_user: bool
    """Whether the current logged in user liked the comment"""
