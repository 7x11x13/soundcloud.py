import datetime
from dataclasses import dataclass
from typing import Tuple, Union

from soundcloud.resource.base import BaseData
from soundcloud.resource.message import Message
from soundcloud.resource.user import BasicUser, MissingUser


@dataclass
class Conversation(BaseData):
    """DM conversation between two users"""

    id: str
    last_message: Message
    read: bool
    started_at: datetime.datetime
    summary: str
    users: Tuple[Union[BasicUser, MissingUser], ...]
