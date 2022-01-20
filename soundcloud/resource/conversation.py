import datetime
from dataclasses import dataclass
from typing import List, Union

from soundcloud.resource.base import BaseData
from soundcloud.resource.message import Message
from soundcloud.resource.user import BasicUser, MissingUser


@dataclass
class Conversation(BaseData):
    id: str
    last_message: Message
    read: bool
    started_at: datetime.datetime
    summary: str
    users: List[Union[BasicUser, MissingUser]]
